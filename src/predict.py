import os
import torch
from dotenv import load_dotenv
from transformers import AutoTokenizer, RobertaForSequenceClassification

# .env laden
load_dotenv()

# 1. Setup
device = "cuda" if torch.cuda.is_available() else "cpu"
model_id = "dxxrk/BERTweet-tuned-ElonTrumpPrediction"
hf_token = os.getenv("HUGGINGFACE_API")

# 2. Modell & Tokenizer laden
tokenizer = AutoTokenizer.from_pretrained("vinai/bertweet-base", normalization=True)
model = RobertaForSequenceClassification.from_pretrained(model_id, token=hf_token).to(device)

def predict(text):
    """Gibt Wahrscheinlichkeiten als Dictionary zurück: {"Donald Trump": float, "Elon Musk": float}"""
    if not text.strip():
        return {"Error": 1.0}

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=128
    ).to(device)

    with torch.no_grad():
        logits = model(**inputs).logits

    probs = torch.softmax(logits, dim=1)[0]

    return {
        "Donald Trump": probs[0].item(),
        "Elon Musk": probs[1].item()
    }

if __name__ == "__main__":
    print(predict("1 big thing: Stunning crime crash: axios.com/newsletters/axios-am"))