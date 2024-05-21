import streamlit as st

conn = st.connection('mysql', type='sql')

# Perform query.
df = conn.query('SELECT * from etf_20240518;', ttl=600)

# Print results.
st.dataframe(df)
