import mysql.connector
import pandas as pd

data = pd.read_csv('')
data = data.drop(['시가총액', '시가총액 구성비중'], axis = 1)
data.fillna(0, inplace = True)

host = "34.22.69.206"
database = "db_etf"
user = "user"
password = "1234"

# MySQL 연결
def connect_to_mysql(host, user, password, database):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            return connection
    except Exception as e:
        print("MySQL 연결에 실패했습니다.", e)
        return None


def drop_table(date) :
    connection = connect_to_mysql(host, user, password, database)
    cursor = connection.cursor()
    drop_query = f"drop table if exists etf_{date}"
    cursor.execute(drop_query)
    cursor.close()
    connection.close()

def create_table(date) :
    connection = connect_to_mysql(host, user, password, database)
    cursor = connection.cursor()

    create_query = f"create table etf_{date} " \
                   f" (etf_code varchar(6)" \
                   f", stock_code varchar(50)" \
                   f", stock_nm varchar(30)" \
                   f", stock_amt int" \
                   f", evl_amt int)"

    cursor.execute(create_query)
    cursor.close()
    connection.close()

def insert_date(date, data) :
    connection = connect_to_mysql(host, user, password, database)
    cursor = connection.cursor()

    insert_query = f"""
    INSERT INTO  etf_{date} 
    (etf_code, stock_code, stock_nm, stock_amt, evl_amt)
    VALUES (%s, %s, %s, %s, %s)
    """

    insert_data = []
    for row in data.iterrows():
        tmp = tuple(row[1].values)
        insert_data.append(tmp)

    cursor.executemany(insert_query, insert_data[:100])
    cursor.fetchall()
    cursor.close()
    connection.commit()
    connection.close()


if __name__ == "__main__" :
    date = '20240519'
    data = pd.read_csv('')


    drop_table(date)
    create_table(date)
    insert_date(date, data)