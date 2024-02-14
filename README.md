# SETUP
 For the setup of the projects, all we need is requests and flask modules. They can be installed using pip install flask and pip install requests.
 After this step, we need to set the correct path for the data set, this can be found in the main.py file. If the data set folder is in the same directory as main.py then there is no need for any change.

# EXECUTION
To run the program, we need to start the flask servers in one terminal using python api.py and start the main code with python main.py
To run main.py we need to pass as argument the recommended number of stocks to be processed per exchange. 
The script will detected all valid stocks in the data set folder, including new exchanges or stocks. The output of the file will be a csv for each stock processed that will be saved in the same folder as the stock.
The CSV includes info about the outliers.
