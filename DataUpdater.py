from datetime import datetime, timedelta
import requests
import pandas as pd
import zipfile
import os

def update_data(etfs: list[str], data_folder: str):
    etfs = [etf.lower() for etf in etfs]

    API_KEY = "zTonLCzba18GX3mVgxwk4QRekny6DQxw"
    BASE_URL = "https://financialmodelingprep.com/api/v3"
    START_DATE = (datetime.now() - timedelta(days=25 * 365)).strftime("%Y-%m-%d")
    END_DATE = datetime.now().strftime("%Y-%m-%d")
    print(START_DATE, END_DATE)

    def fetch_historical_data(symbol):
        url = f"{BASE_URL}/historical-price-full/{symbol}?from={START_DATE}&to={END_DATE}&apikey={API_KEY}"
        response = requests.get(url)
        data = []
        try:
            data = response.json()["historical"]
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
        return pd.DataFrame(data)

    last_updated_path = os.path.join(data_folder, "last_updated.csv")
    if not os.path.exists(last_updated_path):
        # Create last_updated.csv if it doesn't exist
        last_updated_df = pd.DataFrame(columns=["symbol", "updated"])
    else:
        # Read the last_updated.csv file
        last_updated_df = pd.read_csv(last_updated_path)

    def is_updated_recently(symbol):
        current_time = datetime.now()
        day_4pm = datetime(current_time.year, current_time.month, current_time.day, 16, 0)
        if current_time < day_4pm:
            check_time = day_4pm - timedelta(days=1)
        else:
            check_time = day_4pm

        # Check if the symbol has been updated recently
        if symbol in last_updated_df["symbol"].values:
            last_updated_time = pd.to_datetime(last_updated_df[last_updated_df["symbol"] == symbol]["updated"].values[0])
            return last_updated_time >= check_time
        return False

    for symbol in etfs:
        if is_updated_recently(symbol):
            print(f"Skipping {symbol} as it was updated recently.")
            continue
        
        try:
            df: pd.DataFrame = fetch_historical_data(symbol)
            if df.empty:
                print(f"No data found for {symbol}")
                continue

            # Select date, open, high, low, close, volume
            df = df[["date", "open", "high", "low", "close", "volume"]]
            # Convert date form YYYY-MM-DD to YYYYMMDD HH:MM where HH:MM is 16:00
            df["date"] = (pd.to_datetime(df["date"]) + pd.DateOffset(days=1)).dt.strftime("%Y%m%d 00:00")
            # Convert to decicents
            df["open"] = (df["open"] * 10000).astype(int)
            df["high"] = (df["high"] * 10000).astype(int)
            df["low"] = (df["low"] * 10000).astype(int)
            df["close"] = (df["close"] * 10000).astype(int)
            
            # reverse the order of the dataframe
            df = df.iloc[::-1]
            
            # Write to a file with no header in the order date, open, high, low, close, volume
            csv_file_path = f"{symbol}.csv"
            df.to_csv(csv_file_path, index=False, header=False)
            
            # Zip the file into a zip called symbol.zip and write to the path "data/equity/usa/daily"
            # Create a directory if it doesn't exist
            directory = f"{data_folder}/equity/usa/daily"
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Zip the file
            zip_file_path = os.path.join(directory, f"{symbol}.zip")
            with zipfile.ZipFile(zip_file_path, "w") as zip_file:
                zip_file.write(csv_file_path, arcname=f"{symbol}.csv")
                
            print(f"File {symbol}.zip created at {zip_file_path}")

            # Update the last_updated.csv file
            current_time_est = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if symbol in last_updated_df["symbol"].values:
                last_updated_df.loc[last_updated_df["symbol"] == symbol, "updated"] = current_time_est
            else:
                last_updated_df.loc[len(last_updated_df)] = {"symbol": symbol, "updated": current_time_est}
            last_updated_df.to_csv(last_updated_path, index=False)
            
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
        finally:
            if os.path.exists(csv_file_path):
                os.remove(csv_file_path)

if __name__ == "__main__":
    update_data(["SPY", "AAPL"], "/Users/vsai23/Workspace/MBQC2/data")