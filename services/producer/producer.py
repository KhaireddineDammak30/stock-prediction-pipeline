"""
Stock Data Producer
Generates synthetic stock tick data and publishes to Kafka
"""

import os
import time
import json
import random
import logging
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable, KafkaError

# ============================================================================
# Configuration
# ============================================================================
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TOPIC = os.getenv("TOPIC", "ticks")
SYMBOLS = os.getenv("SYMBOLS", "AAPL,MSFT,GOOGL,AMZN").split(",")
INTERVAL = int(os.getenv("INTERVAL_SEC", "3"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "10"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))

# ============================================================================
# Logging Setup
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Kafka Connection
# ============================================================================
def connect_kafka():
    """Connect to Kafka with retry logic"""
    for attempt in range(MAX_RETRIES):
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                acks='all',  # Wait for all replicas
                retries=3,
                max_in_flight_requests_per_connection=1,
                enable_idempotence=True
            )
            logger.info(f"✅ Connected to Kafka at {KAFKA_BROKER}")
            return producer
        except NoBrokersAvailable:
            logger.warning(f"Waiting for Kafka... (attempt {attempt+1}/{MAX_RETRIES})")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            logger.error(f"Unexpected error connecting to Kafka: {e}")
            time.sleep(RETRY_DELAY)
    
    raise RuntimeError(f"❌ Could not connect to Kafka after {MAX_RETRIES} retries")

# ============================================================================
# Data Generation
# ============================================================================
def generate_tick(symbol):
    """
    Generate a synthetic stock tick
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
    
    Returns:
        dict: Stock tick data
    """
    now = datetime.utcnow()
    ts_str = now.strftime("%Y-%m-%dT%H:%M:%S.%f")
    
    # Generate realistic price range based on symbol
    base_price = 150.0  # Base price
    price_variation = random.uniform(-10, 10)
    close_price = base_price + price_variation
    
    return {
        "symbol": symbol,
        "ts": ts_str,  # Format: 2024-01-01T12:00:00.123456 (no Z)
        "open": round(close_price + random.uniform(-2, 2), 2),
        "high": round(close_price + random.uniform(0, 5), 2),
        "low": round(close_price - random.uniform(0, 5), 2),
        "close": round(close_price, 2),
        "volume": random.randint(1000, 10000),
    }

# ============================================================================
# Main Execution
# ============================================================================
def main():
    """Main producer loop"""
    producer = None
    tick_count = 0
    
    try:
    producer = connect_kafka()
        logger.info(f"🚀 Starting producer - Sending ticks to topic '{TOPIC}' every {INTERVAL}s")
        logger.info(f"📊 Symbols: {', '.join(SYMBOLS)}")

    while True:
        for symbol in SYMBOLS:
                try:
            tick = generate_tick(symbol)
                    future = producer.send(TOPIC, tick)
                    
                    # Wait for send to complete (optional, for reliability)
                    record_metadata = future.get(timeout=10)
                    
                    tick_count += 1
                    if tick_count % 10 == 0:  # Log every 10 ticks
                        logger.info(f"✅ Sent {tick_count} ticks (last: {symbol} @ ${tick['close']:.2f})")
                    else:
                        logger.debug(f"Sent tick: {tick}")
                
                except KafkaError as e:
                    logger.error(f"❌ Kafka error sending tick: {e}")
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"❌ Unexpected error: {e}")
                    time.sleep(1)
            
        producer.flush()
        time.sleep(INTERVAL)
    
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down producer...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise
    finally:
        if producer:
            producer.flush()
            producer.close()
            logger.info("✅ Producer closed")

if __name__ == "__main__":
    main()
