from flask import Flask, render_template, request
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load the Superstore data into a pandas DataFrame
orders = pd.read_excel("Sample - Superstore.xls")
app.filtered_orders = orders
app.filters = {}
app.grouper = 'Country/Region'
app.value = 'Profit'
app.agg = 'sum'

# Define the groups, values, and aggregate functions that the user can select
groups = ["Country/Region", "Region", "State/Province"]
values = ["Quantity", "Sales", "Profit"]
aggs = ["sum", "mean", "variance", "count"]

# Define a function for getting possible filter options for each grouper
def get_group_filters():
    group_filters = {group: orders[group].unique().tolist() for group in groups}
    return group_filters

# Define a function that returns the aggregated data
def get_aggregated_data():
    aggregated_data = app.filtered_orders.groupby(app.grouper)[app.value].agg(app.agg).reset_index()
    aggregated_data.columns = ['name', 'value']
    return aggregated_data

# Pass the groups, values, aggregate functions, and group filters to the root.html template
@app.route("/")
def root():
    return render_template(
        'root.html',
        groups=groups,
        values=values,
        aggs=aggs,
        group_filters=get_group_filters()
    )

# Handle updates to the aggregate function
@app.route("/update_aggregate", methods=['POST'])
def update_aggregate():
    data = request.get_json()
    value = data['value']
    key = data['key']

    if key == 'grouper':
        app.grouper = value
    elif key == 'value':
        app.value = value
    elif key == 'agg':
        app.agg = value

    aggregated_data = get_aggregated_data()
    return {'data': aggregated_data.to_dict('records'), 'x_column': app.grouper, 'y_column': app.value}

# Handle updates to the filter
@app.route("/update_filter", methods=['POST'])
def update_filter():
    data = request.get_json()
    value = data['value']
    key = data['key']

    if value != 'all':
        app.filtered_orders = orders[orders[key] == value]
    else:
        app.filtered_orders = orders

    aggregated_data = get_aggregated_data()
    group_filters = {group: app.filtered_orders[group].unique().tolist() for group in groups}

    return {'data': aggregated_data.to_dict('records'), 'x_column': app.grouper, 'y_column': app.value, 'group_filters': group_filters}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)