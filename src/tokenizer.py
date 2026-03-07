# Tokenisierungslogik für das Projekt. 
# Verwendet BERTweet, einen speziell für Tweets trainierten Transformer-basierten Tokenizer von Hugging Face. 
# BERTweet ist eine Variante von BERT, die auf englischen Tweets vortrainiert wurde 
# Verwendet spezielle Tokens für tweet-spezifische Elemente wie Hashtags, Mentions (@), Emojis und Abkürzungen.
# Der Tokenizer bereitet die Daten durch Tokenisierung für die transformer.py vor, wird als Safetensors gespeichert.

# Zusammenspiel mit anderen Dateien:
# - main.py: Ruft die Tokenisierung auf, um Daten vorzubereiten.
# - transformer.py: Verwendet die tokenisierten Daten zum Trainieren des Modells.
# Basismodell für Transformer: BERTweet: https://huggingface.co/docs/transformers/model_doc/bertweet

# Dateiverantwortlicher: Peter Pütz

# Vorklassifizierung der Tweets, um Evaluierung zu ermöglichen. Ergebnis wird mit Klassifizierung abgeglichen -> Genauigkeit
#0 = TRUMP
#1 = ELON
import os 
import torch 
import pandas as pd 
from transformers import AutoTokenizer
from safetensors.torch import save_file
from dotenv import load_dotenv 
def tokenize(data_path, train_data):
    load_dotenv()
    hf_token = os.getenv("HUGGINGFACE_API") # Liest den HuggingFace API-Token aus
    if not hf_token:
        print("Warning: Kein HUGGINGFACE_API Token in .env gefunden!")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    SOURCE_DIR = os.path.join(script_dir, "..", f"{data_path}")

    tokenizer = AutoTokenizer.from_pretrained("vinai/bertweet-base", normalization=True, token=hf_token)  # Lädt BERTweet-Tokenizer

    # 1. Alle CSVs laden & verbinden
    df = pd.concat([
        pd.read_csv(
            os.path.join(SOURCE_DIR, f), 
            on_bad_lines='skip',
            engine='python')
        for f in os.listdir(SOURCE_DIR) if f.endswith('.csv')]) 

    # 2. Tokenisieren
    encodings = tokenizer( 
        df['text'].astype(str).tolist(), # Textspalte als String-Liste übergeben
        truncation=True,                 # Zu lange Texte auf max_length kürzen
        padding=True,                    # Kürzere Texte auf gleiche Länge auffüllen
        max_length=128,                  # Maximale Token-Länge pro Tweet
        return_tensors="pt"              # Ausgabe als PyTorch-Tensoren
    )

    # 3. Speichern der .data: Es extrahiert die reinen Tensoren aus dem BatchEncoding-Objekt
    payload = {
        "input_ids": encodings.input_ids, 
        "attention_mask": encodings.attention_mask,  # Markiert echte vs. Padding-Token
        "labels": torch.tensor(df['label'].values, dtype=torch.int64)  # Klassen-Labels (0=Trump, 1=Elon)
    }

    # Create directory for tokenised data
    os.makedirs(os.path.dirname(train_data), exist_ok=True)
    save_file(payload, train_data)                            # Speichert Tensoren als .safetensors
    print(f"Fertig! {len(df)} Zeilen für Transformer vorbereitet.")

if __name__ == "__main__":
    tokenize("data", ".data/processed_data.safetensors") 