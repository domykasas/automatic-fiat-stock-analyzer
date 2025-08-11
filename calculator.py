"""
DISCLAIMER: 

This software is provided solely for educational and research purposes. 
It is not intended to provide investment advice, and no investment recommendations are made herein. 
The developers are not financial advisors and accept no responsibility for any financial decisions or losses resulting from the use of this software.
Always consult a professional financial advisor before making any investment decisions.
"""


import FreeSimpleGUI as sg
import yfinance as yf
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
import numpy as np
import threading
import requests
from curl_cffi import requests as cfr
import time
import random

# List of popular stocks to analyze (S&P 500 top stocks + some popular tech stocks)
POPULAR_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-B', 'UNH', 'JNJ',
    'JPM', 'V', 'PG', 'HD', 'MA', 'PFE', 'ABBV', 'AVGO', 'KO', 'PEP', 'TMO', 'COST',
    'DHR', 'MRK', 'ACN', 'VZ', 'ADBE', 'CRM', 'NFLX', 'PYPL', 'INTC', 'QCOM', 'AMD',
    'ORCL', 'IBM', 'CSCO', 'TXN', 'INTU', 'AMAT', 'MU', 'KLAC', 'LRCX', 'ADI', 'SNPS',
    'CDNS', 'MCHP', 'AVGO', 'SWKS', 'QRVO', 'CRUS', 'SLAB', 'MXL', 'SMTC', 'DIOD',
    'ON', 'STM', 'NXP', 'ASML', 'TSM', 'UMC', 'SMIC', 'GFS', 'AMBA', 'LSCC', 'XLNX'
]

def get_sp500_stocks():
    """Get S&P 500 stocks from Wikipedia"""
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Simple parsing to extract ticker symbols
            content = response.text
            import re
            # Look for ticker patterns in the table
            tickers = re.findall(r'<td><a[^>]*>([A-Z]{1,5})</a></td>', content)
            if tickers:
                return tickers[:100]  # Return first 100 stocks
    except:
        pass
    
    # Fallback to predefined list
    return POPULAR_STOCKS

def filter_dates(dates):
    today = datetime.today().date()
    cutoff_date = today + timedelta(days=45)
    
    sorted_dates = sorted(datetime.strptime(date, "%Y-%m-%d").date() for date in dates)

    arr = []
    for i, date in enumerate(sorted_dates):
        if date >= cutoff_date:
            arr = [d.strftime("%Y-%m-%d") for d in sorted_dates[:i+1]]  
            break
    
    if len(arr) > 0:
        if arr[0] == today.strftime("%Y-%m-%d"):
            return arr[1:]
        return arr

    raise ValueError("No date 45 days or more in the future found.")


# Create a persistent curl_cffi session (required by newer Yahoo stack)
YF_SESSION = cfr.Session(impersonate="chrome124")
YF_SESSION.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
})


def retry_with_backoff(operation, *, retries=3, base_delay_seconds=0.5, max_delay_seconds=4.0, exceptions=(Exception,), description="operation"):
    """Retry helper with exponential backoff and jitter for network operations."""
    attempt_index = 0
    last_error = None
    while attempt_index < retries:
        try:
            return operation()
        except exceptions as err:
            last_error = err
            attempt_index += 1
            if attempt_index >= retries:
                break
            # Exponential backoff with jitter
            backoff = min(max_delay_seconds, base_delay_seconds * (2 ** (attempt_index - 1)))
            jitter = random.uniform(0.0, 0.25 * backoff)
            sleep_seconds = backoff + jitter
            time.sleep(sleep_seconds)
    raise last_error if last_error else RuntimeError(f"{description} failed with unknown error")


def yang_zhang(price_data, window=30, trading_periods=252, return_last_only=True):
    log_ho = (price_data['High'] / price_data['Open']).apply(np.log)
    log_lo = (price_data['Low'] / price_data['Open']).apply(np.log)
    log_co = (price_data['Close'] / price_data['Open']).apply(np.log)
    
    log_oc = (price_data['Open'] / price_data['Close'].shift(1)).apply(np.log)
    log_oc_sq = log_oc**2
    
    log_cc = (price_data['Close'] / price_data['Close'].shift(1)).apply(np.log)
    log_cc_sq = log_cc**2
    
    rs = log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)
    
    close_vol = log_cc_sq.rolling(
        window=window,
        center=False
    ).sum() * (1.0 / (window - 1.0))

    open_vol = log_oc_sq.rolling(
        window=window,
        center=False
    ).sum() * (1.0 / (window - 1.0))

    window_rs = rs.rolling(
        window=window,
        center=False
    ).sum() * (1.0 / (window - 1.0))

    k = 0.34 / (1.34 + ((window + 1) / (window - 1)) )
    result = (open_vol + k * close_vol + (1 - k) * window_rs).apply(np.sqrt) * np.sqrt(trading_periods)

    if return_last_only:
        return result.iloc[-1]
    else:
        return result.dropna()
    

def build_term_structure(days, ivs):
    days = np.array(days)
    ivs = np.array(ivs)

    sort_idx = days.argsort()
    days = days[sort_idx]
    ivs = ivs[sort_idx]


    spline = interp1d(days, ivs, kind='linear', fill_value="extrapolate")

    def term_spline(dte):
        if dte < days[0]:  
            return ivs[0]
        elif dte > days[-1]:
            return ivs[-1]
        else:  
            return float(spline(dte))

    return term_spline

def get_current_price(ticker):
    todays_data = retry_with_backoff(
        lambda: ticker.history(period='1d'),
        retries=3,
        base_delay_seconds=0.75,
        description="get_current_price: history(period='1d')",
        exceptions=(Exception,)
    )
    if 'Close' not in todays_data or todays_data.empty:
        raise ValueError("No Close data in today's history")
    return todays_data['Close'].iloc[0]

def compute_recommendation(ticker):
    try:
        ticker = ticker.strip().upper()
        if not ticker:
            return "No stock symbol provided."

        # Use shared session and retries
        stock = yf.Ticker(ticker, session=YF_SESSION)

        try:
            stock_options = retry_with_backoff(
                lambda: list(stock.options),
                retries=3,
                base_delay_seconds=0.75,
                description="fetch options list",
                exceptions=(Exception,)
            )
            if len(stock_options) == 0:
                return f"Error: No options found for stock symbol '{ticker}'."
        except Exception as opt_err:
            return f"Error: Failed to fetch options for '{ticker}': {opt_err}"

        try:
            exp_dates = filter_dates(stock_options)
        except Exception:
            return "Error: Not enough option data."

        options_chains = {}
        for exp_date in exp_dates:
            try:
                chain = retry_with_backoff(
                    lambda d=exp_date: stock.option_chain(d),
                    retries=3,
                    base_delay_seconds=0.75,
                    description=f"fetch option_chain({exp_date})",
                    exceptions=(Exception,)
                )
                options_chains[exp_date] = chain
            except Exception:
                # Skip this expiration if it fails after retries
                continue

        try:
            underlying_price = get_current_price(stock)
            if underlying_price is None:
                raise ValueError("No market price found.")
        except Exception as price_err:
            return f"Error: Unable to retrieve underlying stock price: {price_err}"

        atm_iv = {}
        straddle = None
        i = 0
        for exp_date, chain in options_chains.items():
            calls = getattr(chain, 'calls', None)
            puts = getattr(chain, 'puts', None)

            if calls is None or puts is None or calls.empty or puts.empty:
                continue

            if 'strike' not in calls or 'strike' not in puts:
                continue

            call_diffs = (calls['strike'] - underlying_price).abs()
            call_idx = call_diffs.idxmin()
            call_iv = calls.loc[call_idx].get('impliedVolatility', np.nan)

            put_diffs = (puts['strike'] - underlying_price).abs()
            put_idx = put_diffs.idxmin()
            put_iv = puts.loc[put_idx].get('impliedVolatility', np.nan)

            if np.isnan(call_iv) or np.isnan(put_iv):
                continue

            atm_iv_value = (call_iv + put_iv) / 2.0
            atm_iv[exp_date] = atm_iv_value

            if i == 0:
                call_bid = calls.loc[call_idx].get('bid')
                call_ask = calls.loc[call_idx].get('ask')
                put_bid = puts.loc[put_idx].get('bid')
                put_ask = puts.loc[put_idx].get('ask')

                call_mid = ((call_bid + call_ask) / 2.0) if call_bid is not None and call_ask is not None else None
                put_mid = ((put_bid + put_ask) / 2.0) if put_bid is not None and put_ask is not None else None

                if call_mid is not None and put_mid is not None:
                    straddle = (call_mid + put_mid)

            i += 1

        if not atm_iv:
            return "Error: Could not determine ATM IV for any expiration dates."

        today = datetime.today().date()
        dtes = []
        ivs = []
        for exp_date, iv in atm_iv.items():
            exp_date_obj = datetime.strptime(exp_date, "%Y-%m-%d").date()
            days_to_expiry = (exp_date_obj - today).days
            dtes.append(days_to_expiry)
            ivs.append(iv)

        term_spline = build_term_structure(dtes, ivs)

        ts_slope_0_45 = (term_spline(45) - term_spline(dtes[0])) / (45 - dtes[0])

        price_history = retry_with_backoff(
            lambda: stock.history(period='3mo'),
            retries=3,
            base_delay_seconds=0.75,
            description="history(period='3mo')",
            exceptions=(Exception,)
        )

        iv30_rv30 = term_spline(30) / yang_zhang(price_history)

        avg_volume = price_history['Volume'].rolling(30).mean().dropna().iloc[-1]

        expected_move = str(round(straddle / underlying_price * 100, 2)) + "%" if straddle else None

        return {
            'avg_volume': avg_volume >= 1500000,
            'iv30_rv30': iv30_rv30 >= 1.25,
            'ts_slope_0_45': ts_slope_0_45 <= -0.00406,
            'expected_move': expected_move
        }
    except Exception as e:
        return f"Error: {e}"
        
def analyze_stock_auto(ticker):
    """Analyze a single stock and return results with ticker info"""
    try:
        result = compute_recommendation(ticker)
        if isinstance(result, dict):
            # Calculate score for ranking
            score = 0
            if result['avg_volume']:
                score += 1
            if result['iv30_rv30']:
                score += 1
            if result['ts_slope_0_45']:
                score += 1
            
            return {
                'ticker': ticker,
                'result': result,
                'score': score,
                'status': 'success'
            }
        else:
            return {
                'ticker': ticker,
                'result': result,
                'score': 0,
                'status': 'error'
            }
    except Exception as e:
        return {
            'ticker': ticker,
            'result': str(e),
            'score': 0,
            'status': 'error'
        }

def auto_analyze_stocks(progress_callback=None):
    """Automatically analyze multiple stocks and return ranked results (include errors)."""
    stocks_to_analyze = get_sp500_stocks()
    
    results = []
    total_stocks = len(stocks_to_analyze)
    
    for i, ticker in enumerate(stocks_to_analyze):
        try:
            # Update progress
            if progress_callback:
                progress = int((i / total_stocks) * 100)
                progress_callback(progress, f"Analyzing {ticker}... ({i+1}/{total_stocks})")
            
            # Add delay with small jitter to avoid rate limiting
            if i > 0:
                sleep_base = 0.35
                time.sleep(sleep_base + random.uniform(0.0, 0.2))
            
            result = analyze_stock_auto(ticker)
            results.append(result)
            
        except Exception as e:
            results.append({
                'ticker': ticker,
                'result': str(e),
                'score': 0,
                'status': 'error'
            })
    
    # Sort results: successes first by score desc, then errors
    def sort_key(item):
        is_error = 1 if item.get('status') != 'success' else 0
        score_value = item.get('score', 0)
        return (is_error, -score_value)

    results.sort(key=sort_key)
    return results

def main_gui():
    # Use a light theme for better contrast/readability
    try:
        sg.theme('LightGrey1')
    except Exception:
        pass

    main_layout = [
        [sg.Text("🚀 Automatic Fiat Stock Analyzer", font=("Helvetica", 16), justification="center")],
        [sg.Text("This tool will automatically analyze popular stocks and find the best opportunities.", justification="center")],
        [sg.Text("📊 Stocks to analyze: ~100 S&P 500 companies", font=("Helvetica", 10), text_color="blue")],
        [sg.Text("⏱️ Estimated time: 30 seconds – 5 minutes (depends on hardware)", font=("Helvetica", 10), text_color="orange")],
        [sg.Button("🚀 Start Auto Analysis", size=(20, 2), button_color=("white", "#2E8B57")), sg.Button("❌ Exit")],
        [sg.Text("", key="status", size=(60, 2))],
        [sg.Text("", key="loading_text", size=(60, 1), text_color="blue", font=("Helvetica", 10, "bold"))],
        [sg.ProgressBar(100, orientation='h', size=(50, 20), key='main_progress', visible=False)],
        [sg.Text("💡 Tip: Keep this window open during analysis", font=("Helvetica", 9), text_color="black")]
    ]
    
    window = sg.Window("🚀 Automatic Fiat Stock Analyzer", main_layout, size=(550, 350))
    
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "❌ Exit"):
            print("CLI: Exiting program...")
            break

        if event == "🚀 Start Auto Analysis":
            print("CLI: 🚀 Start Auto Analysis button pressed!")
            print("CLI: Event handler started successfully!")
            
            # Immediately show feedback that button was pressed
            window["status"].update("🚀 Starting automatic analysis... Please wait!")
            window.refresh()
            
            # Add immediate visual feedback
            print("CLI: Button pressed! Starting analysis...")
            print("CLI: GUI feedback: Button pressed and analysis starting...")
            
            # Disable the button to prevent multiple clicks
            window["🚀 Start Auto Analysis"].update(disabled=True)
            window["🚀 Start Auto Analysis"].update("⏳ Analysis Running...")
            
            # Show immediate loading indicator
            print("CLI: Loading indicator started...")
            print("CLI: Progress window will open shortly...")
            
            # Show immediate popup to confirm button was pressed
            sg.popup_quick_message("🚀 Analysis Starting!", 
                                  background_color='green', 
                                  text_color='white', 
                                  font=('Helvetica', 16),
                                  auto_close_duration=2)
            
            # Show and animate main progress bar immediately
            window['main_progress'].update(visible=True)
            window['main_progress'].update(10)
            window['loading_text'].update("🔄 Initializing analysis...")
            window.refresh()
            
            # Animate progress bar for immediate feedback
            spinner_chars = ["🔄", "⚡", "📊", "💹", "📈", "🎯"]
            for i in range(10, 25, 5):
                spinner = spinner_chars[(i // 5) % len(spinner_chars)]
                window['main_progress'].update(i)
                window['loading_text'].update(f"{spinner} Initializing analysis... {i}%")
                window.refresh()
                time.sleep(0.1)
            
            # Start analysis in background thread
            result_holder = {}
            
            def worker():
                try:
                    def progress_callback(progress, status):
                        result_holder['progress'] = progress
                        result_holder['status'] = status
                        print(f"CLI Progress: {progress}% - {status}")  # CLI feedback
                    
                    print("CLI: Starting stock analysis...")
                    print("CLI: Fetching stock list...")
                    result_holder['status'] = "Fetching stock list..."
                    result_holder['progress'] = 0
                    
                    results = auto_analyze_stocks(progress_callback)
                    result_holder['results'] = results
                    result_holder['progress'] = 100
                    result_holder['status'] = "Analysis complete!"
                    print(f"CLI: Analysis complete! Found {len(results)} stocks")
                except Exception as e:
                    result_holder['error'] = str(e)
                    print(f"CLI Error: {e}")

            thread = threading.Thread(target=worker, daemon=True)
            thread.start()
            
            # Show progress window with animated elements
            progress_layout = [
                [sg.Text("🔄", font=("Arial", 24), key="spinner")],
                [sg.Text("🚀 Starting Analysis...", key="progress_text", font=("Helvetica", 12))],
                [sg.ProgressBar(100, orientation='h', size=(40, 20), key='progress')],
                [sg.Text("Initializing...", key="status_text", size=(50, 2))],
                [sg.Text("⏱️ This may take several minutes", font=("Helvetica", 10))],
                [sg.Text("📱 Check your terminal/console for CLI updates", font=("Helvetica", 9), text_color="blue")]
            ]
            progress_window = sg.Window("Analysis Progress", progress_layout, modal=True, finalize=True, size=(500, 250))
            
            # Animated progress updates
            spinner_chars = ["🔄", "⚡", "📊", "💹", "📈", "🎯"]
            spinner_idx = 0
            last_progress = 0
            start_time = time.time()
            
            # Add initial progress simulation to show something is happening
            progress_window['progress'].update(5)
            progress_window['status_text'].update("Initializing analysis...")
            progress_window['progress_text'].update("Progress: 5% Complete")
            
            while thread.is_alive():
                event_progress, _ = progress_window.read(timeout=100)
                if event_progress == sg.WINDOW_CLOSED:
                    break
                
                # Update spinner animation
                progress_window['spinner'].update(spinner_chars[spinner_idx])
                spinner_idx = (spinner_idx + 1) % len(spinner_chars)
                
                # Update progress from worker thread
                if 'progress' in result_holder and 'status' in result_holder:
                    current_progress = result_holder['progress']
                    current_status = result_holder['status']
                    
                    if current_progress != last_progress:
                        progress_window['progress'].update(current_progress)
                        progress_window['status_text'].update(current_status)
                        progress_window['progress_text'].update(f"Progress: {current_progress}% Complete")
                        last_progress = current_progress
                
                # Show elapsed time and ensure progress bar moves
                elapsed = int(time.time() - start_time)
                if elapsed > 0:
                    # Simulate some progress if no real progress yet
                    if last_progress == 0 and elapsed > 2:
                        simulated_progress = min(15, elapsed * 2)
                        progress_window['progress'].update(simulated_progress)
                        progress_window['progress_text'].update(f"Progress: {simulated_progress}% Complete")
                        progress_window['status_text'].update(f"Elapsed: {elapsed}s | Initializing...")
                    elif last_progress > 0:
                        progress_window['status_text'].update(f"Elapsed: {elapsed}s | {current_status if 'status' in result_holder else 'Initializing...'}")
            
            # Wait for completion
            thread.join(timeout=1)
            progress_window.close()
            
            # Re-enable the button
            window["🚀 Start Auto Analysis"].update(disabled=False)
            window["🚀 Start Auto Analysis"].update("🚀 Start Auto Analysis")
            
            if 'error' in result_holder:
                window["status"].update(f"❌ Error during analysis: {result_holder['error']}")
            elif 'results' in result_holder:
                results = result_holder['results']
                
                # Show completion animation
                window["status"].update("🎉 Analysis complete! 🎉")
                window.refresh()
                time.sleep(1)
                
                # Show results in a new window
                show_results_window(results)
                
                window["status"].update(f"✅ Analysis complete! Found {len(results)} stocks analyzed. Check results above!")
    
    print("CLI: Program closed successfully.")
    window.close()
    return

def show_results_window(results):
    """Display analysis results in a new window. Always shows something, including errors if no successes."""
    if not results:
        # Extremely unlikely, but show an empty state in-window instead of a popup
        results = []
    
    # Create results layout
    results_layout = [
        [sg.Text("📊 Stock Analysis Results", font=("Helvetica", 16), justification="center")],
        [sg.Text(f"🏆 Top {min(20, len(results))} Stocks by Score:", font=("Helvetica", 12))],
        [sg.HorizontalSeparator()],
    ]
    
    # Add top results (include errors if present)
    any_success = any(r.get('status') == 'success' for r in results)
    for i, result in enumerate(results[:20]):
        if result.get('status') == 'success':
            ticker = result['ticker']
            score = result['score']
            data = result['result']
            
            # Determine recommendation with emojis
            if score == 3:
                rec = "🔥 STRONG BUY 🔥"
                color = "#006600"
                icon = "🚀"
            elif score == 2:
                rec = "✅ BUY ✅"
                color = "#006600"
                icon = "📈"
            elif score == 1:
                rec = "⚠️ CONSIDER ⚠️"
                color = "#ff9900"
                icon = "🤔"
            else:
                rec = "❌ AVOID ❌"
                color = "#800000"
                icon = "📉"
            
            results_layout.append([
                sg.Text(f"{i+1}. {icon} {ticker} - {rec}", text_color=color, font=("Helvetica", 10, "bold")),
                sg.Text(f"Score: {score}/3", text_color="blue")
            ])
            
            # Add details
            if isinstance(data, dict):
                details = []
                if 'avg_volume' in data:
                    details.append(f"Volume: {'✓' if data['avg_volume'] else '✗'}")
                if 'iv30_rv30' in data:
                    details.append(f"IV/RV: {'✓' if data['iv30_rv30'] else '✗'}")
                if 'ts_slope_0_45' in data:
                    details.append(f"Slope: {'✓' if data['ts_slope_0_45'] else '✗'}")
                if 'expected_move' in data and data['expected_move']:
                    details.append(f"Move: {data['expected_move']}")
                
                results_layout.append([
                    sg.Text(f"    {' | '.join(details)}", text_color="gray", font=("Helvetica", 8))
                ])
            
            results_layout.append([sg.HorizontalSeparator()])
        else:
            # Show error entries when present
            ticker = result.get('ticker', 'N/A')
            error_message = result.get('result', 'Unknown error')
            results_layout.append([
                sg.Text(f"{i+1}. ❌ {ticker} - Error", text_color="#800000", font=("Helvetica", 10, "bold")),
                sg.Text("Score: 0/3", text_color="blue")
            ])
            results_layout.append([
                sg.Text(f"    {error_message}", text_color="gray", font=("Helvetica", 8))
            ])
            results_layout.append([sg.HorizontalSeparator()])

    if not any_success:
        # Add a small note if showing only errors
        results_layout.insert(0, [sg.Text("ℹ️ No successful analyses. Showing error details below.", text_color="orange")])
    
    results_layout.append([sg.Button("Close")])
    
    # Create and show results window
    results_window = sg.Window("Analysis Results", results_layout, size=(600, 500), modal=True, finalize=True)
    
    while True:
        event_result, _ = results_window.read()
        if event_result in (sg.WINDOW_CLOSED, "Close"):
            break
    
    results_window.close()

def gui():
    main_gui()

if __name__ == "__main__":
    gui()