import datetime
import requests
import sqlalchemy
from sqlalchemy import create_engine
from dateutil.parser import *
from time import sleep
from tqdm import tqdm

def insert_contract_into_mysql_db(db_connection, contract):
    parsed_contract = Contract(contract=contract)
    try:
        db_connection.execute(
            "INSERT INTO contracts VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}');".format(
            parsed_contract.cid, parsed_contract.end_date, datetime.datetime.now().strftime('%Y-%m-%d %H:%M'), parsed_contract.name,
            parsed_contract.last_trade_price,  parsed_contract.buy_yes, parsed_contract.sell_yes, parsed_contract.buy_no,
            parsed_contract.sell_no, parsed_contract.last_close_price, parsed_contract.volume, parsed_contract.total_shares
                ).replace('%', ''))
    except sqlalchemy.exc.IntegrityError:
        pass

class Contract:
    def __init__(self, contract):
        self.cid = contract['ID']
        try:
            self.end_date = parse(contract['DateEnd'])
        except ValueError:
            self.end_date = '2000-01-01'
        self.name = contract['LongName'].replace('\'', ' ')
        if str(contract['LastTradePrice']) == 'None':
            self.last_trade_price = '0'
        else:
            self.last_trade_price = contract['LastTradePrice']
        if str(contract['LastClosePrice']) == 'None':
            self.last_close_price = '0'
        else:
            self.last_close_price = contract['LastClosePrice']
        if str(contract['BestBuyYesCost']) == 'None':
            self.buy_yes = '0'
        else:
            self.buy_yes = contract['BestBuyYesCost']
        if str(contract['BestSellYesCost']) == 'None':
            self.sell_yes = '0'
        else:
            self.sell_yes = contract['BestSellYesCost']
        if str(contract['BestBuyNoCost']) == 'None':
            self.buy_no = '0'
        else:
            self.buy_no = contract['BestBuyNoCost']
        if str(contract['BestSellNoCost']) == 'None':
            self.sell_no = '0'
        else:
            self.sell_no = contract['BestSellNoCost']
        self.volume = '0'
        self.total_shares = '0'

def create_mysql_connection():
    engine = create_engine(
        'mysql+pymysql://MYSQLUSERNAME:MYSQLPASSWORD@MYSQLHOST/MYSQLUSERNAME$MYSQLDB?charset=utf8?host=localhost?port=3306',
        encoding='utf-8', poolclass=NullPool)
    connection = engine.connect()
    return connection

def main():
    while True:
        db_connection = create_mysql_connection()
        try:
            r = requests.get('https://www.predictit.org/api/marketdata/all/', headers={'Accept': 'application/json'})
            for market in tqdm(r.json()['Markets']):
                for contract in market['Contracts']:
                    try:
                        insert_contract_into_mysql_db(db_connection, contract)
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)
        finally:
            sleep(20)

main()
