# Comment.AI — Scraper + Review Analyzer

A student hackathon prototype that scrapes comments/reviews from Reddit, Amazon, or generic webpages and turns them into an interactive sentiment-analysis dashboard.

## What it does

Comment.AI helps users understand public opinion around a post, product, or webpage by extracting comments/reviews and analysing them using NLP.

The dashboard shows:

- Positive / Negative / Neutral sentiment
- Average polarity score
- Intensity score
- Sarcasm flag for selected patterns
- Optional emotion detection using a Hugging Face model
- Pie chart and bar chart summaries
- Per-comment insight cards

## Tech stack

- Python
- Streamlit
- Requests
- BeautifulSoup
- Pandas
- Plotly
- VADER Sentiment
- Hugging Face Transformers

## Project structure

```text
CommentAI-Hackathon-Submission/
├── app.py
├── requirements.txt
├── README.md
├── run.ps1
├── run.bat
├── demo_urls.txt
├── .env.example
├── .gitignore
├── LICENSE
├── sample_data/
│   └── demo_comments.csv
├── docs/
│   ├── PROJECT_REPORT.md
│   └── PITCH.md
├── assets/
│   └── screenshot_placeholder.txt
└── .streamlit/
    └── config.toml
```

## How to run

### Windows PowerShell

```powershell
cd CommentAI-Hackathon-Submission
.\run.ps1
```

### Windows CMD

```bat
cd CommentAI-Hackathon-Submission
run.bat
```

### Manual setup

```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
streamlit run app.py
```

On Windows PowerShell, activate using:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Demo flow for judges

1. Open the app with `streamlit run app.py`.
2. Choose the source type from the sidebar.
3. Paste a Reddit, Amazon, or generic webpage URL.
4. Set max comments/reviews.
5. Click **Scrape and analyze**.
6. Show the sentiment metrics, charts, and per-comment cards.

## Known limitations

- Amazon often blocks scraping or changes its HTML structure.
- Generic webpages may have different comment structures, so extraction is best-effort.
- Sarcasm detection is rule-based and limited.
- The Hugging Face emotion model can take time to download on first run.

## Future improvements

- Manual paste mode for comments
- CSV export
- Better sarcasm detection
- Saved HTML upload mode
- Streamlit Cloud deployment
- Better review extraction for specific websites

## Hackathon note

This project is built as a functional prototype, not a production scraping platform. It is meant to show a practical NLP workflow: extract real text, analyse sentiment/emotion, and display useful insights in a simple dashboard.
