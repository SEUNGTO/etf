import streamlit as st
import FinanceDataReader as fdr
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import requests
import re
from bs4 import BeautifulSoup
import time

def load_etf_data(type) :
    if type == 'old' :
        url = 'https://raw.githubusercontent.com/SEUNGTO/ETFdata/main/old_data.json'
    elif type == 'new' :
        url = 'https://raw.githubusercontent.com/SEUNGTO/ETFdata/main/new_data.json'
    tmp = requests.get(url)
    return pd.DataFrame(tmp.json(), dtype = str)


def telegram_crawller(url, keyword) :
    telegram_msgs = {
        'msg': []
        , 'date': []
        , 'time': []
        , 'view': []
        , 'link': []
    }
    query = f'{url}?q={keyword}'
    response = requests.get(query)
    soup = BeautifulSoup(response.content, 'html.parser')

    for msg in soup.find_all('div', class_='tgme_widget_message_bubble'):

        msg.find('a').decompose()
        _view = msg.find('span', class_='tgme_widget_message_views').text

        try:
            _msg = msg.find('div', class_='tgme_widget_message_text js-message_text').text

            datetime = pd.to_datetime(msg.find('time', class_='time').attrs['datetime'])
            datetime = datetime.tz_convert('Asia/Seoul')
            _date = datetime.strftime('%Y-%m-%d')
            _time = datetime.strftime('%H:%M')

            telegram_msgs['msg'].append(_msg)
            telegram_msgs['date'].append(_date)
            telegram_msgs['time'].append(_time)
            telegram_msgs['view'].append(_view)

        except:
            _msg = '(메세지없이 링크만 있어요.)'
            telegram_msgs['msg'].append(_msg)
            telegram_msgs['date'].append("-")
            telegram_msgs['time'].append("-")
            telegram_msgs['view'].append(_view)

    for uu in soup.find_all('a', class_='tgme_widget_message_date'):
        _link = uu.attrs['href']
        telegram_msgs['link'].append(_link)

    telegram_msgs = pd.DataFrame(telegram_msgs)
    telegram_msgs.columns = ['메세지', '일자', '시간', '조회수', '링크']
    telegram_msgs.sort_values(by=['일자', '시간'], ascending=[False, False], inplace=True)
    return telegram_msgs

def code_update(name, codeList) :
    st.session_state['code'] = codeList[codeList['Name'] == name]['Symbol'].values[0]
    st.session_state['type'] = codeList[codeList['Name'] == name]['Type'].values[0]

@st.cache_data
def load_codeList() :
    url = 'https://raw.githubusercontent.com/SEUNGTO/botdata/main/ETFcodeList.json'
    data = pd.DataFrame(requests.get(url).json())
    data.columns = ['Name', 'Symbol', 'Type']

    etf = pd.DataFrame(
        {'Name': ['TIGER 200', 'KODEX 200', 'timefolio K바이오액티브', 'Koact 테크핵심소재공급망액티브', 'timefolio Kstock 액티브'],
         'Symbol': ['102110', '069500', '463050', '482030', '385720'],
         'Type': ['ETF', 'ETF', 'ETF', 'ETF', 'ETF']})

    return pd.concat([etf, data])

def search_bar(codeList) :
    col1, col2 = st.columns(2)
    with col1 :
        name = st.selectbox("종목명을 검색해주세요", codeList['Name'].tolist(), placeholder = 'ex. 삼성전자, TIGER 200')
        if name :
            code_update(name, codeList)

    with col2 :
        st.write(" ") # blank
        st.write(" ") # blank
        st.session_state['search'] = st.button(label = '검색')

    return name



url = 'https://t.me/s/FastStockNews'
keyword = '삼성전자'
telegram_msgs = {
    'msg' : []
    , 'date' : []
    , 'time' : []
    , 'view' : []
    , 'link' : []
}
query = f'{url}?q={keyword}'
response = requests.get(query)
soup = BeautifulSoup(response.content, 'html.parser')
msgs = soup.find_all('div', class_='tgme_widget_message_bubble')
msg = msgs[19]
msg.find('span', class_ = 'tgme_widget_message_views').text

for msg in soup.find_all('div', class_='tgme_widget_message_bubble'):

    msg.find('a').decompose()
    _view = msg.find('span', class_='tgme_widget_message_views').text

    try:
        _msg = msg.find('div', class_='tgme_widget_message_text js-message_text').text

        datetime = pd.to_datetime(msg.find('time', class_='time').attrs['datetime'])
        datetime = datetime.tz_convert('Asia/Seoul')
        _date = datetime.strftime('%Y-%m-%d')
        _time = datetime.strftime('%H:%M')

        telegram_msgs['msg'].append(_msg)
        telegram_msgs['date'].append(_date)
        telegram_msgs['time'].append(_time)
        telegram_msgs['view'].append(_view)

    except:
        _msg = '(메세지없이 링크만 있어요.)'
        telegram_msgs['msg'].append(_msg)
        telegram_msgs['date'].append("-")
        telegram_msgs['time'].append("-")
        telegram_msgs['view'].append(_view)

for uu in soup.find_all('a', class_='tgme_widget_message_date'):
    _link = uu.attrs['href']
    telegram_msgs['link'].append(_link)

telegram_msgs = pd.DataFrame(telegram_msgs)
telegram_msgs.columns = ['메세지', '일자', '시간', '조회수', '링크']
telegram_msgs.sort_values(by = ['일자', '시간'], ascending = [False, False], inplace = True)

import time
from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError


def fetch_trends(keyword) :

    pytrends = TrendReq(hl = 'ko-KR', tz = 540)
    kw_list = keyword

    try :
        time.sleep(1)

        pytrends.build_payload(kw_list,
                               timeframe = '2024-04-25 2024-05-25',
                               geo = 'KR')
        time.sleep(3)
        return pytrends.interest_over_time()

    except TooManyRequestsError :
        time.sleep(5)
        fetch_trends(kw_list)


data = fetch_trends(['삼성전자', 'SK하이닉스'])
data