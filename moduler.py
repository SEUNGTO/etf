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
import pytz
from datetime import datetime, timedelta


def load_etf_data(type, code) :

    if type == 'old' :
        url = 'https://raw.githubusercontent.com/SEUNGTO/ETFdata/main/old_data.json'

    elif type == 'new' :
        url = 'https://raw.githubusercontent.com/SEUNGTO/ETFdata/main/new_data.json'

    tmp = requests.get(url)
    tmp = pd.DataFrame(tmp.json(), dtype = str)

    tmp = tmp.loc[tmp['etf_code'] == code, :]
    tmp = tmp.drop('etf_code', axis = 1)
    tmp.columns = ['종목코드', '종목명', '보유량', '평가금액', '비중']
    tmp['보유량'] = tmp['보유량'].astype(float)
    tmp['평가금액'] = tmp['평가금액'].astype(float)
    tmp['비중'] = tmp['비중'].astype(float)

    return tmp


def load_stock_data(type, code) :

    if type == 'old' :
        url = 'https://raw.githubusercontent.com/SEUNGTO/ETFdata/main/old_data.json'

    elif type == 'new' :
        url = 'https://raw.githubusercontent.com/SEUNGTO/ETFdata/main/new_data.json'

    tmp = requests.get(url)
    tmp = pd.DataFrame(tmp.json(), dtype = str)
    tmp = tmp.loc[tmp['stock_code'] == code, :]
    tmp.columns = ['ETF코드','종목코드', '종목명', '보유량', '평가금액', '비중']
    tmp['보유량'] = tmp['보유량'].astype(float)
    tmp['평가금액'] = tmp['평가금액'].astype(float)

    return tmp

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
    url = 'https://raw.githubusercontent.com/SEUNGTO/ETFdata/main/code_list.json'

    return pd.DataFrame(requests.get(url).json())

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


def load_research() :
    url = 'https://raw.githubusercontent.com/SEUNGTO/ETFdata/main/research.json'
    data = pd.DataFrame(requests.get(url).json())
    data['목표가'] = [re.sub('\D', '', t) for t in data['목표가']]
    data = data[data['목표가'] != ""]
    data['목표가'] = data['목표가'].astype(int)

    return data


def load_entire_etf_data(url) :

    tmp = requests.get(url)
    tmp = pd.DataFrame(tmp.json(), dtype = str)

    tmp.columns = ['ETF코드','종목코드', '종목명', '보유량', '평가금액', '비중']
    tmp['보유량'] = tmp['보유량'].astype(float)
    tmp['평가금액'] = tmp['평가금액'].astype(float)
    tmp['비중'] = tmp['비중'].astype(float)

    return tmp

@st.cache
def merge_data() :

    new = load_entire_etf_data(type_dict['new'])
    old = load_entire_etf_data(type_dict['old'])

    entire = pd.merge(new, old.drop('종목명', axis = 1), on = ['ETF코드', '종목코드'], suffixes=['(기준일)', '(비교일)'])

    etf_list = fdr.StockListing('ETF/KR')
    etf_list = etf_list.loc[:, ['Name', 'Symbol']]
    etf_list.columns = ['ETF', 'ETF코드']

    entire = entire.set_index('ETF코드').join(etf_list.set_index('ETF코드'))
    entire = entire.reset_index(drop = True).set_index('ETF')
    entire.fillna(0, inplace = True)

    return entire
