# Project Report: Comment.AI

## Problem statement

Online products, posts, and public discussions generate hundreds or thousands of comments. Manually reading all of them is slow, biased, and difficult. Comment.AI attempts to quickly summarise the overall public reaction by scraping comments or reviews and analysing their sentiment.

## Proposed solution

Comment.AI is a Streamlit web app where a user enters a URL, selects a source type, and receives an analysis dashboard. The app scrapes the main post/product description and extracts available comments or reviews. Each item is scored using VADER sentiment analysis and optionally classified with a transformer-based emotion model.

## Main features

- Reddit JSON scraping
- Amazon product-page extraction, where available
- Generic webpage extraction
- Sentiment classification
- Polarity and intensity scoring
- Basic sarcasm flagging
- Emotion classification
- Charts and per-comment cards

## System workflow

1. User enters a URL.
2. App selects scraper based on source type.
3. Main description and comments/reviews are extracted.
4. Each comment is analysed.
5. Results are converted into a Pandas DataFrame.
6. Streamlit renders metrics, charts, and cards.

## Why this is useful

The project can help with early product feedback analysis, social media monitoring, consumer research, and basic brand sentiment tracking.

## Limitations

The project is dependent on website HTML structure and public access. Some websites block scraping. The sarcasm system is still simple and should be upgraded using stronger NLP models.

## Future scope

- Browser extension
- CSV/PDF reports
- Login-free demo mode
- Better website-specific extractors
- Sentiment trend tracking over time
