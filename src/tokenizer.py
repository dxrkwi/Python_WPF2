# https://huggingface.co/docs/transformers/model_doc/bertweet MODEL BASE FOR THIS TRANSFORMER
# pip3 install emoji==0.6.0 für Emojis

#0 = TRUMP
#1 = ELON
import os
import torch
import pandas as pd
from transformers import AutoTokenizer
from safetensors.torch import save_file
from dotenv import load_dotenv

# Setup
#token für schnelleren Download: kann man hier erstellen https://huggingface.co/settings/tokens
load_dotenv()
hf_token = os.getenv("HUGGINGFACE_API")
if not hf_token:
    print("Warnung: Kein HUGGINGFACE_API Token in .env gefunden!")


script_dir = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(script_dir, "..", "data")
os.makedirs(".data", exist_ok=True)
tokenizer = AutoTokenizer.from_pretrained("vinai/bertweet-base", normalization=True, token=hf_token)

# 1. Alle CSVs laden & verbinden
df = pd.concat([
    pd.read_csv(
        os.path.join(SOURCE_DIR, f), 
        on_bad_lines='skip', 
        engine='python') 
    for f in os.listdir(SOURCE_DIR) if f.endswith('.csv')])

# 2. Tokenisieren
encodings = tokenizer(df['text'].astype(str).tolist(), truncation=True, padding=True, max_length=128, return_tensors="pt")

# 3. Speichern (Clean & Safe)
# .data extrahiert die reinen Tensoren aus dem BatchEncoding-Objekt
payload = {
    "input_ids": encodings.input_ids,
    "attention_mask": encodings.attention_mask,
    "labels": torch.tensor(df['label'].values, dtype=torch.int64) 
}

save_file(payload, ".data/processed_data.safetensors")

print(f"Fertig! {len(df)} Zeilen für Transformer vorbereitet.")