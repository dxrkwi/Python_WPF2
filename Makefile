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

# Show help
help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make dashboard  - Run web interface (http://127.0.0.1:7860)"
	@echo "  make train      - Full training pipeline (tokenize + train)"
	@echo "  make scrape     - Run data scraping"
	@echo "  make predict    - Run prediction in terminal"

.PHONY: install dashboard train scrape predict help