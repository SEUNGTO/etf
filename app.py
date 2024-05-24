import streamlit as st
import FinanceDataReader as fdr
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import re
from fuzzywuzzy import process

st.set_page_config(
    page_title="ETFace",
    page_icon="😎"
)

# 검색 키워드 입력 받기

if 'search' not in st.session_state :
    st.session_state['search'] = True
if 'etf_code' not in st.session_state :
    st.session_state['etf_code'] = '102110'
if 'search_results' not in st.session_state : 
    st.session_state['search_results'] = ['TIGER 200']
if 'keyword' not in st.session_state :
    st.session_state['keyword'] = 'tiger'

st.title('ETF 관상가')

st.write('검색가능한 ETF')
st.write('- TIGER 200(102110)')
st.write('- KODEX 200(069500)')
st.write('- timefolio K바이오액티브(463050)')
st.write('- Koact 테크핵심소재공급망액티브(482030)')
st.write('- timefolio Kstock 액티브(385720)')


# 검색 키워드 입력 받기

# keyword = 'tiger'
# st.dataframe(codeList)
# st.write(codeList['Name'].tolist())
# st.session_state.search_results = process.extract(keyword, codeList['Name'], limit=50)
# st.session_state.search_results

codeList = fdr.StockListing('ETF/KR')
st.session_state.search_result = codeList['Name'].tolist()
for i in st.session_state.search_result[:5] :
    st.write(i)
stocks = {'102110': 'TIGER200', '069500': 'KODEX 200', '463050': 'timefolio K바이오액티브', '482030': 'Koact 테크핵심소재공급망액티브',
          '385720': 'timefolio Kstock 액티브'}

conn = st.connection('mysql', type='sql')

st.session_state['etf_code'] = st.selectbox("종목명을 검색해주세요", st.session_state.search_results)
st.session_state['eft_code'] = codeList[codeList['Name'] == st.session_state.selected_stock]['Symbol'].values[0]

st.session_state['search'] = st.button(label = '검색')
# etf_code = st.session_state['etf_code']
search = ~st.session_state['search']


if search :
    # 전체 내역 조회
    etf_code = st.session_state['etf_code']
    df = conn.query(f'SELECT * from etf_20240521 where etf_code = {etf_code};', ttl=600)
    price = fdr.DataReader(etf_code, start='2024-04-20', end='2024-05-21').reset_index()
    research = conn.query('SELECT * FROM research', ttl=600)
    research.columns = ['종목명', '종목코드', '리포트 제목', 'nid', '목표가', '의견', '게시일자', '증권사', '링크']
    research['목표가'] = [re.sub('\D', '', t) for t in research['목표가']]
    research = research[research['목표가'] != ""]
    research['목표가'] = research['목표가'].astype(int)
    target = research[['종목코드', '목표가']].groupby('종목코드').mean()
    target.columns = ['목표가(가중평균)']

    df = df.loc[:, ['stock_code', 'stock_nm', 'stock_amt', 'evl_amt']]
    df.columns = ['종목코드', '종목명', '보유량', '평가금액']
    df['비중'] = round(df['평가금액'].astype(int) / df['평가금액'].astype(int).sum() * 100, 2)

    st.write(f'### 1. {stocks[etf_code]}의 보유 종목과 비중이에요.')

    tab1, tab2 = st.tabs(["상위 10개 종목의 비중", "보유 종목과 비중"])
    with tab1:
        ratio = df.sort_values('비중', ascending=False)[['종목명', '비중']].head(10)
        ratio.loc['other', :] = ['기타', 100 - sum(ratio['비중'])]

        fig = px.pie(ratio, values='비중', names='종목명')
        fig.update_layout(template='plotly_white')
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    with tab2:
        tmp = df.set_index('종목코드')
        tmp = tmp.join(target, how='left')

        tmp2 = research[['종목코드', '리포트 제목', '의견', '게시일자', '증권사', '링크']]
        tmp2['게시일자'] = pd.to_datetime(tmp2['게시일자'])
        row = tmp2.groupby('종목코드')['게시일자'].idxmax()
        tmp2 = research.loc[row, ['종목코드', '리포트 제목', '의견', '게시일자', '증권사', '링크']]

        tmp = tmp.join(tmp2.set_index('종목코드'), how='left')
        
        tmp = tmp.reset_index().set_index('종목명')
        
        tmp['목표가(가중평균)'] = round(tmp['목표가(가중평균)'])
        st.dataframe(tmp.drop(['종목코드','보유량','평가금액'], axis = 1).sort_values('비중', ascending=False).rename(columns = {'목표가(가중평균)':'목표가(wAvg)'}), column_config={
            "링크": st.column_config.LinkColumn(display_text='\U0001F517'),
"리포트 제목" : st.column_config.TextColumn(width = 'middle'),
            "증권사" : st.column_config.TextColumn(width = 'small'),
            "게시일자" : st.column_config.TextColumn(width = 'small'),
        "목표가(wAvg)" : st.column_config.NumberColumn(width = "small")})
        st.write('\* wAvg : 가중평균')

    st.write(f'### 2. {stocks[etf_code]}의 최근 한 달 주가 추이에요.')

    fig = go.Figure(data=[go.Candlestick(x=price['Date'],
                                         open=price['Open'],
                                         high=price['High'],
                                         low=price['Low'],
                                         close=price['Close'],
                                         name = f'{stocks[etf_code]}')])
    fig.update_layout(
        xaxis_title='날짜',
        yaxis_title='가격',
        margin={'t': 10, 'b': 10},
        xaxis_rangeslider_visible=False
    )


    tmp3 = df[['종목코드', '평가금액', '보유량']]
    tmp3 = tmp3.set_index('종목코드')
    tmp3 = tmp3.join(target, how='left')
    tmp3['종가'] = tmp3['평가금액']/tmp3['보유량']
    tmp3['목표가(가중평균)'].fillna(tmp3['종가'], inplace = True)
    tmp3['시총'] = tmp3['목표가(가중평균)'] * tmp3['보유량']


    target_PQ = tmp3['시총'].dropna().sum()
    real_PQ = tmp3['평가금액'].dropna().sum()
    idx = real_PQ/target_PQ

    st.metric(label = '리포트 대비 현재 가격', value = f'{idx*100:.2f}', delta = f'{((1/idx)-1) * 100:.2f}% 가능')
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    # 최근 내역 비교
    df2 = conn.query(f'SELECT * from etf_20240518 where etf_code = {etf_code};', ttl=600)
    df2 = df2.loc[:, ['stock_code', 'stock_nm', 'stock_amt', 'evl_amt']]
    df2.columns = ['종목코드', '종목명', '보유량', '평가금액']
    df2['비중'] = df2['평가금액'].astype(int) / df2['평가금액'].astype(int).sum() * 100
    tmp = df[['종목코드', '종목명', '비중']].set_index('종목코드').join(df2[['종목코드', '비중']].set_index('종목코드'),
                                                           how='inner', lsuffix='T', rsuffix='C')
    tmp['차이'] = tmp['비중T'] - tmp['비중C']
    tmp.columns = ['종목명', '기준일 비중', '비교일 비중', '차이']
    tmp.reset_index(inplace=True)
    tmp = tmp.set_index('종목명').drop('종목코드', axis=1)

    st.write(f'### 3. 최근 {stocks[etf_code]}에서 가장 비중이 늘어난 종목들이에요.')
    st.dataframe(tmp[tmp['차이'] > 0].sort_values('차이', ascending=False).head(10), use_container_width=True)

    st.write(f'### 4. 최근 {stocks[etf_code]}에서 가장 비중이 줄어든 종목들이에요.')
    st.dataframe(tmp[tmp['차이'] < 0].sort_values('차이', ascending=True).head(10), use_container_width=True)
