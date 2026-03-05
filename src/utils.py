# Utilities
# Lukas Scholz / Cathleen Czechan
import sys
import time
import threading

class Spinner:
    def __init__(self, message="Processing"):
        self.message = message
        self.spinner = ["|","/","-","\\"]
        self.running = False
        self.thread = None
    def spin(self):
        i = 0
        while self.running:
            sys.stdout.write(f"\r{self.message} {self.spinner[i % len(self.spinner)]}  ")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.spin, daemon = True)
        self.thread.start()
    def stop(self):
        self.running = False
        self.thread.join()
        sys.stdout.write("\r✔" + self.message + " done\n")