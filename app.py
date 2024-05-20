# http://172.30.1.57:8501/

import streamlit as st
import requests
import pandas as pd
import io



code = ""
target_date = ""
bas_dt = ""
chgData = pd.DataFrame([])

def header():
    st.write("# ETF 검색")


def inputData():
    global target_date, bas_dt, code
    code = st.text_input("검색할 종목코드를 선택하세요.")
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

    global chgData

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
                chgData = chgData[chgData['변화분'] != 0][['종목코드', '변화분']]
                chgData['ETF'] = code
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

                chgData = pd.concat([chgData, tmp])
        except :
            continue


    ETFcodeName = codeList[['단축코드', '한글종목약명']]
    ETFcodeName.columns = ['ETF', 'ETF종목명']
    chgData = pd.merge(chgData, ETFcodeName, how = 'left', on = 'ETF')
    chgData = chgData[['ETF', 'ETF종목명', '종목코드', '구성종목명', '변화분']]

    return chgData


if __name__ == '__main__' :


    codeList = codeListing()
    codeList = codeList[(codeList['기초시장분류'] == '국내') & (codeList['기초자산분류'] == '주식')]
    resultDict = loadData()

    header()
    inputData()

    confirm = st.button('입력 완료')

    search_all = st.button('전체 내역')
    search_code = st.button('종목 검색')

    if confirm :
        with st.spinner('데이터를 불러오는 중입니다.'):
            changes = findChange(bas_dt, target_date, codeList, resultDict)

    if search_all :
        st.markdown('---------')
        st.write('### 전체 내역')
        st.dataframe(changes.sort_values('변화분', ascending = False))


    if search_code :
        st.markdown('---------')
        st.write('### 해당 종목 내역')
        st.dataframe(changes[changes['종목코드'] == code])
