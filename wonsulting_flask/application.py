from flask import Flask, url_for, render_template, request
from markupsafe import escape
from jinja2 import Template

# libraries for API request
import requests
import json
import pandas as pd

# libraries for plotly
import plotly
import plotly.graph_objs as go
import numpy as np
import plotly.figure_factory as ff

app = Flask(__name__)


apiKey = 'Ayda9RJBQ5BoT6opOauSufMf6fTOhVjqpuZyF6t8'

# foodID = '546613'


def nutrient_API(apiKey, foodID):
    api_resp = json.loads(requests.get(
        'https://api.nal.usda.gov/fdc/v1/' + foodID + '?api_key=' + apiKey).text)
    api_nutrients = api_resp['foodNutrients']
    nutrientDict = {"FoodID": [[api_resp['description'], foodID]]}
    for items in api_nutrients:
        if 'amount' in items:
            nutrientDict.update({(items['nutrient']['name']): [
                                [(items['amount']), (items['nutrient']['unitName'])]]})
    nutrientDict = {k.replace(' ', ''): v for k, v in nutrientDict.items()}
    return(nutrientDict)


def add_multiple(id_):
    values = nutrient_API(apiKey, id_[0])
    id_.pop(0)
    for i in id_:
        values_2 = nutrient_API(apiKey, i)
        for j, k in values_2.items():
            if j in values:
                values[j].append(k[0])
    return values


@app.route('/')
def home():
    return render_template('hello.html')


set_food_id = set()


@app.route('/results', methods=['POST'])
def result():
    food_id = request.form.get('projectFilepath')
    food_ids = []
    food_ids.append(food_id)
    set_food_id.add(food_id)
    data = []
    X = nutrient_API(apiKey, food_id)
    data.append(X)
    if request.method == 'POST':
        if request.form.get('search') == 'Search':
            set_food_id.clear()
            set_food_id.add(food_id)
            print(set_food_id)
            pass
        elif request.form.get('add_to_meal') == 'Add to existing meal':
            data = []
            id_ = request.form.get('projectFilepath')
            set_food_id.add(id_)
            print(set_food_id)
            X = add_multiple(list(set_food_id))
            data.append(X)

    print(data)
    return render_template('hello_add_multiple.html', data=data)
    # # Plot
    # df = pd.DataFrame(X)
    # labels = [
    #     'Protein', 'Totallipid(fat)', 'Carbohydrate,bydifference', 'Sugars,totalincludingNLEA']
    # labels2 = ['Protein', 'Fat', 'Carbs', 'Sugars']
    # values = []
    # for i in labels:
    #     values.append(df[i][0])
    # trace = go.Bar(y=labels2, x=values, orientation='h')
    # fig = [trace]
    # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # return render_template('hello_add_multiple.html', data=data, v=graphJSON)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
