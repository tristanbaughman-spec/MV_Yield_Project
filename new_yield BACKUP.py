import pandas as pd
import plotly.express as px
import streamlit as st

st.title("Optical Sorting Yield Dashboard")


# User Inputs
input_flow = st.number_input("Input Flow (g/min)", value=1000.0)

Gi = st.number_input("Input Good %", value=56.0) / 100
Ga = st.number_input("Accept Good %", value=72.0) / 100
Gr = st.number_input("Reject Good %", value=12.0) / 100

# Calculations
accept_flow = input_flow * ((Gi - Gr) / (Ga - Gr))
reject_flow = input_flow * ((Ga - Gi) / (Ga - Gr))

good_in_accept = Ga * accept_flow
good_in_reject = Gr * reject_flow
good_in_input = Gi * input_flow

yield_pct = (good_in_accept / good_in_input) * 100

# Metrics
st.subheader("Results")

col1, col2, col3 = st.columns(3)

col1.metric("Accept Flow", f"{accept_flow:.2f} g/min")
col2.metric("Reject Flow", f"{reject_flow:.2f} g/min")
col3.metric("YIELD", f"{yield_pct:.2f}%")

# Dataframe
df = pd.DataFrame({
    "Stream": ["Accept", "Reject"],
    "Flow": [accept_flow, reject_flow]
})

st.dataframe(df)

# Plotly chart
fig = px.pie(
    df,
    names="Stream",
    values="Flow",
    title="Flow Split"
)

st.plotly_chart(fig, use_container_width=True)