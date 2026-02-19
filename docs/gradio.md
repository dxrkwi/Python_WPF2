# Gradio – Dokumentation

## Was ist Gradio?

Gradio ist eine Open-Source Python-Bibliothek, mit der man schnell und einfach interaktive Web-Oberflächen für Machine-Learning-Modelle erstellen kann. Man schreibt nur Python-Code und Gradio generiert automatisch eine vollständige Weboberfläche mit UI-Elementen wie Textfeldern, Buttons, Diagrammen und mehr.

**Vorteile von Gradio:**
- Kein HTML, CSS oder JavaScript nötig
- Läuft lokal oder kann öffentlich geteilt werden (über `share=True`)
- Unterstützt viele Ein-/Ausgabetypen (Text, Bilder, Audio, Diagramme, etc.)
- Einfache Integration mit PyTorch, TensorFlow und anderen ML-Frameworks

**Installation:**
```bash
pip install gradio
```

Gradio wird in diesem Projekt in der Datei `src/dashboard.py` verwendet, um eine interaktive Weboberfläche bereitzustellen.

---

## Aufbau von `src/dashboard.py`

Die Datei ist in mehrere Abschnitte unterteilt:

1. Modell laden
2. Daten laden
3. Vorhersage-Funktion
4. Analyse-Funktionen
5. Diagramme erstellen
6. Gradio-Oberfläche definieren

---

## 1. Modell laden (Zeilen 12–18)

```python
device = "cuda" if torch.cuda.is_available() else "cpu"
model_id = "dxxrk/BERTweet-tuned-ElonTrumpPrediction"

tokenizer = AutoTokenizer.from_pretrained("vinai/bertweet-base", normalization=True)
model = RobertaForSequenceClassification.from_pretrained(model_id).to(device)
```

- **`device`**: Prüft, ob eine GPU (CUDA) verfügbar ist. Falls nicht, wird die CPU verwendet.
- **`model_id`**: Die HuggingFace-Modell-ID des feinabgestimmten BERTweet-Modells.
- **`tokenizer`**: Der BERTweet-Tokenizer wandelt Text in Token (numerische Darstellungen) um, die das Modell verarbeiten kann. Die Option `normalization=True` aktiviert Twitter-spezifische Normalisierung (z.B. URLs und Benutzernamen werden standardisiert).
- **`model`**: Das vortrainierte Klassifikationsmodell wird von HuggingFace heruntergeladen und auf das ausgewählte Gerät (GPU/CPU) geladen.

---

## 2. Daten laden (Zeilen 20–23)

```python
df_musk = pd.read_csv("data/musk_twitter_dataset.csv")
df_trump = pd.read_csv("data/trump_truths_social.csv")
```

Zwei CSV-Dateien werden als Pandas DataFrames geladen:
- **`df_musk`**: Enthält Tweets von Elon Musk (Quelle: Twitter/X)
- **`df_trump`**: Enthält Posts von Donald Trump (Quelle: Truth Social)

Diese Daten werden später für die Analyse-Diagramme im Dashboard verwendet.

---

## 3. Vorhersage-Funktion `predict()` (Zeilen 26–40)

```python
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
```

Diese Funktion ist das Herzstück des Dashboards. Sie nimmt einen Text entgegen und gibt zurück, wie wahrscheinlich es ist, dass der Text von Trump oder Musk stammt.

**Ablauf Schritt für Schritt:**

1. **Leereingabe prüfen**: Falls der Text leer ist, wird ein Fehler zurückgegeben.
2. **Tokenisierung**: Der Text wird in Token umgewandelt (`return_tensors="pt"` erzeugt PyTorch-Tensoren, `truncation=True` kürzt zu lange Texte, `padding=True` füllt kurze Texte auf).
3. **Inferenz**: `torch.no_grad()` deaktiviert die Gradientenberechnung (spart Speicher, da wir nicht trainieren). Das Modell gibt Logits (Rohwerte) zurück.
4. **Softmax**: Die Logits werden über `torch.softmax()` in Wahrscheinlichkeiten umgewandelt (Werte zwischen 0 und 1, die sich zu 1 addieren).
5. **Rückgabe**: Ein Dictionary mit den Wahrscheinlichkeiten für Trump (`probs[0]`) und Musk (`probs[1]`).

---

## 4. Analyse-Funktionen (Zeilen 42–84)

### `extract_emojis(text)` (Zeile 43–44)
Extrahiert alle Emojis aus einem Text mithilfe der `emoji`-Bibliothek.

### `extract_mentions(text)` (Zeile 46–47)
Findet alle Erwähnungen (z.B. `@elonmusk`) im Text mithilfe eines regulären Ausdrucks (`@(\w+)`).

### `extract_hashtags(text)` (Zeile 49–50)
Findet alle Hashtags (z.B. `#MAGA`) im Text mithilfe eines regulären Ausdrucks (`#(\w+)`).

### `get_top_items(items, n=10)` (Zeile 52–53)
Zählt die Häufigkeit von Elementen in einer Liste und gibt die `n` häufigsten zurück. Verwendet `Counter` aus der Python-Standardbibliothek.

### `analyze_data()` (Zeilen 55–84)
Die Hauptanalysefunktion, die alle Texte beider Datensätze durchgeht und für Musk und Trump jeweils folgendes extrahiert:
- **Top 15 Emojis**
- **Top 15 Erwähnungen (@mentions)**
- **Top 15 Hashtags**
- **Gesamtanzahl der Posts**

Das Ergebnis wird als Dictionary zurückgegeben und in der globalen Variable `analysis` gespeichert (Zeile 87).

---

## 5. Diagramme erstellen (Zeilen 89–208)

Alle Diagramme werden mit **Plotly** erstellt. Plotly ist eine Bibliothek für interaktive Diagramme, die direkt in Gradio eingebettet werden können.

### `create_emoji_chart()` (Zeilen 90–111)
- Erstellt ein **Balkendiagramm** mit zwei Spalten (Subplots): Links Musk, rechts Trump.
- Zeigt die am häufigsten verwendeten Emojis als Balken an.
- **Farben**: Blau (`#1DA1F2`) für Musk, Rot (`#E91D32`) für Trump.
- Verwendet das dunkle Plotly-Theme (`plotly_dark`).

### `create_mentions_chart()` (Zeilen 113–136)
- Erstellt ein **horizontales Balkendiagramm** mit den meisterwähnten Benutzern.
- Horizontale Balken (`orientation='h'`) für bessere Lesbarkeit der Benutzernamen.
- Ebenfalls zwei Spalten: Musk links, Trump rechts.

### `create_hashtags_chart()` (Zeilen 138–161)
- Erstellt ein **horizontales Balkendiagramm** mit den meistverwendeten Hashtags.
- Gleiche Struktur wie das Mentions-Diagramm.

### `create_style_comparison()` (Zeilen 163–192)
- Vergleicht den **Schreibstil** von Musk und Trump anhand drei Metriken:
  - **Durchschnittliche Textlänge** (in Zeichen)
  - **Großbuchstaben-Anteil** (in Prozent) – zeigt, wie oft in CAPS geschrieben wird
  - **Ausrufezeichen** (Durchschnitt pro Post, skaliert x10 für bessere Sichtbarkeit)
- Verwendet ein **gruppiertes Balkendiagramm** (`barmode='group'`).

### `create_overview_stats()` (Zeilen 194–208)
- Gibt eine **Markdown-Tabelle** zurück (kein Plotly-Diagramm).
- Zeigt eine Zusammenfassung: Gesamtanzahl Posts, Anzahl verschiedener Emojis, meistverwendetes Emoji und meisterwähnter Benutzer.

---

## 6. Gradio-Oberfläche (Zeilen 210–259)

### Grundstruktur

```python
with gr.Blocks(title="Trump vs Musk Analyzer", theme=gr.themes.Soft()) as demo:
```

- **`gr.Blocks`**: Die flexibelste Gradio-Layout-Komponente. Ermöglicht freie Anordnung von UI-Elementen.
- **`title`**: Der Titel, der im Browser-Tab angezeigt wird.
- **`theme=gr.themes.Soft()`**: Ein vordefiniertes Gradio-Theme mit weichen, abgerundeten Stilen.

### Tabs

Die Oberfläche ist in zwei Tabs unterteilt:

#### Tab 1: Predictor (Zeilen 217–240)

```python
with gr.TabItem("Predictor"):
```

Dieser Tab enthält die interaktive Vorhersage-Funktion:

- **`gr.Textbox`**: Ein mehrzeiliges Eingabefeld, in das der Benutzer einen Text eingeben kann.
- **`gr.Button("Predict", variant="primary")`**: Ein Button, der die Vorhersage auslöst. `variant="primary"` gibt dem Button eine hervorgehobene Farbe.
- **`gr.Label`**: Zeigt das Ergebnis der Vorhersage an – mit Prozentwerten für Trump und Musk. `num_top_classes=2` zeigt beide Klassen an.
- **`predict_btn.click(fn=predict, inputs=text_input, outputs=output_label)`**: Verknüpft den Button mit der `predict()`-Funktion. Beim Klick wird der Text aus dem Eingabefeld an die Funktion übergeben und das Ergebnis im Label angezeigt.
- **`gr.Examples`**: Zeigt vordefinierte Beispieltexte an, die der Benutzer anklicken kann, um sie schnell zu testen.

#### Tab 2: Data Analysis (Zeilen 243–256)

```python
with gr.TabItem("Data Analysis"):
```

Dieser Tab zeigt die statische Datenanalyse:

- **`gr.Markdown`**: Rendert die Übersichtsstatistiken als Markdown-Tabelle.
- **`gr.Plot`**: Bettet interaktive Plotly-Diagramme in die Oberfläche ein. Jedes Diagramm wird in einer eigenen **`gr.Row()`** platziert, damit sie untereinander angezeigt werden.

Die Reihenfolge der Diagramme:
1. Schreibstil-Vergleich (`create_style_comparison()`)
2. Emoji-Nutzung (`create_emoji_chart()`)
3. Erwähnungen (`create_mentions_chart()`)
4. Hashtags (`create_hashtags_chart()`)

### App starten

```python
if __name__ == "__main__":
    demo.launch()
```

Startet den Gradio-Server. Standardmäßig läuft die App auf `http://localhost:7860`.

---

## Verwendete Gradio-Komponenten (Zusammenfassung)

| Komponente | Beschreibung |
|---|---|
| `gr.Blocks` | Flexibles Layout-System für die gesamte App |
| `gr.Markdown` | Rendert Markdown-Text (Überschriften, Tabellen, etc.) |
| `gr.Tabs` / `gr.TabItem` | Erstellt eine Tab-Navigation |
| `gr.Row` / `gr.Column` | Layout-Elemente für horizontale/vertikale Anordnung |
| `gr.Textbox` | Texteingabefeld |
| `gr.Button` | Klickbarer Button |
| `gr.Label` | Zeigt Klassifikationsergebnisse mit Prozentwerten |
| `gr.Plot` | Bettet Plotly-Diagramme ein |
| `gr.Examples` | Zeigt vordefinierte Beispiele zum Anklicken |

---

## Verwendete Bibliotheken

| Bibliothek | Zweck |
|---|---|
| `gradio` | Web-Oberfläche |
| `torch` | PyTorch für Modell-Inferenz |
| `transformers` | HuggingFace-Bibliothek für Tokenizer und Modell |
| `pandas` | Laden und Verarbeiten der CSV-Daten |
| `plotly` | Interaktive Diagramme |
| `emoji` | Emoji-Erkennung in Texten |
| `re` | Reguläre Ausdrücke für Mentions und Hashtags |
| `collections.Counter` | Zaehlen von Häufigkeiten |
