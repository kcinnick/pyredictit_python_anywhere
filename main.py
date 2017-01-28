import plotly
from sqlalchemy.pool import NullPool
plotly.tools.set_credentials_file(username='MY_USERNAME', api_key='MY_API_KEY')
from sqlalchemy import create_engine
from flask import Flask
from flask import render_template
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.tools as tls

app = Flask(__name__)

def create_mysql_connection():
    engine = create_engine(
        'mysql+pymysql://MYUSERNAME:MYPASSWORD@MYHOST/MYSQLUSERNAME$MYSQLDATABASE?charset=utf8?host=localhost?port=3306',
        encoding='utf-8', poolclass=NullPool)
    connection = engine.connect()
    return connection


def read_from_db(contract_id):
    db_connection = create_mysql_connection()
    result = list(db_connection.execute(
        "SELECT * FROM contracts WHERE cid = {0} ORDER BY insert_time DESC;".format(contract_id)))[0:360]
    db_connection.close()
    return result

@app.route('/')
def hello_world():
    db_connection = create_mysql_connection()
    result = db_connection.execute("SELECT * FROM contracts ORDER BY insert_time DESC LIMIT 500;")
    result = [i for i in result]
    db_connection.close()
    return render_template('index.html', result=result)

@app.route('/contract/<cid>')
def show_individual_contract(cid):
    db_connection = create_mysql_connection()
    result = list(db_connection.execute(
        "SELECT * FROM contracts WHERE cid = {0} ORDER BY insert_time DESC;".format(cid)))[0:100]
    x = [r[2] for r in result]
    buy_yes = [r[5] for r in result]
    sell_yes = [r[6] for r in result]
    buy_no = [r[7] for r in result]
    sell_no = [r[8] for r in result]
    data = [go.Scatter(x=x, y=buy_yes, name='Buy Yes'),
            go.Scatter(x=x, y=sell_yes, name='Sell Yes'),
            go.Scatter(x=x, y=buy_no, name='Buy No'),
            go.Scatter(x=x, y=sell_no, name='Sell No')
            ]
    url = py.plot(data)
    db_connection.close()
    return '<iframe frameborder="0" style="border: 0; width: 100%; height: 100%" scrolling="no" src="{0}.embed"></iframe>'.format(url[6:])
