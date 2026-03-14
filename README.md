# Stock Sentiment Analyzer 📈

An AI-powered tool that combines real stock market data with NLP-based 
sentiment analysis on financial news headlines to analyze market trends.

## What This Project Does
- Fetches 1 year of real-time stock price data for NSE-listed companies 
  (Reliance, TCS, Infosys, HDFC Bank, Wipro) using yfinance
- Calculates technical indicators — RSI, SMA, EMA, and MACD — to identify 
  trends and momentum
- Scrapes live financial news headlines using NewsAPI
- Runs sentiment analysis on each headline using VADER NLP, classifying 
  them as POSITIVE, NEGATIVE, or NEUTRAL with a confidence score

## Tech Stack
- Python, Pandas, NumPy
- yfinance — stock data
- pandas-ta — technical indicators
- NewsAPI — financial news
- VADER Sentiment — NLP
- Matplotlib — data visualization

## Project Structure
```
stock-sentiment-analyzer/
├── data/              # Saved CSVs of stock prices and news
├── notebooks/         # Jupyter notebooks for each stage
│   ├── 01_stock_data.ipynb
│   ├── 02_technical_indicators.ipynb
│   ├── 03_news_data.ipynb
│   └── 04_sentiment.ipynb
├── src/               # Source code (coming soon)
└── app.py             # Streamlit dashboard (coming soon)
```

## What I Learned
- How to work with real financial market data using Python
- Technical analysis indicators used by traders (RSI, MACD, Moving Averages)
- How to consume REST APIs and parse JSON data
- NLP sentiment analysis on financial text using VADER
- Connecting news sentiment to stock price movements

## Next Steps
- [ ] Correlate sentiment scores with actual price movements
- [ ] Build ML classification model to predict next-day price direction
- [ ] Deploy as a Streamlit dashboard
- [ ] Upgrade sentiment model to FinBERT for better financial NLP accuracy

## Status
🚧 Active development — Day 1 complete
