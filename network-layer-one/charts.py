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


def plot_bar(data, on_y, on_x, aggregate, properties={}):
    bar = alt.Chart(data, title=f"{on_y} vs. {on_x}").mark_bar(
        opacity=0.5).encode(
        x=alt.X(on_x, title=on_x),
        y=alt.Y(on_y, title=on_y),
        color='network',
        tooltip=[on_y, on_x]).interactive()

    if properties:
        bar = bar.properties(height=properties['height'])

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
        tooltip=[on_y, on_x]).interactive()

    if aggregate:
        rule = plot_aggregate(aggregate, data, on_y)
        st.altair_chart((area + rule), use_container_width=True)
        return

    st.altair_chart(area, use_container_width=True)


def plot_box(prefix, data):
    data['count (normalized)'] = data[f'{prefix}_count'].div(
        data.groupby(['network'])[f'{prefix}_count'].transform('sum'))

    base = alt.Chart(data).encode(
        alt.X('timestamp'),
        color='network'
    )

    rule = base.mark_rule().encode(
        alt.Y(f'{prefix}_min', title=None),
        alt.Y2(f'{prefix}_max', title=None)
    )

    bar = base.mark_bar(
        size=10
    ).encode(
        alt.Y(f'{prefix}_lower_quartile', title=None),
        alt.Y2(f'{prefix}_upper_quartile', title=None),
        opacity='count (normalized)',
        tooltip=['network', f'{prefix}_min', f'{prefix}_max',
                 f'{prefix}_lower_quartile', f'{prefix}_upper_quartile', f'{prefix}_mean', f'{prefix}_count']
    ).interactive()

    tick_mean = alt.Chart(data).mark_tick(
        thickness=2,
        size=10 * 1,
    ).encode(
        alt.Y(f'{prefix}_mean', title=None),
        alt.X('timestamp'),
        color='network'
    )

    st.altair_chart((rule + bar + tick_mean),
                    use_container_width=True)
