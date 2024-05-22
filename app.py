import streamlit as st
import FinanceDataReader as fdr
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
test = pd.DataFrame({'name' : ['naver'],  'url' : ['https://www.naver.com']})
st.dataframe(test, column_config={
        "url": st.column_config.LinkColumn(display_text = 🔗)
    })
stocks = {'102110' : 'TIGER200', '069500' : 'KODEX 200', '463050' : 'timefolio K바이오액티브', '482030' : 'Koact 테크핵심소재공급망액티브', '385720' : 'timefolio Kstock 액티브'}

conn = st.connection('mysql', type='sql')

st.title('ETF 검색기')
st.write('검색가능한 ETF')
st.write('- TIGER 200(102110)')
st.write('- KODEX 200(069500)')
st.write('- timefolio K바이오액티브(463050)')
st.write('- Koact 테크핵심소재공급망액티브(482030)')
st.write('- timefolio Kstock 액티브(385720)')

etf_code = st.text_input('ETF코드를 입력해주세요.')
if st.button('검색'):
    # 전체 내역 조회
    st.write(f'### 1. {stocks[etf_code]}의 보유 종목과 비중이에요.')
    df = conn.query(f'SELECT * from etf_20240521 where etf_code = {etf_code};', ttl=600)
    df = df.loc[:, ['stock_code', 'stock_nm', 'stock_amt', 'evl_amt']]
    df.columns = ['종목코드', '종목명', '보유량', '평가금액']
    df['비중'] = df['평가금액'].astype(int)/df['평가금액'].astype(int).sum() * 100
    ratio = df.sort_values('비중', ascending = False)[['종목명', '비중']].head(10)
    
    ratio.loc['other', :] = ['기타', 100-sum(ratio['비중'])]
    fig = px.pie(ratio, values = '비중', names = '종목명', title = '상위 10개 종목의 비중')
    fig.update_layout(template='plotly_white')
    st.plotly_chart(fig, use_container_width = True)
    st.dataframe(df.sort_values('평가금액', ascending = False).set_index('종목코드'))

    st.write(f'### 2. {stocks[etf_code]}의 최근 한 달 주가 추이에요.')
    
    plotData = fdr.DataReader(etf_code, start ='2024-04-20', end = '2024-05-22').reset_index()
    
    fig = go.Figure(data=[go.Candlestick(x=plotData['Date'],
                open=plotData['Open'],
                high=plotData['High'],
                low=plotData['Low'],
                close=plotData['Close'])])
    fig.update_layout(
    xaxis_title='날짜',
    yaxis_title='가격',
    margin = {'t' : 10},
    xaxis_rangeslider_visible=False
)
    
    st.plotly_chart(fig, use_container_width=True)
 
    # 최근 내역 비교
    df2 = conn.query(f'SELECT * from etf_20240518 where etf_code = {etf_code};', ttl=600)
    df2 = df2.loc[:, ['stock_code', 'stock_nm', 'stock_amt', 'evl_amt']]
    df2.columns = ['종목코드', '종목명', '보유량', '평가금액']
    df2['비중'] = df2['평가금액'].astype(int)/df2['평가금액'].astype(int).sum()*100
    tmp = df[['종목코드', '종목명', '비중']].set_index('종목코드').join(df2[['종목코드', '비중']].set_index('종목코드'), 
                                                                             how = 'inner', lsuffix = 'T', rsuffix = 'C')
    tmp['차이'] = tmp['비중T'] - tmp['비중C']
    tmp.columns = ['종목명', '기준일 비중', '비교일 비중', '차이']

    st.write(f'### 3. {stocks[etf_code]}는 최근 아래 종목의 비중이 늘었어요.')
    st.dataframe(tmp[tmp['차이'] > 0].sort_values('차이', ascending = False).head(10))

    st.write(f'### 4. {stocks[etf_code]}는 최근 아래 종목의 비중이 줄었어요.')
    st.dataframe(tmp[tmp['차이'] < 0].sort_values('차이', ascending = True).head(10))

    
stock_code = st.text_input('종목코드를 입력해주세요.')
if st.button('종목검색') :
    df = conn.query(f'SELECT * from etf_20240518 where stock_code = {stock_code};', ttl=600)
    st.dataframe(df)
