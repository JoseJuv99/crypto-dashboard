import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime

st.set_page_config(layout="wide", page_title="BTC/USDT Dashboard")

# === Sidebar Info ===
st.sidebar.title("📈 BTC/USDT Crypto Signals")
st.sidebar.markdown("""
**Features:**
- RSI 14 Overbought/Oversold
- Global M2 Liquidity Overlay (manual CSV)
- TradingView Live Chart
""")

# === Title ===
st.title("🧠 BTC/USDT Technical Dashboard")

# === Load BTC Data ===
st.subheader("📊 Price & RSI Chart (1H, 7D)")
btc = yf.download("BTC-USD", interval="1h", period="7d")
btc.dropna(inplace=True)

# === RSI Calculation ===
delta = btc["Close"].diff()
gain = delta.where(delta > 0, 0)
loss = -delta.where(delta < 0, 0)
avg_gain = gain.rolling(window=14).mean()
avg_loss = loss.rolling(window=14).mean()
rs = avg_gain / avg_loss
btc["RSI"] = 100 - (100 / (1 + rs))

# === Plot RSI ===
rsi_fig = go.Figure()
rsi_fig.add_trace(go.Scatter(x=btc.index, y=btc["RSI"], mode='lines', name='RSI 14'))
rsi_fig.add_hline(y=70, line_dash="dash", line_color="red", name="Overbought")
rsi_fig.add_hline(y=30, line_dash="dash", line_color="green", name="Oversold")
rsi_fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
st.plotly_chart(rsi_fig, use_container_width=True)

# === RSI Signal ===
latest_rsi = btc["RSI"].iloc[-1]
rsi_status = "Overbought" if latest_rsi > 80 else "Oversold" if latest_rsi < 30 else "Neutral"
st.metric("Current RSI 14", f"{latest_rsi:.2f}", help="Relative Strength Index")

# === TradingView Embed ===
st.subheader("📺 Live BTC/USDT Chart")
tv_embed = """
<iframe src="https://www.tradingview.com/widgetembed/?frameElementId=tradingview_ea098&symbol=BINANCE:BTCUSDT&interval=60&hidesidetoolbar=1&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=[]&theme=dark&style=1&timezone=Etc/UTC&withdateranges=1&hidevolume=1&hidelegend=0&studies_overrides={}&overrides={}&enabled_features=[]&disabled_features=[]&locale=en"
 width="100%" height="500" frameborder="0" allowtransparency="true" scrolling="no"></iframe>
"""
st.components.v1.html(tv_embed, height=500)

# === M2 Liquidity Chart ===
st.subheader("💰 Global M2 Liquidity (Sample Data)")
try:
    m2_data = pd.read_csv("m2_data.csv")
    m2_data["Date"] = pd.to_datetime(m2_data["Date"])
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=m2_data["Date"], y=m2_data["Value"], name="M2 Liquidity", line=dict(color="yellow")))
    fig2.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig2, use_container_width=True)
except Exception as e:
    st.error("M2 data file missing or invalid. Please upload 'm2_data.csv'.")

# === Footer ===
st.caption("Made with ❤️ using Streamlit | Data: Yahoo Finance, TradingView, Manual M2")
