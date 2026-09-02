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
   Set `TELEGRAM_BOT_TOKEN`, `GOLDAPI_KEY`, etc.

5. **Run the bot:**
   ```bash
   python main.py
   ```
