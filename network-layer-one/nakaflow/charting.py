"""
Module for making charts,
The aim is to make this as flexible as possible
"""
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates

def plotly_lines(df: pd.DataFrame, fig: go.Figure = None) -> go.Figure:
    """
    Doing a line plot, index should be datetime, eveything else is fine
    """

    new_fig = fig if fig else go.Figure()
    for col in df.columns:
        new_fig.add_trace(go.Scatter(x=df.index, y=df[col].astype(float), name=col))
    return new_fig


def plotly_box_plot(
    df: pd.DataFrame,
    name: str,
    upper: bool = True,
    lower: bool = True,
    mean: bool = True,
    ylabel: str = None,
) -> go.Figure:
    # Reference: https://plotly.com/python/box-plots/
    fig = go.Figure()

    dates = df.index
    fig.add_trace(go.Box(y=[], x=dates, name=f"{name} BoxPlot"))

    mean_list = df[f"{name}.mean"] if mean else None
    median = df[f"{name}.median"]

    lowerfence = df[f"{name}.min"] if lower else None
    upperfence = df[f"{name}.max"] if upper else None

    std = df[f"{name}.std"]

    q1 = df[f"{name}.q1"]
    q3 = df[f"{name}.q3"]

    # y_title = ylabel

    fig.update_layout(
        title=name,
        xaxis_title="date",
        yaxis_title=ylabel,
    )

    fig.update_traces(
        q1=q1,
        q3=q3,
        median=median,
        lowerfence=lowerfence,
        upperfence=upperfence,
        mean=mean_list,
        sd=std,
        # notchspan=[ 0.2, 0.4, 0.6 ]
    )
    return fig


def clean_plotly_fig(fig: go.Figure) -> go.Figure:
    """
    Remove x-axis & y-axis lines
    Remove figure background
    """
    fig.update_layout(
        yaxis=dict(showgrid=False),
        xaxis=dict(showgrid=False),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    # Bold move to go full RH here
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig
