# 5.2 Statement

## Problem Statement

Today, there is a huge amount of stock-market information available online, but finding and understanding all of it in one place can be difficult. A person who wants to study a company may have to visit different websites to check its current price, past performance, technical indicators, financial details, risk information, and recent news.

This project was created to make that process simpler. The **AI Investment Research Terminal** brings different types of stock information together in one command-line application. A user can search for an Indian/NSE-listed company and get information about its price history, performance, technical indicators, financial details, risk, and recent financial news from the same place.

The project also includes features such as basic news sentiment analysis, stock comparison, portfolio tracking, and a personal watchlist. Along with being useful for basic stock research, the project gives practical experience in areas such as Python programming, data handling, financial calculations, APIs, and sentiment analysis.

The main purpose of the project is to make stock research more convenient and easier to understand. It is designed for **learning and research purposes** and should not be considered a source of guaranteed predictions or professional financial advice.

---

## Scope of the Project

This project focuses on building a Python-based tool that can be used to explore and analyze information about stocks in the Indian market.

The main things covered by the project are:

* Searching for companies by their name, stock ticker, sector, or business group.
* Fetching historical stock-price data from online market-data sources.
* Showing recent market information about a selected stock.
* Calculating commonly used technical indicators such as:

  * 20-day, 50-day, and 200-day Simple Moving Average (SMA)
  * 20-day Exponential Moving Average (EMA)
  * Relative Strength Index (RSI)
  * Moving Average Convergence Divergence (MACD)
  * Bollinger Bands
* Checking returns for different periods, including daily, weekly, monthly, six-month, and one-year returns.
* Studying historical risk using measures such as volatility, maximum drawdown, Sharpe ratio, downside volatility, beta, and correlation with the NIFTY 50.
* Collecting recent financial news related to a company.
* Performing basic sentiment analysis on financial news using a VADER-based model with finance-related terms.
* Comparing multiple stocks using important performance and fundamental metrics.
* Checking how closely different stocks have moved together by calculating their historical return correlations.
* Creating and maintaining a personal watchlist.
* Adding portfolio holdings and keeping track of their value and returns.
* Saving some data locally and using caching so that the same market data does not have to be downloaded repeatedly.

The project is mainly focused on **research and analysis**. It does not place stock orders, connect to a user's brokerage account, or automatically trade in the market.

---

## Target Users

The project can be useful for different types of users, especially people who want to learn about or explore the stock market.

### Students and Learners

Students can use the project to understand how programming can be applied to a real-world problem. It also shows how concepts such as data analysis, APIs, technical indicators, databases, and sentiment analysis can work together in one application.

### Beginner Investors

People who are new to the stock market can use the application to explore basic information about companies without having to manually collect information from several different websites.

### Retail Investors

Individual investors can use the terminal to quickly look at stock performance, technical indicators, financial information, risk metrics, and recent company-related news.

### Developers and Finance-Data Learners

The project can also be useful for anyone interested in working with financial APIs, processing market data using Python, or building applications related to finance and investment research.

---

## High-Level Features

### 1. Company Search

Users can search for a company using its name, ticker symbol, sector, or business group. This makes it easier to find the stock they want to study.

### 2. Stock Market Data

Once a company is selected, the application can show available market information such as:

* Current or recent stock price
* Opening, high, and low prices
* Trading volume
* Previous closing price
* 52-week high and low
* Market capitalization, when available
* Historical price data

### 3. Technical Analysis

The application calculates several commonly used technical indicators, including:

* SMA 20
* SMA 50
* SMA 200
* EMA 20
* RSI
* MACD
* Bollinger Bands

Based on these indicators, the application also provides simple bullish, bearish, or neutral signals using the rules implemented in the project.

### 4. Historical Performance

Users can check how a stock has performed over different periods, such as:

* Daily
* Weekly
* Monthly
* Six months
* One year

This gives a quick view of the stock's past performance across different time periods.

### 5. Risk Analysis

The project includes several historical risk measures, including:

* Annualized volatility
* Maximum drawdown
* Sharpe ratio
* Downside volatility
* Beta compared with the NIFTY 50
* Correlation with the NIFTY 50

These values are calculated using historical data and are meant to help users understand past risk. They are not predictions of future performance.

### 6. Financial News and Sentiment Analysis

The application collects recent financial news related to a selected company. It then analyzes the headlines using a VADER-based sentiment-analysis approach that has been adapted with finance-related terms.

The news is grouped into:

* Positive
* Neutral
* Negative

The application also provides an overall summary based on the available headlines.

### 7. Stock Comparison

Users can compare more than one stock using metrics such as:

* Current price
* One-month return
* One-year return
* P/E ratio
* ROE

The application can also show a correlation matrix to give users an idea of how the historical returns of different stocks are related.

### 8. Portfolio Tracking

Users can manually add their holdings by entering the stock ticker, quantity, and purchase price.

The application can then keep track of:

* Total amount invested
* Current portfolio value
* Returns on individual holdings
* Overall portfolio return

### 9. Watchlist

Users can add stocks to a personal watchlist and keep them saved for later. This makes it easier to come back to companies they are interested in researching.

### 10. Local Storage and Caching

The project stores information such as the portfolio and watchlist locally. It also uses cached market data where possible, which helps reduce repeated requests for the same information and makes the application more efficient.

### 11. Command-Line Interface

The whole application works through a simple menu-based terminal interface. The main sections include:

* Search & Analyze
* Compare Stocks
* Portfolio
* Watchlist
* Exit

The command-line approach keeps the application simple while still providing all of its main stock-analysis features.
