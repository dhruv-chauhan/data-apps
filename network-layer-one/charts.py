# import plotly.graph_objects as go
# import pandas as pd
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


def plot_box(data, prefix, on_x, opacity_factor):
    data[f'{opacity_factor} (normalized)'] = data[f'{prefix}_{opacity_factor}'].div(
        data.groupby(['network'])[f'{prefix}_{opacity_factor}'].transform('sum'))

    base = alt.Chart(data).encode(
        alt.X(on_x),
        color='network'
    )

    rule = base.mark_rule().encode(
        alt.Y(f'{prefix}_min', title=None),
        alt.Y2(f'{prefix}_max', title=None)
    )

    tooltip = ['network', f'{prefix}_min', f'{prefix}_max',
               f'{prefix}_lower_quartile', f'{prefix}_upper_quartile', f'{prefix}_mean', f'{prefix}_{opacity_factor}']

    tick_mean = alt.Chart(data).mark_tick(
        thickness=2,
        size=10 * 1,
    ).encode(
        alt.Y(f'{prefix}_mean', title=None),
        alt.X(on_x),
        color='network'
    )
    ticks = tick_mean

    if f'{prefix}_median' in data.columns:
        tick_median = alt.Chart(data).mark_tick(
            thickness=2,
            size=10 * 1,
        ).encode(
            alt.Y(f'{prefix}_median', title=None),
            alt.X(on_x),
            color='network'
        )

        tooltip.append(f'{prefix}_median')
        ticks = ticks + tick_median

    if f'{prefix}_std' in data.columns:
        tick_std = alt.Chart(data).mark_tick(
            thickness=2,
            size=10 * 1,
        ).encode(
            alt.Y(f'{prefix}_std', title=None),
            alt.X(on_x),
            color='network'
        )

        tooltip.append(f'{prefix}_std')
        ticks = ticks + tick_std

    bar = base.mark_bar(
        size=10
    ).encode(
        alt.Y(f'{prefix}_lower_quartile', title=None),
        alt.Y2(f'{prefix}_upper_quartile', title=None),
        opacity=f'{opacity_factor} (normalized)',
        tooltip=tooltip
    ).interactive()

    st.altair_chart((rule + bar + ticks),
                    use_container_width=True)


# def plotly_box_plot(
#     df: pd.DataFrame,
#     name: str,
#     upper: bool = True,
#     lower: bool = True,
#     mean: bool = True,
#     ylabel: str = None,
# ) -> go.Figure:
#     # Reference: https://plotly.com/python/box-plots/
#     fig = go.Figure()

#     dates = df.index
#     colors = ['red', 'yellow']
#     for i, network in enumerate(df['network'].unique()):
#         fig.add_trace(go.Box(y=[], x=dates, name=f"{name} BoxPlot", line=dict(color=colors[i])))

#     mean_list = df[f"{name}_mean"] if mean else None
#     median = df[f"{name}_median"]

#     lowerfence = df[f"{name}_min"] if lower else None
#     upperfence = df[f"{name}_max"] if upper else None

#     std = df[f"{name}_std"]

#     q1 = df[f"{name}_lower_quartile"]
#     q3 = df[f"{name}_upper_quartile"]

#     # y_title = ylabel

#     fig.update_layout(
#         title=name,
#         xaxis_title="date",
#         yaxis_title=ylabel,
#     )

#     fig.update_traces(
#         q1=q1,
#         q3=q3,
#         median=median,
#         lowerfence=lowerfence,
#         upperfence=upperfence,
#         mean=mean_list,
#         sd=std,
#         # notchspan=[ 0.2, 0.4, 0.6 ]
#     )
#     return fig
