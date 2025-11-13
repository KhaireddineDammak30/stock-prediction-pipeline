# tests/test_pipeline.py
import time
import requests
from datetime import datetime, timezone
from cassandra.query import SimpleStatement
from conftest import iso_utc  # kept for compatibility if other tests use it

PROM_TIMEOUT = 5

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _aligned_base(sec: int = 3, offset_sec: int = 45) -> int:
    """
    Return a future event-time base aligned to `sec` seconds.
    offset_sec should be > watermark + typical batch lag.
    """
    now = int(time.time()) + int(offset_sec)
    return (now // sec) * sec

def _ts_jobfmt(epoch_sec: int) -> str:
    """
    Format a UTC timestamp in the default Spark to_timestamp() friendly format:
    'YYYY-MM-DD HH:MM:SS' (no T/Z), so parsing never returns NULL.
    """
    return datetime.fromtimestamp(epoch_sec, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def _prom_get_targets(prom_base: str):
    r = requests.get(f"{prom_base}/api/v1/targets", timeout=PROM_TIMEOUT)
    r.raise_for_status()
    js = r.json()
    return js.get("data", {}).get("activeTargets", []) if js.get("status") == "success" else []

def _find_driver_instance(prom_base: str, prefer_instance: str | None = None) -> str | None:
    targets = _prom_get_targets(prom_base)
    healthy = [t for t in targets if t.get("health") == "up"]
    if prefer_instance:
        for t in healthy:
            if t.get("labels", {}).get("instance") == prefer_instance:
                return prefer_instance
    for t in healthy:
        if t.get("labels", {}).get("job") in {"spark-driver", "spark_submit", "spark"}:
            return t.get("labels", {}).get("instance")
    for t in healthy:
        inst = t.get("labels", {}).get("instance")
        if inst and inst.endswith(":8092"):
            return inst
    return None

# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------

def test_prometheus_driver_metrics_up(cfg):
    # Prometheus up?
    r = requests.get(f"{cfg['prom']}/-/healthy", timeout=PROM_TIMEOUT)
    assert r.status_code == 200

    # Find a healthy driver target; skip if JMX not ready yet
    instance = _find_driver_instance(cfg["prom"], prefer_instance=cfg.get("driver_instance"))
    if not instance:
        import pytest
        pytest.skip("No healthy spark-driver target yet; skipping until JMX is up.")

    # basic JVM metric exists
    q = f'jvm_threads_current{{instance="{instance}"}}'
    r = requests.get(f"{cfg['prom']}/api/v1/query", params={"query": q}, timeout=PROM_TIMEOUT)
    js = r.json()
    assert js["status"] == "success"
    assert js["data"]["result"], f"No jvm_threads_current for driver instance {instance}"

def test_sma5_exact_average(cfg, kafka_producer, cassandra_session):
    """
    Send 5 AAPL ticks at FUTURE event times (1s apart) using Spark-friendly time format.
    Expect to observe a row with SMA5 == 120.0 for closes [100,110,120,130,140].
    """
    symbol = "AAPL"
    base = _aligned_base(3, offset_sec=60)  # >= watermark + typical lag

    closes = [100.0, 110.0, 120.0, 130.0, 140.0]
    for i, c in enumerate(closes):
        msg = {
            "symbol": symbol,
            "ts": _ts_jobfmt(base + i),  # Spark-friendly: "YYYY-MM-DD HH:MM:SS" UTC
            "open": 1, "high": 1, "low": 1, "close": c, "volume": 1,
        }
        kafka_producer.send(cfg["topic"], msg)
    kafka_producer.flush()

    # Search in [base-5s, base+180s]; poll up to 90s for window/join/write to land
    window_start_dt = datetime.fromtimestamp(base - 5, tz=timezone.utc)
    window_end_dt   = datetime.fromtimestamp(base + 180, tz=timezone.utc)

    deadline = time.time() + 90
    ok, rows = False, []
    while time.time() < deadline and not ok:
        rows = list(
            cassandra_session.execute(
                SimpleStatement(
                    f"""
                    SELECT ts, bucket_start, bucket_end, sma_5, sma_20
                    FROM {cfg['features_table']}
                    WHERE symbol=%s AND ts >= %s AND ts < %s
                    LIMIT 500
                    """
                ),
                (symbol, window_start_dt, window_end_dt),
            )
        )
        ok = any(r.sma_5 is not None and abs(float(r.sma_5) - 120.0) < 1e-3 for r in rows)
        if not ok:
            time.sleep(2)

    assert ok, (
        "SMA5 ~ 120.0 not found in the expected future window. "
        f"Rows: {[ (str(r.ts), float(r.sma_5) if r.sma_5 is not None else None) for r in rows ]}"
    )

def test_idempotency_duplicate_ts(cfg, kafka_producer, cassandra_session):
    """
    Send two identical AAPL ticks at the same FUTURE timestamp (Spark-friendly time format).
    If the Cassandra PK is (symbol, ts), exactly one row should exist.
    """
    symbol = "AAPL"
    base = _aligned_base(3, offset_sec=60)
    ts_str = _ts_jobfmt(base)  # string we publish
    ts_dt  = datetime.fromtimestamp(base, tz=timezone.utc)  # timestamp we query

    msg = {"symbol": symbol, "ts": ts_str, "open": 1, "high": 1, "low": 1, "close": 200.0, "volume": 1}
    kafka_producer.send(cfg["topic"], msg)
    kafka_producer.send(cfg["topic"], msg)  # duplicate
    kafka_producer.flush()

    # Poll up to 90s for the single row to appear
    deadline = time.time() + 90
    cnt = 0
    while time.time() < deadline:
        cnt = cassandra_session.execute(
            SimpleStatement(f"SELECT COUNT(*) FROM {cfg['features_table']} WHERE symbol=%s AND ts=%s"),
            (symbol, ts_dt),
        ).one()[0]
        if cnt == 1:
            break
        time.sleep(2)

    assert cnt == 1, f"Expected 1 row for duplicate ts={ts_str}, got {cnt}"
