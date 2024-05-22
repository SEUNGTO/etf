import streamlit as st
stocks = {'102110' : 'TIGER200', '069500' : 'KODEX 200'}

conn = st.connection('mysql', type='sql')

st.title('ETF 검색기')
st.write('ETF는 TIGER 200(102110), KODEX 200(069500)만 검색 가능')
etf_code = st.text_input('ETF코드를 입력해주세요.')
if st.button('검색'):
    # 전체 내역 조회
    st.write(f'### 1. {stocks[etf_code]}의 보유 종목과 비중이에요.')
    df = conn.query(f'SELECT * from etf_20240521 where etf_code = {etf_code};', ttl=600)
    df = df.loc[:, ['stock_code', 'stock_nm', 'stock_amt', 'evl_amt']]
    df.columns = ['종목코드', '종목명', '보유량', '평가금액']
    st.dataframe(df.sort_values('평가금액', ascending = False))

    # 최근 내역 비교
    df2 = conn.query(f'SELECT * from etf_20240518 where etf_code = {etf_code};', ttl=600)
    df2 = df2.loc[:, ['stock_code', 'stock_nm', 'stock_amt', 'evl_amt']]
    df2.columns = ['종목코드', '종목명', '보유량', '평가금액']
    tmp = df[['종목코드', '종목명', '평가금액']].set_index('종목코드').join(df2[['종목코드', '평가금액']].set_index('종목코드'), 
                                                                             how = 'inner', lsuffix = 'T', rsuffix = 'C')
    tmp['차이'] = tmp['평가금액T'].astype(int) - tmp['평가금액C'].astype(int)
    tmp.columns = ['종목명', '기준일 평가금액', '비교일 평가금액', '차이']

    st.write(f'### 2. {stocks[etf_code]}는 최근 아래 종목의 비중을 늘렸어요.')
    st.dataframe(tmp[tmp['차이'] > 0].sort_values('차이', ascending = False).head(10))

    st.write(f'### 2. {stocks[etf_code]}는 최근 아래 종목의 비중을 줄였어요.')
    st.dataframe(tmp[tmp['차이'] < 0].sort_values('차이', ascending = True).head(10))

    
stock_code = st.text_input('종목코드를 입력해주세요.')
if st.button('종목검색') :
    df = conn.query(f'SELECT * from etf_20240518 where stock_code = {stock_code};', ttl=600)
    st.dataframe(df)
