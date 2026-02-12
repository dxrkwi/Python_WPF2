import torch
import gradio as gr
from transformers import AutoTokenizer, RobertaForSequenceClassification

# Setup
device = "cuda" if torch.cuda.is_available() else "cpu"
model_id = "dxxrk/BERTweet-tuned-ElonTrumpPrediction"

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("vinai/bertweet-base", normalization=True)
model = RobertaForSequenceClassification.from_pretrained(model_id).to(device)

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

# Gradio interface
demo = gr.Interface(
    fn=predict,
    inputs=gr.Textbox(
        label="Enter text",
        placeholder="Write something like Trump or Musk would...",
        lines=3
    ),
    outputs=gr.Label(label="Prediction", num_top_classes=2),
    title="Trump vs Musk Predictor",
    description="BERTweet model fine-tuned to detect whether a text was written by Donald Trump or Elon Musk.",
    examples=[
        ["We will make America great again!"],
        ["The future of humanity depends on becoming a multi-planetary species"],
        ["FAKE NEWS!"],
        ["AI is the biggest existential risk we face as a civilization"]
    ]
)

if __name__ == "__main__":
    demo.launch()
