# http://172.30.1.57:8501/

import streamlit as st
import pandas as pd
import io
import time
import json
import requests
import pandas as pd

def codeListing() :

    otp_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
    otp_params = {
        'locale': 'ko_KR',
        'share': '1',
        'csvxls_isNo': 'false',
        'name': 'fileDown',
        'url': 'dbms/MDC/STAT/standard/MDCSTAT04601'
    }
    headers = {'Referer' : 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader'}
    otp = requests.post(otp_url, params = otp_params, headers = headers).text

    down_url = 'http://data.krx.co.kr/comm/fileDn/download_csv/download.cmd'
    down_params = {'code' : otp}
    response = requests.post(down_url, params = down_params, headers = headers)

    data = pd.read_csv(io.BytesIO(response.content), encoding = 'euc-kr', dtype = {'단축코드': 'string'})

    return data

def loadData() :

    url = 'https://raw.githubusercontent.com/SEUNGTO/botdata/main/resultDict.json'
    response = requests.get(url)
    resultDict = response.json()

    for code in resultDict.keys() :
        for date in resultDict[code].keys() :
            resultDict[code][date] = pd.DataFrame(resultDict[code][date])

    return resultDict

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
                chgStocks = chgData[chgData['변화분'] != 0][['종목코드', '변화분']]
                chgStocks['ETF'] = code
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

                chgStocks = pd.concat([chgStocks, tmp])
        except :
            continue


    ETFcodeName = codeList[['단축코드', '한글종목약명']]
    ETFcodeName.columns = ['ETF', 'ETF종목명']
    chgStocks = pd.merge(chgStocks, ETFcodeName, how = 'left', on = 'ETF')
    chgStocks = chgStocks[['ETF', 'ETF종목명', '종목코드', '구성종목명', '변화분']]

    return chgStocks



if __name__ == '__main__' :
    codeList = codeListing()
    codeList = codeList[(codeList['기초시장분류'] == '국내') & (codeList['기초자산분류'] == '주식')]
    resultDict = loadData()

    bas_dt = '20240502'
    target_date = '20240516'

    st.write('# 종목명 검색')
    st.write('### 코드명 입력')

    code = ''
    code = st.text_input('※ 원하는 종목의 코드를 입력하세요')

    if code == "" :
        pass

    elif code != "" :

        chgStocks = findChange(bas_dt, target_date, codeList, resultDict)

        tmp = chgStocks[chgStocks['종목코드'] == code]
        tmp