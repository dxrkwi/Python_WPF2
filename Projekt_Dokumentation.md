# **Transformer Based Person Recognition for Study Purposes**

## **Projektübersicht**

Das Projekt _Transformer Based Person Recognition for Study Purposes_ dient der Entwicklung eines maschinellen Lernmodells zur Erkennung von Personen basierend auf ihren Social-Media-Posts. Das System nutzt Transformer-Modelle, um Tweets von Donald J. Trump und Elon Musk zu klassifizieren. Der Fokus liegt auf dem Scraping von Daten, der Tokenisierung, dem Training eines Modells und der Bereitstellung einer interaktiven Weboberfläche zur Vorhersage.

### **Rahmendaten des Projekts**

- **Veranstaltung:** Programmieren in Python (WPF II)
- **Projektzeitraum:** Sommersemester 2025
- **Abgabedatum:** Mittwoch, 12. März 2025
- **Dozent:** Prof. Dr.-Ing. Michael Arnold

## **Projektbeteiligte**

| Name             | Matrikelnummer |
| ---------------- | -------------- |
| Lukas Scholz     |  |
| Mark Widulla     |  |  
| Janik Dehnhardt  |  |    
| Cathleen Czechan |  |
| Kevin Karahali   |  |
| Peter Pütz       | 46658          |

---

## **Projektbeschreibung**

### **Hintergrund und Zielsetzung**

Social-Media-Posts enthalten oft charakteristische Merkmale, die es ermöglichen, den Autor zu identifizieren. Dieses Projekt zielt darauf ab, ein Transformer-basiertes Modell zu trainieren, das Tweets von Donald J. Trump (von Truth Social) und Elon Musk (von Twitter) unterscheidet. Die Daten werden gesammelt, verarbeitet und das Modell evaluiert, um eine hohe Genauigkeit zu erreichen.

### **Bisherige Vorgehensweise**

- Manuelles Sammeln von Tweets.
- Händische Annotation der Daten.
- Einfache Modelle ohne Transformer.

### **Zukünftige Vorgehensweise mit diesem Projekt**

- Automatisiertes Scraping von Truth Social für Trump-Daten.
- Verwendung vorhandener Musk-Datensätze.
- Tokenisierung und Training eines BERTweet-Modells.
- Bereitstellung einer Gradio-basierten Weboberfläche für interaktive Vorhersagen.
- Evaluation des Modells auf Genauigkeit.

### **Identifikationsmerkmale für die Erkennung**

Die Klassifikation basiert auf:

- Textinhalt der Tweets
- Stilistische Merkmale (z.B. Emojis, Hashtags)
- Kontextuelle Informationen

---

## **Funktionale Anforderungen**

- Scraping von Truth Social für Trump-Tweets.
- Laden und Konvertierung von Musk-Twitter-Datensätzen.
- Tokenisierung der Daten mit BERTweet-Tokenizer.
- Training eines Sequence-Classification-Modells.
- Vorhersage von Tweet-Autorenschaft.
- Bereitstellung einer interaktiven Gradio-Weboberfläche.
- Evaluation des Modells.

---

## **Technische Anforderungen**

- **Plattformunabhängigkeit:** Die Anwendung läuft unter Linux, Windows und macOS.
- **Entwicklungsumgebung:** Microsoft Visual Studio Code mit Erweiterungen wie Python, Pylint.
- **Pakete und Abhängigkeiten:**
  - Installation der Python-Pakete über:
    ```bash
    pip install -r requirements.txt
    ```
  - Zusätzliche Pakete für Scraping: Playwright (optional).

---

## **Anwendungsstruktur**

Die Anwendung ist in folgende Module unterteilt:

| Modul                            | Verantwortliche               | Ordner       |
| -------------------------------- | ----------------------------- | ------------ |
| **Scraping**                     | Janik Dehnhardt & Lukas Scholz| `data/`      |
| **Tokenisierung**                | Peter Pütz                    | `src/`       |
| **Transformer-Training**         | ...                           | `src/`       |
| **Vorhersage**                   | ...                           | `src/`       |
| **Dashboard (Gradio)**           | Kevin Karahali                | `src/`       |
| **Evaluation**                   | Mark Widulla                  | `src/`       |
| **Utilities**                    | ...                           | `src/`       |

---

## **Projektstart & Debugging**

Zur Ausführung:

1. Für lokales Training: `python src/main.py --data_dir /path/to/data --local`
2. Für Vorhersage: Interaktiver Modus in main.py.
3. Dashboard: `python src/dashboard.py`

Debugging erfolgt über VS Code mit Python-Debugger.

---

## **Tests & Qualitätssicherung**

Evaluation in `src/eval.py`. Automatisierte Tests können mit unittest durchgeführt werden, falls vorhanden.

---

## **Konfigurationsdatei**

Verwendung von `.env` für Hugging Face API-Token:

```env
HUGGINGFACE_API=your_token_here
```