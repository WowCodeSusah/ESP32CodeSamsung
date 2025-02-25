from flask import Flask, request 
from pymongo import MongoClient 

app = Flask(__name__) 
client = MongoClient('mongodb+srv://michaelbengawan1:mZiKGshslHSpfcH0@sensordata.1gn4t.mongodb.net/?retryWrites=true&w=majority&appName=SensorData') 
db = client['SensorDataTable'] 
collection = db['SensorData']

@app.route('/add_data', methods=['POST']) 
def add_data(): 
    # Get data from request 
    data = request.json 
  
    # Insert data into MongoDB 
    collection.insert_one(data) 
  
    return 'Data added to MongoDB'
  
@app.route('/') 
def hello_world(): 
    return 'Hello, World!'
  
  
if __name__ == '__main__': 
    app.run() 