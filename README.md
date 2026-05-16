# CommentAI Review Analyzer and Sentiment Determination

A student hackathon prototype that scrapes comments and reviews from Reddit, Amazon, or generic webpages and turns them into an interactive sentiment-analysis dashboard.

## What it does

Comment.AI helps users understand public opinion around a post, product, or webpage by extracting comments and analysing them using NLP modules.

The dashboard shows:

- Positive or Negative or Neutral sentiment
- Average polarity score
- Intensity score
- Sarcasm flag for selected patterns
- Optional emotion detection using a Hugging Face model
- Pie chart and bar chart summaries
- insight cards for each comment

## Tech stack

- Python
- Streamlit
- Requests
- BeautifulSoup
- Pandas
- Plotly
- VADER Sentiment
- Hugging Face Transformers

## Known limitations

- Amazon often blocks scraping or changes its HTML structure.
- Generic webpages may have different comment structures, so extraction for these is not optimised is the best of what we could do.
- Sarcasm detection is limited.
- The Accuracy is not over 90%

## Hackathon note

This project is built as a functional prototype, not a production scraping platform. It is meant to show a practical NLP workflow, i.e extracting real text, analyzing sentiment and emotion, and display useful insights in a simple dashboard.
