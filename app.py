# http://172.30.1.57:8501/

import streamlit as st
import requests
import pandas as pd
import io



def header():
    st.write("# Hello")

code = ""
target_date = ""
bas_dt = ""

def inputData():
    global code, target_date, bas_dt
    code = st.text_input("검색하고자 하는 종목코드를 입력하세요.")
    target_date = st.text_input("기준일자를 선택하세요(yyyymmdd형식).")
    bas_dt = st.text_input("비교일자를 선택하세요(yyyymmdd형식).")


@st.cache_data()
def loadData():
    url = 'https://raw.githubusercontent.com/SEUNGTO/botdata/main/resultDict.json'
    response = requests.get(url)
    resultDict = response.json()

    for code in resultDict.keys():
        for date in resultDict[code].keys():
            resultDict[code][date] = pd.DataFrame(resultDict[code][date])

    return resultDict

@st.cache_resource()
def codeListing():

    url = 'https://raw.githubusercontent.com/SEUNGTO/botdata/main/codeList.json'
    response = requests.get(url)
    codeList = response.json()

    return pd.DataFrame(codeList)


def findChange(bas_dt, target_date, codeList, resultDict) :

    for idx, code in enumerate(codeList['단축코드']) :
        try :
            if idx == 0 :

                basData = resultDict[code][bas_dt]
                targetData = resultDict[code][target_date]

                chgData = pd.merge(basData[['종목코드', '구성종목명','주식수(계약수)']],
                                targetData[['종목코드', '주식수(계약수)']],
                                how = 'left',
                                on = '종목코드'
                                )
                chgData['변화분'] = chgData['주식수(계약수)_y'] - chgData['주식수(계약수)_x']
                chgData.fillna(0, inplace = True)
                _chgStocks = chgData[chgData['변화분'] != 0][['종목코드', '변화분']]
                _chgStocks['ETF'] = code
            else :
                basData = resultDict[code][bas_dt]
                targetData = resultDict[code][target_date]

                tmp = pd.merge(basData[['종목코드', '구성종목명','주식수(계약수)']],
                                targetData[['종목코드', '주식수(계약수)']],
                                how = 'left',
                                on = '종목코드'
                                            )
                tmp['변화분'] = tmp['주식수(계약수)_y'] - tmp['주식수(계약수)_x']
                tmp.fillna(0, inplace = True)
                tmp = tmp[tmp['변화분'] != 0][['종목코드','구성종목명', '변화분']]
                tmp['ETF'] = code

                _chgStocks = pd.concat([_chgStocks, tmp])
        except :
            continue


    ETFcodeName = codeList[['단축코드', '한글종목약명']]
    ETFcodeName.columns = ['ETF', 'ETF종목명']
    _chgStocks = pd.merge(_chgStocks, ETFcodeName, how = 'left', on = 'ETF')
    _chgStocks = _chgStocks[['ETF', 'ETF종목명', '종목코드', '구성종목명', '변화분']]

    return _chgStocks


if __name__ == '__main__' :


    with st.spinner('데이터를 불러오는 중입니다.') :
        codeList = codeListing()
        codeList = codeList[(codeList['기초시장분류'] == '국내') & (codeList['기초자산분류'] == '주식')]
        resultDict = loadData()
        chgStocks = findChange(bas_dt, target_date, codeList, resultDict)

    header()
    inputData()

    if code != "" and bas_dt != "" and target_date != "" :
        st.wrtie(f'{code}, {bas_dt}, {target_date}')
