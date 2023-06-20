from flask import Flask, request, jsonify, render_template
from datetime import datetime
import pandas as pd
import calendar

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/total_items', methods=['GET'])
def get_total_items():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    department = request.args.get('department')

    df = pd.read_csv('data.csv')

    df['date'] = pd.to_datetime(df['date']).dt.date

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    filtered_df = df[(df['date'] >= start_date) & (
        df['date'] <= end_date) & (df['department'] == department)]

    total_items_sold = int(filtered_df['seats'].sum())

    response = {'total_items_sold': total_items_sold}
    return jsonify(response)


@app.route('/api/nth_most_total_item', methods=['GET'])
def get_nth_most_total_item():
    item_by = request.args.get('item_by')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    n = int(request.args.get('n'))

    df = pd.read_csv('data.csv')

    df['date'] = pd.to_datetime(df['date']).dt.date

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    if item_by == 'quantity':
        item_column = 'seats'
    elif item_by == 'price':
        item_column = 'amount'
    else:
        return jsonify({'error': 'Invalid item_by parameter. Must be "quantity" or "price".'})

    top_n_items = filtered_df.groupby(
        'software')[item_column].sum().nlargest(n)

    print(top_n_items)
    if len(top_n_items) >= n:
        nth_item = top_n_items.index[n - 1]
        return jsonify({'nth_most_total_item': nth_item})
    else:
        return jsonify({'error': 'Insufficient data to find the nth most item.'})


@app.route('/api/percentage_of_department_wise_sold_items', methods=['GET'])
def get_percentage_of_department_wise_sold_items():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    df = pd.read_csv('data.csv')

    df['date'] = pd.to_datetime(df['date']).dt.date

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    total_items_sold = filtered_df['seats'].sum()

    department_sold_count = filtered_df.groupby('department')['seats'].sum()
    department_sold_percentage = (
        department_sold_count / total_items_sold) * 100
    department_sold_percentage = department_sold_percentage.round(2)

    response = department_sold_percentage.to_dict()
    # print(response)
    return jsonify(response)


@app.route('/api/monthly_sales', methods=['GET'])
def get_monthly_sales():
    product = request.args.get('product')
    year = int(request.args.get('year'))

    df = pd.read_csv('data.csv')
    df['date'] = pd.to_datetime(df['date'])

    monthly_sales = df[(df['software'] == product) & (
        df['date'].dt.year == year)].groupby(df['date'].dt.month)['seats'].sum().tolist()

    month_names = [calendar.month_name[i] for i in range(1, 13)]
    monthly_sales_dict = {month_names[i-1]: monthly_sales[i-1]
                          if i <= len(monthly_sales) else 0 for i in range(1, 13)}

    print(monthly_sales_dict)
    return jsonify(monthly_sales_dict)


if __name__ == '_main_':
    app.run()
