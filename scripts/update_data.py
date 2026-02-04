#!/usr/bin/env python3
"""
Crypto Treasury Companies Data Updater
- Stocks: yfinance
- Crypto: CoinCap API (free, no API key required)
"""

import json
import os
from datetime import datetime, timedelta
import yfinance as yf
import requests
import time

# Treasury Companies by Crypto
TREASURY_COMPANIES = {
    "BTC": {
        "coin_id": "bitcoin",
        "coin_symbol": "BTC",
        "color": "#f7931a",
        "companies": [
            {"ticker": "MSTR", "name": "Strategy"},
            {"ticker": "XXI", "name": "Twenty One"},
            {"ticker": "CEPO", "name": "Bitcoin Standard"},
            {"ticker": "ASST", "name": "Strive"},
            {"ticker": "NAKA", "name": "KindlyMD (Nakamoto)"},
            {"ticker": "BRR", "name": "PropCap BTC"},
            {"ticker": "SQNS", "name": "Sequans Comm"},
        ]
    },
    "ETH": {
        "coin_id": "ethereum",
        "coin_symbol": "ETH",
        "color": "#627eea",
        "companies": [
            {"ticker": "BMNR", "name": "BitMine"},
            {"ticker": "SBET", "name": "Sharplink Gaming"},
            {"ticker": "ETHM", "name": "Ether Machine"},
            {"ticker": "BTBT", "name": "Bit Digital"},
            {"ticker": "BTCS", "name": "BTCS Inc."},
            {"ticker": "ETHZ", "name": "ETHZilla"},
            {"ticker": "FGNX", "name": "FG Nexus"},
            {"ticker": "GAME", "name": "GameSquare Holdings"},
        ]
    },
    "SOL": {
        "coin_id": "solana",
        "coin_symbol": "SOL",
        "color": "#00ffa3",
        "companies": [
            {"ticker": "FWDI", "name": "Forward Industries"},
            {"ticker": "HSDT", "name": "Solana Company"},
            {"ticker": "DFDV", "name": "DeFi Development"},
            {"ticker": "UPXI", "name": "Upexi"},
            {"ticker": "STSS", "name": "Sharps Technology"},
            {"ticker": "STKE", "name": "Sol Strategies"},
            {"ticker": "SLMT", "name": "Solmate"},
            {"ticker": "SLAI", "name": "SOLAI Limited"},
        ]
    },
    "HYPE": {
        "coin_id": "hyperliquid",
        "coin_symbol": "HYPE",
        "color": "#00d4aa",
        "companies": [
            {"ticker": "PURR", "name": "Sonnet BioTher"},
            {"ticker": "HYPD", "name": "Hyperion DeFi"},
        ]
    },
    "SUI": {
        "coin_id": "sui",
        "coin_symbol": "SUI",
        "color": "#4da2ff",
        "companies": [
            {"ticker": "SUIG", "name": "SUI Group Holdings"},
        ]
    },
    "INJ": {
        "coin_id": "injective-protocol",
        "coin_symbol": "INJ",
        "color": "#00f2fe",
        "companies": [
            {"ticker": "PAPL", "name": "Pineapple Financial"},
        ]
    },
    "BNB": {
        "coin_id": "binancecoin",
        "coin_symbol": "BNB",
        "color": "#f3ba2f",
        "companies": [
            {"ticker": "BNC", "name": "CEA Industries"},
        ]
    },
    "BONK": {
        "coin_id": "bonk",
        "coin_symbol": "BONK",
        "color": "#ff6b35",
        "companies": [
            {"ticker": "BNKK", "name": "Bonk Inc."},
        ]
    },
    "IP": {
        "coin_id": "story-protocol",
        "coin_symbol": "IP",
        "color": "#9945ff",
        "companies": [
            {"ticker": "IPST", "name": "Heritage Distilling"},
        ]
    }
}

# Stock colors
STOCK_COLORS = [
    "#ef4444", "#f97316", "#eab308", "#84cc16", "#22c55e",
    "#14b8a6", "#06b6d4", "#3b82f6", "#8b5cf6", "#ec4899"
]


def get_stock_data(ticker: str, days: int = 400) -> list:
    """Fetch stock price data using yfinance"""
    try:
        stock = yf.Ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty:
            print(f"  Warning: No data for {ticker}")
            return []
        
        prices = []
        for date, row in df.iterrows():
            prices.append({
                "date": date.strftime("%Y-%m-%d"),
                "price": round(row["Close"], 2)
            })
        
        return prices
    except Exception as e:
        print(f"  Error fetching {ticker}: {e}")
        return []


def get_crypto_data(coin_id: str, symbol: str, days: int = 400) -> list:
    """Fetch crypto price data using CoinCap API (free, no API key)"""
    
    print(f"  Fetching {coin_id} prices from CoinCap...")
    
    # CoinCap uses different IDs for some coins
    COINCAP_IDS = {
        "bitcoin": "bitcoin",
        "ethereum": "ethereum",
        "solana": "solana",
        "binancecoin": "binance-coin",
        "injective-protocol": "injective-protocol",
        "sui": "sui",
        "bonk": "bonk",
        "hyperliquid": "hyperliquid",
        "story-protocol": "story",
    }
    
    coincap_id = COINCAP_IDS.get(coin_id, coin_id)
    
    try:
        # Calculate start and end timestamps
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        url = f"https://api.coincap.io/v2/assets/{coincap_id}/history"
        params = {
            "interval": "d1",
            "start": start_time,
            "end": end_time
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code != 200:
            print(f"    Error: {response.status_code} - {response.text[:100]}")
            return []
        
        data = response.json()
        
        prices = []
        for item in data.get("data", []):
            price = float(item["priceUsd"])
            date = item["date"][:10]  # "2024-01-01T00:00:00.000Z" -> "2024-01-01"
            
            # Handle very small prices (like BONK)
            if price < 0.01:
                prices.append({"date": date, "price": round(price, 8)})
            elif price < 1:
                prices.append({"date": date, "price": round(price, 6)})
            else:
                prices.append({"date": date, "price": round(price, 2)})
        
        # Remove duplicates (keep last entry for each date)
        seen = {}
        for p in prices:
            seen[p["date"]] = p
        prices = list(seen.values())
        prices.sort(key=lambda x: x["date"])
        
        return prices
        
    except Exception as e:
        print(f"    Error fetching {coin_id}: {e}")
        return []


def calculate_performance(prices: list) -> dict:
    """Calculate performance for different periods"""
    if not prices or len(prices) < 2:
        return {"1W": None, "3M": None, "6M": None, "YTD": None, "1Y": None}
    
    current_price = prices[-1]["price"]
    current_date = datetime.strptime(prices[-1]["date"], "%Y-%m-%d")
    
    periods = {
        "1W": 7,
        "3M": 90,
        "6M": 180,
        "1Y": 365
    }
    
    performance = {}
    
    for period_name, days in periods.items():
        target_date = current_date - timedelta(days=days)
        
        # Find closest price to target date
        closest_price = None
        min_diff = float('inf')
        
        for p in prices:
            p_date = datetime.strptime(p["date"], "%Y-%m-%d")
            diff = abs((p_date - target_date).days)
            if diff < min_diff and p_date <= current_date:
                min_diff = diff
                closest_price = p["price"]
        
        if closest_price and closest_price > 0:
            perf = ((current_price - closest_price) / closest_price) * 100
            performance[period_name] = round(perf, 2)
        else:
            performance[period_name] = None
    
    # Calculate YTD (Year-to-Date)
    ytd_start = datetime(current_date.year, 1, 1)
    ytd_price = None
    min_diff = float('inf')
    
    for p in prices:
        p_date = datetime.strptime(p["date"], "%Y-%m-%d")
        diff = abs((p_date - ytd_start).days)
        if diff < min_diff and p_date >= ytd_start:
            min_diff = diff
            ytd_price = p["price"]
    
    if ytd_price and ytd_price > 0:
        ytd_perf = ((current_price - ytd_price) / ytd_price) * 100
        performance["YTD"] = round(ytd_perf, 2)
    else:
        performance["YTD"] = None
    
    return performance


def main():
    print("=" * 60)
    print("Crypto Treasury Companies Data Updater")
    print("Using: yfinance (stocks) + CoinCap (crypto)")
    print("=" * 60)
    
    output_data = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "categories": {}
    }
    
    for category, config in TREASURY_COMPANIES.items():
        print(f"\n[{category}] Processing...")
        
        category_data = {
            "coin_id": config["coin_id"],
            "coin_symbol": config["coin_symbol"],
            "coin_color": config["color"],
            "coin_prices": [],
            "coin_performance": {},
            "companies": []
        }
        
        # Fetch crypto data
        coin_prices = get_crypto_data(config["coin_id"], config["coin_symbol"])
        category_data["coin_prices"] = coin_prices
        category_data["coin_performance"] = calculate_performance(coin_prices)
        print(f"    -> {len(coin_prices)} data points")
        
        time.sleep(1)  # Rate limiting for CoinGecko
        
        # Fetch stock data for each company
        for i, company in enumerate(config["companies"]):
            ticker = company["ticker"]
            name = company["name"]
            
            print(f"  Fetching {ticker} ({name})...")
            stock_prices = get_stock_data(ticker)
            
            company_data = {
                "ticker": ticker,
                "name": name,
                "color": STOCK_COLORS[i % len(STOCK_COLORS)],
                "prices": stock_prices,
                "performance": calculate_performance(stock_prices)
            }
            
            category_data["companies"].append(company_data)
            print(f"    -> {len(stock_prices)} data points")
            
            time.sleep(0.5)  # Rate limiting
        
        output_data["categories"][category] = category_data
    
    # Save to JSON
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "treasury_data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False)
    
    print(f"\n{'=' * 60}")
    print(f"Data saved to {output_path}")
    print(f"Updated at: {output_data['updated_at']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
