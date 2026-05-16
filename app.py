
import json
import re
from typing import List, Optional
from urllib.parse import quote

import emoji
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.set_page_config(page_title="Comment.AI Scraper Analyzer", page_icon="🧠", layout="wide")

vader = SentimentIntensityAnalyzer()

try:
    from transformers import pipeline
    emotion_pipe = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=1,
    )
    EMOTION_ENABLED = True
except Exception:
    emotion_pipe = None
    EMOTION_ENABLED = False


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 CommentAI/1.0 Safari/537.36"


def analyze_single(text: str, post_context: str = "") -> dict:
    score = vader.polarity_scores(text)["compound"]

    txt_lower = text.lower()
    post_lower = post_context.lower()

    if any(bad in post_lower for bad in ["horrendous", "terrible", "worst", "bad", "ruined", "scam"]) and any(
        relief in txt_lower for relief in ["bye bye", "finally", "good riddance", "thank god"]
    ):
        score = -0.90

    caps = sum(1 for c in text if c.isupper()) / len(text) if len(text) > 8 else 0
    excl = text.count("!") + text.count("?")
    emoji_boost = len(emoji.emoji_list(text)) * 0.4
    intensity = min(1.0, abs(score) * 1.6 + caps * 1.3 + min(excl * 0.5, 2.0) + emoji_boost)

    if score >= 0.35:
        rhetoric = "Positive"
        rtype = "praise"
    elif score <= -0.35:
        rhetoric = "Negative"
        rtype = "criticism"
    else:
        rhetoric = "Neutral"
        rtype = "neutral"

    sarcasm = any(w in txt_lower for w in ["bye bye", "finally", "good riddance"]) or (
        excl >= 3 and score < -0.25
    )

    dominant_emotion = "neutral"
    if EMOTION_ENABLED:
        try:
            dominant_emotion = emotion_pipe(text)[0][0]["label"]
        except Exception:
            dominant_emotion = "neutral"

    insight = f"Score: {score:.2f} | Intensity: {intensity:.2f} | Emotion: {dominant_emotion.capitalize()}"
    if sarcasm:
        insight += " | Sarcasm detected"

    return {
        "text": text[:280],
        "rhetoric": rhetoric,
        "score": round(score, 3),
        "intensity": round(intensity, 2),
        "sarcasm_flag": sarcasm,
        "rhetoric_type": rtype,
        "dominant_emotion": dominant_emotion,
        "insight": insight,
    }


def request_html(url: str) -> str:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"},
        timeout=25,
    )
    response.raise_for_status()
    return response.text


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def scrape_reddit(url: str, max_comments: int = 50) -> tuple[str, List[str]]:
    json_url = url.rstrip("/") + ".json?limit=500"
    response = requests.get(json_url, headers={"User-Agent": USER_AGENT}, timeout=25)
    response.raise_for_status()
    data = response.json()

    post = data[0]["data"]["children"][0]["data"]
    post_title = clean_text(post.get("title", ""))
    post_body = clean_text(post.get("selftext", ""))
    post_text = f"{post_title}. {post_body}".strip()

    comments: List[str] = []

    def walk(items):
        for item in items:
            if len(comments) >= max_comments:
                return
            if item.get("kind") != "t1":
                continue
            body = clean_text(item["data"].get("body", ""))
            if body and body not in ("[deleted]", "[removed]"):
                comments.append(body)
            replies = item["data"].get("replies")
            if isinstance(replies, dict):
                walk(replies.get("data", {}).get("children", []))

    walk(data[1]["data"]["children"])
    return post_text, comments


def scrape_amazon(url: str, max_reviews: int = 30) -> tuple[str, List[str]]:
    html = request_html(url)
    soup = BeautifulSoup(html, "html.parser")

    title = clean_text((soup.select_one("#productTitle") or soup.select_one("title") or {}).get_text(" ", strip=True) if (soup.select_one("#productTitle") or soup.select_one("title")) else "")
    bullets = [clean_text(li.get_text(" ", strip=True)) for li in soup.select("#feature-bullets li") if clean_text(li.get_text(" ", strip=True))]
    description = clean_text((soup.select_one("#productDescription") or soup.select_one("#bookDescription_feature_div") or soup.select_one("meta[name='description']") or {}).get_text(" ", strip=True) if (soup.select_one("#productDescription") or soup.select_one("#bookDescription_feature_div")) else (soup.select_one("meta[name='description']")["content"] if soup.select_one("meta[name='description']") and soup.select_one("meta[name='description']").has_attr("content") else ""))

    post_text = " ".join(x for x in [title, description] + bullets[:6] if x)

    reviews = []
    selectors = [
        "[data-hook='review-body'] span",
        "[data-hook='review-collapsed']",
        ".review-text-content span",
    ]
    for selector in selectors:
        for node in soup.select(selector):
            text = clean_text(node.get_text(" ", strip=True))
            if text and text not in reviews:
                reviews.append(text)
            if len(reviews) >= max_reviews:
                return post_text, reviews

    return post_text, reviews


def scrape_generic(url: str, max_comments: int = 40) -> tuple[str, List[str]]:
    html = request_html(url)
    soup = BeautifulSoup(html, "html.parser")

    title = clean_text((soup.title.get_text(" ", strip=True) if soup.title else ""))
    desc_tag = soup.select_one("meta[name='description']")
    description = clean_text(desc_tag.get("content", "")) if desc_tag else ""

    comments = []
    comment_selectors = [
        "[class*='comment']",
        "[id*='comment']",
        "[class*='review']",
        "[class*='reply']",
        "article",
    ]
    for selector in comment_selectors:
        for node in soup.select(selector):
            text = clean_text(node.get_text(" ", strip=True))
            if 20 <= len(text) <= 500 and text not in comments:
                comments.append(text)
            if len(comments) >= max_comments:
                break
        if comments:
            break

    post_text = " ".join(x for x in [title, description] if x)
    return post_text, comments


def scrape_by_mode(mode: str, url: str, max_items: int) -> tuple[str, List[str], str]:
    if mode == "Reddit":
        post_text, comments = scrape_reddit(url, max_items)
        return post_text, comments, "reddit"
    if mode == "Amazon":
        post_text, comments = scrape_amazon(url, max_items)
        return post_text, comments, "amazon"
    post_text, comments = scrape_generic(url, max_items)
    return post_text, comments, "generic"


def build_results(post_text: str, comments: List[str]) -> pd.DataFrame:
    rows = [analyze_single(comment, post_text) for comment in comments if comment.strip()]
    return pd.DataFrame(rows)


def render_metrics(df: pd.DataFrame):
    total = len(df)
    avg_pol = float(df["score"].mean()) if total else 0.0
    avg_intensity = float(df["intensity"].mean()) if total else 0.0
    neg_count = int((df["rhetoric"] == "Negative").sum()) if total else 0

    a, b, c, d = st.columns(4)
    a.metric("Comments / reviews", total)
    b.metric("Avg polarity", f"{avg_pol:+.3f}")
    c.metric("Avg intensity", f"{avg_intensity:.2f}")
    d.metric("Negative", neg_count)


st.markdown("""
<style>
.block-container { padding-top: 1.2rem; }
.post-card {
    border-left: 4px solid #444;
    padding: 12px 14px;
    margin-bottom: 10px;
    border-radius: 0 10px 10px 0;
    background: rgba(255,255,255,0.03);
}
.post-card.pos { border-left-color: #2d7d46; }
.post-card.neg { border-left-color: #c0392b; }
.post-card.neu { border-left-color: #9aa0a6; }
.small-note { color: #9aa0a6; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

st.title("Comment.AI Scraper + Review Analyzer")
st.caption("Exact analysis logic from main.py, with real URL scraping for Reddit, Amazon, and generic pages.")

with st.sidebar:
    mode = st.selectbox("Source type", ["Reddit", "Amazon", "Generic Webpage"])
    url = st.text_input("Thread / product / webpage URL")
    max_items = st.slider("Max comments / reviews", 5, 100, 30, 5)
    run = st.button("Scrape and analyze", use_container_width=True)

st.warning("Amazon pages often rate-limit or change markup. If Amazon blocks the request, open the product page in your browser, save the HTML, or test another page. Reddit JSON scraping is usually the most reliable.")

if run:
    if not url.strip():
        st.error("Paste a URL first.")
    else:
        try:
            with st.spinner("Scraping page..."):
                post_text, comments, source_kind = scrape_by_mode(mode, url.strip(), max_items)

            if not post_text and not comments:
                st.error("Could not extract usable content from that page.")
            else:
                st.subheader("Main post / product description")
                st.write(post_text or "No description found.")

                if not comments:
                    st.warning("No comments / reviews were extracted from that page.")
                else:
                    st.subheader("Extracted comments / reviews")
                    st.write(f"Found {len(comments)} items from {source_kind}.")
                    with st.expander("Preview extracted text", expanded=False):
                        for i, text in enumerate(comments, start=1):
                            st.write(f"{i}. {text}")

                    df = build_results(post_text, comments)
                    render_metrics(df)

                    left, right = st.columns(2)
                    with left:
                        pie_df = df["rhetoric"].value_counts().reset_index()
                        pie_df.columns = ["rhetoric", "count"]
                        st.plotly_chart(px.pie(pie_df, values="count", names="rhetoric", hole=0.45), use_container_width=True)
                    with right:
                        emo_df = df["dominant_emotion"].value_counts().reset_index()
                        emo_df.columns = ["emotion", "count"]
                        st.plotly_chart(px.bar(emo_df, x="emotion", y="count"), use_container_width=True)

                    st.subheader("Per-item analysis")
                    for _, row in df.iterrows():
                        css = "pos" if row["rhetoric"] == "Positive" else "neg" if row["rhetoric"] == "Negative" else "neu"
                        st.markdown(
                            f"""
                            <div class="post-card {css}">
                              <b>{row['text']}</b><br>
                              <span class="small-note">
                                {row['rhetoric']} | score: {row['score']:+.3f} | intensity: {row['intensity']:.2f}
                                | type: {row['rhetoric_type']} | emotion: {row['dominant_emotion']}
                              </span><br>
                              <span class="small-note">{row['insight']}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

        except requests.HTTPError as e:
            st.error(f"HTTP error while scraping: {e}")
        except Exception as e:
            st.error(f"Scrape/analyze failed: {e}")
