import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# 1. Setup (Der Einzeiler)
device = "cuda" if torch.cuda.is_available() else "cpu"
model_path = "./final_model"

# 2. Modell & Tokenizer laden
tokenizer = AutoTokenizer.from_pretrained("vinai/bertweet-base", normalization=True)
model = AutoModelForSequenceClassification.from_pretrained(model_path).to(device)

def predict(text):
    # Text tokenisieren und auf die GPU (5080) schieben
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)
    
    with torch.no_grad():
        logits = model(**inputs).logits
    
    # Ergebnis auswerten (0 = Trump, 1 = Musk)
    idx = logits.argmax().item()
    prob = torch.softmax(logits, dim=1)[0][idx].item()
    
    author = "Elon Musk" if idx == 1 else "Donald Trump"
    return f"Autor: {author} (Sicherheit: {prob:.2%})"

# Testlauf
print(predict("I spoke with Savannah Guthrie, and let her know that I am directing ALL Federal Law Enforcement to be at the family’s, and Local Law Enforcement’s, complete disposal, IMMEDIATELY. We are deploying all resources to get her mother home safely. The prayers of our Nation are with her and her family. GOD BLESS AND PROTECT NANCY! PRESIDENT DONALD J. TRUMP"))
print(predict("Building an interstellar civilization"))
