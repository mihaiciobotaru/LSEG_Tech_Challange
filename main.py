import os
import requests
import datetime
import sys
# pip install requests

URL = 'http://127.0.0.1:5000/'
DATA_SET_PATH = './stock_price_data_files/'

def add_days(timestamp, days):
    # helper function to determine outlier timestamp based on timestamp of set and outlier index
    date = datetime.datetime.strptime(timestamp, "%d-%m-%Y")
    date += datetime.timedelta(days=days)
    return date.strftime("%d-%m-%Y")

def make_req(endpoint, data):
    # helper function used for making requests to the API
    try:
        r = requests.get(url = URL + endpoint + "/" + data)
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None
    
    response_code = r.status_code

    if response_code != 200:
        print(f"{r.json()}")
        return None
    return r.json()

def get_data_points(exchange, stock):
    # returns the stock prices and the timestamp of the first stock price
    return make_req('get-data-points', f'{exchange}/{stock}.csv')


def get_outliers(values):
    # returns the outliers indexes, the mean and standard deviation of the set of values
    values = ",".join([str(value) for value in values["stock_prices"]])
    return make_req('get-outliers', values)

def get_csv_string(stock_id, stock_prices, outliers):
    # Helper function to create the csv string
    # Outliers is an array with indexes of the outliers, not the price values.
    # We determine the outliers timestamp and price based on the index of the outlier and the stock_prices array
    header = "Stock-ID, Timestamp, Stock Price, Mean of 30 data points, Stock Price - Mean, % deviation above the threshold\n"

    first_timestamp = stock_prices["timestamp"]
    mean = float(outliers["mean"])
    std_dev = float(outliers["std_dev"])
    outliers = outliers["outliers"]

    output = []
    for outlier in outliers:
        timestamp_outlier = add_days(first_timestamp, outlier)
        outlier = stock_prices["stock_prices"][outlier]
        deviation = outlier - mean
        percent_deviation = (deviation / std_dev) * 100
        if percent_deviation < 0:
            percent_deviation += 200
        else:
            percent_deviation -= 200

        output.append([stock_id, timestamp_outlier, outlier,  "{:.2f}".format(mean),  
                       "{:.2f}".format(deviation),  "{:.2f}".format(percent_deviation) + "%"])

    csv_string = header
    for line in output:
        csv_string += ",".join([str(value) for value in line]) + "\n"
    return csv_string


def process_stock(stock_exchange, stock_id):
    # Get set of data points from the stock and determine the outliers
    print(f"Processing stock {stock_id} from exchange {stock_exchange}")
    stock_prices = get_data_points(stock_exchange, stock_id)
    if stock_prices is None:
        print("Error getting stock prices")
        return False

    outliers = get_outliers(stock_prices)
    if outliers is None:
        print("Error getting outliers")
        return False

    # Create the csv string and write it to a file with the outliers founds.
    # The csv is saved in the same folder as the stock data file with suffix _outliers.csv
    csv_string = get_csv_string(stock_id, stock_prices, outliers)
    stock_path = f"{DATA_SET_PATH}{stock_exchange}/{stock_id}_outliers.csv"
    with open(stock_path, "w") as f:
        f.write(csv_string)
    print(f" - Result: Found {len(outliers['outliers'])} outliers. Output file: {stock_path}")
    return True

def process_exchange(exchange, number_of_stocks_to_process):
    # Iterate over all stocks in the exchange folder
    # For a given exchange, process maximum number_of_stocks_to_process stocks
    # We accept as a data file only the files that are csvs and do not end with _outliers.csv(Those are the output files of the script)
    stocks = os.listdir(f"{DATA_SET_PATH}{exchange}")
    stocks = [stock for stock in stocks if stock.endswith(".csv") and not stock.endswith("_outliers.csv")]
    stocks_to_process = min(number_of_stocks_to_process, len(stocks))

    success = 0
    errors = 0
    for i in range(stocks_to_process):
        stock_id = stocks[i].split(".")[0]
        result = process_stock(exchange, stock_id)
        if not result:
            print(f"Error processing stock {stock_id} from exchange {exchange}")
            errors += 1
        else:
            success += 1

    return success, errors
            

def process_exchanges(number_of_stocks_to_process):
    # Iterate over all folders in the data set in order to process all exchanges available
    success = 0
    errors = 0
    for folder in os.listdir(DATA_SET_PATH):
        s, e = process_exchange(folder, number_of_stocks_to_process)
        success += s
        errors += e
    
    if success == 0 and errors == 0:
        print("No stocks to process")
        exit(1)
    print(f"Processed {success} stocks successfully and {errors} with errors")

    

if __name__ == "__main__":
    # The script must receive from CLI the numbers of stocks to process as an argument and also it must be an integer.
    args = sys.argv
    if len(args) < 2:
        print("Please provide the number of stocks to process")
        exit(1)
    try:
        number_of_stocks_to_process = int(args[1])
    except ValueError:
        print("Number of stocks to process must be an integer")
        exit(1)    

    process_exchanges(number_of_stocks_to_process)