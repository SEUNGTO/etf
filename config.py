import streamlit as st

def set_session() :
    if 'search' not in st.session_state :
        st.session_state['search'] = True
    if 'etf_code' not in st.session_state :
        st.session_state['code'] = '102110'
    if 'search_results' not in st.session_state :
        st.session_state['search_results'] = []
    if 'etf_name' not in st.session_state :
        st.session_state['name'] = 'TIGER 200'
    if 'type' not in st.session_state :
        st.session_state['type'] = 'ETF'

telegram_dict = {
    '주식 급등일보🚀급등테마·대장주 탐색기': 'https://t.me/s/FastStockNews'
    , '핀터 - 국내공시 6줄 요약': 'https://t.me/s/finter_gpt'
    , 'AWAKE-일정, 테마, 이벤트드리븐' : 'https://t.me/s/awake_schedule'
    # , '조정은 뇌를 뽑아가지': 'https://t.me/s/shlrkQhqgla'
    , '52주 신고가 모니터링' : 'https://t.me/s/awake_realtimeCheck'
    , 'SB 리포트 요약' : 'https://t.me/s/stonereport'

}


type_dict = {
'old': 'https://raw.githubusercontent.com/SEUNGTO/ETFdata/main/old_data.json',
'new' : 'https://raw.githubusercontent.com/SEUNGTO/ETFdata/main/new_data.json'
}
