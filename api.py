import random
from flask import Flask, jsonify 
import datetime

app = Flask(__name__) 

def test_timestamp(timestamp):
    try:
        datetime.datetime.strptime(timestamp, "%d-%m-%Y")
        return True
    except ValueError:
        return False
    
# Receive a file name and return a list of 30 stock prices and the timestamp of the first stock price
@app.route('/get-data-points/<path:input_file>', methods = ['GET']) 
def get_data_points(input_file):
    # Check existence of the file and read it
    input_file = f"../stock_price_data_files/{input_file}"
    try:
        with open(input_file, 'r') as input_file:
            input_file = input_file.read()
    except FileNotFoundError:
        return jsonify({'error': f'File {input_file} not found'}), 400
    
    # remove empty lines
    input_file = "\n".join([line for line in input_file.split("\n") if line.strip() != ""])
    input_file = input_file.split("\n")

    # Select a random 30 stock prices 
    if len(input_file) < 30:
        return jsonify({'error': 'File must have at least 30 stock prices'}), 400
    index = random.randint(0, len(input_file) - 30)
    input_file = input_file[index:index+30]

    # Extract the stock prices from the file and the timestamp of the first stock price
    # Check if the file has the correct format
    try:
        stock_prices = []
        for line in input_file:
            line = line.split(",")
            if len(line) != 3 or not test_timestamp(line[1]) or not float(line[2]):
                raise Exception("Could not parse file correctly. Check the format of the file.")
            stock_prices.append(float(line[2]))
        timestamp = input_file[0].split(",")[1]

    except Exception:
        print(f"Error parsing file {input_file}")
        return jsonify({'error': 'File must have the format: Stock-ID (Ticker), Timestamp (dd-mm-yyyy), stock price value'}), 400

    return jsonify({'stock_prices': stock_prices, 'timestamp': timestamp})
	


# Receive a list of values separated by commas and return a list of indexes of the outliers, the mean and the standard deviation
@app.route('/get-outliers/<string:values>', methods = ['GET']) 
def get_outliers(values): 
    # Check if the values are a list of floats separated by commas
    values = values.split(',')
    try:
        values = [float(value) for value in values]
    except ValueError:
        return jsonify({'error': 'Values must be a list of floats separated by commas'}), 400

    # Calculate the mean, standard deviation and determine the outliers
    mean_value = mean(values)
    std_dev_value = std_dev(values)
    outliers = []
    for i in range(len(values)):
        if is_outlier(values[i], mean_value, std_dev_value):
            outliers.append(i)
    
    return jsonify({'outliers': outliers, "mean": "{:.2f}".format(mean_value), "std_dev": "{:.2f}".format(std_dev_value)})

# helper functions to calculate mean, standard deviation and determine if a value is an outlier
def mean(numbers):
    return sum(numbers) / len(numbers)

def std_dev(numbers):
    avg = mean(numbers)
    variance = sum([(x-avg)**2 for x in numbers]) / len(numbers)
    return variance ** 0.5

def is_outlier(number, mean, std_dev):
    return abs(number - mean) > 2 * std_dev

# Start the Flask server and listen for requests on http://127.0.0.1:5000/
if __name__ == '__main__': 
	app.run(debug = True) 
