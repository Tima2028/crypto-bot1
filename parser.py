import requests
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_price_chart(crypto_id='bitcoin'):
    """
    Fetches 24h price data for a crypto and generates a line chart.
    """
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart?vs_currency=usd&days=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'prices' not in data:
            return None

        # Create a pandas DataFrame
        df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # Determine line color based on price trend
        start_price = df['price'].iloc[0]
        end_price = df['price'].iloc[-1]
        line_color = '#26a69a' if end_price >= start_price else '#ef5350' # Green for up, Red for down

        # Plotting
        plt.style.use('dark_background') # Use a dark theme for the chart
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(df['timestamp'], df['price'], color=line_color)

        # Formatting the plot
        ax.set_title(f'{crypto_id.title()} Price (Last 24h)', fontsize=16, color='white')
        ax.set_ylabel('Price (USD)', color='white')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        
        # Format the x-axis to show time
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=45)

        fig.tight_layout()

        # Save plot to a BytesIO object
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True)
        plt.close(fig)
        buf.seek(0)
        return buf

    except requests.exceptions.RequestException as e:
        print(f"Error fetching chart data for {crypto_id}: {e}")
        return None
    except Exception as e:
        print(f"Error generating chart for {crypto_id}: {e}")
        return None

def get_crypto_price(crypto_name='bitcoin'):
    """
    Gets the price of a cryptocurrency from CoinGecko.
    """
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_name}&vs_currencies=usd"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        if crypto_name in data and 'usd' in data[crypto_name]:
            return f"${data[crypto_name]['usd']}"
        else:
            return "Price data not available at this time"

    except requests.exceptions.RequestException as e:
        return "Service temporarily unavailable - please try again later"

def get_top_5_crypto_prices():
    """
    Gets the prices of the top 5 cryptocurrencies from CoinGecko.
    """
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=5&page=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        prices = []
        for crypto in data:
            prices.append(f"{crypto['name']} ({crypto['symbol'].upper()}): ${crypto['current_price']}")
        return "\n".join(prices)

    except requests.exceptions.RequestException as e:
        return "Couldn't retrieve top cryptocurrencies - please try again later"

def get_top_5_crypto_list():
    """
    Gets the list of the top 5 cryptocurrencies from CoinGecko.
    """
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=5&page=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return [crypto['id'] for crypto in data]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching top 5 crypto list: {e}")
        return []

if __name__ == '__main__':
    # Example of how to use the functions
    price = get_crypto_price('bitcoin')
    print(f"The price of Bitcoin is: {price}")

    top_5_prices = get_top_5_crypto_prices()
    print("\nTop 5 cryptocurrencies:")
    print(top_5_prices)

    top_5_list = get_top_5_crypto_list()
    print("\nTop 5 crypto list:")
    print(top_5_list)