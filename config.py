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
    , 'AWAKE-실시간 주식 공시 정리채널': 'https://t.me/s/darthacking'
    , '조정은 뇌를 뽑아가지': 'https://t.me/s/shlrkQhqgla'
}
