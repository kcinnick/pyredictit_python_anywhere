from urllib.request import urlopen
from dateutil.parser import parse
import plotly
from sqlalchemy.pool import NullPool
plotly.tools.set_credentials_file(username='MY_USERNAME', api_key='MY_KEY')
from sqlalchemy import create_engine
from flask import Flask
from flask import render_template
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.tools as tls
import ast
import datetime

app = Flask(__name__)

class Contract:
    def __init__(self, contract):
        self.cid = contract['ID']
        try:
            self.end_date = parse(contract['DateEnd'])
        except ValueError:
            self.end_date = '2000-01-01'
        self.name = contract['LongName'].replace('\'', ' ')
        if str(contract['LastTradePrice']) == 'None':
            self.last_trade_price = '0.00'
        else:
            self.last_trade_price = contract['LastTradePrice']
        if str(contract['LastClosePrice']) == 'None':
            self.last_close_price = '0.00'
        else:
            self.last_close_price = contract['LastClosePrice']
        if str(contract['BestBuyYesCost']) == 'None':
            self.buy_yes = '0.00'
        else:
            self.buy_yes = contract['BestBuyYesCost']
        if str(contract['BestSellYesCost']) == 'None':
            self.sell_yes = '0.00'
        else:
            self.sell_yes = contract['BestSellYesCost']
        if str(contract['BestBuyNoCost']) == 'None':
            self.buy_no = '0.00'
        else:
            self.buy_no = contract['BestBuyNoCost']
        if str(contract['BestSellNoCost']) == 'None':
            self.sell_no = '0.00'
        else:
            self.sell_no = contract['BestSellNoCost']
        self.volume = '0'
        self.total_shares = '0'
        self.insert_time = datetime.datetime.now()

def create_mysql_connection():
    engine = create_engine(
        'mysql+pymysql://MYSQLUSERNAME:MYSQLPASSWORD@MYSQLHOST/MYSQL$MYSQLDB?charset=utf8?host=localhost?port=3306',
        encoding='utf-8', poolclass=NullPool)
    connection = engine.connect()
    return connection


def read_from_db(contract_id):
    db_connection = create_mysql_connection()
    result = list(db_connection.execute(
        "SELECT * FROM contracts WHERE cid = {0} ORDER BY insert_time DESC;".format(contract_id)))[0:180]
    db_connection.close()
    return result

@app.route('/')
def hello_world():
    result = []
    r = ast.literal_eval(urlopen('https://www.predictit.org/api/marketdata/all/').read().decode(
        'utf-8').replace('true', 'True').replace('false', 'False').replace('null', 'None'))
    for market in r['Markets']:
        for contract in market['Contracts']:
            try:
                new_contract = Contract(contract)
                result.append(new_contract)
            except Exception as e:
                print(e)
    return render_template('index.html', result=result)

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contract/<cid>')
def show_individual_contract(cid):
    cid = cid
    db_connection = create_mysql_connection()
    result = list(db_connection.execute(
        "SELECT * FROM contracts WHERE cid = {0} ORDER BY insert_time DESC;".format(cid)))[0:100]
    x = [r[2] for r in result]
    buy_yes = [r[5] for r in result]
    sell_yes = [r[6] for r in result]
    buy_no = [r[7] for r in result]
    sell_no = [r[8] for r in result]
    title = result[0][3]
    data = [go.Scatter(x=x, y=buy_yes, name='Buy Yes'),
            go.Scatter(x=x, y=sell_yes, name='Sell Yes'),
            go.Scatter(x=x, y=buy_no, name='Buy No'),
            go.Scatter(x=x, y=sell_no, name='Sell No')
            ]
    url = py.plot(data)[6:]
    db_connection.close()
    return render_template('graph.html', url=url, title=title)

@app.route('/internal_testing')
def testing_navbar_look():
    result = []
    r = ast.literal_eval(urlopen('https://www.predictit.org/api/marketdata/all/').read().decode(
        'utf-8').replace('true', 'True').replace('false', 'False').replace('null', 'None'))
    for market in r['Markets']:
        for contract in market['Contracts']:
            try:
                new_contract = Contract(contract)
                result.append(new_contract)
            except Exception as e:
                print(e)
    return render_template('navbar_example.html', result=result)
