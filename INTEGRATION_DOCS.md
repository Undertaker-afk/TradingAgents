# TradingAgents Integration Documentation

## Overview
This document describes the integration of sentiment analysis functionality and Gradio interface into the TradingAgents framework.

## New Features

### 1. Sentiment Analysis News Provider

A new sentiment-based news data source has been integrated into TradingAgents, providing news articles with AI-powered sentiment analysis as a fallback option.

**Location:** `tradingagents/dataflows/sentiment_news.py`

**Features:**
- Fetches news articles from GoogleNews
- Analyzes sentiment using DistilRoBERTa financial sentiment model
- Provides positive/negative/neutral classification with confidence scores
- Available as a fallback news source in TradingAgents

**Usage in TradingAgents:**

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Create custom config with sentiment news
config = DEFAULT_CONFIG.copy()
config["data_vendors"] = {
    "news_data": "sentiment"  # Use sentiment news as primary source
    # or
    "news_data": "alpha_vantage,sentiment"  # Use sentiment as fallback
}

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("NVDA", "2024-05-10")
```

**Available News Vendors:**
- `alpha_vantage` - Alpha Vantage news API (default)
- `sentiment` - GoogleNews with AI sentiment analysis (NEW)
- `openai` - OpenAI-powered news analysis
- `google` - Google News scraping
- `local` - Local/offline news sources

### 2. Gradio Web Interface

A new web-based interface has been created to make TradingAgents more accessible and user-friendly.

**Location:** `tradingagents_gradio.py`

**Features:**

#### Tab 1: Trading Analysis
- Full TradingAgents multi-agent analysis
- Configure LLM models (deep think and quick think)
- Adjust debate rounds for research depth
- Select news data sources
- View trading decisions and detailed analysis

#### Tab 2: Sentiment Analysis
- Standalone sentiment analysis tool
- Analyze news sentiment for any asset/ticker
- Configurable lookback period and article limit
- Visual sentiment summary

**Running the Interface:**

```bash
# Command line
python tradingagents_gradio.py

# Or in Python code
from tradingagents_gradio import create_tradingagents_interface
demo = create_tradingagents_interface()
demo.launch()
```

The interface will be available at `http://localhost:7860` by default.

## Configuration Examples

### Using Sentiment News as Fallback

```python
config = DEFAULT_CONFIG.copy()
config["data_vendors"] = {
    "core_stock_apis": "yfinance",
    "technical_indicators": "yfinance",
    "fundamental_data": "alpha_vantage",
    "news_data": "alpha_vantage,sentiment"  # Sentiment as fallback
}
```

### Using Multiple News Sources

The system will automatically fall back to other sources if the primary source fails:

```python
config["data_vendors"] = {
    "news_data": "alpha_vantage,sentiment,google,local"
}
```

Order matters: sources are tried left-to-right, stopping at the first successful one (for single-vendor configs).

## Dependencies

New dependencies added to `requirements.txt`:
- `gradio` - Web interface framework
- `transformers` - For sentiment analysis model
- `torch` - PyTorch for model inference
- `GoogleNews` - Google News scraping
- `textblob` - Text processing utilities
- `beautifulsoup4` - HTML parsing
- `scikit-learn` - Machine learning utilities
- `plotly` - Interactive visualizations (for app.py compatibility)
- `chronos-forecasting` - Time series forecasting (for app.py compatibility)

## Installation

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install specific new dependencies
pip install gradio transformers torch GoogleNews textblob beautifulsoup4
```

## API Reference

### Sentiment News Provider

```python
from tradingagents.dataflows.sentiment_news import get_sentiment_provider

# Get provider instance
provider = get_sentiment_provider()

# Fetch and analyze news
result = provider.get_news_with_sentiment(
    ticker="AAPL",
    start_date="2024-01-01",
    end_date="2024-01-10",
    max_results=10
)

# Get global market news
global_news = provider.get_global_news_with_sentiment(
    curr_date="2024-01-10",
    look_back_days=7,
    limit=5
)
```

### Gradio Interface

```python
from tradingagents_gradio import create_tradingagents_interface

# Create and launch interface
demo = create_tradingagents_interface()
demo.launch(
    server_name="0.0.0.0",  # Listen on all interfaces
    server_port=7860,        # Port number
    share=False,             # Don't create public link
    show_error=True          # Show detailed errors
)
```

## Architecture Integration

The sentiment news provider integrates seamlessly with TradingAgents' existing vendor routing system:

1. **Sentiment Module** (`sentiment_news.py`) provides:
   - `get_news_sentiment()` - For stock-specific news
   - `get_global_news_sentiment()` - For market-wide news

2. **Interface Module** (`interface.py`) registers sentiment as a vendor:
   - Added to `VENDOR_METHODS['get_news']`
   - Added to `VENDOR_METHODS['get_global_news']`

3. **Fallback System** automatically tries sentiment if primary sources fail

## Limitations and Notes

1. **Network Requirements:**
   - Sentiment analysis requires internet access to:
     - Download the DistilRoBERTa model from HuggingFace (first time only)
     - Fetch news from Google News
   
2. **Rate Limiting:**
   - GoogleNews has rate limits; use responsibly
   - Consider using Alpha Vantage as primary with sentiment as fallback

3. **Model Caching:**
   - The sentiment model is downloaded once and cached locally
   - Subsequent runs will use the cached model

4. **Fallback Behavior:**
   - If sentiment analysis fails (network issues, rate limits), the system automatically falls back to the next configured vendor

## Examples

### Example 1: Basic Trading Analysis with Sentiment News

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini"
config["quick_think_llm"] = "gpt-4o-mini"
config["max_debate_rounds"] = 1
config["data_vendors"]["news_data"] = "sentiment"

ta = TradingAgentsGraph(debug=True, config=config)
state, decision = ta.propagate("TSLA", "2024-05-10")
print(f"Decision: {decision}")
```

### Example 2: Standalone Sentiment Analysis

```python
from tradingagents.dataflows.sentiment_news import get_sentiment_provider
from datetime import datetime, timedelta

provider = get_sentiment_provider()

# Analyze Bitcoin news sentiment
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

result = provider.get_news_with_sentiment(
    ticker="Bitcoin",
    start_date=start_date.strftime("%Y-%m-%d"),
    end_date=end_date.strftime("%Y-%m-%d"),
    max_results=10
)

print(result)
```

### Example 3: Gradio Interface with Custom Settings

```python
from tradingagents_gradio import create_tradingagents_interface

# Create interface
demo = create_tradingagents_interface()

# Launch with custom settings
demo.launch(
    server_name="127.0.0.1",  # Local only
    server_port=8080,          # Custom port
    share=True,                # Create shareable link
    auth=("admin", "password") # Add authentication
)
```

## Troubleshooting

### Issue: "Failed to download model from HuggingFace"
**Solution:** Ensure you have internet access. The model will be cached after the first download.

### Issue: "No articles found"
**Solution:** GoogleNews may be rate-limiting or temporarily unavailable. Configure a fallback:
```python
config["data_vendors"]["news_data"] = "alpha_vantage,sentiment"
```

### Issue: "Gradio interface not launching"
**Solution:** Check that all dependencies are installed:
```bash
pip install gradio transformers torch
```

## Future Enhancements

Potential improvements for future versions:
1. Support for additional sentiment analysis models
2. Caching of news articles to reduce API calls
3. Historical sentiment tracking and trending
4. Integration with more news sources
5. Real-time sentiment monitoring

## Contributing

To contribute to the sentiment analysis or Gradio interface:
1. Follow the existing code style
2. Add tests for new functionality
3. Update this documentation
4. Submit a pull request

## Support

For issues or questions:
1. Check this documentation first
2. Review the code comments in `sentiment_news.py` and `tradingagents_gradio.py`
3. Open an issue on GitHub with detailed error messages and environment info
