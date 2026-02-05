import json
import pandas as pd
import time
import re
import random
import os
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

# Konstanten
TRUMP_ID = "107780257626128497"
SAVE_FILE = "trump_truths_progress.csv"
ID_TRACKER = "last_id.txt"

def clean_html(raw_html):
    if not raw_html: return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.replace('\n', ' ').replace('\r', '').replace(',', ';').strip()

def run_resilient_scraper(user_id, target_count=10000):
    all_truths = []
    
    # Lade die letzte ID, falls das Skript neu gestartet wurde
    max_id = None
    if os.path.exists(ID_TRACKER):
        with open(ID_TRACKER, 'r') as f:
            max_id = f.read().strip()
            print(f"Setze Scraping ab ID {max_id} fort...")

    # Persistenter Context speichert Cookies/Session, damit man das Captcha nur einmal lösen muss
    user_data_dir = "user_data"
    
    with sync_playwright() as p:
        # Launch Persistent Context mit weniger spezifischen Argumenten, 
        # um native Browser-Eigenschaften zu behalten.
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            channel="chrome", # Versucht, den installierten Google Chrome zu nutzen!
            args=[
                "--disable-blink-features=AutomationControlled", 
                "--start-maximized",
                "--no-sandbox"
            ],
            viewport=None
        )
        
        page = browser.pages[0]
        # stealth_sync(page) # Testweise deaktiviert, da Chrome Channel oft besser ohne läuft
        
        print("Versuche echten Chrome Browser zu nutzen...")

        # Response Listener, um die Daten "passiv" abzufangen beim Scrollen
        # Das vermeidet, dass wir selbst API Requests stellen müssen, die geblockt werden.
        def handle_response(response):
            # Prüfen ob es ein Status-Update Response ist
            if "api/v1/accounts" in response.url and "statuses" in response.url and response.status == 200:
                try:
                    data = response.json()
                    new_batch = []
                    
                    # Manchmal kommt eine Liste, manchmal Pagination-Objekt? 
                    # Bei Mastodon/TruthSocial ist es meist eine Liste.
                    if isinstance(data, list):
                        items = data
                    else:
                        return # Unbekanntes Format

                    if not items: return

                    local_max_id = None
                    for entry in items:
                        content = clean_html(entry.get('content', ''))
                        if content:
                            new_batch.append(["Trump", content])
                        local_max_id = entry.get('id')
                    
                    if new_batch:
                        # Speichern
                        df_temp = pd.DataFrame(new_batch)
                        df_temp.to_csv(SAVE_FILE, mode='a', index=False, header=False, encoding='utf-8')
                        
                        all_truths.extend(new_batch)
                        print(f"Captured {len(new_batch)} posts via scrolling. Total: {len(all_truths)}")

                        # ID Tracker updaten (optional, da wir eh scrollen)
                        if local_max_id:
                            with open(ID_TRACKER, 'w') as f:
                                f.write(str(local_max_id))
                                
                except Exception as e:
                    # JSON Fehler oder so
                    pass

        page.on("response", handle_response)

        print("Initialisiere Seite...")
        page.goto("https://truthsocial.com/@realDonaldTrump", wait_until="domcontentloaded")
        
        print("--- BITTE MANUELL CLOUDFLARE/CAPTCHA LÖSEN FALLS NÖTIG ---")
        print("Das Skript wartet und beginnt dann zu scrollen.")
        
        # Warte, bis der User das Captcha gelöst hat
        print("Warte auf Umgehung der Cloudflare-Seite...")
        
        start_wait = time.time()
        max_wait = 600 # 10 Minuten
        
        while True:
            current_title = page.title()
            current_url = page.url
            
            # Check Cloudflare indicators
            is_cloudflare = "Just a moment" in current_title or "Nur einen Moment" in current_title or "Cloudflare" in current_title
            
            # Check Success indicators
            has_feed = page.locator('div[role="feed"]').count() > 0
            has_article = page.locator('article').count() > 0
            has_header = page.locator('div[data-testid="header"]').count() > 0
            
            print(f"Status: Title='{current_title}' | Feed={has_feed} | Article={has_article} | Header={has_header}")
            
            if (not is_cloudflare) and (has_feed or has_article or has_header or "Trump" in current_title):
                print("Timeline/Content erkannt! Beginne mit Scrollen...")
                break
                
            if time.time() - start_wait > max_wait:
                print("Zeitüberschreitung beim Warten auf Content.")
                break
                
            time.sleep(2)

        print("Timeline erkannt! Wechsle zum Hochgeschwindigkeits-Modus (API Fetch)...")
        
        # Backoff Variablen
        backoff_time = 10
        consecutive_errors = 0
        
        while len(all_truths) < target_count:
            # URL bauen
            api_url = f"https://truthsocial.com/api/v1/accounts/{user_id}/statuses?limit=40" # Limit 40 ist oft Standard
            if max_id:
                api_url += f"&max_id={max_id}"
                
            print(f"Hole Daten... (Gesamt: {len(all_truths)})")
            
            try:
                # Führe fetch() direkt im Browser-Kontext aus
                # Das nutzt exakt die Cookies/Headers des eingeloggten Users/Browsers
                response_data = page.evaluate(f"""async () => {{
                    try {{
                        const response = await fetch("{api_url}", {{
                            headers: {{
                                'Accept': 'application/json, text/plain, */*',
                                'Content-Type': 'application/json'
                            }}
                        }});
                        return {{
                            status: response.status,
                            json: await response.json().catch(() => null)
                        }};
                    }} catch (e) {{
                        return {{ status: 0, error: e.toString() }};
                    }}
                }}""")
                
                status = response_data.get('status')
                
                if status == 200:
                    data = response_data.get('json')
                    
                    if not data:
                        print("Keine weiteren Daten empfangen (Leere Liste).")
                        break
                        
                    # Daten verarbeiten
                    new_batch = []
                    for entry in data:
                        content = clean_html(entry.get('content', ''))
                        if content:
                            new_batch.append(["Trump", content])
                        max_id = entry.get('id')
                    
                    # Speichern
                    if new_batch:
                        df_temp = pd.DataFrame(new_batch)
                        df_temp.to_csv(SAVE_FILE, mode='a', index=False, header=False, encoding='utf-8')
                        all_truths.extend(new_batch)
                        print(f" + {len(new_batch)} Posts geladen. (ID: {max_id})")
                    
                    # Reset Error Counters
                    backoff_time = 5
                    consecutive_errors = 0
                    
                    # Save ID
                    if max_id:
                        with open(ID_TRACKER, 'w') as f:
                            f.write(str(max_id))
                            
                    # Kurze Pause für API Fairness (schneller als Scrollen, aber nicht zu aggressiv)
                    time.sleep(random.uniform(1.0, 2.0))
                    
                elif status == 429:
                    print(f"Rate Limit (429). Warte {backoff_time}s...")
                    time.sleep(backoff_time)
                    backoff_time = min(backoff_time * 2, 60) # Max 60s
                    
                elif status == 403:
                    print("Zugriff 403 (Forbidden). Cloudflare Check? Warte und bewege Maus...")
                    page.mouse.move(random.uniform(100, 500), random.uniform(100, 500))
                    time.sleep(5)
                    consecutive_errors += 1
                    
                else:
                    print(f"Unerwarteter Status: {status}")
                    time.sleep(5)
                    consecutive_errors += 1
                    
                if consecutive_errors > 5:
                    print("Zu viele Fehler in Folge. Breche ab (oder Pause).")
                    time.sleep(30)
                    # Versuch eines Reloads um Session zu fixen
                    page.reload()
                    time.sleep(10)
                    consecutive_errors = 0
            
            except Exception as e:
                print(f"Fehler bei Request: {e}")
                time.sleep(5)
            
        browser.close()

run_resilient_scraper(TRUMP_ID, 10000)