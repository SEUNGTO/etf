import streamlit as st
import mysql.connector

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
            st.write("MySQL에 성공적으로 연결되었습니다.")
            return connection
    except Exception as e:
        st.write("MySQL 연결에 실패했습니다.", e)
        return None


# 데이터베이스에서 데이터 가져오기
def fetch_data(connection, query):
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        return data
    except Exception as e:
        st.write("데이터를 가져오는 데 실패했습니다.", e)
        return None


# Streamlit 앱
def main():
    st.title("MySQL 데이터 조회")

    # MySQL 연결 정보 입력
    host = st.text_input("MySQL 호스트")
    user = st.text_input("MySQL 사용자")
    password = st.text_input("MySQL 비밀번호")
    database = st.text_input("MySQL 데이터베이스")

    if st.button("MySQL 연결"):
        connection = connect_to_mysql(host, user, password, database)

        query = 'select * from tb_etf'

        data = fetch_data(connection, query)

        st.write("조회 결과:")
        st.write(data)