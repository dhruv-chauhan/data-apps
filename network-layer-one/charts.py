import streamlit as st
import altair as alt


def plot_aggregate(aggregate, data, on_y):
    rule = alt.Chart(data).mark_rule().encode(
        y=alt.Y(on_y, aggregate=aggregate),
        color='network',
        size=alt.value(2)
    )
    return rule


def plot_line(data, on_y, on_x, aggregate):
    line = alt.Chart(data, title=f"{on_y} vs. {on_x}").mark_line().encode(
        x=alt.X(on_x, title=on_x),
        y=alt.Y(on_y, title=on_y),
        color='network',
        tooltip=[on_y, on_x]).interactive()

    if aggregate:
        rule = plot_aggregate(aggregate, data, on_y)
        st.altair_chart((line + rule), use_container_width=True)
        return

    st.altair_chart(line, use_container_width=True)


def plot_bar(data, on_y, on_x, aggregate):
    bar = alt.Chart(data, title=f"{on_y} vs. {on_x}").mark_bar(
        cornerRadiusTopLeft=3,
        cornerRadiusTopRight=3,
        opacity=0.5).encode(
        x=alt.X(on_x, title=on_x),
        y=alt.Y(on_y, title=on_y),
        color='network',
        tooltip=[on_y, on_x])

    if aggregate:
        rule = plot_aggregate(aggregate, data, on_y)
        st.altair_chart((bar + rule), use_container_width=True)
        return

    st.altair_chart(bar, use_container_width=True)


def plot_area(data, on_y, on_x, aggregate):
    area = alt.Chart(data, title=f"{on_y} vs. {on_x}").mark_area(
        opacity=0.5).encode(
        x=alt.X(on_x, title=on_x),
        y=alt.Y(on_y, title=on_y, stack=None),
        color='network',
        tooltip=[on_y, on_x])

    if aggregate:
        rule = plot_aggregate(aggregate, data, on_y)
        st.altair_chart((area + rule), use_container_width=True)
        return

    st.altair_chart(area, use_container_width=True)
