# Lead Scraper Project

## Overview
This tool is designed to extract professional contact information (Name, Title, Company) from public LinkedIn profiles. It demonstrates a robust, zero-dependency approach to web scraping and data enrichment.

## Features
- **Zero-Dependency Architecture**: Built entirely with Python standard libraries (`urllib`, `html.parser`, `re`), ensuring easy deployment without complex environment setups (no `pip install` required).
- **Authentication Support**: Accepts LinkedIn `li_at` session cookies to bypass authwalls and access real profile data.
- **Resilient Parsing**: Uses regex and flexible pattern matching to handle dynamic HTML structures.
- **Smart Enrichment**: Auto-generates probable corporate email addresses based on collected data (Pattern: `first.last@company.com`).
- **Data Validation**: Includes syntax checking for generated emails.
- **Demo Mode**: Includes a built-in simulation mode to demonstrate extraction logic safely.

## Structure
- `tools/`: Contains the executable Python scripts.
- `workflows/`: Standard Operating Procedures (SOPs) for usage.
- `.tmp/`: Stores extraction outputs (CSV).

## 🚀 Quick Start
### For Windows Users (Easiest)
1. **Clone or Download** this repository.
2. Double-click **`run_ui.bat`**.
3. That's it! The script will install dependencies and open the App.

### For Developers (Manual)
```bash
# 1. Clone repo
git clone https://github.com/AldoPgm/lead-scraper-pro.git
cd lead-scraper-pro

# 2. Install requirements
pip install streamlit pandas duckduckgo-search

# 3. Run App
streamlit run app.py
```

## Usage
### 1. Web Interface (Streamlit)
Run purely in demo mode to test the logic:
```bash
python tools/scrape_leads.py --urls "https://www.linkedin.com/in/target" --demo
```

### 2. Live Scraper (With Cookie)
For actual extraction, provide your `li_at` cookie:
```bash
python tools/scrape_leads.py --urls "https://www.linkedin.com/in/real-profile" --cookie "YOUR_LI_AT_COOKIE"
```

### 3. Web Interface (Streamlit)
For a visual experience with CSV export:
1. Double-click `run_ui.bat`.
2. The browser will open automatically at `http://localhost:8501`.
3. Enter URLs, configure settings, and download your data.

To see the help menu:
```bash
python tools/scrape_leads.py --help
```

## Disclaimer
This tool is for educational and testing purposes. Automated scraping of LinkedIn may violate their Terms of Service. Use responsibly.
