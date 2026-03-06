import pandas as pd
import time
import re
import random
import os
from playwright.sync_api import sync_playwright
from rich.console import Console
from rich.panel import Panel

console = Console()
yellow_console = Console(style="yellow")
warning_console = Console(style="bold red")

TRUMP_ID = "107780257626128497"
SAVE_FILE = "trump_truths_progress.csv"
ID_TRACKER = "last_id.txt"
USERNAME = "@realDonaldTrump"
MAX_WAIT = 600 # 10 minuten
_HTML_TAG_RE = re.compile('<.*?>')

class resilient_scraper:
    def __init__(self, user_id, username, target_count=10000):
        """
        Initialize the scraper and resume from last saved ID if available.

        Args:
            user_id: The Truth Social account ID to scrape.
            username: The Truth Social username (e.g. @realDonaldTrump).
            target_count: Number of posts to collect before stopping.
        """
        self.user_id = user_id
        self.username = username
        self.target_count = target_count
        self.all_posts = []
        self.max_id = None
        self.backoff_time = 10
        self.consecutive_errors = 0

        if os.path.exists(ID_TRACKER):
            with open(ID_TRACKER, 'r') as f:
                saved_id = f.read().strip()
                if saved_id.isdigit():
                    self.max_id = saved_id
                    console.print(f"Setze Scraping ab ID {self.max_id} fort...")
                else:
                    console.print(f"[yellow]Ungültige ID '{saved_id}' in {ID_TRACKER} – wird ignoriert.[/yellow]")

    def clean_html(self, raw_html):
        """
        Remove HTML tags and normalize whitespace from a raw HTML string.

        Args:
            raw_html: Raw HTML string to clean.

        Returns:
            Cleaned plain text string, or empty string if input is unfitting.
        """
        if not raw_html: return ""
        return re.sub(_HTML_TAG_RE, '', raw_html).replace('\n', ' ').replace('\r', '').replace(',', ';').strip()

    def _parse_batch(self, data):
        """
        Extract non-empty post content from a list of API response entries.

        Args:
            data: List of post objects returned by the Truth Social API.

        Returns:
            List of [author, content] pairs with HTML stripped.
        """
        return [
            ["Trump", content]
            for entry in data
            if (content := self.clean_html(entry.get('content', '')))
        ]

    def save_batch(self, new_batch, max_id, message):
        """
        Append a batch of posts to the CSV file and update the ID tracker.

        Args:
            new_batch: List of [author, content] pairs to save.
            max_id: The pagination cursor ID to write to last_id.txt.
            message: Status message to print to the console after saving.
        """
        if new_batch:
            pd.DataFrame(new_batch).to_csv(SAVE_FILE, mode='a', index=False, header=False, encoding='utf-8')
            self.all_posts.extend(new_batch)
            console.print(message)
            if max_id:
                with open(ID_TRACKER, 'w') as f:
                    f.write(str(max_id))

    def handle_response(self, response):
        """
        Playwright response event handler that captures posts intercepted during page scrolling.

        Args:
            response: Playwright Response object from the page event listener.
        """
        if not ("api/v1/accounts" in response.url and "statuses" in response.url and response.status == 200):
            return
        try:
            data = response.json()
            if not isinstance(data, list): return
            if not data: return

            new_batch = self._parse_batch(data)
            self.max_id = data[-1].get('id')
            self.save_batch(new_batch, self.max_id, f"Captured {len(new_batch)} posts via scrolling. Total: {len(self.all_posts)}")

        except Exception as e:
            warning_console.print(f"Error handling response: {e}")

    def wait_for_content(self, page):
        """
        Block until the page has loaded real content or the timeout is reached.
        Prompts the user to solve any Cloudflare challenge if needed.

        Args:
            page: Playwright Page object to monitor.
        """
        warning_console.print(Panel("--- CLOUDFLARE/CAPTCHA LÖSEN FALLS NÖTIG ---"))
        yellow_console.print("Warte auf Content...")
        start_wait = time.time()

        while True:
            current_title = page.title()
            is_cloudflare = any(s in current_title for s in ["Just a moment", "Nur einen Moment", "Cloudflare"])
            has_feed = page.locator('div[role="feed"]').count() > 0
            has_article = page.locator('article').count() > 0
            has_header = page.locator('div[data-testid="header"]').count() > 0

            console.print(f"Status: Title='{current_title}' | Feed={has_feed} | Article={has_article} | Header={has_header}")

            content_detected = not is_cloudflare and (has_feed or has_article or has_header or "Trump" in current_title)
            if content_detected:
                console.print("Timeline/Content erkannt! Beginne mit Scrollen...")
                break

            if time.time() - start_wait > MAX_WAIT:
                warning_console.print("Zeitüberschreitung beim Warten auf Content.")
                break

            time.sleep(5)

    def fetch_batch(self, page):
        """
        Fetch the next batch of posts from the Truth Social API via page.evaluate.
        Uses max_id as a pagination cursor to retrieve older posts.

        Args:
            page: Playwright Page object used to execute the fetch request.

        Returns:
            Dict with 'status' (HTTP status code) and 'json' (response data or None).
        """
        api_url = f"https://truthsocial.com/api/v1/accounts/{self.user_id}/statuses?limit=40"
        if self.max_id:
            api_url += f"&max_id={self.max_id}"

        return page.evaluate(f"""async () => {{
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

    def handle_status(self, status, response_data, page):
        """
        Handle the API response status code and take appropriate action.

        Args:
            status: HTTP status code from the fetch response.
            response_data: Full response dict containing 'status' and 'json'.
            page: Playwright Page object, used for mouse movement on 403.

        Returns:
            True to continue scraping, False to stop.
        """
        match status:
            case 200:
                data = response_data.get('json')
                if not data:
                    warning_console.print("Keine weiteren Daten empfangen (Leere Liste).")
                    return False  # Signal to stop

                new_batch = self._parse_batch(data)
                self.max_id = data[-1].get('id')
                self.save_batch(new_batch, self.max_id, f" + {len(new_batch)} Posts geladen. (ID: {self.max_id})")
                self.backoff_time = 5
                self.consecutive_errors = 0
                time.sleep(random.uniform(1.0, 2.0))

            case 429:
                yellow_console.print(f"Rate Limit (429). Warte {self.backoff_time}s...")
                time.sleep(self.backoff_time)
                self.backoff_time = min(self.backoff_time * 2, 60)

            case 403:
                warning_console.print("Zugriff 403 (Forbidden). Cloudflare? Warte und bewege Maus...")
                page.mouse.move(random.uniform(100, 500), random.uniform(100, 500))
                time.sleep(5)
                self.consecutive_errors += 1

            case _:
                warning_console.print(f"Unerwarteter Status: {status}")
                time.sleep(5)
                self.consecutive_errors += 1

        return True  # Continue

    def run(self):
        """
        Launch the browser, navigate to the target profile, and run the scraping loop
        until the target post count is reached. 
        """
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir="user_data",
                headless=False,
                channel="chrome",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                    "--no-sandbox"
                ],
                viewport=None
            )

            page = browser.pages[0]
            console.print("Versuche echten Chrome Browser zu nutzen...")
            page.on("response", self.handle_response)

            page.goto("https://truthsocial.com/" + self.username, wait_until="domcontentloaded")
            self.wait_for_content(page)
            console.print("Wechsle zum Hochgeschwindigkeits-Modus (API Fetch)...")

            while len(self.all_posts) < self.target_count:
                console.print(f"Hole Daten... (Gesamt: {len(self.all_posts)})")
                try:
                    response_data = self.fetch_batch(page)
                    status = response_data.get('status')
                    should_continue = self.handle_status(status, response_data, page)
                    if not should_continue:
                        break

                    if self.consecutive_errors > 5:
                        warning_console.print("Zu viele Fehler. Pause und Reload...")
                        time.sleep(30)
                        page.reload()
                        time.sleep(10)
                        self.consecutive_errors = 0

                except Exception as e:
                    warning_console.print(f"Fehler bei Request: {e}")
                    time.sleep(5)

            browser.close()
            console.print(Panel(f"[green]Scraping abgeschlossen! {len(self.all_posts)} Posts gesammelt.[/]", title="Done"))

if __name__ == "__main__":
    resilient_scraper(TRUMP_ID, USERNAME, 10000).run()
