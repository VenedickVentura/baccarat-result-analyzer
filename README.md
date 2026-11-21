# Baccarat Result Analyzer

A Streamlit dashboard for recording baccarat outcomes and reviewing descriptive statistics.

## Features
- Manual Player / Banker / Tie entry
- Screenshot upload with text OCR for visible PLAYER/BANKER/TIE labels
- OCR review and confirmation before importing results
- Counts, observed frequencies, recent history, and streak display
- Smoothed probability estimates and 10 illustrative sample picks
- CSV export

## Run locally
1. Install Python 3.10 or newer.
2. Install the Tesseract OCR engine and make sure `tesseract` is on PATH.
3. Install packages:
   `pip install -r requirements.txt`
4. Start:
   `streamlit run app.py`

## Deploy on Streamlit Community Cloud
1. Open https://share.streamlit.io/
2. Connect GitHub and select this repository.
3. Set main file path to `app.py`.
4. Deploy.

## Important limitations
- Text OCR only detects visible words such as PLAYER, BANKER, and TIE. It does not reliably decode baccarat road maps made only of colored circles.
- Always verify OCR results before importing.
- Results are stored in Streamlit session memory and may be lost when the session restarts. Download CSV to keep a copy.
- Baccarat outcomes are independent. Historical streaks do not predict the next hand. The 10 picks are illustrative samples, not guaranteed predictions or betting advice.
- The theoretical reference percentages are approximate standard 8-deck baccarat probabilities and may vary by game rules.
