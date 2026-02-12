# ============================================
# Trump vs Musk Predictor - Makefile
# ============================================

# Install all dependencies
install:
	pip install -r requirements.txt

# Run the Gradio dashboard (web interface)
dashboard:
	python src/dashboard.py

# Full training pipeline (tokenize + train)
train:
	python src/tokenizer.py
	python src/Transformer.py

# Run data scraping (requires playwright)
scrape:
	pip install -r requirements-scrape.txt
	playwright install
	python data/scrape.py

# Run prediction from terminal
predict:
	python src/predict.py

# Stop the dashboard
stop:
	pkill -f dashboard.py || true

# Restart the dashboard
restart: stop dashboard

# Show help
help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make dashboard  - Run web interface (http://127.0.0.1:7860)"
	@echo "  make train      - Full training pipeline (tokenize + train)"
	@echo "  make scrape     - Run data scraping"
	@echo "  make predict    - Run prediction in terminal"
	@echo "  make stop       - Stop the dashboard"
	@echo "  make restart    - Restart the dashboard"

.PHONY: install dashboard train scrape predict stop restart help