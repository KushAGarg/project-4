from flask import Flask, render_template, request, redirect
from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Configure your MongoDB URI
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Housing'
mongo = PyMongo(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['Housing']
collection = db['Houses']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = {
            'square_feet': request.form.get('square_feet'),
            'bedrooms': request.form.get('bedrooms'),
            'bathrooms': request.form.get('bathrooms'),
            'neighborhood': request.form.get('neighborhood'),
            'year_built': request.form.get('year_built'),
        }
        collection.insert_one(data)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
