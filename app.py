import streamlit.components.v1 as components
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinance as yf
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="FinSight - Stock Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS for fintech look ───────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252a3d);
        border: 1px solid #2e3450;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 5px;
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #00d4aa; }
    .metric-label { font-size: 13px; color: #8892b0; margin-top: 5px; }
    .positive { color: #00d4aa; }
    .negative { color: #ff4b6e; }
    .alert-box {
        background: #1a1f2e;
        border-left: 4px solid #f0b429;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
    }
    h1 { color: #ccd6f6 !important; }
    h2, h3 { color: #a8b2d8 !important; }
    .stSelectbox label { color: #8892b0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────
st.markdown("# FinSight - Stock Intelligence Platform")
st.markdown("*AI-powered sentiment analysis and portfolio tracking for Indian markets*")
st.divider()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Settings")
    ticker_map = {
        "Reliance": "RELIANCE.NS",
        "TCS": "TCS.NS",
        "Infosys": "INFY.NS",
        "HDFC Bank": "HDFCBANK.NS",
        "Wipro": "WIPRO.NS",
        "Nifty 50": "^NSEI",
        "Adani Ports": "ADANIPORTS.NS",
        "Asian Paints": "ASIANPAINT.NS"
    }
    company = st.selectbox("Select Stock", list(ticker_map.keys()))
    period = st.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y"], index=1)
    api_key = st.text_input("NewsAPI Key", type="password")
    st.divider()
    st.markdown("### Price Alerts")
    alert_price = st.number_input("Alert me if price goes below (Rs.)", min_value=0.0, value=0.0)
    alert_high = st.number_input("Alert me if price goes above (Rs.)", min_value=0.0, value=0.0)

ticker = ticker_map[company]

# ── Fetch Data ────────────────────────────────────────────
stock = yf.download(ticker, period=period, auto_adjust=True)

close = stock["Close"].squeeze()
current_price = float(close.iloc[-1])
prev_price = float(close.iloc[-2])
change = current_price - prev_price
change_pct = (change / prev_price) * 100
high_52w = float(close.max())
low_52w = float(close.min())

# ── Price Alert Check ─────────────────────────────────────
if alert_price > 0 and current_price < alert_price:
    st.markdown(f"""
    <div class="alert-box">
    ALERT: {company} is below your target of Rs.{alert_price:.0f} — Current: Rs.{current_price:.1f}
    </div>""", unsafe_allow_html=True)

if alert_high > 0 and current_price > alert_high:
    st.markdown(f"""
    <div class="alert-box">
    ALERT: {company} is above your target of Rs.{alert_high:.0f} — Current: Rs.{current_price:.1f}
    </div>""", unsafe_allow_html=True)

# ── Metric Cards ──────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
color = "positive" if change >= 0 else "negative"
arrow = "▲" if change >= 0 else "▼"

with col1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">Rs.{current_price:.1f}</div>
        <div class="metric-label">Current Price</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value {color}">{arrow} {change_pct:.2f}%</div>
        <div class="metric-label">Today's Change</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">Rs.{high_52w:.1f}</div>
        <div class="metric-label">Period High</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">Rs.{low_52w:.1f}</div>
        <div class="metric-label">Period Low</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Candlestick Chart ─────────────────────────────────────
st.markdown("### Price Chart with Technical Indicators")

stock["SMA_20"] = close.rolling(window=20).mean()
stock["EMA_20"] = close.ewm(span=20, adjust=False).mean()

delta = close.diff()
gain = delta.clip(lower=0).rolling(window=14).mean()
loss = -delta.clip(upper=0).rolling(window=14).mean()
stock["RSI"] = 100 - (100 / (1 + gain / loss))

fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                    row_heights=[0.7, 0.3],
                    vertical_spacing=0.05)

fig.add_trace(go.Candlestick(
    x=stock.index,
    open=stock["Open"].squeeze(),
    high=stock["High"].squeeze(),
    low=stock["Low"].squeeze(),
    close=close,
    name="Price",
    increasing_line_color="#00d4aa",
    decreasing_line_color="#ff4b6e"
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=stock.index, y=stock["SMA_20"],
    line=dict(color="#f0b429", width=1.2, dash="dash"),
    name="SMA 20"
), row=1, col=1)

fig.add_trace(go.Scatter(
    x=stock.index, y=stock["EMA_20"],
    line=dict(color="#7c6aff", width=1.2, dash="dash"),
    name="EMA 20"
), row=1, col=1)

rsi_vals = stock["RSI"].squeeze()
fig.add_trace(go.Scatter(
    x=stock.index, y=rsi_vals,
    line=dict(color="#a78bfa", width=1.2),
    name="RSI"
), row=2, col=1)

fig.add_hline(y=70, line_dash="dash", line_color="#ff4b6e", line_width=0.8, row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="#00d4aa", line_width=0.8, row=2, col=1)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0e1117",
    plot_bgcolor="#1e2130",
    height=600,
    showlegend=True,
    xaxis_rangeslider_visible=False,
    title=dict(text=f"{company} — {period} Candlestick Chart",
               font=dict(color="#ccd6f6", size=14)),
    legend=dict(bgcolor="#1e2130", font=dict(color="#ccd6f6"))
)
fig.update_yaxes(gridcolor="#2e3450", tickfont=dict(color="#8892b0"))
fig.update_xaxes(gridcolor="#2e3450", tickfont=dict(color="#8892b0"))

st.plotly_chart(fig, use_container_width=True)
# ── Live TradingView Chart ────────────────────────────────
st.divider()
st.markdown("### Live Chart")

# Map your tickers to TradingView format
tv_map = {
    "Reliance": "BSE:RELIANCE",
    "TCS": "BSE:TCS",
    "Infosys": "BSE:INFY",
    "HDFC Bank": "BSE:HDFCBANK",
    "Wipro": "BSE:WIPRO",
    "Nifty 50": "NSE:NIFTY",
    "Adani Ports": "BSE:ADANIPORTS",
    "Asian Paints": "BSE:ASIANPAINT"
}

tv_symbol = tv_map[company]

tv_html = f"""
<div class="tradingview-widget-container" style="height:500px;">
  <div id="tradingview_chart"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
  <script type="text/javascript">
  new TradingView.widget({{
    "width": "100%",
    "height": 500,
    "symbol": "{tv_symbol}",
    "interval": "D",
    "timezone": "Asia/Kolkata",
    "theme": "dark",
    "style": "1",
    "locale": "en",
    "toolbar_bg": "#1e2130",
    "enable_publishing": false,
    "allow_symbol_change": true,
    "studies": ["RSI@tv-basicstudies", "MASimple@tv-basicstudies"],
    "container_id": "tradingview_chart"
  }});
  </script>
</div>
"""

st.components.v1.html(tv_html, height=520)

# ── Portfolio Tracker ─────────────────────────────────────
st.divider()
st.markdown("### Portfolio Tracker")
st.markdown("*Add your holdings to track real-time P&L*")

if "portfolio" not in st.session_state:
    st.session_state.portfolio = []

col_a, col_b, col_c, col_d = st.columns([2, 1, 1, 1])
with col_a:
    p_stock = st.selectbox("Stock", list(ticker_map.keys()), key="p_stock")
with col_b:
    p_qty = st.number_input("Quantity", min_value=1, value=10, key="p_qty")
with col_c:
    p_buy = st.number_input("Buy Price (Rs.)", min_value=1.0, value=100.0, key="p_buy")
with col_d:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Add to Portfolio"):
        st.session_state.portfolio.append({
            "Stock": p_stock,
            "Ticker": ticker_map[p_stock],
            "Qty": p_qty,
            "Buy Price": p_buy
        })
        st.success(f"Added {p_stock}!")

if st.session_state.portfolio:
    rows = []
    total_invested = 0
    total_current = 0

    for holding in st.session_state.portfolio:
        live = yf.download(holding["Ticker"], period="1d", auto_adjust=True)
        live_price = float(live["Close"].values[-1])
        invested = holding["Buy Price"] * holding["Qty"]
        current = live_price * holding["Qty"]
        pnl = current - invested
        pnl_pct = (pnl / invested) * 100
        total_invested += invested
        total_current += current
        rows.append({
            "Stock": holding["Stock"],
            "Qty": holding["Qty"],
            "Buy Price": f"Rs.{holding['Buy Price']:.1f}",
            "Current Price": f"Rs.{live_price:.1f}",
            "Invested": f"Rs.{invested:,.0f}",
            "Current Value": f"Rs.{current:,.0f}",
            "P&L": f"{'+ ' if pnl >= 0 else '- '}Rs.{abs(pnl):,.0f}",
            "Return %": f"{'▲' if pnl >= 0 else '▼'} {abs(pnl_pct):.2f}%"
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True)

    total_pnl = total_current - total_invested
    total_pct = (total_pnl / total_invested) * 100
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Invested", f"Rs.{total_invested:,.0f}")
    c2.metric("Current Value", f"Rs.{total_current:,.0f}")
    c3.metric("Total P&L", f"Rs.{total_pnl:,.0f}", f"{total_pct:.2f}%")

    if st.button("Clear Portfolio"):
        st.session_state.portfolio = []
        st.rerun()

# ── Stock Comparison ──────────────────────────────────────
st.divider()
st.markdown("### Stock Comparison")
st.markdown("*Compare two stocks side by side*")

col_s1, col_s2 = st.columns(2)
with col_s1:
    stock1_name = st.selectbox("Stock 1", list(ticker_map.keys()), index=0, key="s1")
with col_s2:
    stock2_name = st.selectbox("Stock 2", list(ticker_map.keys()), index=1, key="s2")

if stock1_name != stock2_name:
    s1 = yf.download(ticker_map[stock1_name], period=period, auto_adjust=True)
    s2 = yf.download(ticker_map[stock2_name], period=period, auto_adjust=True)

    s1_norm = (s1["Close"].squeeze() / s1["Close"].squeeze().iloc[0]) * 100
    s2_norm = (s2["Close"].squeeze() / s2["Close"].squeeze().iloc[0]) * 100

    fig_cmp = go.Figure()

    fig_cmp.add_trace(go.Scatter(
        x=s1.index, y=s1_norm,
        name=stock1_name,
        line=dict(color="#00d4aa", width=2)
    ))

    fig_cmp.add_trace(go.Scatter(
        x=s2.index, y=s2_norm,
        name=stock2_name,
        line=dict(color="#ff4b6e", width=2)
    ))

    fig_cmp.add_hline(y=100, line_dash="dash",
                      line_color="#8892b0", line_width=0.8)

    fig_cmp.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#1e2130",
        height=400,
        title=dict(
            text=f"{stock1_name} vs {stock2_name} — Normalized Performance (Base 100)",
            font=dict(color="#ccd6f6", size=13)
        ),
        legend=dict(bgcolor="#1e2130", font=dict(color="#ccd6f6")),
        yaxis=dict(title="Indexed Price (Start = 100)",
                   gridcolor="#2e3450",
                   tickfont=dict(color="#8892b0")),
        xaxis=dict(gridcolor="#2e3450",
                   tickfont=dict(color="#8892b0"))
    )

    st.plotly_chart(fig_cmp, use_container_width=True)

    # Performance summary
    s1_return = ((s1["Close"].squeeze().iloc[-1] / s1["Close"].squeeze().iloc[0]) - 1) * 100
    s2_return = ((s2["Close"].squeeze().iloc[-1] / s2["Close"].squeeze().iloc[0]) - 1) * 100
    winner = stock1_name if s1_return > s2_return else stock2_name

    c1, c2, c3 = st.columns(3)
    c1.metric(f"{stock1_name} Return", f"{s1_return:.2f}%",
              f"{'▲' if s1_return >= 0 else '▼'}")
    c2.metric(f"{stock2_name} Return", f"{s2_return:.2f}%",
              f"{'▲' if s2_return >= 0 else '▼'}")
    c3.metric("Winner", winner, f"by {abs(s1_return - s2_return):.2f}%")
else:
    st.warning("Please select two different stocks to compare!")

# ── AI Stock Analyst Chatbot ──────────────────────────────
st.divider()
st.markdown("### AI Stock Analyst")
st.markdown("*Ask anything about the selected stock*")

groq_key = st.sidebar.text_input("Groq API Key (Free)", type="password")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if question := st.chat_input(f"Ask about {company}..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    if groq_key:
        context = f"""
        You are a financial analyst assistant. The user is viewing {company} stock.
        Current price: Rs.{current_price:.1f}
        Today's change: {change_pct:.2f}%
        Period high: Rs.{high_52w:.1f}
        Period low: Rs.{low_52w:.1f}
        RSI: {float(stock['RSI'].squeeze().iloc[-1]):.1f}
        Answer concisely and clearly. Focus on facts and analysis.
        """

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": context},
                    {"role": "user", "content": question}
                ],
                "max_tokens": 500
            }
        )

        resp_json = response.json()
        if "choices" in resp_json:
            answer = resp_json["choices"][0]["message"]["content"]
        elif "error" in resp_json:
            answer = f"API Error: {resp_json['error']['message']}"
        else:
            answer = f"Unexpected response: {resp_json}"

        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    else:
        with st.chat_message("assistant"):
            st.markdown("Please enter your Groq API key in the sidebar. Get one free at console.groq.com!")
# ── News Sentiment ────────────────────────────────────────
st.divider()
st.markdown("### News Sentiment Analysis")

if api_key:
    params = {
        "q": f"{company} stock",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": api_key
    }
    response = requests.get("https://newsapi.org/v2/everything", params=params)
    articles = response.json().get("articles", [])
    analyzer = SentimentIntensityAnalyzer()
    news_data = []
    for article in articles:
        score = analyzer.polarity_scores(str(article["title"]))["compound"]
        sentiment = "POSITIVE" if score > 0.05 else ("NEGATIVE" if score < -0.05 else "NEUTRAL")
        news_data.append({
            "Date": article["publishedAt"][:10],
            "Headline": article["title"],
            "Sentiment": sentiment,
            "Score": round(score, 3)
        })
    news_df = pd.DataFrame(news_data)
    if not news_df.empty:
        st.dataframe(news_df, use_container_width=True)
        avg = news_df["Score"].mean()
        col1, col2 = st.columns(2)
        col1.metric("Average Sentiment", f"{avg:.3f}", "Bullish" if avg > 0 else "Bearish")
        pos = len(news_df[news_df["Sentiment"] == "POSITIVE"])
        neg = len(news_df[news_df["Sentiment"] == "NEGATIVE"])
        col2.metric("Positive vs Negative", f"{pos} vs {neg}")
    else:
        st.warning("No news articles found. Try a different company or check your API key.")
else:
    st.info("Enter your NewsAPI key in the sidebar to see live news sentiment")