import pandas as pd
import re

def transform_musk_final_fix(input_file, output_file):
    """
    1. Wandelt Format in 'Musk,Text' um.
    2. Entfernt Zeilenumbrüche innerhalb von Tweets.
    3. Ersetzt Text-Kommas durch Semikolons (außer nach 'Musk').
    """
    try:
        # 1. Daten laden
        df = pd.read_csv(input_file, engine='python', on_bad_lines='skip')
        
        if 'fullText' not in df.columns:
            print(f"Fehler: Spalte 'fullText' fehlt.")
            return

        processed_lines = []
        
        for text in df['fullText'].dropna():
            # SCHRITT A: Zeilenumbrüche entfernen
            # Wir ersetzen \n (Newline) und \r (Carriage Return) durch ein Leerzeichen
            clean_text = str(text).replace('\n', ' ').replace('\r', ' ')
            
            # SCHRITT B: "Musk," Prefix hinzufügen
            raw_line = f"Musk,{clean_text}"
            
            # SCHRITT C: Komma-Logik (Negative Lookbehind)
            # Nur Kommas ersetzen, die NICHT auf 'Musk' folgen
            final_line = re.sub(r'(?<!Musk),', ';', raw_line)
            
            processed_lines.append(final_line)

        # 2. Speichern der bereinigten Daten
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in processed_lines:
                f.write(line + '\n')
                
        print(f"Datei erfolgreich bereinigt und gespeichert: {output_file}")

    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    transform_musk_final_fix('all_musk_posts.csv', 'musk_fixed_final.csv')