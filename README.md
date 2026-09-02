# Trading Bot (Oltin Bozor Prognoz)

Gold Market Analytics and Telegram Trading Bot.

## Overview
This bot analyzes gold (XAU/USD) market data, computes technical indicators, macroeconomic snapshots, and AI-driven market predictions, and provides interactive Telegram commands.

## Features
- Real-time & historical Gold data fetching (GoldAPI, YFinance)
- Technical analysis engine (RMA/EMA, RSI, MACD, Support/Resistance)
- Market regime classification & Macro analysis
- AI-powered market forecasts using Gemini API
- Telegram Bot interface (Aiogram 3)
- Embedded HTTP Health Check Endpoint (`/health` & `/`) to keep the bot active 24/7 on free hosts
- SQLite local database storage
- Paper trading & risk management modules

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/raximovjavohirlek-hash/trading-bot.git
   cd trading-bot
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
   Set `TELEGRAM_BOT_TOKEN`, `GOLDAPI_KEY`, `GEMINI_API_KEY`, etc.

5. **Run the bot locally:**
   ```bash
   python main.py
   ```

---

## 🚀 Deploying to Render (Free Tier)

### Render Settings:
- **Service Type:** `Web Service`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`
- **Environment Variables:**
  - `TELEGRAM_BOT_TOKEN`: *your bot token from @BotFather*
  - `GOLDAPI_KEY`: *your GoldAPI key*
  - `GEMINI_API_KEY`: *your Gemini API key*
  - `PYTHON_VERSION`: `3.11.0`

### ⏰ Preventing Sleep Mode with UptimeRobot:
Render's free tier Web Services go to sleep after 15 minutes of inactivity. To keep your bot awake **24/7 for FREE**:

1. Register on [UptimeRobot.com](https://uptimerobot.com) (Free Plan).
2. Click **Add New Monitor**.
3. Configure the monitor:
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `Trading Bot`
   - **URL (or IP):** `https://<your-render-app-name>.onrender.com/health`
   - **Monitoring Interval:** `5 minutes`
4. Click **Create Monitor**. UptimeRobot will ping your Render service every 5 minutes, preventing it from spinning down!
