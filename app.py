from moduler import *
from config import *
st.set_page_config(
    page_title="ETFace",
    page_icon="😎"
)


# session 정의
set_session()

# if 'search' not in st.session_state:
#     st.session_state['search'] = True
# if 'etf_code' not in st.session_state:
#     st.session_state['code'] = '102110'
# if 'etf_name' not in st.session_state:
#     st.session_state['name'] = 'TIGER 200'
# if 'type' not in st.session_state:
#     st.session_state['type'] = 'ETF'

# def code_update(name, codeList) :
#     st.session_state['code'] = codeList[codeList['Name'] == name]['Symbol'].values[0]
#     st.session_state['type'] = codeList[codeList['Name'] == name]['Type'].values[0]


# 기본 변수 세팅
codeList = load_codeList()
etf = pd.DataFrame({'Name' : ['TIGER 200', 'KODEX 200', 'timefolio K바이오액티브', 'Koact 테크핵심소재공급망액티브', 'timefolio Kstock 액티브'],
                    'Symbol' : ['102110', '069500', '463050', '482030', '385720'],
                    'Type' : ['ETF', 'ETF', 'ETF', 'ETF', 'ETF']})
codeList = pd.concat([etf, codeList])

col1, col2 = st.columns(2)
with col2 :
    with st.expander("검색가능한 종목"):
        st.dataframe(codeList.rename(columns = {'Name' : '종목명', 'Symbol' : '종목코드', 'Type' : 'ETF/Stock'}).set_index('종목명'))


st.title('ETF 관상가')

# stocks = {'102110': 'TIGER200', '069500': 'KODEX 200', '463050': 'timefolio K바이오액티브',
#           '482030': 'Koact 테크핵심소재공급망액티브', '385720': 'timefolio Kstock 액티브',
#           '005930' : '삼성전자', '009150' : '삼성전기', '000660' : 'SK하이닉스', '005380' : '현대차', '068270' : '셀트리온'}


col1, col2 = st.columns(2)
with col1 :
    name = st.selectbox("종목명을 검색해주세요", codeList['Name'].tolist(), placeholder = 'ex. 삼성전자, TIGER 200')
    if name :
        code_update(name, codeList)

with col2 :
    st.write(" ") # blank
    st.write(" ") # blank
    st.session_state['search'] = st.button(label = '검색')


search = ~st.session_state['search']
code = st.session_state['code']
type = st.session_state['type']

conn = st.connection('mysql', type='sql')

if search and type == 'ETF':
    # 전체 내역 조회
    
    df = conn.query(f'SELECT * from etf_20240521 where etf_code = {code};', ttl=600)
    price = fdr.DataReader(code, start='2024-04-20', end='2024-05-21').reset_index()
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

    st.write(f'## 1. {name}의 보유 종목과 비중이에요.')

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
        _list = tmp.drop(['종목코드','보유량','평가금액'], axis = 1).sort_values('비중', ascending=False).rename(columns = {'목표가(가중평균)':'목표가(wAvg)'})
        st.dataframe(_list, column_config={
            "링크": st.column_config.LinkColumn(display_text='\U0001F517'),
            "리포트 제목" : st.column_config.TextColumn(width = 'middle'),
            "증권사" : st.column_config.TextColumn(width = 'small'),
            "게시일자" : st.column_config.TextColumn(width = 'small'),
            "목표가(wAvg)" : st.column_config.NumberColumn(width = "small")})
        st.caption('\* wAvg : 가중평균')

    st.write(f'## 2. {name} 10개 종목과 관련된 이야기들이에요.')
    _top10 = ratio.drop('other')['종목명'].tolist()
    _teles = [tele for tele in telegram_dict.keys()]

    for tab, _tele in zip(st.tabs(_teles), _teles) :
        url = telegram_dict[_tele]
        with tab :
            for stocks in _top10 :
                with st.expander(f'{stocks}(비중 : {ratio[ratio["종목명"]==stocks]["비중"].values[0]}%)'):
                    st.write(f'{stocks}와 관련있는 최근 메세지를 가져왔어요. (링크 : [\U0001F517]({url}))')
                    st.caption('※ 메세지를 열어보시려면 오른쪽 끝에 :blue[링크]를 클릭하세요.')
                    st.dataframe(telegram_crawller(url, stocks)
                                 , hide_index=True
                                 , column_config={"링크": st.column_config.LinkColumn(display_text='\U0001F517', width='small'),
                                                  "메세지": st.column_config.TextColumn(width='middle')}
                                 , use_container_width=True
                                 )

    st.write(f'## 3. {name}의 최근 한 달 주가 추이에요.')

    fig = go.Figure(data=[go.Candlestick(
        x=price['Date'].apply(lambda x : x.strftime('%m-%d')),
        open=price['Open'],
        high=price['High'],
        low=price['Low'],
        close=price['Close'],
        name = f'{name}')])

    fig.update_layout(
        xaxis_title='날짜',
        yaxis_title='가격',
        margin={'t': 10, 'b': 10},
        xaxis=dict(type='category', tickangle=45),
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

    col1, col2, col3, col4 = st.columns(4)
    with col1 : 
        st.metric(label = '리포트 대비 현재 가격', value = f'{idx*100:.2f}%', delta = f'{((1/idx)-1) * 100:.2f}% 가능')
    with col2 :
        close = price['Close'].tail(1).values[0]
        high = price['High'].max()
        delta = close - high
        st.metric(label = '종가(고점 대비)', value = f'{close:,}',  delta = f'{delta:,}')
    with col3 :
        high = price['High'].max()
        low = price['Low'].min()
        delta = high - low
        st.metric(label = '최고점(저점 대비)', value = f'{high:,}', delta = f'{delta:,}')
        
    
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    # 최근 내역 비교
    df2 = conn.query(f'SELECT * from etf_20240518 where etf_code = {code};', ttl=600)
    df2 = df2.loc[:, ['stock_code', 'stock_nm', 'stock_amt', 'evl_amt']]
    df2.columns = ['종목코드', '종목명', '보유량', '평가금액']
    df2['비중'] = round(df2['평가금액'].astype(int) / df2['평가금액'].astype(int).sum() * 100, 2)
    tmp = df[['종목코드', '종목명', '비중']].set_index('종목코드').join(df2[['종목코드', '비중']].set_index('종목코드'),
                                                           how='inner', lsuffix='T', rsuffix='C')
    tmp['차이'] = tmp['비중T'] - tmp['비중C']
    tmp.columns = ['종목명', '기준일 비중', '비교일 비중', '차이']
    tmp.reset_index(inplace=True)
    tmp = tmp.set_index('종목명').drop('종목코드', axis=1)


    st.write(f'## 4. 📈 최근 {name}에서 가장 비중이 늘어난 종목들이에요.')
    increase = tmp[tmp['차이'] > 0].sort_values('차이', ascending=False)
    st.dataframe(increase.head(10), use_container_width=True)

    st.write(f'## 5. 📉 최근 {name}에서 가장 비중이 줄어든 종목들이에요')
    decrease = tmp[tmp['차이'] < 0].sort_values('차이', ascending=True)
    st.dataframe(decrease.head(10), use_container_width=True)


elif search and type == 'Stock' :

    df = conn.query(f'SELECT * from etf_20240521 where stock_code = {code};', ttl=600)
    df = df.loc[:, ['etf_code','stock_code', 'stock_nm', 'stock_amt', 'evl_amt']]
    df.columns = ['ETF코드','종목코드', '종목명', '보유량', '평가금액']
    df['비중'] = round(df['평가금액'].astype(int) / df['평가금액'].astype(int).sum() * 100, 2)


    price = fdr.DataReader(code, start='2024-04-20', end='2024-05-21').reset_index()

    research = conn.query(f'SELECT * FROM research where code = {code} ', ttl=600)
    research.columns = ['종목명', '종목코드', '리포트 제목', 'nid', '목표가', '의견', '게시일자', '증권사', '링크']
    research['목표가'] = [re.sub('\D', '', t) for t in research['목표가']]
    research = research[research['목표가'] != ""]
    research['목표가'] = research['목표가'].astype(int)
    target = research[['종목코드', '목표가']].groupby('종목코드').mean()
    target.columns = ['목표가(가중평균)']

    st.write(f'## 1. {name}에 대해 이런 이야기들이 있어요.')

    tab1, tab2, tab3, tab4 = st.tabs(['증권사 리포트', '뉴스', '텔레그램', '유튜브(예정)'])

    with tab1 :
        if research.shape[0] > 0 : 
            tmp = research.set_index('종목명').drop(['종목코드', 'nid'], axis = 1).sort_values('게시일자', ascending = False)
            st.write(f' 총 **{len(tmp["목표가"])}**개의 리포트가 있어요.')

            st.write(f' 증권사의 평균 목표가는 **{tmp["목표가"].mean():,.0f}**원이에요.')
            st.write(f'- 가장 높은 목표가는 {tmp[tmp["목표가"] == tmp["목표가"].max()]["증권사"].values[0]}의 {tmp["목표가"].max():,.0f}원이에요.')
            st.write(f'- 가장 낮은 목표가는 {tmp[tmp["목표가"] == tmp["목표가"].min()]["증권사"].values[0]}의 {tmp["목표가"].min():,.0f}원이에요.')
            st.dataframe(tmp.reset_index(drop=True),
                         column_config= {'링크' : st.column_config.LinkColumn(display_text='\U0001F517')},
                         use_container_width=True,
hide_index = True)
        else : st.error('증권사 리포트가 없어요.')
    with tab2 :

        st.write(f'**네이버 뉴스**에서 방금 {name}를 검색한 결과에요.')

        url = f'https://openapi.naver.com/v1/search/news.json'
        params = {'query' : name,
                  'display' : '50'}
        headers = {
            'X-Naver-Client-Id' : st.secrets["clientid"],
            'X-Naver-Client-Secret' : st.secrets["clientsecret"]}

        response = requests.get(url, params = params, headers = headers)
        newsData = pd.DataFrame(response.json()['items'])[['title', 'pubDate', 'link']]

        newsData['title'] = newsData['title'].apply(lambda x : x.replace('<b>', '').replace('</b>', ''))
        newsData['pubDate'] = pd.to_datetime(newsData['pubDate'])
        newsData['pubDate'] = newsData['pubDate'].apply(lambda x : x.strftime('%Y-%m-%d'))

        newsData.columns = ['기사 제목', '날짜', '링크']

        st.dataframe(newsData,
                     hide_index = True,
                     column_config = {"링크": st.column_config.LinkColumn(display_text='\U0001F517')})

    with tab3 :

        for telegram, url in telegram_dict.items() :

            with st.expander(f'{telegram}') :
                st.write(f'##### {name}와 관련있는 최근 메세지를 가져왔어요. (링크 : [\U0001F517]({url}))')
                st.caption('※ 메세지를 열어보시려면 오른쪽 끝에 :blue[링크]를 클릭하세요.')
                st.dataframe(telegram_crawller(url, name)
                             , hide_index=True
                             ,column_config={"링크": st.column_config.LinkColumn(display_text='\U0001F517', width = 'small'),
                                            "메세지" : st.column_config.TextColumn(width = 'middle')}
                             ,use_container_width = True
                             )


    with tab4 :
        st.info('🚧업데이트 중이에요.')

    st.write(f'## 2. {name}의 최근 한 달 주가 추이에요.')

    fig = go.Figure(data=[go.Candlestick(
        x=price['Date'].apply(lambda x : x.strftime('%m-%d')),
        open=price['Open'],
        high=price['High'],
        low=price['Low'],
        close=price['Close'],
        name = f'{name}')])

    fig.update_layout(
        xaxis_title='날짜',
        yaxis_title='가격',
        margin={'t': 10, 'b': 10},
        xaxis=dict(type='category', tickangle=45),
        xaxis_rangeslider_visible=False
    )


    tmp3 = df[['종목코드', '평가금액', '보유량']]
    tmp3 = tmp3.set_index('종목코드')
    tmp3 = tmp3.join(target, how='left')
    tmp3['종가'] = tmp3['평가금액']/tmp3['보유량']
    tmp3['목표가(가중평균)'].fillna(tmp3['종가'], inplace = True)
    tmp3['시총'] = tmp3['목표가(가중평균)'] * tmp3['보유량']

    close = price['Close'].tail(1).values[0]
    highest = high = price['High'].max()
    target = research['목표가'].mean()
    ma = price['Close'].mean()


    idx = close/target

    col1, col2, col3, col4 = st.columns(4)
    with col1 :
        if target > 0 :
            st.metric(label = '리포트 대비 현재 가격', value = f'{idx*100:.2f}%', delta = f'{((1/idx)-1) * 100:.2f}% 가능')
        else :
            st.metric(label='평균 대비 현재 가격', value = f'{close/ma*100:,.2f}%', help = '리포트가 없어 평균가격으로 대체했어요.')

    with col2 :
        st.metric(label='평균 가격(종가대비)', value=f'{ma:,.0f}', delta = f'{ma-close:,.0f}')

    with col3 :
        delta = close - highest
        st.metric(label = '종가(고점 대비)', value = f'{close:,}',  delta = f'{delta:,}')
    with col4 :
        high = price['High'].max()
        low = price['Low'].min()
        delta = high - low
        st.metric(label = '최고점(저점 대비)', value = f'{highest:,}', delta = f'{delta:,}')
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)




    ########### 비중 늘리고 줄인 ETF 계산 ##################
    df2 = conn.query(f'SELECT * from etf_20240518 where stock_code = {code};', ttl=600)
    df2 = df2.loc[:, ['etf_code', 'stock_code', 'stock_nm', 'stock_amt', 'evl_amt']]
    df2.columns = ['ETF코드', '종목코드', '종목명', '보유량', '평가금액']
    df2['비중'] = round(df2['평가금액'].astype(int) / df2['평가금액'].astype(int).sum() * 100, 2)

    tmp = df[['ETF코드', '종목명', '비중']].set_index('ETF코드').join(df2[['ETF코드', '비중']].set_index('ETF코드'),
                                                           how='inner', lsuffix='T', rsuffix='C')
    tmp['차이'] = tmp['비중T'] - tmp['비중C']
    tmp = tmp.join(codeList[['Name', 'Symbol']].rename(columns = {'Symbol' : 'ETF코드', 'Name' : 'ETF'}).set_index('ETF코드'), how = 'inner')

    tmp.columns = ['종목명', '기준일 비중', '비교일 비중', '차이', 'ETF']
    tmp.reset_index(inplace=True, drop=True)
    tmp = tmp.drop('종목명', axis = 1)
    tmp = tmp.set_index('ETF')

    with st.expander('※ 수정 예정 사항(24.5.25.)') :
        st.write(f'{name}를 포함한 애들끼리만 모아서 비중을 계산해서 오류 있음(df1, df2 모두)')
        st.write(f'DB 내에 미리 비중을 계산해두어야 함')
        st.dataframe(tmp)

    # DB 변경 이후에 수정해야 함

    st.write(f'## 3. 최근 {name}에 관심을 갖고 있는 ETF들이에요.')
    st.write(f'### 📈 {name}의 비중이 높은 ETF들이에요.')
    total = df.set_index('ETF코드').join(codeList[['Name', 'Symbol']].rename(columns = {'Symbol' : 'ETF코드', 'Name' : 'ETF'}).set_index('ETF코드'), how = 'inner')
    total = total.drop(['종목코드', '종목명'], axis = 1)
    total.reset_index(inplace = True, drop = True)
    total = total.set_index('ETF')
    st.dataframe(total.head(10).sort_values('비중', ascending = False))
    

    col1, col2 = st.columns(2)
    with col1 :
        st.write(f'### 📈 최근 비중을 늘렸어요.')
        increase = tmp[tmp['차이'] > 0].sort_values('차이', ascending=False)
        st.write(f'**총 {len(increase)}개**의 ETF에서 {name}의 비중을 늘렸어요.')
        st.dataframe(increase.head(10), use_container_width=True)

    with col2 :

        st.write(f'### 📉 최근 비중을 줄였어요.')

        decrease = tmp[tmp['차이'] > 0].sort_values('차이', ascending=False).head(10)
        st.write(f'**총 {len(decrease)}개**의 ETF에서 {name}의 비중을 줄였어요.')
        st.dataframe(decrease.head(10), use_container_width=True,)


    col3, col4 = st.columns(2)
    with col3 :
        st.write(f'### 🆕 새로 포트폴리오에 넣었어요.')

        new = pd.DataFrame({'ETF' : ['KODEX 200', 'TIGER 200', 'HANARO 200'],
                            '보유 비중' : [20.00, 30.00, 10.00],
                            '매수 금액' : [50000, 20000, 5000]})
        new = new.set_index('ETF')

        st.write(f'**총 {len(new)}개의 ETF**에서 {name}를 처음으로 담았어요.')

        st.write(f'- 평균적으로 **{new["매수 금액"].mean():,.0f}**원만큼 샀어요.')
        st.write(f'- 가장 크게 비중을 늘린 ETF는 **{new["보유 비중"].max():,.2f}**%만큼 늘린 **{new.index[new["보유 비중"].argmax()]}**이에요.')
        st.write(f'- 가장 큰 금액을 산 ETF는 **{new["매수 금액"].max():,.0f}**원을 매수한 **{new.index[new["매수 금액"].argmax()]}**이에요.')

        new.loc['평균', :] = new.mean()

        st.dataframe(new, use_container_width=True)


    with col4 :

        st.write(f'### ❎ 포트폴리오에서 제외했어요.')
        drop = pd.DataFrame({'ETF' : ['timefolio', 'HANARO 200'],
                            '원래 비중' : [20.00, 30.00],
                            '매도 금액' : [10000, 20000]})
        drop = drop.set_index('ETF')

        st.write(f'**총 {len(drop)}개의 ETF**에서 {name}를 모두 정리했어요.')
        st.write(f'- 평균 **{drop["매도 금액"].mean():,.0f}**원만큼 팔았어요.')
        st.write(f'- 가장 크게 비중을 줄인 ETF는 **{drop["원래 비중"].max():,.2f}**%의 비중을 정리한 **{drop.index[drop["원래 비중"].argmax()]}**이에요.')
        st.write(f'- 가장 큰 금액을 판 ETF는 **{drop["매도 금액"].max():,.0f}**원을 매도한 **{drop.index[drop["매도 금액"].argmax()]}**이에요.')

        drop.loc['평균', :] = drop.mean()
        st.dataframe(drop, use_container_width=True)

