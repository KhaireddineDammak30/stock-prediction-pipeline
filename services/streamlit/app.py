"""
Stock Prediction Pipeline - Professional Dashboard
Real-time visualization of stock predictions and pipeline metrics
"""

import os
import sys
import time
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

# ============================================================================
# Configuration
# ============================================================================
HOST = os.getenv("CASSANDRA_HOST", "cassandra")
KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "market")
TABLE_PRED = os.getenv("CASSANDRA_TABLE_PRED", "predictions")
TABLE_FEATURES = os.getenv("CASSANDRA_TABLE_FEATURES", "features")

# ============================================================================
# Custom CSS for Professional Look
# ============================================================================
st.set_page_config(
    page_title="Stock Prediction Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196F3;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Database Connection
# ============================================================================
@st.cache_resource
def get_cassandra_session():
    """Get Cassandra session with retry logic"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            cluster = Cluster([HOST], connect_timeout=10)
    session = cluster.connect()
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor':'1'}};
    """)
    session.set_keyspace(KEYSPACE)
            return session, cluster
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                st.error(f"❌ Failed to connect to Cassandra after {max_retries} attempts: {e}")
                st.stop()
    return None, None

# ============================================================================
# Data Fetching Functions
# ============================================================================
@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_predictions(symbol, limit=5000):
    """Fetch predictions for a symbol"""
    try:
        session, _ = get_cassandra_session()
        query = session.prepare(f"""
            SELECT ts, y_pred, model, horizon 
            FROM {TABLE_PRED}
            WHERE symbol=? 
            ORDER BY ts DESC
            LIMIT ?
        """)
        rows = list(session.execute(query, [symbol, limit]))
        return rows
    except Exception as e:
        st.error(f"Error fetching predictions: {e}")
        return []

@st.cache_data(ttl=60)
def fetch_features(symbol, limit=1000):
    """Fetch features for a symbol"""
    try:
        session, _ = get_cassandra_session()
        query = session.prepare(f"""
            SELECT ts, sma_5, sma_20, bucket_start, bucket_end
            FROM {TABLE_FEATURES}
            WHERE symbol=?
            ORDER BY ts DESC
            LIMIT ?
        """)
        rows = list(session.execute(query, [symbol, limit]))
        return rows
    except Exception:
        return []

@st.cache_data(ttl=300)
def get_available_symbols():
    """Get list of available symbols"""
    try:
        session, _ = get_cassandra_session()
        query = SimpleStatement(f"SELECT DISTINCT symbol FROM {TABLE_PRED} LIMIT 100")
        symbols = [r.symbol for r in session.execute(query)]
        return sorted(set(symbols))
    except Exception:
        return []

# ============================================================================
# Visualization Functions
# ============================================================================
def create_prediction_chart(df):
    """Create professional prediction chart"""
    fig = go.Figure()
    
    # Main prediction line
    fig.add_trace(go.Scatter(
        x=df['ts'],
        y=df['y_pred'],
        mode='lines',
        name='Predicted Price',
        line=dict(color='#1f77b4', width=2),
        hovertemplate='<b>%{fullData.name}</b><br>' +
                      'Time: %{x}<br>' +
                      'Price: $%{y:.2f}<extra></extra>'
    ))
    
    # Add trend line
    if len(df) > 1:
        z = np.polyfit(range(len(df)), df['y_pred'], 1)
        p = np.poly1d(z)
        fig.add_trace(go.Scatter(
            x=df['ts'],
            y=p(range(len(df))),
            mode='lines',
            name='Trend',
            line=dict(color='#ff7f0e', width=1, dash='dash'),
            opacity=0.7
        ))
    
    fig.update_layout(
        title={
            'text': f'Stock Price Predictions - {df["symbol"].iloc[0] if "symbol" in df.columns else "N/A"}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title="Timestamp",
        yaxis_title="Predicted Price ($)",
        hovermode='x unified',
        template='plotly_white',
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_features_chart(features_df):
    """Create features visualization"""
    if features_df.empty:
        return None
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Moving Averages', 'Price Prediction'),
        vertical_spacing=0.1,
        row_heights=[0.5, 0.5]
    )
    
    # SMA lines
    if 'sma_5' in features_df.columns:
        fig.add_trace(
            go.Scatter(x=features_df['ts'], y=features_df['sma_5'], 
                      name='SMA-5', line=dict(color='#2ca02c')),
            row=1, col=1
        )
    
    if 'sma_20' in features_df.columns:
        fig.add_trace(
            go.Scatter(x=features_df['ts'], y=features_df['sma_20'], 
                      name='SMA-20', line=dict(color='#d62728')),
            row=1, col=1
        )
    
    fig.update_layout(
        title="Technical Indicators",
        template='plotly_white',
        height=600,
        showlegend=True
    )
    
    return fig

# ============================================================================
# Main Application
# ============================================================================
def main():
    # Initialize connection
    try:
        session, cluster = get_cassandra_session()
    except Exception as e:
        st.error(f"❌ Database connection error: {e}")
        st.stop()
    
    # Header
    st.markdown('<h1 class="main-header">📈 Stock Prediction Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Symbol selection
        available_symbols = get_available_symbols()
        if available_symbols:
            selected_symbol = st.selectbox(
                "Select Stock Symbol",
                options=available_symbols,
                index=0 if 'AAPL' in available_symbols else 0
            )
        else:
            selected_symbol = st.text_input("Enter Stock Symbol", value="AAPL").upper().strip()
        
        st.markdown("---")
        
        # Refresh button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        
        # Pipeline status
        st.header("📊 Pipeline Status")
        st.info("""
        **Services:**
        - Producer: ✅ Running
        - Spark: ✅ Active
        - Cassandra: ✅ Connected
        """)
        
        st.markdown("---")
        
        # Quick links
        st.header("🔗 Quick Links")
        st.markdown("""
        - [Spark UI](http://localhost:8080)
        - [Prometheus](http://localhost:9090)
        - [Grafana](http://localhost:3000)
        """)
    
    # Main content
    if not selected_symbol:
        st.warning("⚠️ Please select or enter a stock symbol")
        st.stop()
    
    # Fetch data
    with st.spinner(f"Loading predictions for {selected_symbol}..."):
        predictions = fetch_predictions(selected_symbol)
        features = fetch_features(selected_symbol)
    
    if not predictions:
        st.warning(f"⚠️ No predictions found for symbol '{selected_symbol}'")
        
        if available_symbols:
            st.info(f"💡 Available symbols: {', '.join(available_symbols)}")
        else:
            st.info("💡 Make sure you've run the batch training job to generate predictions")
        st.stop()
    
    # Convert to DataFrame
    df = pd.DataFrame([{
        "symbol": selected_symbol,
        "ts": r.ts,
        "y_pred": float(r.y_pred) if r.y_pred is not None else None,
        "model": r.model,
        "horizon": r.horizon
    } for r in predictions])
    
    df = df.sort_values("ts").reset_index(drop=True)
    df = df.dropna(subset=["y_pred"])

if df.empty:
        st.warning("No valid predictions to display")
        st.stop()
    
    # Key Metrics
    st.markdown("### 📊 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Predictions",
            f"{len(df):,}",
            help="Total number of predictions available"
        )
    
    with col2:
        latest_price = df['y_pred'].iloc[-1]
        prev_price = df['y_pred'].iloc[-2] if len(df) > 1 else latest_price
        delta = latest_price - prev_price
        st.metric(
            "Latest Prediction",
            f"${latest_price:.2f}",
            delta=f"${delta:.2f}" if len(df) > 1 else None
        )
    
    with col3:
        avg_price = df['y_pred'].mean()
        st.metric(
            "Average Price",
            f"${avg_price:.2f}",
            help="Average predicted price"
        )
    
    with col4:
        min_price = df['y_pred'].min()
        max_price = df['y_pred'].max()
        price_range = max_price - min_price
        st.metric(
            "Price Range",
            f"${price_range:.2f}",
            help=f"Min: ${min_price:.2f}, Max: ${max_price:.2f}"
        )
    
    with col5:
        model = df['model'].iloc[0] if 'model' in df.columns else "N/A"
        st.metric(
            "Model",
            model,
            help="ML model used for predictions"
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📈 Price Predictions")
        fig = create_prediction_chart(df)
    st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Statistics")
        
        stats_data = {
            "Metric": ["Mean", "Median", "Std Dev", "Min", "Max"],
            "Value": [
                f"${df['y_pred'].mean():.2f}",
                f"${df['y_pred'].median():.2f}",
                f"${df['y_pred'].std():.2f}",
                f"${df['y_pred'].min():.2f}",
                f"${df['y_pred'].max():.2f}"
            ]
        }
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    # Features visualization
    if features:
        st.markdown("---")
        st.markdown("### 🔍 Technical Indicators")
        features_df = pd.DataFrame([{
            "ts": r.ts,
            "sma_5": float(r.sma_5) if r.sma_5 else None,
            "sma_20": float(r.sma_20) if r.sma_20 else None,
        } for r in features])
        features_df = features_df.sort_values("ts").reset_index(drop=True)
        
        if not features_df.empty:
            fig_features = create_features_chart(features_df)
            if fig_features:
                st.plotly_chart(fig_features, use_container_width=True)
    
    # Data table
    st.markdown("---")
    st.markdown("### 📋 Recent Predictions")
    
    display_df = df[["ts", "y_pred", "model", "horizon"]].tail(20).copy()
    display_df["y_pred"] = display_df["y_pred"].apply(lambda x: f"${x:.2f}")
    display_df.columns = ["Timestamp", "Predicted Price", "Model", "Horizon"]
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; padding: 1rem;'>"
        "Stock Prediction Pipeline Dashboard | Last updated: " + 
        datetime.now().strftime("%Y-%m-%d %H:%M:%S") +
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
