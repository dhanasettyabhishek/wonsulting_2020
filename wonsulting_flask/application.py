from flask import Flask, url_for, render_template, request
from markupsafe import escape
from jinja2 import Template

# libraries for API request
import requests
import json
import pandas as pd

app = Flask(__name__)


apiKey = 'Ayda9RJBQ5BoT6opOauSufMf6fTOhVjqpuZyF6t8'

# foodID = '546613'


def nutrient_API(apiKey, foodID):
    api_resp = json.loads(requests.get('https://api.nal.usda.gov/fdc/v1/' +
                                       foodID + '?api_key=' + apiKey).text)
    api_nutrients = api_resp['foodNutrients']
    nutrientDict = {"FoodID": [
        api_resp['description'], foodID, api_resp['dataType']]}
    for items in api_nutrients:
        if 'amount' in items:
            nutrientDict.update({(items['nutrient']['name']): [(
                items['nutrient']['id']), (items['amount']), (items['nutrient']['unitName'])]})
    nutrientDict = {k.replace(' ', ''): v for k, v in nutrientDict.items()}
    return nutrientDict


@app.route('/')
def home():
    return render_template('hello.html')


@app.route('/results', methods=['POST'])
def result():
    food_id = request.form.get('projectFilepath')
    data = []
    X = nutrient_API(apiKey, food_id)
    data.append(X)
    return render_template('hello.html', data=data)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
