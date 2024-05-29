import pandas as pd
import mysql.connector
from tqdm import tqdm

data = pd.read_excel('../data/etf_20240514.xlsx',
                     dtype = str)
data.fillna(0, inplace = True)


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


def drop_table(type) :
    connection = connect_to_mysql(host, user, password, database)
    cursor = connection.cursor()
    drop_query = f"drop table if exists etf_{type}"
    cursor.execute(drop_query)
    cursor.close()
    connection.close()

def create_table(type) :
    connection = connect_to_mysql(host, user, password, database)
    cursor = connection.cursor()

    create_query = f"create table etf_{type} " \
                   f" (etf_code varchar(6)" \
                   f", stock_code varchar(50)" \
                   f", stock_nm varchar(30)" \
                   f", stock_amt int" \
                   f", evl_amt int" \
                   f", ratio varchar(30)" \
                   f")"

    cursor.execute(create_query)
    cursor.close()
    connection.close()

def insert_date(type, data, batch_size) :

    _len = data.shape[0]

    for i in tqdm(range(0, _len, batch_size)) :

        batch = data[i:i+batch_size].drop('평가금액', axis = 1)
        connection = connect_to_mysql(host, user, password, database)
        cursor = connection.cursor()


        insert_query = f"""
        INSERT INTO  etf_{type} 
        (etf_code, stock_code, stock_nm, stock_amt, evl_amt, ratio)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        insert_data = []
        for row in batch.iterrows():
            tmp = tuple(row[1].values)
            insert_data.append(tmp)

        cursor.executemany(insert_query, insert_data)
        cursor.fetchall()
        cursor.close()
        connection.commit()
        connection.close()


if __name__ == "__main__" :

    # drop_table('old')
    # create_table('old')
    # insert_date('old', data, 1000)

    host = "34.22.69.206"
    database = "db_etf"
    user = "user"
    password = "1234"

    query = '''
    SELECT * FROM research
    '''

    connection = connect_to_mysql(host, user, password, database)
    cursor = connection.cursor()
    cursor.execute(query)

    data = cursor.fetchall()
    data = pd.DataFrame(data)
    data.columns = ['종목명', '종목코드', '리포트 제목', 'nid', '목표가', '의견', '게시일자', '증권사', '링크']
    data.to_json('research.json')



    connection = connect_to_mysql(host, user, password, database)
    cursor = connection.cursor()
    drop_query = f"select * from etf_new"
    data = cursor.execute(drop_query)
    data