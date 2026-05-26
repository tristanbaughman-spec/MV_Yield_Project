import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


st.set_page_config(page_title="Yield Dashboard", layout="wide")


# ------------------------------------------------
# PAGE HEADER
# ------------------------------------------------

title_col, logo_col = st.columns([5, 1])

with title_col:
    st.title("MV360 & 3U USA Yield Calculator")

with logo_col:
    try:
        st.image("assets/3U-Vision-USAdarksilhouette.png", width=200)
        st.image("assets/Logotipo-MachVision-spanish-1.png", width=200)
    except Exception:
        pass


# -----------------------------
# CALCULATIONS
# -----------------------------

def calculate_yield(input_flow, Gi_pct, Ga_pct, Gr_pct):
    Gi = Gi_pct / 100
    Ga = Ga_pct / 100
    Gr = Gr_pct / 100

    if input_flow <= 0:
        raise ValueError("Input flow must be greater than 0.")

    if Gi <= 0:
        raise ValueError("Input Good % must be greater than 0.")

    if Ga == Gr:
        raise ValueError("Accept Good % and Reject Good % cannot be the same.")

    accept_flow = input_flow * ((Gi - Gr) / (Ga - Gr))
    reject_flow = input_flow * ((Ga - Gi) / (Ga - Gr))

    good_in_input = Gi * input_flow
    good_in_accept = Ga * accept_flow

    yield_pct = (good_in_accept / good_in_input) * 100

    return accept_flow, reject_flow, yield_pct, good_in_accept, good_in_input


def linear_yield_model(x, x1, y1, x2, y2):
    if x1 == x2:
        return y1

    slope = (y2 - y1) / (x2 - x1)
    return y1 + slope * (x - x1)


def create_yield_curve(current_flow, x1, y1, x2, y2):
    flow_range = np.linspace(min(x1, x2), max(x1, x2), 100)

    yields = [
        linear_yield_model(flow, x1, y1, x2, y2)
        for flow in flow_range
    ]

    current_yield = linear_yield_model(current_flow, x1, y1, x2, y2)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=flow_range,
        y=yields,
        mode="lines",
        name="Estimated Yield Curve",
        line=dict(width=4),
    ))

    fig.add_trace(go.Scatter(
        x=[x1, x2],
        y=[y1, y2],
        mode="markers",
        name="Measured Runs",
        marker=dict(size=12),
    ))

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
    "Optional Run 2",
    "Results"
])


# -----------------------------
# RUN 1
# -----------------------------

with tab1:
    st.subheader("Run 1 Inputs")

    input_flow_1 = st.number_input("Run 1 Input Flow", value=333.73, key="run1_flow")
    Gi_1 = st.number_input("Run 1 Input Good %", value=56.0, key="run1_gi")
    Ga_1 = st.number_input("Run 1 Accept Good %", value=72.0, key="run1_ga")
    Gr_1 = st.number_input("Run 1 Reject Good %", value=12.0, key="run1_gr")


# -----------------------------
# RUN 2 OPTIONAL
# -----------------------------

with tab2:
    st.subheader("Run 2 Inputs")

    use_run_2 = st.checkbox(
        "Add Run 2 for comparison",
        value=False,
        key="use_run_2"
    )

    if use_run_2:
        input_flow_2 = st.number_input("Run 2 Input Flow", value=667.47, key="run2_flow")
        Gi_2 = st.number_input("Run 2 Input Good %", value=56.0, key="run2_gi")
        Ga_2 = st.number_input("Run 2 Accept Good %", value=68.0, key="run2_ga")
        Gr_2 = st.number_input("Run 2 Reject Good %", value=15.0, key="run2_gr")
    else:
        st.info("Run 2 is optional. Turn this on only when you want a comparison.")


# -----------------------------
# RESULTS TAB
# -----------------------------

with tab3:
    st.subheader("Yield Results")

    try:
        accept_1, reject_1, yield_1, good_accept_1, good_input_1 = calculate_yield(
            input_flow_1,
            Gi_1,
            Ga_1,
            Gr_1,
        )

        results = [{
            "Run": "Run 1",
            "Input Flow": input_flow_1,
            "Accept Flow": accept_1,
            "Reject Flow": reject_1,
            "Good Input Weight": good_input_1,
            "Good Yield by Weight": good_accept_1,
            "Yield %": yield_1,
        }]

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Run 1 Yield", f"{yield_1:.2f}%")
        col2.metric("Run 1 Good Yield by Weight", f"{good_accept_1:.2f}")
        col3.metric("Run 1 Accept Flow", f"{accept_1:.2f}")
        col4.metric("Run 1 Reject Flow", f"{reject_1:.2f}")

        if use_run_2:
            accept_2, reject_2, yield_2, good_accept_2, good_input_2 = calculate_yield(
                input_flow_2,
                Gi_2,
                Ga_2,
                Gr_2,
            )

            yield_difference = yield_2 - yield_1
            good_yield_difference = good_accept_2 - good_accept_1

            results.append({
                "Run": "Run 2",
                "Input Flow": input_flow_2,
                "Accept Flow": accept_2,
                "Reject Flow": reject_2,
                "Good Input Weight": good_input_2,
                "Good Yield by Weight": good_accept_2,
                "Yield %": yield_2,
            })

            st.divider()

            col5, col6, col7, col8 = st.columns(4)

            col5.metric("Run 2 Yield", f"{yield_2:.2f}%")
            col6.metric("Run 2 Good Yield by Weight", f"{good_accept_2:.2f}")
            col7.metric("Yield Difference", f"{yield_difference:.2f}%")
            col8.metric("Good Yield Weight Difference", f"{good_yield_difference:.2f}")

        results_df = pd.DataFrame(results)

        st.dataframe(results_df, use_container_width=True)

        fig_bar_pct = px.bar(
            results_df,
            x="Run",
            y="Yield %",
            text="Yield %",
            title="Yield % Result" if not use_run_2 else "Yield % Comparison"
        )

        fig_bar_pct.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside"
        )

        st.plotly_chart(fig_bar_pct, use_container_width=True)

        fig_bar_weight = px.bar(
            results_df,
            x="Run",
            y="Good Yield by Weight",
            text="Good Yield by Weight",
            title="Good Yield by Weight" if not use_run_2 else "Good Yield by Weight Comparison"
        )

        fig_bar_weight.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside"
        )

        st.plotly_chart(fig_bar_weight, use_container_width=True)

        if use_run_2:
            st.subheader("Estimated Yield Curve")

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

            st.metric("Estimated Yield", f"{estimated_yield:.2f}%")
            st.plotly_chart(fig_curve, use_container_width=True)
        else:
            st.info("Add Run 2 to enable comparison, yield difference, and estimated yield curve.")

    except ValueError as e:
        st.error(str(e))
