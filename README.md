## 🚀 Automatic Fiat Stock Analyzer ("Fiat Trade Calculator")

A desktop GUI tool that automatically scans a broad list of popular U.S. stocks (S&P 500 subset + popular tech tickers) and ranks them by a simple 3-point criteria using options-implied data from Yahoo Finance.

> This app is for educational and research use only. It does not provide investment advice.

### ✨ Key features
- 🔎 **Automatic scan**: Analyzes ~100 widely traded tickers with one click
- 📡 **Live market data**: Pulls quotes, options chains, and volumes via `yfinance`
- 🧮 **Options-driven metrics**:
  - 📈 **IV30/RV30** using Yang–Zhang realized volatility
  - 📉 **Term structure slope** between near and ~45 DTE expiries
  - 🎯 **Expected move** from ATM straddle mid-price on the first considered expiry
- ⭐ **Simple scoring (0–3)** and an at-a-glance recommendation label
- 🖥️ **Responsive UI** with progress bar and real-time console logs

### 🧠 How scoring works (high level)
For each ticker:
- 🏁 **Scored criteria (1 point each):**
  - 📊 **Volume filter**: 30D average volume ≥ 1,500,000
  - ⚡ **Volatility premium**: IV30/RV30 ≥ 1.25 (RV via Yang–Zhang)
  - 📉 **Term structure**: Slope between earliest included expiry and ~45 DTE ≤ -0.00406
- ℹ️ **Informational (not scored):**
  - 🎯 **Expected move**: Displayed when ATM straddle mid can be computed

Total score is the number of scored criteria met (0–3). "Expected move" does not affect the score. The UI maps score to a visual recommendation.

🧭 In simple terms:
- 3 points: Strong Buy (🔥)
- 2 points: Buy (✅)
- 1 point: Consider (⚠️)
- 0 points: Avoid (❌)

A stock earns 1 point for each check it passes: volume, IV vs RV, and term-structure slope.

### 🧰 Requirements
- 🐍 **Python**: 3.10–3.12 (NumPy 2.x and SciPy ≥ 1.15 require Python ≥ 3.10)
- 🖥️ **OS**: Windows, macOS, or Linux
- 🌐 **Network access**: Required to reach Yahoo Finance and Wikipedia

Python dependencies (also in `requirements.txt`):
```
FreeSimpleGUI==5.1.1
numpy==2.1
scipy==1.15.1
yfinance==0.2.54
requests==2.31.0
```

### 🛠️ Install
1. Create and activate a virtual environment
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - macOS/Linux:
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```
2. Install dependencies
   ```bash
   pip install -U pip setuptools wheel
   pip install -r requirements.txt
   ```

### ▶️ Run
```bash
python calculator.py
```
Then click "Start Auto Analysis". Keep the window open during analysis. Progress and helpful logs also appear in the terminal.

### 📝 Notes and data sources
- 🏷️ **Tickers**: Fetched from Wikipedia’s S&P 500 page when available; otherwise falls back to a built-in popular list
- 💹 **Options/quotes**: Pulled via `yfinance` from Yahoo Finance
- 🧩 **Interpolation**: Linear spline over ATM IVs across expirations using SciPy
- 🖥️ **GUI**: Built with `FreeSimpleGUI`

### 🧯 Troubleshooting
- 🔧 **SciPy/NumPy install issues**: Ensure a 64-bit Python and an up-to-date `pip`/`setuptools`/`wheel`.
- 🚦 **Rate limits or missing data**: Yahoo Finance may throttle. Re-run later or reduce frequency.
- 📅 **"No options found" / "Not enough option data"**: Some tickers or sessions won’t have chains or expiries meeting the ~45 DTE requirement.
- 🌐 **Network/SSL errors**: Confirm internet connectivity and that corporate proxies/firewalls allow access to Yahoo/Wikipedia.
- 🖼️ **Emoji rendering**: If UI emojis look odd, it’s just a font/OS rendering quirk; functionality is unaffected.

### ⚠️ Limitations
- 🌐 Uses end-user network and public sources; stability and coverage can vary
- 🌍 Not all non-U.S. symbols are supported
- 🧪 Results are heuristic and simplified; they may not reflect tradable liquidity or spreads

### ⚖️ Disclaimer
This software is provided solely for educational and research purposes. It is not intended to provide investment advice. The developers are not financial advisors and accept no responsibility for any financial decisions or losses resulting from use of this software. Always consult a professional financial advisor before making any investment decisions.

### 🙏 Acknowledgments
- **Volatility Vibes**: Credit for the YouTube video ["Upgrading Options Scanner Script" (YouTube)](https://www.youtube.com/watch?v=oW6MHjzxHpU), which inspired and informed this project. This script was created by upgrading and adapting the approach demonstrated in that video.

### 📄 License
No license specified. If you plan to distribute or modify, add a license to this repository.
