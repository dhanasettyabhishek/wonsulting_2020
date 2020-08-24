from flask import Flask, url_for, render_template, request
from markupsafe import escape
from jinja2 import Template

# libraries for API request
import random
import requests
import json
import pandas as pd

# libraries for plotly
import plotly
import plotly.graph_objs as go

app = Flask(__name__)

apiKeys = ["WEmcd6DkxgyCerLC1mLNfLxuU0yTL8IzrzpaNbFf", "OVPFv146FkxVhRv2CCBLZ4aaxdJSXNLu8wGnCCbA",
           'Ayda9RJBQ5BoT6opOauSufMf6fTOhVjqpuZyF6t8', "DqannebfgACLvWlhbjY3SeEkD0iepY6RudjLixsI",
           "OXr1dRlCSW5AHaVCC3SLtFm7EKy1GVOiMPlQH79Z", "CKW4XukWilX86KOGlmjRkojWHT9UK6o4mXu9mHw2",
           "extc6yduRq7J49GuMj2Qld1Bm0SVQBhEqo9RrovA", "jyEvK7JgiJuyKHQelqYEyisOMuclq49kExvsbEnJ",
           "ZfADi6khGtyAwI6goSldliOwcSIDLHLkeVUGmTB8", "LsWUY5z0b031P4SN49XnsfCiTNR4fm5g8E5RIIou"]
apiKey = random.choice(apiKeys)

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


def DVpercentage(daily_value, sum_):
    percentage = {}
    for i, total in daily_value.items():
        value = sum_[i][0]
        if value == 0:
            percentage[i] = 0
        else:
            percent = (value / total) * 100
            percentage[i] = int(percent)
    return percentage


daily_value = {'SugarstotalincludingNLEA': 50.0,
               'Cholesterol': 0.3,
               'Fibertotaldietary': 28.0,
               'Totallipidfat': 78.0,
               'Protein': 50.0,
               'Fattyacidstotalsaturated': 20.0,
               'SodiumNa': 2.3,
               'Carbohydratebydifference': 275.0,
               'Energy': 2000.0}


def summing_values(mul):
    foodItems = []
    final_result = dict()
    all_units = {'kcal', 'g', 'IU'}
    for i, j in mul.items():
        if i == "FoodID":
            for k in j:
                x = k[0]
                split_ = x.split(",")
                foodItems.append("".join(split_))
        else:
            summed_value = list()
            units = ""
            sum_ = 0
            for k in j:
                if k[1] in all_units:
                    units = k[1]
                    sum_ += k[0]
                else:
                    if k[1] == 'kJ':
                        units = "kcal"
                        sum_ += convert('kcal', k[1], k[0])
                    if k[1] == 'mg':
                        units = "g"
                        sum_ += convert('g', k[1], k[0])
                    if k[1] == 'µg':
                        units = "g"
                        sum_ += convert('g', k[1], k[0])
                summed_value.append(k)
            sum_ = round(sum_, 2)
            i = ''.join(e for e in i if e.isalnum())
            final_result[i] = [sum_, units, str(sum_)+" "+units]
    food_items = ""
    for i in foodItems:
        food_items += " | " + i.title()
    food_items = food_items.strip()
    final_result['foodItems'] = [food_items[2:], len(foodItems), foodItems]
    percentage = DVpercentage(daily_value, final_result)
    for i, j in final_result.items():
        if i in percentage:
            final_result[i].append(str(percentage[i])+'%')
        else:
            final_result[i].append(str(0)+'%')
    return final_result


def convert(to_unit, from_unit, value):
    result = 0
    if to_unit == 'kcal' and from_unit == 'kJ':
        result = value * 0.239
    if to_unit == 'g' and from_unit == 'mg':
        result = value * 0.001
    if to_unit == 'g' and from_unit == 'µg':
        result = value * 10**-6
    return result


@app.route('/search')
def search_engine():
    return render_template('search.html')


@app.route('/')
def home():
    with open('description.json') as f:
        description = json.load(f)
    return render_template('hello.html', description=description)


@app.route('/whyN')
def whyN():
    return render_template('whyN.html')


@app.route('/About')
def About():
    return render_template('About.html')


@app.route('/Questions')
def Questions():
    return render_template('Questions.html')


@app.route('/credits')
def credits():
    return render_template("Credits.html")


set_food_id = set()


@app.route('/results', methods=['POST'])
def result():
    with open('description.json') as f:
        description = json.load(f)
    description_dict = dict()
    for i in description:
        description_dict[i['label']] = i['value']
    food_id_description = request.form.get('projectFilepath')
    food_id = str(description_dict[food_id_description])
    print(food_id)
    food_ids = []
    food_ids.append(food_id)
    set_food_id.add(food_id)
    data = []
    api_value = nutrient_API(apiKey, food_id)
    X = summing_values(api_value)
    data.append(X)
    if request.method == 'POST':
        if request.form.get('search') == 'Search':
            set_food_id.clear()
            set_food_id.add(food_id)
            print(set_food_id)
            pass
        elif request.form.get('add_to_meal') == 'Add to existing meal':
            data = []
            id_description = request.form.get('projectFilepath')
            id_ = str(description_dict[id_description])
            set_food_id.add(id_)
            print("====", set_food_id)
            api_value = add_multiple(list(set_food_id))
            X = summing_values(api_value)
            data.append(X)
    L = api_value['Energy']
    cal_ = [0]
    value = 0
    for k in L:
        if k[1] == 'kJ':
            value += convert('kcal', 'kJ', k[0])
            cal_.append(value)
        else:
            value += k[0]
            cal_.append(value)

    split_ = ['Start']+X['foodItems'][2]
    print(cal_, split_)
    # # Plot
    df = pd.DataFrame(X)
    labels = ['Protein', 'Totallipidfat',
              'Carbohydratebydifference', 'SugarstotalincludingNLEA']
    labels2 = ['Protein', 'Fat', 'Carbs', 'Sugars']
    values = []
    for i in labels:
        values.append(df[i][0])
    fig = go.Figure(data=[go.Bar(y=labels2, x=values, orientation='h')])
    fig.update_layout(title_text='Nutrition Plot', yaxis=dict(
        title='Nutriants',
    ), xaxis=dict(
        title='No.of grams',
    ))
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Plot 2
    fig2 = go.Figure(data=go.Scatter(x=split_, y=cal_))
    fig2.update_layout(title_text='Total calories plot', yaxis=dict(
        title='Calories',
    ), xaxis=dict(
        title='Food Items',
    ))
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('hello_add_multiple.html', data=data, v=graphJSON, v2=graphJSON2, description=description)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
