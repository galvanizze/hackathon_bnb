# Binance DEXPLORE

Open-source free metrics, portfolio and trading statistics from Binance DEX.

Project has two main parts:

1. Binance DEX metrics & KPIs

- Trades + volume overview 
- Asset overview - price tickers, market cap, volume
- Biggest traders and trades - track the whale moves
- Advanced filters - by trading pair, date range...

2. Binance DEX explorer on steroids

- Input multiple addresses - combine them in single dashboard
- My portfolio - track binance assets balance in BNB, USD, EUR, BTC, ETH 
- My Trades - trading history, filter by date, pair, size (5 biggest trades, last 5 trades)
- My fees - how much have I paid in trading fees? by time, pair, average fees/spread 

Who will use DEXPLORE ?

- Binance DEX power users - institutional traders and investors
- (Potentially all users - it's free)
- Data analysts and researchers
- Builders (via open source blockAPI library)

This project came to life on Hack To The Moon hackathon in Prague, organized by Binance_X and Rockaway Blockchain.
Built by Devmons - team behind Crypkit.com.

Technologies used:

- DB: PostgreSQL
- backend: python, flask
- frontend: vue.js

Data sources:

- Binance Chain lightnode: https://docs.binance.org/light-client.html
- HTTP API: https://docs.binance.org/api-reference/dex-api/paths.html
- Price feeds BNB vs EUR, USD, BTC, ETH: www.coingecko.com

Contact us:

e-mail: info@crypkit.com
www.crypkit.com

- github hackathon: https://github.com/galvanizze/hackathon_bnb 
- github blockAPI: https://github.com/crypkit/blockapi 
- website (soon): www.binancedexplore.com  

