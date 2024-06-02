from config import *
from moduler import *


st.set_page_config(
    page_title="ETFace",
    page_icon="😎"
)


# session 정의
set_session()

# 기본 변수 세팅
codeList = load_codeList() # 종목코드 리스팅

# 시간 변수
tz = pytz.timezone('Asia/Seoul')
now = datetime.now(tz)
today = now.strftime('%Y-%m-%d')
one_month_ago = now - timedelta(days = 90) # 사실은 3달 전
one_month_ago = one_month_ago.strftime('%Y-%m-%d')

# Main UI
st.title('ETF 관상가')

name = search_bar(codeList)

search = ~st.session_state['search']
code = st.session_state['code']
type = st.session_state['type']

if search and type == 'ETF':
    # 전체 내역 조회
    df = load_etf_data('new', code)  
    df['비중'] = round(df['비중'], 2)
    

    price = fdr.DataReader(code, start=one_month_ago, end=today).reset_index()

    research = load_research()
    research['목표가'] = [re.sub('\D', '', v) if v is not None else '' for v in research['목표가']]
    ind = research['목표가'] == ""
    research.loc[ind, '목표가'] = np.nan
    research['목표가'] = research['목표가'].astype(float)
    research = research[research['종목코드'].isin(df['종목코드'])]
    target = research[['종목코드', '목표가']].groupby('종목코드').mean()
    target.columns = ['목표가(가중평균)']

    # 재무제표
    with st.expander(f'🧾 {name}의 가상 재무제표'):

        st.write(f'**{name}**이 보유한 종목들의 지분률을 감안해서 재무제표를 작성했어요.')
        st.write(f'- [참고] 종목들의 평가금액을 합치면 {df["평가금액"].sum():,.0f}원이에요.')

        url = 'https://raw.githubusercontent.com/SEUNGTO/ETFdata/main/fs.json'
        fs = pd.DataFrame(requests.get(url).json())
        fs = fs.loc[fs['종목코드'].isin(df['종목코드']), : ]
        fs = fs.set_index('종목코드').join(df.set_index('종목코드')['보유량'])
        for col in fs.columns :
            fs[col] *= fs['보유량']
        fs = fs.reset_index(drop = True).drop('보유량', axis = 1).sum()
        
        fs.index.name = '계정명'
        # fs.columns = ['금액']
        balance = round(fs[['자산총계', '유동자산', '부채총계', '유동부채', '비유동부채', '자본총계', '자본금', '이익잉여금']], 0)
        income = round(fs[['매출액', '영업이익', '영업비용', '이자비용','당기순이익', '총포괄손익']], 0)
        col1, col2 = st.columns(2)
        with col1 :
            st.write(f'📊 {name}의 재무상태표')
            st.dataframe(balance, use_container_width=True)
        with col2 :
            st.write(f'💰 {name}의 손익계산서')
            st.dataframe(income, use_container_width=True)

            st.caption('※ 금융업은 제외')

    st.write(f'## 1. {name}의 보유 종목과 비중이에요.')

    tab1, tab2 = st.tabs(["상위 10개 종목의 비중", "보유 종목별 주요 리포트"])

    with tab1:
        ratio = df.sort_values('비중', ascending=False)[['종목명', '비중']].head(10)
        ratio.loc['other', :] = ['기타', 100 - sum(ratio['비중'].astype(float))]

        fig = px.pie(ratio, values='비중', names='종목명')
        fig.update_layout(template='plotly_white'
                          , margin={'t': 10, 'b': 5})
        st.plotly_chart(fig
                        , theme="streamlit"
                        , use_container_width=True)
        with st.expander(f'{name}의 보유종목 한 눈에 보기') :
            st.dataframe(df[['종목명', '비중', '평가금액']].sort_values('비중', ascending=False)
                        ,hide_index = True
                        ,use_container_width=True)


    with tab2:
        tmp = df.set_index('종목코드')
        tmp = tmp.join(target, how='left')

        tmp2 = research[['종목코드', '리포트 제목', '의견', '게시일자', '증권사', '링크', 'nid']]
        row = tmp2.groupby('종목코드')['nid'].idxmax()
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

    st.write(f'## 2. {name}의 상위 5개 종목과 관련된 이야기들이에요.')

    with st.spinner('🔍텔레그램 채널을 돌아다니며 정보를 모으고 있어요.') :

        _topList = ratio.head(5)['종목명'].tolist()
        _teles = [tele for tele in telegram_dict.keys()]

        for tab, _tele in zip(st.tabs(_teles), _teles) :
            url = telegram_dict[_tele]
            with tab :
                for stocks in _topList :
                    with st.expander(f'{stocks}(비중 : {ratio[ratio["종목명"]==stocks]["비중"].values[0]}%)'):
                        st.write(f'{stocks}와 관련있는 최근 메세지를 가져왔어요. (링크 : [\U0001F517]({url}))')
                        st.caption('※ 메세지를 열어보시려면 오른쪽 끝에 :blue[링크]를 클릭하세요.')
                        st.dataframe(telegram_crawller(url, stocks)
                                     , hide_index=True
                                     , column_config={"링크": st.column_config.LinkColumn(display_text='\U0001F517', width='small'),
                                                      "메세지": st.column_config.TextColumn(width='middle')}
                                     , use_container_width=True
                                     )
    st.success('텔레그램 채널에서 정보를 모두 모아왔어요.')

    st.write(f'## 3. {name}의 최근 세 달간의 주가 추이에요.')

    fig = go.Figure(data=[go.Candlestick(
        x=price['Date'].apply(lambda x : x.strftime('%m-%d')),
        open=price['Open'],
        high=price['High'],
        low=price['Low'],
        close=price['Close'],
        name = f'{name}')])

    etf_target = None
    etf_target = load_etf_target_price(code)

    stock_min_period = min(price['Date'].apply(lambda x : x.strftime('%Y-%m-%d')))
    cutoff_date = max(one_month_ago, stock_min_period)

    if etf_target is not None :
        etf_target = etf_target[etf_target.index >= cutoff_date]
        fig.add_trace(go.Scatter(
                x = [idx[-5:] for idx in etf_target.index],
                y = standardize(etf_target).values,
                mode='lines', 
                name='목표가', 
                yaxis='y2',
                line=dict(dash='dash', color = 'black')
            ))
    
    fig.update_layout(
        xaxis_title='날짜',
        xaxis=dict(type='category', tickangle=45),
        yaxis = dict(title = f'{name}'),
        yaxis2 = dict(title = '목표가', overlaying = 'y', side = 'right'),
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
    df2 = load_etf_data('old', code)
    df2['비중'] = round(df2['비중'], 2)

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

    st.write(f'## 6. 📉 {name}와 유사한 종목들이에요.')
    similar_etf = None
    similar_etf = load_similar_etf(code)
    if similar_etf is not None : 
        col1, col2 = st.columns(2)
        with col1 :
            with st.container(border = True):
                st.write(f'### {name}')
                ratio = df.sort_values('비중', ascending=False)[['종목명', '비중']].head(10)
                ratio.loc['other', :] = ['기타', 100 - sum(ratio['비중'].astype(float))]
                fig = px.pie(ratio, values='비중', names='종목명')
                fig.update_layout(template='plotly_white'
                                  , margin={'t': 10, 'b': 5})
                st.plotly_chart(fig
                                , theme="streamlit"
                                , use_container_width=True)
                with st.expander(f'{name}의 보유종목 한 눈에 보기') :
                    st.dataframe(df[['종목명', '비중', '평가금액']].sort_values('비중', ascending=False)
                                ,hide_index = True
                                ,use_container_width=True)
        with col2 :
            with st.container(border = True):
                comp_nm_list = [codeList.loc[codeList['Symbol'] == comp_code, "Name"].values[0] for comp_code in similar_etf]
                for tab, comp_code in zip(st.tabs(comp_nm_list), similar_etf) :
                    with tab :
                        comp_df = load_etf_data('new', comp_code)  
                        comp_df['비중'] = round(comp_df['비중'], 2)
                        comp_ratio = comp_df.sort_values('비중', ascending=False)[['종목명', '비중']].head(10)
                        comp_ratio.loc['other', :] = ['기타', 100 - sum(comp_ratio['비중'].astype(float))]
        
                        fig = px.pie(comp_ratio, values='비중', names='종목명')
                        fig.update_layout(template='plotly_white'
                                          , margin={'t': 10, 'b': 5})
                        st.plotly_chart(fig
                                        , theme="streamlit"
                                        , use_container_width=True)
                        with st.expander(f'보유종목 한 눈에 보기') :
                            st.dataframe(comp_df[['종목명', '비중', '평가금액']].sort_values('비중', ascending=False)
                                        ,hide_index = True
                                        ,use_container_width=True)
    else  : 
        st.error('유사한 ETF를 찾을 수 없어요.')

                
    
    with st.expander('모든 ETF종목 비교') :
        entire = merge_data(type_dict)
        st.dataframe(entire)



elif search and type == 'Stock' :

    df = load_stock_data('new', code)
    df['비중'] = round(df['비중'], 2)

    price = fdr.DataReader(code, start=one_month_ago, end=today).reset_index()

    research = load_research()
    research['목표가'] = [re.sub('\D', '', v) if v is not None else '' for v in research['목표가']]
    ind = research['목표가'] == ""
    research.loc[ind, '목표가'] = np.nan
    research['목표가'] = research['목표가'].astype(float)
    research = research[research['종목코드'].isin([code])]
    target = research[['종목코드', '목표가']].groupby('종목코드').mean()
    target.columns = ['목표가(가중평균)']

    st.write(f'## 1. {name}에 대해 이런 이야기들이 있어요.')

    tab1, tab2, tab3, tab4 = st.tabs(['증권사 리포트', '뉴스', '텔레그램', '유튜브(예정)'])

    with tab1 :
        if research.shape[0] > 0 : 
            
            tmp = research.set_index('종목명').drop(['종목코드', 'nid'], axis = 1).sort_values('게시일자', ascending = False)
            st.write(f' 최근 6개월동안, 총 **{len(tmp["목표가"])}**개의 리포트가 나왔어요.')

            if tmp["목표가"].mean() is not np.nan : 
                st.write(f' 증권사의 평균 목표가는 **{tmp["목표가"].mean():,.0f}**원이에요.')
                st.write(f'- 가장 높은 목표가는 {tmp[tmp["목표가"] == tmp["목표가"].max()]["증권사"].values[0]}의 {tmp["목표가"].max():,.0f}원이에요.')
                st.write(f'- 가장 낮은 목표가는 {tmp[tmp["목표가"] == tmp["목표가"].min()]["증권사"].values[0]}의 {tmp["목표가"].min():,.0f}원이에요.')
            st.dataframe(tmp.reset_index(drop=True),
                         column_config= {'링크' : st.column_config.LinkColumn(display_text='\U0001F517')},
                         use_container_width=True,
                         hide_index = True)
        else : st.error('증권사 리포트가 없어요.')

    with tab2 :

        try :

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

            st.write(f'**네이버 뉴스**에서 방금 {name}를 검색한 결과에요.')
            st.dataframe(newsData,
                         hide_index = True,
                         column_config = {"링크": st.column_config.LinkColumn(display_text='\U0001F517')})
        except :
            st.error('검색된 뉴스가 없어요.')

    with tab3 :

        with st.spinner('🔍텔레그램 채널을 돌아다니며 정보를 모으고 있어요.') :

            for telegram, url in telegram_dict.items() :

                try :
                    with st.expander(f'{telegram}') :
                        tele = telegram_crawller(url, name)
                        st.write(f'##### {name}와 관련있는 최근 메세지를 가져왔어요. (링크 : [\U0001F517]({url}))')
                        st.caption('※ 메세지를 열어보시려면 오른쪽 끝에 :blue[링크]를 클릭하세요.')
                        st.dataframe(tele
                                     , hide_index=True
                                     ,column_config={"링크": st.column_config.LinkColumn(display_text='\U0001F517', width = 'small'),
                                                    "메세지" : st.column_config.TextColumn(width = 'middle')}
                                     ,use_container_width = True
                                     )
                except :
                    with st.expander(f'{telegram}'):
                        st.error('검색된 내용이 없어요')

        st.success('텔레그램 채널에서 정보를 모두 모아왔어요.')


    with tab4 :
        st.info('🚧업데이트 중이에요.')


    st.write(f'## 2. {name}의 최근 세 달 주가 추이에요.')

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
        margin={'t': 10, 'b': 10, 'l' : 0, 'r': 0},
        xaxis=dict(type='category', tickangle=45),
        xaxis_rangeslider_visible=False
    )
    
    fig.update_layout(yaxis2=dict(title='목표가', overlaying='y', side='right'))
    ewm_data = load_ewm_data()
    
    if code in ewm_data.keys() : 
        ewm_data = pd.Series(pd.Series(ewm_data[code]).values, index = pd.Series(ewm_data['Date']))
        ewm_data = ewm_data[ewm_data.index >= one_month_ago]

        fig.add_trace(go.Scatter(
            x = [idx[-5:] for idx in ewm_data.index],
            y = standardize(ewm_data).values,
            mode='lines', 
            name='목표가', 
            yaxis='y2',
            line=dict(dash='dash', color = 'black')
        ))


    tmp3 = df[['종목코드', '평가금액', '보유량']]
    tmp3 = tmp3.set_index('종목코드')
    tmp3 = tmp3.join(target, how='left')
    tmp3['종가'] = tmp3['평가금액']/tmp3['보유량']
    tmp3['목표가(가중평균)'].fillna(tmp3['종가'], inplace = True)
    tmp3['시총'] = tmp3['목표가(가중평균)'] * tmp3['보유량']

    close = price['Close'].tail(1).values[0]
    highest = price['High'].max()
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
        
        low = price['Low'].min()
        delta = highest - low
        st.metric(label = '최고점(저점 대비)', value = f'{highest:,}', delta = f'{delta:,}')

    st.plotly_chart(fig, theme="streamlit", use_container_width=True)


    ########### 비중 늘리고 줄인 ETF 계산 ##################
    df2 = load_stock_data('old', code)
    df2['종목코드'] = code
    df2['비중'] = round(df2['비중'], 2)


    tmp = df[['ETF코드', '종목명', '비중']].set_index('ETF코드').join(df2[['ETF코드', '비중']].set_index('ETF코드'),
                                                           how='left', lsuffix='T', rsuffix='C')
    tmp['차이'] = tmp['비중T'].astype(float) - tmp['비중C'].astype(float)
    tmp['차이'] = round(tmp['차이'].astype(float), 2)
    tmp['비중T'] = round(tmp['비중T'].astype(float), 2)
    tmp['비중C'] = round(tmp['비중C'].astype(float), 2)
    tmp = tmp.join(codeList[['Name', 'Symbol']].rename(columns = {'Symbol' : 'ETF코드', 'Name' : 'ETF'}).set_index('ETF코드'), how = 'inner')

    tmp.columns = ['종목명', '기준일 비중', '비교일 비중', '차이', 'ETF']
    tmp.reset_index(inplace=True, drop=True)
    tmp = tmp.drop('종목명', axis = 1)
    tmp = tmp.set_index('ETF')

    # DB 변경 이후에 수정해야 함

    st.write(f'## 3. 최근 {name}에 관심을 갖고 있는 ETF들이에요.')
    st.write(f'### 📈 {name}의 비중이 높은 ETF들이에요.')
    total = df.set_index('ETF코드').join(codeList[['Name', 'Symbol']].rename(columns = {'Symbol' : 'ETF코드', 'Name' : 'ETF'}).set_index('ETF코드'), how = 'left')
    total = total.drop(['종목코드', '종목명'], axis = 1)
    total = total.dropna()
    total['비중'] = round(total['비중'].astype(float), 2)
    total.reset_index(inplace = True, drop = True)
    total = total.set_index('ETF')
    st.dataframe(total.reset_index().sort_values('비중', ascending = False).head(10)
                 , use_container_width=True
                ,hide_index = True)

    col1, col2 = st.columns(2)

    with col1 :
        st.write(f'### 📈 최근 비중을 늘렸어요.')
        increase = tmp[tmp['차이'] > 0].sort_values('차이', ascending=False)
        st.write(f'**총 {len(increase)}개**의 ETF에서 {name}의 비중을 늘렸어요.')
        st.dataframe(increase.head(10).reset_index(),
                     use_container_width=True,
                     hide_index=True
                     )

    with col2 :

        st.write(f'### 📉 최근 비중을 줄였어요.')

        decrease = tmp[tmp['차이'] < 0].sort_values('차이', ascending=True).head(10)
        st.write(f'**총 {len(decrease)}개**의 ETF에서 {name}의 비중을 줄였어요.')
        st.dataframe(decrease.head(10).reset_index(),
                     use_container_width=True,
                     hide_index=True)



    col3, col4 = st.columns(2)
    with col3 :

        st.write(f'### 🆕 포트폴리오에 추가했어요.')

        new = None
        new = tmp[tmp.fillna(0)['비교일 비중'] == 0]
        new.fillna(0, inplace = True)

        if new.shape[0] == 0 or new is None : 
            st.info(f'{name}을 새롭게 추가한 ETF는 없어요.')

        elif new.shape[0] != 0 or new is not None:

            st.write(f'**총 {len(new)}개의 ETF**에서 {name}를 처음으로 담았어요.')

            # st.write(f'- 평균적으로 **{new["매수 금액"].mean():,.0f}**원만큼 샀어요.')
            # st.write(f'- 가장 크게 비중을 늘린 ETF는 **{new["보유 비중"].max():,.2f}**%만큼 늘린 **{new.index[new["보유 비중"].argmax()]}**이에요.')
            # st.write(f'- 가장 큰 금액을 산 ETF는 **{new["매수 금액"].max():,.0f}**원을 매수한 **{new.index[new["매수 금액"].argmax()]}**이에요.')

            # new.loc['평균', :] = new.mean()
            new['차이'] = new['기준일 비중'] - new['비교일 비중']
            st.dataframe(new.reset_index(), 
                         use_container_width=True,
                        hide_index = True)
        


    with col4 :

        st.write(f'### ❎ 포트폴리오에서 제외했어요.')

        drop = None
        drop = tmp[tmp.fillna(0)['기준일 비중'] == 0]
        drop.fillna(0, inplace = True)

        if drop.shape[0] == 0 or drop is None :
            st.info(f'{name}을 모두 정리한 ETF는 없어요.')
        elif drop.shape[0] != 0 or drop is not None :

            st.write(f'**총 {len(drop)}개의 ETF**에서 {name}를 모두 정리했어요.')

            # st.write(f'- 평균 **{drop["매도 금액"].mean():,.0f}**원만큼 팔았어요.')
            # st.write(f'- 가장 크게 비중을 줄인 ETF는 **{drop["원래 비중"].max():,.2f}**%의 비중을 정리한 **{drop.index[drop["원래 비중"].argmax()]}**이에요.')
            # st.write(f'- 가장 큰 금액을 판 ETF는 **{drop["매도 금액"].max():,.0f}**원을 매도한 **{drop.index[drop["매도 금액"].argmax()]}**이에요.')
            # drop.loc['평균', :] = drop.mean()

            drop['차이'] = drop['기준일 비중'] - drop['비교일 비중']
            st.dataframe(drop.reset_index(), 
                         use_container_width=True,
                        hide_index = True)
