"""
AI Investment Research Terminal - CLI version
Run with: python app.py
"""

from tabulate import tabulate

from services.company_search import CompanySearch
from services.market_data import get_history, get_quote, get_fundamentals, \
    get_benchmark_history, MarketDataError
from services.news_data import get_company_news
from models.sentiment_model import analyze_headlines, aggregate_sentiment
from analysis.technical import compute_all_indicators, compute_returns
from analysis.risk import risk_summary
from analysis.portfolio import portfolio_summary, correlation_matrix
from utils.storage import add_to_watchlist, get_watchlist, add_holding, get_portfolio, \
    clear_portfolio

search_engine = CompanySearch()


def line(char="-", width=60):
    print(char * width)


def header(title: str):
    print()
    line("=")
    print(title.center(60))
    line("=")


def safe_float_input(prompt: str, default=None):
    raw = input(prompt).strip()
    if raw == "" and default is not None:
        return default
    try:
        return float(raw)
    except ValueError:
        print("Invalid number, try again.")
        return safe_float_input(prompt, default)


def show_company_detail(ticker: str, name: str):
    header(f"{name}  ({ticker})")

    try:
        quote = get_quote(ticker)
    except MarketDataError as e:
        print(f"[ERROR] {e}")
        return

    freshness = "LIVE/NEAR-LIVE" if quote["data_freshness"] == "live_or_near_live" \
        else "DELAYED / LAST CLOSE"
    print(f"As of: {quote['as_of']}  |  Data: {freshness}  |  Source: Yahoo Finance")
    print(f"Price: Rs.{quote['price']}   Volume: {quote['volume']}")
    print(f"52W High: {quote['week52_high']}   52W Low: {quote['week52_low']}")

    try:
        hist = get_history(ticker)
    except MarketDataError as e:
        print(f"[ERROR] {e}")
        return
    hist = compute_all_indicators(hist)
    latest = hist.iloc[-1]

    print("\n--- Technical Indicators (latest) ---")
    tech_rows = [
        ["SMA 20", round(latest["SMA_20"], 2) if latest["SMA_20"] == latest["SMA_20"] else "N/A"],
        ["SMA 50", round(latest["SMA_50"], 2) if latest["SMA_50"] == latest["SMA_50"] else "N/A"],
        ["RSI (14)", round(latest["RSI_14"], 2) if latest["RSI_14"] == latest["RSI_14"] else "N/A"],
        ["MACD", round(latest["MACD"], 2) if latest["MACD"] == latest["MACD"] else "N/A"],
    ]
    print(tabulate(tech_rows, headers=["Indicator", "Value"], tablefmt="simple"))

    print("\n--- Returns ---")
    returns = compute_returns(hist)
    return_rows = [[k.replace("_pct", "").replace("_", " ").title(),
                     f"{v}%" if v is not None else "N/A"] for k, v in returns.items()]
    print(tabulate(return_rows, tablefmt="simple"))

    print("\n--- Fundamentals ---")
    fundamentals = get_fundamentals(ticker)
    fund_rows = [[k.replace("_", " ").title(), v if v is not None else "Not available"]
                 for k, v in fundamentals.items()]
    print(tabulate(fund_rows, tablefmt="simple"))

    print("\n--- Risk Analysis ---")
    try:
        benchmark_hist = get_benchmark_history()
        risk = risk_summary(hist, benchmark_hist)
    except MarketDataError:
        risk = risk_summary(hist)
    for k, v in risk.items():
        print(f"{k.replace('_', ' ').title()}: {v}")

    print("\n--- Recent News & Sentiment ---")
    headlines = get_company_news(name)
    if not headlines:
        print("No recent headlines found.")
    else:
        analyzed = analyze_headlines(headlines)
        agg = aggregate_sentiment(analyzed)
        for h, a in zip(headlines, analyzed):
            tag = {"positive": "[+]", "neutral": "[ ]", "negative": "[-]"}[a["label"]]
            print(f"{tag} {h['title']}  ({a['label']}, {a['compound']:+.2f})")

        print(f"\nAggregate: {agg['positive_pct']}% positive | "
              f"{agg['neutral_pct']}% neutral | {agg['negative_pct']}% negative "
              f"(over {agg['n_headlines']} headlines) -> overall: {agg['overall_label'].upper()}")
        print("Note: sentiment is model output (lexicon-based), not a price prediction.")

    print()
    if input("Add this stock to your watchlist? (y/n): ").strip().lower() == "y":
        add_to_watchlist(ticker)
        print(f"Added {ticker} to watchlist.")


def menu_search():
    header("SEARCH & ANALYZE")
    print("Search by ticker, company name, group (e.g. 'tata'), or sector (e.g. 'banking').")
    query = input("Search: ").strip()
    if not query:
        return

    results = search_engine.search(query)
    if results.empty:
        print("No matches found in the company mapping.")
        return

    print(f"\n{len(results)} match(es):\n")
    display_rows = [[i + 1, r["name"], r["ticker"], r["group"], r["sector"]]
                     for i, r in results.iterrows()]
    print(tabulate(display_rows, headers=["#", "Name", "Ticker", "Group", "Sector"],
                    tablefmt="simple"))

    choice = input("\nEnter number to view details (or press Enter to go back): ").strip()
    if not choice:
        return
    try:
        idx = int(choice) - 1
        row = results.iloc[idx]
        show_company_detail(row["ticker"], row["name"])
    except (ValueError, IndexError):
        print("Invalid selection.")


def menu_compare():
    header("COMPARE STOCKS")
    print("Enter 2-5 tickers or company names, separated by commas.")
    print("Example: tcs, infosys, hcltech")
    raw = input("Compare: ").strip()
    if not raw:
        return

    queries = [q.strip() for q in raw.split(",") if q.strip()]
    tickers, names = [], []
    for q in queries:
        matches = search_engine.search(q)
        if matches.empty:
            print(f"[WARN] No match for '{q}', skipping.")
            continue
        row = matches.iloc[0]
        tickers.append(row["ticker"])
        names.append(row["name"])

    if len(tickers) < 2:
        print("Need at least 2 valid companies to compare.")
        return

    rows = []
    for ticker, name in zip(tickers, names):
        try:
            quote = get_quote(ticker)
            hist = get_history(ticker)
            returns = compute_returns(hist)
            fundamentals = get_fundamentals(ticker)
            rows.append([
                name, ticker, quote["price"],
                returns.get("monthly_return_pct"), returns.get("one_year_return_pct"),
                fundamentals.get("pe_ratio"), fundamentals.get("roe"),
            ])
        except MarketDataError as e:
            rows.append([name, ticker, "ERROR", str(e), "", "", ""])

    print()
    print(tabulate(rows, headers=["Name", "Ticker", "Price", "1M Return %",
                                   "1Y Return %", "P/E", "ROE"], tablefmt="simple"))

    print("\n--- Return Correlation Matrix (6-month daily returns) ---")
    corr = correlation_matrix(tickers)
    if not corr.empty:
        print(tabulate(corr, headers="keys", tablefmt="simple"))
    else:
        print("Not enough data to compute correlation.")


def menu_portfolio():
    while True:
        header("PORTFOLIO")
        print("1. View portfolio")
        print("2. Add a holding")
        print("3. Clear portfolio")
        print("4. Back to main menu")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            holdings = get_portfolio()
            if not holdings:
                print("No holdings yet.")
                continue
            summary = portfolio_summary(holdings)
            rows = [[h["ticker"], h["quantity"], h["purchase_price"], h["invested"],
                     h["current_price"], h["current_value"], h["gain_pct"]]
                    for h in summary["holdings"]]
            print(tabulate(rows, headers=["Ticker", "Qty", "Buy Price", "Invested",
                                           "Current Price", "Current Value", "Gain %"],
                            tablefmt="simple"))
            print(f"\nTotal Invested: Rs.{summary['total_invested']:,.2f}")
            print(f"Total Current Value: Rs.{summary['total_current_value']:,.2f}")
            if summary["total_gain_pct"] is not None:
                print(f"Overall Return: {summary['total_gain_pct']}%")

        elif choice == "2":
            ticker = input("Ticker (e.g. TCS.NS): ").strip().upper()
            qty = safe_float_input("Quantity: ")
            price = safe_float_input("Purchase Price (Rs.): ")
            if ticker and qty > 0:
                add_holding(ticker, qty, price)
                print(f"Added {qty} shares of {ticker}.")

        elif choice == "3":
            confirm = input("Are you sure you want to clear the portfolio? (y/n): ").strip().lower()
            if confirm == "y":
                clear_portfolio()
                print("Portfolio cleared.")

        elif choice == "4":
            break
        else:
            print("Invalid option.")


def menu_watchlist():
    header("WATCHLIST")
    watchlist = get_watchlist()
    if not watchlist:
        print("Nothing here yet - add stocks from the Search & Analyze menu.")
        return
    for t in watchlist:
        print(f"- {t}")


def main():
    print("=" * 60)
    print("AI INVESTMENT RESEARCH TERMINAL".center(60))
    print("Indian-market research tool - Not investment advice".center(60))
    print("=" * 60)

    while True:
        print("\nMAIN MENU")
        print("1. Search & Analyze")
        print("2. Compare Stocks")
        print("3. Portfolio")
        print("4. Watchlist")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            menu_search()
        elif choice == "2":
            menu_compare()
        elif choice == "3":
            menu_portfolio()
        elif choice == "4":
            menu_watchlist()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()
