import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Yield Comparison Dashboard")

def calculate_yield(input_flow, Gi_pct, Ga_pct, Gr_pct):
    Gi = Gi_pct / 100
    Ga = Ga_pct / 100
    Gr = Gr_pct / 100

    accept_flow = input_flow * ((Gi - Gr) / (Ga - Gr))
    reject_flow = input_flow * ((Ga - Gi) / (Ga - Gr))

    good_in_accept = Ga * accept_flow
    good_in_input = Gi * input_flow

    yield_pct = (good_in_accept / good_in_input) * 100

    return accept_flow, reject_flow, yield_pct


tab1, tab2, tab3 = st.tabs(["Run 1 Input", "Run 2 Input", "Comparison"])

with tab1:
    st.subheader("Run 1")

    input_flow_1 = st.number_input("Run 1 Input Flow", value=1000.0, key="flow1")
    Gi_1 = st.number_input("Run 1 Input Good %", value=56.0, key="gi1")
    Ga_1 = st.number_input("Run 1 Accept Good %", value=72.0, key="ga1")
    Gr_1 = st.number_input("Run 1 Reject Good %", value=12.0, key="gr1")

with tab2:
    st.subheader("Run 2")

    input_flow_2 = st.number_input("Run 2 Input Flow", value=2000.0, key="flow2")
    Gi_2 = st.number_input("Run 2 Input Good %", value=56.0, key="gi2")
    Ga_2 = st.number_input("Run 2 Accept Good %", value=68.0, key="ga2")
    Gr_2 = st.number_input("Run 2 Reject Good %", value=15.0, key="gr2")

accept_1, reject_1, yield_1 = calculate_yield(input_flow_1, Gi_1, Ga_1, Gr_1)
accept_2, reject_2, yield_2 = calculate_yield(input_flow_2, Gi_2, Ga_2, Gr_2)

yield_difference = yield_2 - yield_1

with tab3:
    st.subheader("Yield Comparison")

    col1, col2, col3 = st.columns(3)

    col1.metric("Run 1 Yield", f"{yield_1:.2f}%")
    col2.metric("Run 2 Yield", f"{yield_2:.2f}%")
    col3.metric("Yield Difference", f"{yield_difference:.2f}%")

    results_df = pd.DataFrame({
        "Run": ["Run 1", "Run 2"],
        "Input Flow": [input_flow_1, input_flow_2],
        "Accept Flow": [accept_1, accept_2],
        "Reject Flow": [reject_1, reject_2],
        "Yield %": [yield_1, yield_2],
    })

    st.dataframe(results_df, use_container_width=True)

    fig = px.bar(
        results_df,
        x="Run",
        y="Yield %",
        text="Yield %",
        title="Yield Comparison"
    )

    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.line(
        results_df,
        x="Input Flow",
        y="Yield %",
        markers=True,
        title="Estimated Yield vs Throughput"
    )

    st.plotly_chart(fig2, use_container_width=True)

    ###plotly


import streamlit as st  
import plotly.graph_objects as go  
import numpy as np  
  
def get_throughput_rate(time_seconds, grams=10012):  
    """Calculate throughput in grams per second."""  
    return grams / time_seconds  
  
def linear_yield_model(time_seconds):  
    """Linear interpolation between the two data points."""  
    t1, y1 = 30, 94.0  
    t2, y2 = 15, 86.4  
    slope = (y2 - y1) / (t2 - t1)  
    yield_pct = y1 + slope * (time_seconds - t1)  
    return yield_pct  
  
def create_yield_curve_with_point(time_seconds):  
    """Create chart with curve and current slider position."""  
    time_range = np.linspace(15, 30, 100)  
    yields = [linear_yield_model(t) for t in time_range]  
    throughputs = [get_throughput_rate(t) for t in time_range]  
      
    fig = go.Figure()  
      
    fig.add_trace(go.Scatter(  
        x=time_range,  
        y=yields,  
        mode='lines',  
        name='Yield Curve',  
        line=dict(width=3),  
        hovertemplate='Time: %{x:.1f}s<br>Yield: %{y:.1f}%<br>Throughput: %{customdata:.1f} g/s<extra></extra>',  
        customdata=throughputs  
    ))  
      
    fig.add_trace(go.Scatter(  
        x=[30, 15],  
        y=[94.0, 86.4],  
        mode='markers',  
        name='Measured Points',  
        marker=dict(size=10, line=dict(width=2, color='white')),  
        hovertemplate='Time: %{x}s<br>Yield: %{y}%<extra></extra>'  
    ))  
      
    yield_pct = linear_yield_model(time_seconds)  
    fig.add_trace(go.Scatter(  
        x=[time_seconds],  
        y=[yield_pct],  
        mode='markers',  
        name='Current Selection',  
        marker=dict(size=15, symbol='diamond', line=dict(width=2, color='white')),  
        hovertemplate='Time: %{x:.1f}s<br>Yield: %{y:.1f}%<extra></extra>'  
    ))  
      
    fig.update_xaxes(title_text="Time (seconds)", automargin=True)  
    fig.update_yaxes(title_text="Yield (%)", automargin=True)  
    fig.update_layout(hovermode='closest', showlegend=True)  
      
    return fig  
  
# Main app  
st.title("Throughput & Yield Analysis")  
  
time_seconds = st.slider(  
    "Processing Time (seconds)",  
    min_value=15.0,  
    max_value=30.0,  
    value=22.5,  
    step=0.5  
)  
  
throughput = get_throughput_rate(time_seconds)  
yield_pct = linear_yield_model(time_seconds)  
  
col1, col2, col3 = st.columns(3)  
  
with col1:  
    st.metric("Processing Time", f"{time_seconds:.1f}s")  
  
with col2:  
    st.metric("Throughput", f"{throughput:.1f} g/s")  
  
with col3:  
    st.metric("Yield", f"{yield_pct:.1f}%")  
  
fig = create_yield_curve_with_point(time_seconds)  
st.plotly_chart(fig, use_container_width=True)  
  