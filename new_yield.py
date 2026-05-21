import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


st.set_page_config(page_title="Yield Dashboard", layout="wide")

st.title("Throughput & Yield Analysis Dashboard")


# -----------------------------
# CALCULATIONS
# -----------------------------

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


def linear_yield_model(x, x1, y1, x2, y2):

    slope = (y2 - y1) / (x2 - x1)

    return y1 + slope * (x - x1)


def create_yield_curve(current_flow, x1, y1, x2, y2):

    flow_range = np.linspace(min(x1, x2), max(x1, x2), 100)

    yields = [
        linear_yield_model(flow, x1, y1, x2, y2)
        for flow in flow_range
    ]

    current_yield = linear_yield_model(
        current_flow,
        x1,
        y1,
        x2,
        y2,
    )

    fig = go.Figure()

    # Yield curve
    fig.add_trace(go.Scatter(
        x=flow_range,
        y=yields,
        mode="lines",
        name="Estimated Yield Curve",
        line=dict(width=4),
    ))

    # User measured points
    fig.add_trace(go.Scatter(
        x=[x1, x2],
        y=[y1, y2],
        mode="markers",
        name="Measured Runs",
        marker=dict(size=12),
    ))

    # Current estimate point
    fig.add_trace(go.Scatter(
        x=[current_flow],
        y=[current_yield],
        mode="markers",
        name="Current Estimate",
        marker=dict(size=18, symbol="diamond"),
    ))

    fig.update_layout(
        title="Estimated Yield vs Throughput",
        xaxis_title="Input Flow Rate",
        yaxis_title="Yield %",
        hovermode="closest",
        height=550,
    )

    return fig, current_yield


# -----------------------------
# INPUT TABS
# -----------------------------

tab1, tab2, tab3 = st.tabs([
    "Run 1",
    "Run 2",
    "Comparison"
])


# -----------------------------
# RUN 1
# -----------------------------

with tab1:

    st.subheader("Run 1 Inputs")

    input_flow_1 = st.number_input(
        "Run 1 Input Flow",
        value=333.73,
        key="run1_flow"
    )

    Gi_1 = st.number_input(
        "Run 1 Input Good %",
        value=56.0,
        key="run1_gi"
    )

    Ga_1 = st.number_input(
        "Run 1 Accept Good %",
        value=72.0,
        key="run1_ga"
    )

    Gr_1 = st.number_input(
        "Run 1 Reject Good %",
        value=12.0,
        key="run1_gr"
    )


# -----------------------------
# RUN 2
# -----------------------------

with tab2:

    st.subheader("Run 2 Inputs")

    input_flow_2 = st.number_input(
        "Run 2 Input Flow",
        value=667.47,
        key="run2_flow"
    )

    Gi_2 = st.number_input(
        "Run 2 Input Good %",
        value=56.0,
        key="run2_gi"
    )

    Ga_2 = st.number_input(
        "Run 2 Accept Good %",
        value=68.0,
        key="run2_ga"
    )

    Gr_2 = st.number_input(
        "Run 2 Reject Good %",
        value=15.0,
        key="run2_gr"
    )


# -----------------------------
# CALCULATE BOTH RUNS
# -----------------------------

accept_1, reject_1, yield_1 = calculate_yield(
    input_flow_1,
    Gi_1,
    Ga_1,
    Gr_1,
)

accept_2, reject_2, yield_2 = calculate_yield(
    input_flow_2,
    Gi_2,
    Ga_2,
    Gr_2,
)

yield_difference = yield_2 - yield_1


# -----------------------------
# COMPARISON TAB
# -----------------------------

with tab3:

    st.subheader("Yield Comparison")

    selected_flow = st.slider(
        "Estimate Yield at Input Flow",
        min_value=float(min(input_flow_1, input_flow_2)),
        max_value=float(max(input_flow_1, input_flow_2)),
        value=float((input_flow_1 + input_flow_2) / 2),
        step=1.0,
    )

    fig_curve, estimated_yield = create_yield_curve(
        selected_flow,
        input_flow_1,
        yield_1,
        input_flow_2,
        yield_2,
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Run 1 Yield",
        f"{yield_1:.2f}%"
    )

    col2.metric(
        "Run 2 Yield",
        f"{yield_2:.2f}%"
    )

    col3.metric(
        "Yield Difference",
        f"{yield_difference:.2f}%"
    )

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "Run 1 Accept Flow",
        f"{accept_1:.2f}"
    )

    col5.metric(
        "Run 2 Accept Flow",
        f"{accept_2:.2f}"
    )

    col6.metric(
        "Estimated Yield",
        f"{estimated_yield:.2f}%"
    )

    # Results dataframe
    results_df = pd.DataFrame({
        "Run": ["Run 1", "Run 2"],
        "Input Flow": [input_flow_1, input_flow_2],
        "Accept Flow": [accept_1, accept_2],
        "Reject Flow": [reject_1, reject_2],
        "Yield %": [yield_1, yield_2],
    })

    st.dataframe(results_df, use_container_width=True)

    # Bar chart
    fig_bar = px.bar(
        results_df,
        x="Run",
        y="Yield %",
        text="Yield %",
        title="Yield Comparison"
    )

    fig_bar.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    # Curve chart
    st.plotly_chart(
        fig_curve,
        use_container_width=True
    )