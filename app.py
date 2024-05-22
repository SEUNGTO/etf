import streamlit as st

conn = st.connection('mysql', type='sql')

st.title('ETF 검색기')
st.write('ETF는 TIGER200(102110), KODEX200(069500)만 검색 가능')
etf_code = st.text_input('ETF코드를 입력해주세요.')
if st.button('검색'):
    st.write('### 1. 보유 내역')
    df = conn.query(f'SELECT * from etf_20240521 where etf_code = {etf_code};', ttl=600)
    df = df.loc[:, ['stock_code', 'stock_nm', 'stock_amt', 'evl_amt']]
    df.columns = ['종목코드', '종목명', '보유량', '평가금액']
    st.dataframe(df.sort_values('평가금액', ascending = False))

stock_code = st.text_input('종목코드를 입력해주세요.')
if st.button('종목검색') :
    df = conn.query(f'SELECT * from etf_20240518 where stock_code = {stock_code};', ttl=600)
    st.dataframe(df)
