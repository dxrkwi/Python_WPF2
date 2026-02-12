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
    # 1. Vorverarbeitung: Ersetzen von Kommas durch Semikolons
    text = text.replace(",", ";")
    # 2. Tokenisierung
    inputs = tokenizer(
        text, 
        return_tensors="pt", 
        truncation=True, 
        padding="max_length", 
        max_length=128
    ).to(device)
    # 3. Modell-Inferenz (Vorhersage ohne Gradientenberechnung)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
    # 4. Ergebnis auswerten
    # Bestimmung der Klasse (0 = Trump, 1 = Musk)
    idx = logits.argmax().item()
    # Berechnung der Wahrscheinlichkeit mittels Softmax
    probs = torch.softmax(logits, dim=1)
    prob = probs[0][idx].item()
    # Zuordnung des Labels
    author = "Elon Musk" if idx == 1 else "Donald Trump"
    return f"Autor: {author} (Sicherheit: {prob:.2%})"
# Testlauf
print(predict("1 big thing: Stunning crime crash: axios.com/newsletters/axios-am"))