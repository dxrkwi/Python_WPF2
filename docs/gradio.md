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

1. Import der Vorhersage-Funktion
2. Daten laden
3. Analyse-Funktionen
4. Diagramme erstellen
5. Gradio-Oberfläche definieren

---

## 1. Import der Vorhersage-Funktion (Zeile 6)

```python
from predict import predict
```

Das Modell und der Tokenizer werden **nicht** direkt in `dashboard.py` geladen. Stattdessen wird die Funktion `predict()` aus `predict.py` importiert, die das Modell dort zentral lädt und verwaltet. Das vermeidet doppelten Code und sorgt dafür, dass das Modell nur einmal geladen wird.

---

## 2. Daten laden (Zeilen 12–14)

```python
df_musk = pd.read_csv("data/musk_twitter_dataset.csv")
df_trump = pd.read_csv("data/trump_truths_social.csv")
```

Zwei CSV-Dateien werden als Pandas DataFrames geladen:
- **`df_musk`**: Enthält Tweets von Elon Musk (Quelle: Twitter/X)
- **`df_trump`**: Enthält Posts von Donald Trump (Quelle: Truth Social)

Diese Daten werden später für die Analyse-Diagramme im Dashboard verwendet.

---

## 3. Vorhersage-Funktion `predict()` (importiert aus `predict.py`)

Die Funktion `predict()` ist in `src/predict.py` definiert und wird von `dashboard.py` importiert. Sie nimmt einen Text entgegen und gibt ein Dictionary mit Wahrscheinlichkeiten zurück:

```python
{"Donald Trump": 0.12, "Elon Musk": 0.88}
```

Die vollständige Logik (Tokenisierung, Inferenz, Softmax) befindet sich in `predict.py`. Siehe dort für Details.

---

## 4. Analyse-Funktionen (Zeilen 17–58)

### `extract_emojis(text)` (Zeile 17–18)
Extrahiert alle Emojis aus einem Text mithilfe der `emoji`-Bibliothek.

### `extract_mentions(text)` (Zeile 20–21)
Findet alle Erwähnungen (z.B. `@elonmusk`) im Text mithilfe eines regulären Ausdrucks (`@(\w+)`).

### `extract_hashtags(text)` (Zeile 23–24)
Findet alle Hashtags (z.B. `#MAGA`) im Text mithilfe eines regulären Ausdrucks (`#(\w+)`).

### `get_top_items(items, n=10)` (Zeile 26–27)
Zählt die Häufigkeit von Elementen in einer Liste und gibt die `n` häufigsten zurück. Verwendet `Counter` aus der Python-Standardbibliothek.

### `analyze_data()` (Zeilen 29–58)
Die Hauptanalysefunktion, die alle Texte beider Datensätze durchgeht und für Musk und Trump jeweils folgendes extrahiert:
- **Top 15 Emojis**
- **Top 15 Erwähnungen (@mentions)**
- **Top 15 Hashtags**
- **Gesamtanzahl der Posts**

Das Ergebnis wird als Dictionary zurückgegeben und in der globalen Variable `analysis` gespeichert (Zeile 61).

---

## 5. Diagramme erstellen (Zeilen 63–182)

Alle Diagramme werden mit **Plotly** erstellt. Plotly ist eine Bibliothek für interaktive Diagramme, die direkt in Gradio eingebettet werden können.

### `create_emoji_chart()` (Zeilen 64–85)
- Erstellt ein **Balkendiagramm** mit zwei Spalten (Subplots): Links Musk, rechts Trump.
- Zeigt die am häufigsten verwendeten Emojis als Balken an.
- **Farben**: Blau (`#1DA1F2`) für Musk, Rot (`#E91D32`) für Trump.
- Verwendet das dunkle Plotly-Theme (`plotly_dark`).

### `create_mentions_chart()` (Zeilen 87–110)
- Erstellt ein **horizontales Balkendiagramm** mit den meisterwähnten Benutzern.
- Horizontale Balken (`orientation='h'`) für bessere Lesbarkeit der Benutzernamen.
- Ebenfalls zwei Spalten: Musk links, Trump rechts.

### `create_hashtags_chart()` (Zeilen 112–135)
- Erstellt ein **horizontales Balkendiagramm** mit den meistverwendeten Hashtags.
- Gleiche Struktur wie das Mentions-Diagramm.

### `create_style_comparison()` (Zeilen 137–166)
- Vergleicht den **Schreibstil** von Musk und Trump anhand drei Metriken:
  - **Durchschnittliche Textlänge** (in Zeichen)
  - **Großbuchstaben-Anteil** (in Prozent) – zeigt, wie oft in CAPS geschrieben wird
  - **Ausrufezeichen** (Durchschnitt pro Post, skaliert x10 für bessere Sichtbarkeit)
- Verwendet ein **gruppiertes Balkendiagramm** (`barmode='group'`).

### `create_overview_stats()` (Zeilen 168–182)
- Gibt eine **Markdown-Tabelle** zurück (kein Plotly-Diagramm).
- Zeigt eine Zusammenfassung: Gesamtanzahl Posts, Anzahl verschiedener Emojis, meistverwendetes Emoji und meisterwähnter Benutzer.

---

## 6. Gradio-Oberfläche (Zeilen 184–233)

### Grundstruktur

```python
with gr.Blocks(title="Trump vs Musk Analyzer", theme=gr.themes.Soft()) as demo:
```

- **`gr.Blocks`**: Die flexibelste Gradio-Layout-Komponente. Ermöglicht freie Anordnung von UI-Elementen.
- **`title`**: Der Titel, der im Browser-Tab angezeigt wird.
- **`theme=gr.themes.Soft()`**: Ein vordefiniertes Gradio-Theme mit weichen, abgerundeten Stilen.

### Tabs

Die Oberfläche ist in zwei Tabs unterteilt:

#### Tab 1: Predictor (Zeilen 191–214)

```python
with gr.TabItem("Predictor"):
```

Dieser Tab enthält die interaktive Vorhersage-Funktion:

- **`gr.Textbox`**: Ein mehrzeiliges Eingabefeld, in das der Benutzer einen Text eingeben kann.
- **`gr.Button("Predict", variant="primary")`**: Ein Button, der die Vorhersage auslöst. `variant="primary"` gibt dem Button eine hervorgehobene Farbe.
- **`gr.Label`**: Zeigt das Ergebnis der Vorhersage an – mit Prozentwerten für Trump und Musk. `num_top_classes=2` zeigt beide Klassen an.
- **`predict_btn.click(fn=predict, inputs=text_input, outputs=output_label)`**: Verknüpft den Button mit der importierten `predict()`-Funktion aus `predict.py`. Beim Klick wird der Text aus dem Eingabefeld an die Funktion übergeben und das Ergebnis im Label angezeigt.
- **`gr.Examples`**: Zeigt vordefinierte Beispieltexte an, die der Benutzer anklicken kann, um sie schnell zu testen.

#### Tab 2: Data Analysis (Zeilen 216–230)

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
| `predict` (intern) | Importiert `predict()` für die Vorhersage (lädt Modell & Tokenizer intern) |
| `pandas` | Laden und Verarbeiten der CSV-Daten |
| `plotly` | Interaktive Diagramme |
| `emoji` | Emoji-Erkennung in Texten |
| `re` | Reguläre Ausdrücke für Mentions und Hashtags |
| `collections.Counter` | Zählen von Häufigkeiten |
