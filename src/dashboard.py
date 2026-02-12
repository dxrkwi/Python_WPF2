import torch
import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from transformers import AutoTokenizer, RobertaForSequenceClassification
from collections import Counter
import re
import emoji

# ============== LOAD MODEL ==============
device = "cuda" if torch.cuda.is_available() else "cpu"
model_id = "dxxrk/BERTweet-tuned-ElonTrumpPrediction"

print("Loading model...")
tokenizer = AutoTokenizer.from_pretrained("vinai/bertweet-base", normalization=True)
model = RobertaForSequenceClassification.from_pretrained(model_id).to(device)

# ============== LOAD DATA ==============
print("Loading data...")
df_musk = pd.read_csv("data/musk_twitter_dataset.csv")
df_trump = pd.read_csv("data/trump_truths_social.csv")

# ============== PREDICTOR FUNCTION ==============
def predict(text):
    if not text.strip():
        return {"Error": 1.0}

    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)

    with torch.no_grad():
        logits = model(**inputs).logits

    probs = torch.softmax(logits, dim=1)[0]

    return {
        "Donald Trump": probs[0].item(),
        "Elon Musk": probs[1].item()
    }

# ============== ANALYSIS FUNCTIONS ==============
def extract_emojis(text):
    return [c for c in str(text) if c in emoji.EMOJI_DATA]

def extract_mentions(text):
    return re.findall(r'@(\w+)', str(text))

def extract_hashtags(text):
    return re.findall(r'#(\w+)', str(text))

def get_top_items(items, n=10):
    return Counter(items).most_common(n)

def analyze_data():
    # Extract patterns from both datasets
    musk_emojis = []
    musk_mentions = []
    musk_hashtags = []

    trump_emojis = []
    trump_mentions = []
    trump_hashtags = []

    for text in df_musk['text']:
        musk_emojis.extend(extract_emojis(text))
        musk_mentions.extend(extract_mentions(text))
        musk_hashtags.extend(extract_hashtags(text))

    for text in df_trump['text']:
        trump_emojis.extend(extract_emojis(text))
        trump_mentions.extend(extract_mentions(text))
        trump_hashtags.extend(extract_hashtags(text))

    return {
        'musk_emojis': get_top_items(musk_emojis, 15),
        'musk_mentions': get_top_items(musk_mentions, 15),
        'musk_hashtags': get_top_items(musk_hashtags, 15),
        'trump_emojis': get_top_items(trump_emojis, 15),
        'trump_mentions': get_top_items(trump_mentions, 15),
        'trump_hashtags': get_top_items(trump_hashtags, 15),
        'musk_total': len(df_musk),
        'trump_total': len(df_trump),
    }

print("Analyzing data patterns...")
analysis = analyze_data()

# ============== CREATE CHARTS ==============
def create_emoji_chart():
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Elon Musk - Top Emojis", "Donald Trump - Top Emojis"))

    # Musk emojis
    musk_data = analysis['musk_emojis']
    if musk_data:
        emojis, counts = zip(*musk_data)
        fig.add_trace(go.Bar(x=list(emojis), y=list(counts), marker_color='#1DA1F2', name='Musk'), row=1, col=1)

    # Trump emojis
    trump_data = analysis['trump_emojis']
    if trump_data:
        emojis, counts = zip(*trump_data)
        fig.add_trace(go.Bar(x=list(emojis), y=list(counts), marker_color='#E91D32', name='Trump'), row=1, col=2)

    fig.update_layout(
        title_text="Emoji Usage Comparison",
        showlegend=False,
        height=400,
        template="plotly_dark"
    )
    return fig

def create_mentions_chart():
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Elon Musk - Top Mentions", "Donald Trump - Top Mentions"))

    # Musk mentions
    musk_data = analysis['musk_mentions']
    if musk_data:
        mentions, counts = zip(*musk_data)
        mentions = ['@' + m for m in mentions]
        fig.add_trace(go.Bar(y=list(mentions), x=list(counts), orientation='h', marker_color='#1DA1F2', name='Musk'), row=1, col=1)

    # Trump mentions
    trump_data = analysis['trump_mentions']
    if trump_data:
        mentions, counts = zip(*trump_data)
        mentions = ['@' + m for m in mentions]
        fig.add_trace(go.Bar(y=list(mentions), x=list(counts), orientation='h', marker_color='#E91D32', name='Trump'), row=1, col=2)

    fig.update_layout(
        title_text="Who do they mention most?",
        showlegend=False,
        height=500,
        template="plotly_dark"
    )
    return fig

def create_hashtags_chart():
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Elon Musk - Top Hashtags", "Donald Trump - Top Hashtags"))

    # Musk hashtags
    musk_data = analysis['musk_hashtags']
    if musk_data:
        hashtags, counts = zip(*musk_data)
        hashtags = ['#' + h for h in hashtags]
        fig.add_trace(go.Bar(y=list(hashtags), x=list(counts), orientation='h', marker_color='#1DA1F2', name='Musk'), row=1, col=1)

    # Trump hashtags
    trump_data = analysis['trump_hashtags']
    if trump_data:
        hashtags, counts = zip(*trump_data)
        hashtags = ['#' + h for h in hashtags]
        fig.add_trace(go.Bar(y=list(hashtags), x=list(counts), orientation='h', marker_color='#E91D32', name='Trump'), row=1, col=2)

    fig.update_layout(
        title_text="Most Used Hashtags",
        showlegend=False,
        height=500,
        template="plotly_dark"
    )
    return fig

def create_style_comparison():
    # Calculate style metrics
    musk_texts = df_musk['text'].astype(str)
    trump_texts = df_trump['text'].astype(str)

    musk_avg_len = musk_texts.str.len().mean()
    trump_avg_len = trump_texts.str.len().mean()

    musk_caps_ratio = musk_texts.apply(lambda x: sum(1 for c in x if c.isupper()) / max(len(x), 1)).mean() * 100
    trump_caps_ratio = trump_texts.apply(lambda x: sum(1 for c in x if c.isupper()) / max(len(x), 1)).mean() * 100

    musk_exclaim = musk_texts.str.count('!').mean()
    trump_exclaim = trump_texts.str.count('!').mean()

    # Create comparison chart
    categories = ['Avg Length (chars)', 'CAPS Usage (%)', 'Exclamation marks (avg)']
    musk_values = [musk_avg_len, musk_caps_ratio, musk_exclaim * 10]  # Scale exclamation for visibility
    trump_values = [trump_avg_len, trump_caps_ratio, trump_exclaim * 10]

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Elon Musk', x=categories, y=musk_values, marker_color='#1DA1F2'))
    fig.add_trace(go.Bar(name='Donald Trump', x=categories, y=trump_values, marker_color='#E91D32'))

    fig.update_layout(
        title_text="Writing Style Comparison",
        barmode='group',
        height=400,
        template="plotly_dark"
    )
    return fig

def create_overview_stats():
    stats_md = f"""
## Dataset Overview

| Metric | Elon Musk | Donald Trump |
|--------|-----------|--------------|
| Total Posts | {analysis['musk_total']:,} | {analysis['trump_total']:,} |
| Unique Emojis | {len(set(e for e, _ in analysis['musk_emojis']))} | {len(set(e for e, _ in analysis['trump_emojis']))} |
| Top Emoji | {analysis['musk_emojis'][0][0] if analysis['musk_emojis'] else 'N/A'} | {analysis['trump_emojis'][0][0] if analysis['trump_emojis'] else 'N/A'} |
| Top Mention | @{analysis['musk_mentions'][0][0] if analysis['musk_mentions'] else 'N/A'} | @{analysis['trump_mentions'][0][0] if analysis['trump_mentions'] else 'N/A'} |

---
*Data sources: Twitter/X (Musk), Truth Social (Trump)*
"""
    return stats_md

# ============== GRADIO INTERFACE ==============
with gr.Blocks(title="Trump vs Musk Analyzer", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🔍 Trump vs Musk Analyzer")
    gr.Markdown("BERTweet model fine-tuned to detect authorship + Data Analysis")

    with gr.Tabs():
        # Tab 1: Predictor
        with gr.TabItem("🎯 Predictor"):
            gr.Markdown("### Enter text to predict if it was written by Trump or Musk")
            with gr.Row():
                with gr.Column():
                    text_input = gr.Textbox(
                        label="Enter text",
                        placeholder="Write something like Trump or Musk would...",
                        lines=3
                    )
                    predict_btn = gr.Button("Predict", variant="primary")
                with gr.Column():
                    output_label = gr.Label(label="Prediction", num_top_classes=2)

            predict_btn.click(fn=predict, inputs=text_input, outputs=output_label)

            gr.Examples(
                examples=[
                    ["We will make America great again!"],
                    ["The future of humanity depends on becoming a multi-planetary species"],
                    ["FAKE NEWS! The media is the enemy of the people!"],
                    ["AI is probably the biggest existential risk we face as a civilization"]
                ],
                inputs=text_input
            )

        # Tab 2: Data Analysis
        with gr.TabItem("📊 Data Analysis"):
            gr.Markdown(create_overview_stats())

            with gr.Row():
                gr.Plot(create_style_comparison())

            with gr.Row():
                gr.Plot(create_emoji_chart())

            with gr.Row():
                gr.Plot(create_mentions_chart())

            with gr.Row():
                gr.Plot(create_hashtags_chart())

if __name__ == "__main__":
    demo.launch()
