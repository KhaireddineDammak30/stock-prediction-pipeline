CREATE KEYSPACE IF NOT EXISTS market
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};

-- Features table for streaming job output (when TABLE_FEATURES != "features_by_bucket")
-- This stores aggregated features (SMA) computed from streaming windows
CREATE TABLE IF NOT EXISTS market.features (
    symbol text,
    ts timestamp,
    bucket_start timestamp,
    bucket_end timestamp,
    sma_5 double,
    sma_20 double,
    PRIMARY KEY (symbol, ts)
) WITH CLUSTERING ORDER BY (ts ASC);

CREATE TABLE IF NOT EXISTS market.predictions (
    symbol text,
    ts timestamp,
    y_pred double,
    model text,
    horizon text,
    PRIMARY KEY (symbol, ts)
) WITH CLUSTERING ORDER BY (ts ASC);

CREATE TABLE IF NOT EXISTS market.features_by_bucket (
    symbol       text,
    bucket_start timestamp,
    bucket_end   timestamp,
    sma_5        double,
    sma_20       double,
    PRIMARY KEY ((symbol), bucket_start)
) WITH CLUSTERING ORDER BY (bucket_start DESC)
  AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy'}
  AND compression = {'class': 'org.apache.cassandra.io.compress.LZ4Compressor'};
