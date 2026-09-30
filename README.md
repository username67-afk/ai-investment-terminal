# 📈 AI Investment Research Terminal

An AI-powered stock research terminal built for the Indian stock market.

The idea behind this project is pretty simple: instead of having to open multiple websites to check a company's price, performance, technical indicators, risk, and recent news, I wanted to bring the most useful information together in one place.

You enter a company name or stock ticker, and the terminal collects the latest available market data, calculates important indicators, looks at recent news, and gives you a quick overview of what is happening with that stock.

The project is designed mainly as a **stock research and learning tool**, rather than something that tells you what you should buy or sell.

> **Important:** This project is not investment advice. The sentiment score is based on analysing news headlines and is not intended to predict future stock prices.

---

## What can it do?

### 🔎 Search for companies

You don't necessarily have to remember the exact stock ticker.

You can search using:

* Stock ticker
* Company name
* Business group, such as `tata`
* Sector, such as `banking`

The project currently has around **115 NSE-listed companies** included in its company mapping.

### 💰 Get live market information

Once you select a company, the application fetches its latest available market information through Yahoo Finance.

Some of the information includes:

* Current price
* Trading volume
* 52-week high and low
* P/E ratio
* EPS
* ROE
* Profit margins
* Other available fundamentals

The data is fetched dynamically rather than being manually stored in the program.

### 📊 Technical analysis

The terminal also calculates some commonly used technical indicators:

* SMA
* RSI
* MACD
* Bollinger Bands

It also calculates the stock's historical returns over:

* 1 month
* 3 months
* 6 months
* 1 year

This gives a quick way to look at both recent and longer-term performance.

### ⚠️ Risk analysis

Looking only at returns doesn't tell the whole story, so the project also includes several risk-related measurements.

These include:

* Volatility
* Maximum drawdown
* Sharpe ratio
* Downside volatility
* Beta
* Correlation with the Nifty 50

The goal here is to give a more complete picture of how a stock has behaved rather than focusing only on whether its price went up or down.

### 📰 News and sentiment

The application pulls recent Indian market-related headlines from Google News.

Those headlines are then analysed using **VADER sentiment analysis**.

Since normal sentiment analysis isn't really designed around financial language, the project also uses a finance-specific vocabulary containing words and phrases such as:

* `downgrade`
* `buyback`
* `profit surge`

The result is a simple sentiment score showing how positive or negative the recent news coverage appears to be.

It is important to treat this as an indication of **headline sentiment**, not as a prediction of where the stock price will go.

### 🔄 Compare different stocks

You can compare between **2 and 5 companies** at the same time.

The comparison includes their relevant performance information along with a return correlation matrix, which helps show how similarly the selected stocks have behaved historically.

### 💼 Portfolio and watchlist

The terminal also has basic portfolio functionality.

You can keep track of:

* Your holdings
* Amount invested
* Current value
* Overall gain

There is also a watchlist for keeping an eye on companies you're interested in.

This information is stored locally in:

`data/user_data.json`

### 📈 Terminal-based charts

The project uses simple ASCII charts instead of relying on a graphical charting library.

This means the charts can be displayed directly inside the terminal and the project doesn't need an additional charting dependency just to show basic visual information.

---

## Getting started

### 1. Create a virtual environment

This step is optional, but using a virtual environment keeps the project's dependencies separate from your other Python projects.

```bash
python -m venv venv
```

On macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 2. Install the required packages

```bash
pip install -r requirements.txt
```

### 3. Start the application

```bash
python app.py
```

After starting the program, you'll see a simple menu:

**Search & Analyze → Compare Stocks → Portfolio → Watchlist → Exit**

From there, you can choose what you want to work with.

---

## How the project is organised

I’ve kept the project divided into different parts so that market data, analysis, sentiment, and the terminal interface don't all get mixed together.

```text
app.py            Main CLI menu and application loop

config/           Project settings such as the benchmark,
                  cache duration and risk-free rate

services/         Market data, news and company search

models/           Sentiment analysis model
                  (VADER + finance-specific vocabulary)

analysis/         Technical indicators, risk calculations,
                  signals and portfolio calculations

ui/               Terminal-based ASCII charts

utils/            Caching and local data storage

data/             Company list, cached data and
                  saved portfolio information
```

This structure also makes it easier to add new features later without having to rewrite the whole application.

---

## A few things to know

There are a couple of implementation details worth knowing before running the project.

* API/data responses are cached for **15 minutes** to reduce unnecessary requests and keep the application responsive.
* NSE stocks use the `.NS` ticker suffix. For example, TCS is represented as `TCS.NS`.
* The project currently uses:

  * `yfinance`
  * `pandas`
  * `numpy`
  * `feedparser`
  * `vaderSentiment`
  * `tabulate`

---

## What I'd like to improve next

There are still a few things I'd like to build on top of the current version.

### 1. Connect the signal engine

The project already has a signal engine in:

`analysis/signals.py`

I'd like to connect it properly to the main menu so that the analysis can make use of the signals that are already implemented.

### 2. Connect the terminal charts

The ASCII chart functionality is already present in:

`ui/terminal_charts.py`

The next step is to integrate it directly into the main analysis flow.

### 3. Add more companies

The current company mapping can be expanded by adding more stocks to:

`data/company_mapping.csv`

### 4. Improve financial sentiment analysis

The current sentiment system uses VADER with a finance-specific lexicon.

A future version could replace this with a finance-focused language model such as **FinBERT**, which would make the news analysis more suitable for financial text.

---

## Why I built this

This project started from a simple idea: **make stock research easier to do from the terminal.**

Instead of treating market data, technical analysis, risk calculations and news as completely separate things, I wanted to experiment with bringing them together into one small application.

It also gave me a practical way to work with things that are usually taught separately — Python programming, APIs, data processing, financial calculations, sentiment analysis and building a usable command-line interface.

There is still plenty that can be improved, but the current version provides a working foundation that I can continue building on.

---

*Built as a hands-on project to explore financial data, Python, and AI-assisted stock research — with a preference for keeping things simple and useful.*
