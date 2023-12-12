from flask import Flask, render_template, request, redirect
from flask_pymongo import PyMongo
from pymongo import MongoClient
from flask_cors import CORS
from bs4 import BeautifulSoup
import tensorflow as tf
from pathlib import Path

app = Flask(__name__)

CORS(app)

# Configure your MongoDB URI
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Housing'
mongo = PyMongo(app)

client = MongoClient('mongodb://localhost:27017/')
db = client['Housing']
houses = db['Houses']

if "FakeHouses" in db.list_collection_names():
    db['FakeHouses'].drop()
fake_houses = db['FakeHouses']

model = tf.keras.models.load_model(Path("./neural-network/models/optimized_model_5.h5"))
print(model.summary())

def transform_input(sqft, bed, bath, loc, year):
    ret = [sqft, bed, bath, year]
    if loc.lower() == "rural":
        ret += [1, 0, 0]
    elif loc.lower() == "suburban":
        ret += [0, 1, 0]
    elif loc.lower() == "urban":
        ret += [0, 0, 1]
    else:
        return []
    return ret

def assignH3String(s):
    f = open(Path("./front-end/templates/index.html"), "r")
    soup = BeautifulSoup(f.read())
    f.close()

    parent = soup.find("div", class_ = "left-part")
    parent.h3.string = s

    f = open(Path("./front-end/templates/index.html"), "w")
    f.write(str(soup))
    f.close()

def assignH4String(s):
    f = open(Path("./front-end/templates/index.html"), "r")
    soup = BeautifulSoup(f.read())
    f.close()

    parent = soup.find("div", class_ = "left-part")
    parent.h4.string = s

    f = open(Path("./front-end/templates/index.html"), "w")
    f.write(str(soup))
    f.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    assignH3String("")
    assignH4String("")
    if request.method == 'POST':
        assignH3String("")
        assignH4String("")
        data = {
            'SquareFeet': int(request.form.get('square_feet')),
            'Bedrooms': int(request.form.get('bedrooms')),
            'Bathrooms': int(request.form.get('bathrooms')),
            'Neighborhood': request.form.get('neighborhood'),
            'YearBuilt': int(request.form.get('year_built')),
        }
        
        price_output = None
        found_data = fake_houses.find(data)
        elem = None
        for x in found_data:
            elem = x
        print("NEXT")
        if elem != None:
            assignH4String("Price pulled from Mongo")
            price_output = elem['Price']
        else:
            vals = list(data.values())
            inp = transform_input(vals[0], vals[1], vals[2], vals[3], vals[4])
            price_output = round(float(model.predict([inp])[0][0]), 2)
        data['Price'] = price_output
        
        assignH3String(str(price_output))
        
        output = fake_houses.insert_one(data)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)