import altair as alt
import streamlit as st

from analysis import downtime_by_cause, kpis, load_data, operator_breakdown, product_summary
st.set_page_config(page_title="MES Downtime Intelligence", page_icon="🏭", layout="wide")

st.title("🏭 MES Downtime Intelligence")
st.caption("Performance analytics for a soda bottling line")

batches, events = load_data()
k = kpis(batches)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Line efficiency", f"{k['efficiency']:.1f}%")
col2.metric("Time lost", f"{k['total_lost'] / 60:.1f} h")
col3.metric("Total run time", f"{k['total_time'] / 60:.1f} h")
col4.metric("Batches", k["batches"])

st.subheader("Where is time lost?")

causes = downtime_by_cause(events)
chart = (
    alt.Chart(causes)
    .mark_bar()
    .encode(
        x=alt.X("Minutes:Q", title="Minutes lost"),
        y=alt.Y("Description:N", sort="-x", title=None),
        color=alt.Color("Operator Error:N", title="Operator error"),
        tooltip=["Description", "Minutes", "Share %", "Operator Error"],
    )
)
st.altair_chart(chart, use_container_width=True)


left, right = st.columns(2)

with left:
    st.subheader("Operators: lost time per batch")
    ops = operator_breakdown(batches, events)
    op_chart = (
        alt.Chart(ops)
        .mark_bar()
        .encode(
            x=alt.X("Min per batch:Q", title="Minutes lost per batch"),
            y=alt.Y("Operator:N", sort="-x", title=None),
            color=alt.Color("Type:N", title=None),
            tooltip=["Operator", "Type", "Min per batch", "Batches"],
        )
    )
    st.altair_chart(op_chart, use_container_width=True)
    st.caption("Per batch, since operators ran different numbers of batches.")

with right:
    st.subheader("Products: efficiency")
    products = product_summary(batches)
    prod_chart = (
        alt.Chart(products)
        .mark_bar()
        .encode(
            x=alt.X("Efficiency %:Q", scale=alt.Scale(domain=[0, 100])),
            y=alt.Y("Product:N", sort="x", title=None),
            tooltip=["Product", "Efficiency %", "Batches"],
        )
    )
    st.altair_chart(prod_chart, use_container_width=True)
    st.caption("Products with very few batches (e.g. OR-600, 1 batch) are not reliable.")