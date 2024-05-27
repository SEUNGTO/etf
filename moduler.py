import streamlit as st
import FinanceDataReader as fdr
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import requests
import re
from bs4 import BeautifulSoup


def telegram_crawller(url, keyword) :
    telegram_msgs = {
        'msg': []
        , 'date': []
        , 'time': []
        , 'link': []
    }
    query = f'{url}?q={keyword}'
    response = requests.get(query)
    soup = BeautifulSoup(response.content, 'html.parser')

    for msg in soup.find_all('div', class_='tgme_widget_message_bubble'):

        msg.find('a').decompose()
        try:
            _msg = msg.find('div', class_='tgme_widget_message_text js-message_text').text

            datetime = pd.to_datetime(msg.find('time', class_='time').attrs['datetime'])
            datetime = datetime.tz_convert('Asia/Seoul')
            _date = datetime.strftime('%Y-%m-%d')
            _time = datetime.strftime('%H:%M')

            telegram_msgs['msg'].append(_msg)
            telegram_msgs['date'].append(_date)
            telegram_msgs['time'].append(_time)

        except:
            _msg = '(메세지없이 링크만 있어요.)'
            telegram_msgs['msg'].append(_msg)
            telegram_msgs['date'].append("-")
            telegram_msgs['time'].append("-")

    for uu in soup.find_all('a', class_='tgme_widget_message_date'):
        _link = uu.attrs['href']
        telegram_msgs['link'].append(_link)

    telegram_msgs = pd.DataFrame(telegram_msgs)
    telegram_msgs.columns = ['메세지', '일자', '시간', '링크']
    return telegram_msgs.sort_values(by = ('일자', '시간'), ascending = ('False', 'False'))

def code_update(name, codeList) :
    st.session_state['code'] = codeList[codeList['Name'] == name]['Symbol'].values[0]
    st.session_state['type'] = codeList[codeList['Name'] == name]['Type'].values[0]

@st.cache_data
def load_codeList() :
    url = 'https://raw.githubusercontent.com/SEUNGTO/botdata/main/ETFcodeList.json'
    data = pd.DataFrame(requests.get(url).json())
    data.columns = ['Name', 'Symbol', 'Type']

    return data


#
#
# url = 'https://t.me/s/FastStockNews'
# keyword = '삼성전자'
#
# telegram_msgs = {
#     'msg': []
#     , 'date': []
#     , 'time': []
#     , 'link': []
# }
# query = f'{url}?q={keyword}'
# response = requests.get(query)
# soup = BeautifulSoup(response.content, 'html.parser')
#
# msgs = soup.find_all('div', class_='tgme_widget_message_bubble')
# msg = msgs[0]
# for msg in msgs :
#
#     datetime = msg.find('time', class_ = 'time').attrs['datetime']
#     datetime = pd.to_datetime(datetime)
#     datetime = datetime.tz_convert('Asia/Seoul')
#     date = datetime.strftime('%Y-%m-%d')
#     _time = datetime.strftime('%H:%M')
#
# for msg in soup.find_all('div', class_='tgme_widget_message_bubble'):
#
#     msg.find('a').decompose()
#     try:
#         msg = msg.find('div', class_='tgme_widget_message_text js-message_text').text
#         telegram_msgs['msg'].append(msg)
#
#         datetime = pd.to_datetime(msg.find('time', class_='time').attrs['datetime'])
#         datetime = datetime.tz_convert('Asia/Seoul')
#         date = datetime.strftime('%Y-%m-%d')
#         _time = datetime.strftime('%H:%M')
#
#         telegram_msgs['date'].append(date)
#         telegram_msgs['time'].append(_time)
#
#     except:
#         msg = '(메세지없이 링크만 있어요.)'
#         telegram_msgs['msg'].append(msg)
#
#         datetime = pd.to_datetime(msg.find('time', class_='time').attrs['datetime'])
#         datetime = datetime.tz_convert('Asia/Seoul')
#         date = datetime.strftime('%Y-%m-%d')
#         _time = datetime.strftime('%H:%M')
#
#         telegram_msgs['date'].append(date)
#         telegram_msgs['time'].append(_time)
#
#
# for uu in soup.find_all('a', class_='tgme_widget_message_date'):
#     link = uu.attrs['href']
#     telegram_msgs['link'].append(link)
#
# telegram_msgs = pd.DataFrame(telegram_msgs)
# telegram_msgs.columns = ['메세지', '일자', '시간', '링크']
#
# telegram_msgs.sort_values(by = ['일자', '시간'], ascending=[False, False])



url = 'https://t.me/s/FastStockNews'
keyword = '삼성전자'

telegram_msgs = {
    'msg': []
    , 'date': []
    , 'time': []
    , 'link': []
}
query = f'{url}?q={keyword}'
response = requests.get(query)
soup = BeautifulSoup(response.content, 'html.parser')

for msg in soup.find_all('div', class_='tgme_widget_message_bubble'):

    msg.find('a').decompose()
    try:
        _msg = msg.find('div', class_='tgme_widget_message_text js-message_text').text
        telegram_msgs['msg'].append(_msg)

        datetime = pd.to_datetime(msg.find('time', class_='time').attrs['datetime'])
        datetime = datetime.tz_convert('Asia/Seoul')
        date = datetime.strftime('%Y-%m-%d')
        _time = datetime.strftime('%H:%M')

        telegram_msgs['date'].append(date)
        telegram_msgs['time'].append(_time)

    except:
        _msg = '(메세지없이 링크만 있어요.)'
        telegram_msgs['msg'].append(_msg)
        telegram_msgs['date'].append("-")
        telegram_msgs['time'].append("-")

for uu in soup.find_all('a', class_='tgme_widget_message_date'):
    link = uu.attrs['href']
    telegram_msgs['link'].append(link)

telegram_msgs = pd.DataFrame(telegram_msgs)
telegram_msgs.columns = ['메세지', '일자', '시간', '링크']


for key, item in telegram_msgs.items() :
    print(key, len(item))

