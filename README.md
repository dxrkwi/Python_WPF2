# Transformer Based Person Recognition for Study Purposes
This project is for Educational purposes only and in the end should create a "Person Recognizer" with Datasets Labeled with the Author's Name and written "Tweet/Text" on Social Media.

This Dataset only Purpose is the Transformer Detection Rate eval via Social Media, which often gets new Data
# Data:
### Donald J. Trump:
- Scraped Truthsocial via scrape.py
### Elon R. Musk
- Simplified Dataset from via Convert.py: Dada Lyndell. (2025). Elon Musk Tweets 2010 to 2025 (April) [Data set]. Kaggle. https://doi.org/10.34740/KAGGLE/DSV/11393660

## Running scraper via docker
inside data directory
```bash
docker build -f dockerfile -t scrape . && docker run -it \
  -p 6080:6080 \
  -v $(pwd)/user_data:/app/user_data \
  scrape:latest
```
Then in the browser visit: [vnc link](http://localhost:6080/vnc.html)
