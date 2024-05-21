import streamlit as st

conn = st.connection('mysql', type='sql')

etf_code = st.text_input('ETF코드를 입력해주세요.')
if st.button('검색'):
# Perform query.

    df = conn.query(f'SELECT * from etf_20240518 where etf_code = {etf_code};', ttl=600)

    st.dataframe(df)

stock_code = st.text_input('종목코드를 입력해주세요.')
if st.button('종목검색') :
    df = conn.query(f'SELECT * from etf_20240518 where stock_code = {stock_code};', ttl=600)
    st.dataframe(df)