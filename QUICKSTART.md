# Quick Start Guide - Sentiment Analysis & Gradio Interface

## New Features

This repository now includes:
1. **Sentiment Analysis News Provider** - AI-powered news sentiment analysis using GoogleNews and DistilRoBERTa
2. **Gradio Web Interface** - User-friendly web interface for TradingAgents

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
export OPENAI_API_KEY=your_openai_api_key
export ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
```

Or create a `.env` file:
```
OPENAI_API_KEY=your_openai_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
```

### 3. Launch Gradio Interface

```bash
python tradingagents_gradio.py
```

Then open your browser to `http://localhost:7860`

## Using Sentiment Analysis as Fallback News Source

The sentiment analysis provider is integrated as a fallback news source. To use it:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Configure sentiment news as fallback
config = DEFAULT_CONFIG.copy()
config["data_vendors"]["news_data"] = "alpha_vantage,sentiment"

# Initialize and run
ta = TradingAgentsGraph(debug=True, config=config)
state, decision = ta.propagate("NVDA", "2024-05-10")
```

## Features

### Gradio Interface
- **Trading Analysis Tab**: Full multi-agent trading analysis with configurable LLMs
- **Sentiment Analysis Tab**: Standalone news sentiment analysis for any asset

### Sentiment News Provider
- Fetches news from GoogleNews
- AI-powered sentiment analysis (positive/negative/neutral)
- Integrates seamlessly with TradingAgents fallback system
- Works as standalone tool or integrated news source

## Available News Data Vendors

- `alpha_vantage` - Alpha Vantage API (default)
- `sentiment` - GoogleNews with AI sentiment (NEW)
- `openai` - OpenAI-powered analysis
- `google` - Google News scraping
- `local` - Local/offline sources

Configure vendors in order of preference; system automatically falls back if primary fails:

```python
config["data_vendors"]["news_data"] = "alpha_vantage,sentiment,google"
```

## Documentation

See [INTEGRATION_DOCS.md](INTEGRATION_DOCS.md) for detailed documentation including:
- API reference
- Configuration examples
- Troubleshooting guide
- Architecture details

## Examples

### Example 1: Web Interface
```bash
python tradingagents_gradio.py
```

### Example 2: CLI with Sentiment News
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["data_vendors"]["news_data"] = "sentiment"

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("AAPL", "2024-05-10")
print(decision)
```

### Example 3: Standalone Sentiment Analysis
```python
from tradingagents.dataflows.sentiment_news import get_sentiment_provider

provider = get_sentiment_provider()
result = provider.get_news_with_sentiment(
    ticker="Bitcoin",
    start_date="2024-01-01",
    end_date="2024-01-10"
)
print(result)
```

## Requirements

Key new dependencies:
- `gradio` - Web interface
- `transformers` - Sentiment analysis models
- `torch` - Model inference
- `GoogleNews` - News scraping
- `textblob`, `beautifulsoup4`, `scikit-learn`, `plotly`

All dependencies are in `requirements.txt`.

## Notes

1. First run will download the sentiment model (~500MB) from HuggingFace
2. Requires internet access for model download and news fetching
3. GoogleNews has rate limits - use fallback configuration for reliability
4. See [INTEGRATION_DOCS.md](INTEGRATION_DOCS.md) for troubleshooting

## Original TradingAgents Documentation

See [README.md](README.md) for the original TradingAgents documentation and features.
