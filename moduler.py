import streamlit as st
import FinanceDataReader as fdr
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup

def telegram_crawller(url, keyword) :
    telegram_msgs = {
            'msg': []
            , 'link': []
        }

    query = f'{url}?q={keyword}'
    response = requests.get(query)
    soup = BeautifulSoup(response.content, 'html.parser')

    for msg in soup.find_all('div', class_='tgme_widget_message_bubble'):

        msg.find('a').decompose()
        try:
            msg = msg.find('div', class_='tgme_widget_message_text js-message_text').text
            telegram_msgs['msg'].append(msg)

        except:
            msg = '(메세지없이 링크만 있어요.)'
            telegram_msgs['msg'].append(msg)

    for uu in soup.find_all('a', class_='tgme_widget_message_date'):
        link = uu.attrs['href']
        telegram_msgs['link'].append(link)

    telegram_msgs = pd.DataFrame(telegram_msgs)
    telegram_msgs.columns = ['메세지', '링크']
    return telegram_msgs

def code_update(name, codeList) :
    st.session_state['code'] = codeList[codeList['Name'] == name]['Symbol'].values[0]
    st.session_state['type'] = codeList[codeList['Name'] == name]['Type'].values[0]

def load_codeList() :
    url = 'https://raw.githubusercontent.com/SEUNGTO/botdata/main/ETFcodeList.json'
    data = requests.get(url)

    return pd.DataFrame(data.json()).rename({'Code' : 'Symbol'})
