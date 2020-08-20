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


def summing_values(mul):
    foodItems = []
    final_result = dict()
    for i, j in mul.items():
        if i == "FoodID":
            for k in j:
                x = k[0]
                split_ = x.split(",")
                foodItems.append(split_[0])
        else:
            summed_value = list()
            units = j[0][1]
            sum_ = 0
            for k in j:
                if k[1] == units:
                    sum_ += k[0]
                else:
                    sum_ += convert(units, k[1], k[0])
                summed_value.append(k)
            sum_ = round(sum_, 2)
            i = ''.join(e for e in i if e.isalnum())
            final_result[i] = (sum_, units, str(sum_) + " " + units)
    food_items = ""
    for i in foodItems:
        food_items += ", " + i.title()
    food_items = food_items.strip()
    final_result['foodItems'] = (food_items[2:], foodItems)
    return final_result


def convert(to_unit, from_unit, value):
    result = 0
    if to_unit == 'kcal' and from_unit == 'kJ':
        result = value * 0.239
    return result


@app.route('/search')
def search_engine():
    return render_template('search.html')


@app.route('/')
def home():
    return render_template('hello.html')

@app.route('/whyN')
def whyN():
    return render_template('whyN.html')

set_food_id = set()


@app.route('/results', methods=['POST'])
def result():
    food_id = request.form.get('projectFilepath')
    food_ids = []
    food_ids.append(food_id)
    set_food_id.add(food_id)
    data = []
    X = nutrient_API(apiKey, food_id)
    X = summing_values(X)
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
            X = summing_values(X)
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
