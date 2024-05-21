import streamlit as st

conn = st.connection('mysql', type='sql')

# Perform query.
df = conn.query('SELECT * from tb_etf;', ttl=600)

# Print results.
st.write(df)
for row in df.itertuples():
    st.write(f"{row}")