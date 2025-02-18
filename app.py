from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the Superstore data into a pandas DataFrame
orders = pd.read_excel("Sample - Superstore.xls")
app.filtered_orders = orders.copy()
app.filters = {}
app.grouper = 'Country/Region'
app.value = 'Quantity'
app.agg = 'sum'

# Define the groups, values, and aggregate functions that the user can select
groups = ["Country/Region", "Region", "State/Province"]
values = ["Quantity", "Sales", "Profit"]
aggs = ["sum", "mean", "variance", "count"]

# Function to get possible filter options
def get_group_filters():
    return {group: orders[group].unique().tolist() for group in groups}

# Function to get aggregated data
def get_aggregated_data():
    aggregated_data = app.filtered_orders.groupby(app.grouper)[app.value].agg(app.agg).reset_index()
    aggregated_data.columns = ['name', 'value']
    return aggregated_data

@app.route("/")
def root():
    return render_template(
        'root.html',
        groups=groups,
        values=values,
        aggs=aggs,
        group_filters=get_group_filters()
    )

@app.route("/update_aggregate", methods=['POST'])
def update_aggregate():
    data = request.get_json()
    key, value = data['key'], data['value']
    
    if key in ['grouper', 'value', 'agg']:
        setattr(app, key, value)
    
    aggregated_data = get_aggregated_data()
    return {'data': aggregated_data.to_dict('records'), 'x_column': app.grouper, 'y_column': app.value}

@app.route("/update_filter", methods=['POST'])
def update_filter():
    data = request.get_json()
    key, value = data['key'], data['value']
    
    if key == 'Country/Region':
        app.filters = {key: value} if value != 'all' else {}
    elif key == 'Region':
        if value == 'all':
            app.filters.pop('Region', None)
            app.filters.pop('State/Province', None)
        else:
            app.filters['Region'] = value
            app.filters.pop('State/Province', None)
    elif key == 'State/Province' and value == 'all':
        app.filters.pop('State/Province', None)
    elif value != 'all':
        app.filters[key] = value
    else:
        app.filters.pop(key, None)
    
    filtered_df = orders.copy()
    for f_key, f_value in app.filters.items():
        filtered_df = filtered_df[filtered_df[f_key] == f_value]
    
    app.filtered_orders = filtered_df
    group_filters = {group: app.filtered_orders[group].unique().tolist() for group in groups if group not in app.filters}
    
    aggregated_data = get_aggregated_data()
    return {'data': aggregated_data.to_dict('records'), 'x_column': app.grouper, 'y_column': app.value, 'group_filters': group_filters}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)