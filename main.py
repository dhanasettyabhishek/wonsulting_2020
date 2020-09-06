from flask import Flask, url_for, render_template, request, redirect
from markupsafe import escape
from jinja2 import Template
from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError
from wtforms.validators import InputRequired

# libraries for API request
import random
import requests
import json
import pandas as pd

# libraries for plotly
import plotly
import plotly.graph_objs as go

app = Flask(__name__)
app.config['SECRET_KEY'] = "wonsulting2020"


with open('description.json') as f:
    description = json.load(f)
validation = set(map(lambda x: x['label'], description))


# class SearchForm(FlaskForm):
#     # projectFilepath = StringField('projectFilepath', render_kw={
#     #     "placeholder": "Select a food item"}, validators=[InputRequired(message="Food Name Required")])
#     projectFilepath = StringField('projectFilepath', render_kw={
#         "placeholder": "Select a food item"}, validators=[])

# def validate_projectFilepath(self, projectFilepath):
#     print(projectFilepath.data)
#     if projectFilepath.data not in validation:
#         raise ValidationError(
#             "Please select an option from the suggested list.")


set_food_id = set()


@app.route('/')
def home():
    # form = SearchForm()
    set_food_id.clear()
    return render_template('index.html', description=description)


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


key_value = {'apples_.x': 'apples', 'banana_.x': 'bananas',
             "beef_.x": "beef, ground, 85% lean meat / 15% fat (includes foods for usda's food distribution program)", "blueberries_.x":
             "blueberries", "carrots_.x": "carrots", "cheddar_cheese_.x":
             "cheese, cheddar, sharp, sliced", "cherries_.x": "cherries, sour, red", "chicken_.x": "chicken, skin (drumsticks and thighs)",
             "eggs_.x": "egg, whole, fresh", "grapes_.x": "grapes, american type (slip skin)", "kale_.x": "kale", "potatoes_.x": "potatoes, flesh and skin",
             "spinach_.x": "spinach", "strawberries_.x": "strawberries",
             "tomatoes_.x": "tomatoes, red, ripe, year round average",
             "whole_milk_.x": "milk, chocolate beverage, hot cocoa, homemade"}


@app.route('/results', methods=['POST'])
def result():
    with open('description.json') as f:
        description = json.load(f)
    description_dict = dict()
    for i in description:
        description_dict[i['label']] = i['value']

    data = []
    graphJSON = None
    graphJSON2 = None
    formName = None

    for key, value in request.form.items():
        print(key, value)
        if key == 'form1' or key == 'form2':
            food_id_description = value
        if key in key_value:
            food_id_description = key_value[key]
    if food_id_description not in description_dict:
        return render_template('index.html', flag='Please enter text from the suggestions.', description=description)
    food_id = str(description_dict[food_id_description])
    print(food_id)
    food_ids = []
    food_ids.append(food_id)
    set_food_id.add(food_id)
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
            id_description = request.form.get('form2')
            id_ = str(description_dict[id_description])
            set_food_id.add(id_)
            print("====", set_food_id)
            api_value = add_multiple(list(set_food_id))
            X = summing_values(api_value)
            data.append(X)
    L = api_value['Energy']
    cal_ = []
    value = 0
    for k in L:
        if k[1] == 'kJ':
            value = convert('kcal', 'kJ', k[0])
            cal_.append(value)
        else:
            value = k[0]
            cal_.append(value)
    target = 2000
    temp = 0
    for i in cal_:
        temp = target - i
        target = temp
    cal_.append(temp)
    split_ = X['foodItems'][2]
    split_.append("Remaining value")
    print(cal_, split_)
    # # Plot
    df = pd.DataFrame(X)
    labels = ['Protein', 'Totallipidfat',
              'Carbohydratebydifference', 'SugarstotalincludingNLEA']
    labels2 = ['Protein', 'Fat', 'Carbs', 'Sugars']
    colors = ['lightcyan', 'cyan', 'royalblue', 'darkblue']
    values = []
    for i in labels:
        values.append(df[i][0])
    fig = go.Figure(
        data=[go.Bar(y=labels2, x=values, orientation='h', marker_color=colors, text=list(map(lambda orig_string: str(orig_string) + ' g', values)), textposition='auto')])

    fig.update_layout(title_text='Nutrition Plot', yaxis=dict(
        title='Nutrients',
    ), xaxis=dict(
        title='No.of grams',
    ))
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # Plot 2
    # fig2 = go.Figure(data=go.Scatter(x=split_, y=cal_))
    fig2 = go.Figure(data=go.Pie(labels=split_, values=cal_))
    fig2.update_traces(textinfo='value')
    fig2.update_layout(
        title_text='Source of Calories (based on recommended 2,000 cal. )')
    fig2.update_layout(
        legend=dict(
            x=0.5,
            y=-0.25,
            traceorder="reversed"
        )
    )
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('hello_add_multiple.html', data=data, v=graphJSON, v2=graphJSON2, description=description)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
