# WhatsApp Chat Analyzer (Streamlit)

A Streamlit-based app to analyze WhatsApp group chat `.txt` export files. Upload your exported chat and get instant visual insights with multiple interactive tabs.

## Features
- Parses WhatsApp chat exports in the format `DD/MM/YY, HH:MM - Sender: Message`.
- Supports overall and individual user filtering.
- Shows basic statistics: total messages, total users, media shared, links shared.
- Visualizes messages over time: daily, monthly, hourly activity.
- Displays top emojis used with counts and descriptions.
- Highlights top media sharers in the group.
- Generates word clouds from chat messages.
- Interactive UI with separate tabs for stats, messages over time, emojis, media shares, and word cloud.

## Run locally
- Requirements: Python 3.7+ and the required Python packages.
- Install dependencies:

```bash
pip install streamlit pandas matplotlib seaborn emoji wordcloud
```
Run the app from the project root directory:

streamlit run app.py
Open the provided local URL (usually http://localhost:8501) in your web browser.

## Project structure
app.py: Main Streamlit application with chat parsing, analysis, and UI.

## requirements.txt: List of Python packages (optional).

## Customization
Adjust chat parsing regex in app.py to support different WhatsApp export formats.

Modify matplotlib and seaborn styling and figure sizes inside app.py.

Extend functionality by adding new tabs or charts in the Streamlit app.
