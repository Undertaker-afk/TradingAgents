"""
Gradio Interface for TradingAgents with Sentiment Analysis
This module provides a web interface for the TradingAgents framework
"""
import gradio as gr
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, Tuple
import json

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.dataflows.sentiment_news import get_sentiment_provider

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize sentiment provider
sentiment_provider = get_sentiment_provider()


def create_tradingagents_interface():
    """Create the TradingAgents Gradio interface"""
    
    with gr.Blocks(title="TradingAgents - Multi-Agent Trading Framework") as demo:
        gr.Markdown("# 🤖 TradingAgents - Multi-Agent Trading Framework")
        gr.Markdown(
            "Analyze stocks using multiple specialized AI agents: Fundamental Analyst, "
            "Sentiment Analyst, News Analyst, Technical Analyst, Bull/Bear Researchers, "
            "Trader, and Risk Manager."
        )
        
        with gr.Tabs():
            # Tab 1: Trading Analysis
            with gr.Tab("Trading Analysis"):
                gr.Markdown("## Stock Trading Analysis")
                gr.Markdown(
                    "Get comprehensive trading recommendations from our multi-agent system."
                )
                
                with gr.Row():
                    with gr.Column(scale=1):
                        ticker_input = gr.Textbox(
                            label="Stock Ticker",
                            placeholder="Enter stock symbol (e.g., NVDA, AAPL, TSLA)",
                            value="NVDA"
                        )
                        date_input = gr.Textbox(
                            label="Analysis Date (YYYY-MM-DD)",
                            placeholder="Enter date or leave empty for today",
                            value=""
                        )
                        
                        # LLM Configuration
                        gr.Markdown("### LLM Configuration")
                        deep_think_llm = gr.Dropdown(
                            choices=["gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini"],
                            value="gpt-4o-mini",
                            label="Deep Think LLM (for complex reasoning)"
                        )
                        quick_think_llm = gr.Dropdown(
                            choices=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
                            value="gpt-4o-mini",
                            label="Quick Think LLM (for fast analysis)"
                        )
                        
                        # Research Depth
                        max_debate_rounds = gr.Slider(
                            minimum=1,
                            maximum=5,
                            value=1,
                            step=1,
                            label="Max Debate Rounds (higher = more thorough but slower)"
                        )
                        
                        # Data Source Configuration
                        gr.Markdown("### Data Source Configuration")
                        news_source = gr.Dropdown(
                            choices=["alpha_vantage", "sentiment", "openai", "google", "local"],
                            value="alpha_vantage,sentiment",
                            label="News Data Source (sentiment = GoogleNews with AI analysis)",
                            multiselect=False
                        )
                        
                        analyze_btn = gr.Button("🚀 Analyze Stock", variant="primary", size="lg")
                    
                    with gr.Column(scale=2):
                        # Output displays
                        gr.Markdown("### Analysis Results")
                        
                        status_output = gr.Textbox(
                            label="Status",
                            lines=2,
                            interactive=False
                        )
                        
                        decision_output = gr.JSON(
                            label="Trading Decision"
                        )
                        
                        analysis_details = gr.JSON(
                            label="Detailed Analysis"
                        )
                
                gr.Examples(
                    examples=[
                        ["NVDA", "", "gpt-4o-mini", "gpt-4o-mini", 1, "alpha_vantage,sentiment"],
                        ["AAPL", "", "gpt-4o-mini", "gpt-4o-mini", 2, "sentiment"],
                        ["TSLA", "", "gpt-4o", "gpt-4o", 1, "alpha_vantage"],
                    ],
                    inputs=[ticker_input, date_input, deep_think_llm, quick_think_llm, max_debate_rounds, news_source],
                )
            
            # Tab 2: Sentiment Analysis
            with gr.Tab("Sentiment Analysis"):
                gr.Markdown("## 📊 News Sentiment Analysis")
                gr.Markdown(
                    "Analyze market sentiment from news articles using GoogleNews and AI-powered sentiment analysis."
                )
                
                with gr.Row():
                    with gr.Column(scale=1):
                        sentiment_ticker = gr.Textbox(
                            label="Asset/Ticker",
                            placeholder="Enter ticker or company name",
                            value="Bitcoin"
                        )
                        
                        sentiment_days = gr.Slider(
                            minimum=1,
                            maximum=30,
                            value=7,
                            step=1,
                            label="Look Back Days"
                        )
                        
                        sentiment_limit = gr.Slider(
                            minimum=5,
                            maximum=20,
                            value=10,
                            step=1,
                            label="Maximum Articles"
                        )
                        
                        sentiment_btn = gr.Button("📈 Analyze Sentiment", variant="primary")
                    
                    with gr.Column(scale=2):
                        sentiment_output = gr.Dataframe(
                            headers=["Sentiment", "Title", "Description", "Date"],
                            datatype=["markdown", "html", "markdown", "markdown"],
                            wrap=False,
                            label="Articles and Sentiment"
                        )
                        
                        sentiment_summary = gr.Textbox(
                            label="Sentiment Summary",
                            lines=4,
                            interactive=False
                        )
                
                gr.Examples(
                    examples=[
                        ["Bitcoin", 7, 10],
                        ["Tesla", 3, 15],
                        ["Apple", 14, 10],
                    ],
                    inputs=[sentiment_ticker, sentiment_days, sentiment_limit],
                )
        
        # Define the analysis function
        def analyze_stock(
            ticker: str,
            date: str,
            deep_llm: str,
            quick_llm: str,
            debate_rounds: int,
            news_src: str
        ) -> Tuple[str, Dict, Dict]:
            """Run TradingAgents analysis on a stock"""
            try:
                # Use today's date if not provided
                if not date or date.strip() == "":
                    date = datetime.now().strftime("%Y-%m-%d")
                
                # Validate date format
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    return "❌ Invalid date format. Use YYYY-MM-DD", {}, {}
                
                # Create custom config
                config = DEFAULT_CONFIG.copy()
                config["deep_think_llm"] = deep_llm
                config["quick_think_llm"] = quick_llm
                config["max_debate_rounds"] = int(debate_rounds)
                
                # Configure news data source
                config["data_vendors"] = config.get("data_vendors", {})
                config["data_vendors"]["news_data"] = news_src
                
                # Initialize TradingAgents
                status_msg = f"🔄 Initializing analysis for {ticker} on {date}..."
                logging.info(status_msg)
                
                ta = TradingAgentsGraph(debug=True, config=config)
                
                # Run analysis
                status_msg = f"🔄 Running multi-agent analysis (this may take a few minutes)..."
                logging.info("Starting propagation...")
                
                state, decision = ta.propagate(ticker, date)
                
                # Extract decision details
                decision_data = {
                    "ticker": ticker,
                    "date": date,
                    "decision": decision,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Extract state details
                analysis_data = {
                    "state_summary": str(state)[:500] + "..." if len(str(state)) > 500 else str(state),
                    "agents_involved": "Fundamental, Sentiment, News, Technical Analysts, Bull/Bear Researchers, Trader, Risk Manager"
                }
                
                status_msg = f"✅ Analysis complete for {ticker}!"
                logging.info(status_msg)
                
                return status_msg, decision_data, analysis_data
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                logging.error(f"Analysis failed: {e}", exc_info=True)
                return error_msg, {"error": str(e)}, {}
        
        # Define sentiment analysis function
        def analyze_sentiment(ticker: str, days: int, limit: int) -> Tuple[pd.DataFrame, str]:
            """Analyze sentiment from news articles"""
            try:
                # Calculate date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
                
                # Fetch and analyze articles
                articles = sentiment_provider.fetch_articles(
                    ticker,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                    limit
                )
                
                if not articles:
                    return pd.DataFrame(), f"No articles found for {ticker}"
                
                # Analyze sentiment
                analyzed_articles = [
                    sentiment_provider.analyze_article_sentiment(article)
                    for article in articles
                ]
                
                # Convert to DataFrame
                df = pd.DataFrame(analyzed_articles)
                
                # Format for display
                def sentiment_badge(sentiment):
                    colors = {
                        "negative": "red",
                        "neutral": "gray",
                        "positive": "green",
                    }
                    label = sentiment.get("label", "neutral")
                    score = sentiment.get("score", 0.0)
                    color = colors.get(label, "grey")
                    return f'<span style="background-color: {color}; color: white; padding: 2px 6px; border-radius: 4px;">{label.upper()} ({score:.2f})</span>'
                
                display_df = pd.DataFrame()
                display_df["Sentiment"] = df["sentiment"].apply(sentiment_badge)
                display_df["Title"] = df.apply(
                    lambda row: f'<a href="{row["link"]}" target="_blank">{row["title"]}</a>',
                    axis=1,
                )
                display_df["Description"] = df["desc"].apply(lambda x: str(x)[:200] + "...")
                display_df["Date"] = df["date"]
                
                # Calculate summary
                sentiments = df["sentiment"].tolist()
                positive_count = sum(1 for s in sentiments if s.get("label") == "positive")
                negative_count = sum(1 for s in sentiments if s.get("label") == "negative")
                neutral_count = sum(1 for s in sentiments if s.get("label") == "neutral")
                total = len(sentiments)
                
                summary = f"""
Sentiment Analysis Summary for {ticker}:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Articles Analyzed: {total}
Positive: {positive_count} ({positive_count/total*100:.1f}%)
Negative: {negative_count} ({negative_count/total*100:.1f}%)
Neutral: {neutral_count} ({neutral_count/total*100:.1f}%)

Overall Sentiment: {"🟢 POSITIVE" if positive_count > negative_count else "🔴 NEGATIVE" if negative_count > positive_count else "⚪ NEUTRAL"}
"""
                
                return display_df, summary
                
            except Exception as e:
                logging.error(f"Sentiment analysis failed: {e}", exc_info=True)
                return pd.DataFrame(), f"Error: {str(e)}"
        
        # Connect the buttons
        analyze_btn.click(
            fn=analyze_stock,
            inputs=[
                ticker_input,
                date_input,
                deep_think_llm,
                quick_think_llm,
                max_debate_rounds,
                news_source
            ],
            outputs=[status_output, decision_output, analysis_details]
        )
        
        sentiment_btn.click(
            fn=analyze_sentiment,
            inputs=[sentiment_ticker, sentiment_days, sentiment_limit],
            outputs=[sentiment_output, sentiment_summary]
        )
    
    return demo


if __name__ == "__main__":
    logging.info("Starting TradingAgents Gradio Interface...")
    demo = create_tradingagents_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
