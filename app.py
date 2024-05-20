# http://172.30.1.57:8501/

import streamlit as st
import requests
import pandas as pd

class main() :

    def __init__(self):
        self.header()
        self.data = self.loadData()

        self.SearchCode()

    def header(self):
        st.write("# Hello")

    def loadData(self):
        url = 'https://raw.githubusercontent.com/SEUNGTO/botdata/main/resultDict.json'
        response = requests.get(url)
        resultDict = response.json()

        for code in resultDict.keys():
            for date in resultDict[code].keys():
                resultDict[code][date] = pd.DataFrame(resultDict[code][date])

        return resultDict


    def SearchCode(self):
        code = st.text_input("검색하고자 하는 ETF 코드를 입력하세요.")
        target_date = st.text_input("기준일자를 선택하세요(yyyymmdd형식).")
        bas_dt = st.text_input("비교일자를 선택하세요(yyyymmdd형식).")
        if not code and not target_date and not bas_dt :
            st.wrtie(f'{code}, {target_date}, {bas_dt}' )



if __name__ == '__main__' :

    main()