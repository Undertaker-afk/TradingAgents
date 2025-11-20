"""
Sentiment Analysis News Data Source using GoogleNews and DistilRoBERTa
This module provides sentiment-analyzed news as a fallback news source for TradingAgents
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

try:
    from GoogleNews import GoogleNews
    from transformers import pipeline
    import torch
    SENTIMENT_AVAILABLE = True
except ImportError:
    SENTIMENT_AVAILABLE = False
    logging.warning("Sentiment analysis dependencies not available. Install gradio, transformers, torch, and GoogleNews.")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

SENTIMENT_ANALYSIS_MODEL = (
    "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
)

class SentimentNewsProvider:
    """Provides news with sentiment analysis using GoogleNews and DistilRoBERTa"""
    
    def __init__(self):
        self.sentiment_analyzer = None
        if SENTIMENT_AVAILABLE:
            try:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                logging.info(f"Initializing sentiment analyzer on device: {device}")
                self.sentiment_analyzer = pipeline(
                    "sentiment-analysis", 
                    model=SENTIMENT_ANALYSIS_MODEL, 
                    device=device
                )
                logging.info("Sentiment analyzer initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize sentiment analyzer: {e}")
                self.sentiment_analyzer = None
    
    def fetch_articles(self, query: str, start_date: str = None, end_date: str = None, max_results: int = 10) -> List[Dict]:
        """
        Fetch articles from GoogleNews for a given query and date range
        
        Args:
            query: Search query (e.g., stock ticker or company name)
            start_date: Start date in yyyy-mm-dd format (optional)
            end_date: End date in yyyy-mm-dd format (optional)
            max_results: Maximum number of articles to return
            
        Returns:
            List of article dictionaries
        """
        if not SENTIMENT_AVAILABLE:
            logging.error("GoogleNews not available")
            return []
        
        try:
            logging.info(f"Fetching articles for query: '{query}'")
            googlenews = GoogleNews(lang="en")
            
            # Set date range if provided
            if start_date and end_date:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                googlenews.set_time_range(start.strftime("%m/%d/%Y"), end.strftime("%m/%d/%Y"))
            
            googlenews.search(query)
            articles = googlenews.result()
            
            # Limit results
            articles = articles[:max_results] if len(articles) > max_results else articles
            
            logging.info(f"Fetched {len(articles)} articles")
            return articles
        except Exception as e:
            logging.error(f"Error fetching articles for '{query}': {e}")
            return []
    
    def analyze_article_sentiment(self, article: Dict) -> Dict:
        """
        Analyze sentiment for a single article
        
        Args:
            article: Article dictionary with 'title' and 'desc' keys
            
        Returns:
            Article dictionary with added 'sentiment' key
        """
        if not self.sentiment_analyzer:
            article["sentiment"] = {"label": "neutral", "score": 0.0}
            return article
        
        try:
            # Combine title and description for analysis
            text = f"{article.get('title', '')} {article.get('desc', '')}"
            if not text.strip():
                article["sentiment"] = {"label": "neutral", "score": 0.0}
                return article
            
            # Analyze sentiment
            sentiment = self.sentiment_analyzer(text[:512])[0]  # Limit to 512 tokens
            article["sentiment"] = sentiment
            logging.debug(f"Analyzed sentiment for: {article.get('title', 'Unknown')[:50]}...")
            
        except Exception as e:
            logging.error(f"Error analyzing sentiment: {e}")
            article["sentiment"] = {"label": "neutral", "score": 0.0}
        
        return article
    
    def get_news_with_sentiment(
        self, 
        ticker: str, 
        start_date: str, 
        end_date: str,
        max_results: int = 10
    ) -> str:
        """
        Get news articles with sentiment analysis for a ticker
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date in yyyy-mm-dd format
            end_date: End date in yyyy-mm-dd format
            max_results: Maximum number of articles to return
            
        Returns:
            Formatted string containing news with sentiment analysis
        """
        # Fetch articles
        articles = self.fetch_articles(ticker, start_date, end_date, max_results)
        
        if not articles:
            return f"No news articles found for {ticker} between {start_date} and {end_date}"
        
        # Analyze sentiment for each article
        analyzed_articles = [self.analyze_article_sentiment(article) for article in articles]
        
        # Format output
        result = f"News sentiment analysis for {ticker} ({start_date} to {end_date}):\n\n"
        
        for i, article in enumerate(analyzed_articles, 1):
            sentiment = article.get("sentiment", {})
            sentiment_label = sentiment.get("label", "neutral").upper()
            sentiment_score = sentiment.get("score", 0.0)
            
            result += f"{i}. [{sentiment_label} ({sentiment_score:.2f})] {article.get('title', 'No title')}\n"
            result += f"   Source: {article.get('media', 'Unknown')} | Date: {article.get('date', 'Unknown')}\n"
            result += f"   {article.get('desc', 'No description')[:200]}...\n"
            result += f"   Link: {article.get('link', 'No link')}\n\n"
        
        # Calculate overall sentiment
        sentiments = [a.get("sentiment", {}) for a in analyzed_articles]
        positive_count = sum(1 for s in sentiments if s.get("label") == "positive")
        negative_count = sum(1 for s in sentiments if s.get("label") == "negative")
        neutral_count = sum(1 for s in sentiments if s.get("label") == "neutral")
        
        result += f"\nOverall Sentiment Summary:\n"
        result += f"Positive: {positive_count} ({positive_count/len(sentiments)*100:.1f}%)\n"
        result += f"Negative: {negative_count} ({negative_count/len(sentiments)*100:.1f}%)\n"
        result += f"Neutral: {neutral_count} ({neutral_count/len(sentiments)*100:.1f}%)\n"
        
        return result
    
    def get_global_news_with_sentiment(
        self, 
        curr_date: str, 
        look_back_days: int = 7, 
        limit: int = 5
    ) -> str:
        """
        Get global market news with sentiment analysis
        
        Args:
            curr_date: Current date in yyyy-mm-dd format
            look_back_days: Number of days to look back
            limit: Maximum number of articles to return
            
        Returns:
            Formatted string containing global news with sentiment
        """
        # Calculate date range
        end_date = datetime.strptime(curr_date, "%Y-%m-%d")
        start_date = end_date - timedelta(days=look_back_days)
        
        # Search for general market news
        query = "stock market OR financial markets OR economy"
        
        articles = self.fetch_articles(
            query, 
            start_date.strftime("%Y-%m-%d"), 
            end_date.strftime("%Y-%m-%d"),
            limit
        )
        
        if not articles:
            return f"No global news articles found for the past {look_back_days} days"
        
        # Analyze sentiment
        analyzed_articles = [self.analyze_article_sentiment(article) for article in articles]
        
        # Format output
        result = f"Global market news sentiment ({look_back_days} days):\n\n"
        
        for i, article in enumerate(analyzed_articles, 1):
            sentiment = article.get("sentiment", {})
            sentiment_label = sentiment.get("label", "neutral").upper()
            sentiment_score = sentiment.get("score", 0.0)
            
            result += f"{i}. [{sentiment_label} ({sentiment_score:.2f})] {article.get('title', 'No title')}\n"
            result += f"   {article.get('desc', 'No description')[:150]}...\n\n"
        
        return result


# Global instance
_sentiment_provider = None

def get_sentiment_provider() -> SentimentNewsProvider:
    """Get or create global sentiment provider instance"""
    global _sentiment_provider
    if _sentiment_provider is None:
        _sentiment_provider = SentimentNewsProvider()
    return _sentiment_provider


def get_news_sentiment(ticker: str, start_date: str, end_date: str) -> str:
    """
    Get news with sentiment analysis for a ticker (fallback news source)
    
    Args:
        ticker: Stock ticker symbol
        start_date: Start date in yyyy-mm-dd format
        end_date: End date in yyyy-mm-dd format
        
    Returns:
        Formatted string containing news with sentiment analysis
    """
    provider = get_sentiment_provider()
    return provider.get_news_with_sentiment(ticker, start_date, end_date)


def get_global_news_sentiment(curr_date: str, look_back_days: int = 7, limit: int = 5) -> str:
    """
    Get global news with sentiment analysis (fallback news source)
    
    Args:
        curr_date: Current date in yyyy-mm-dd format
        look_back_days: Number of days to look back
        limit: Maximum number of articles to return
        
    Returns:
        Formatted string containing global news with sentiment
    """
    provider = get_sentiment_provider()
    return provider.get_global_news_with_sentiment(curr_date, look_back_days, limit)
