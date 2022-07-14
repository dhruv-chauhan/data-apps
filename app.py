import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from datetime import date, datetime, timedelta
from st_aggrid import AgGrid

import config
import fetchers
import charts


def set_refresh_interval(frequency):
    if frequency == 'Daily':
        refresh_interval = 60 * 60 * 24
    if frequency == 'Hourly':
        refresh_interval = 60 * 60

    st_autorefresh(interval=refresh_interval * 1000)


st.set_page_config(layout="wide")
st.title("Blockchain Network Layer Metrics")

st.markdown('---')
st.subheader('Schema and Deployments')
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.write("Schema")
        st.write(config.schema)
    with col2:
        st.write("Deployments")
        st.json(config.deployments)

st.markdown('---')
st.subheader('Query Parameters')
with st.container():
    networks = st.multiselect(
        'Select networks',
        ['Arbitrum One', 'Arweave', 'Aurora', 'Avalanche', 'Boba', 'BSC', 'Celo', 'Clover', 'Cosmos', 'Fantom', 'Fuse',
            'Harmony', 'Mainnet', 'Matic', 'Moonbeam', 'Moonriver', 'Optimism', 'xDai'],
        ['Cosmos', 'Harmony', 'Optimism'])

    col1, col2, col3 = st.columns(3)
    with col1:
        frequency = st.selectbox(
            'Select frequency of snapshots',
            ('Hourly', 'Daily'))

    date_now = date.today()
    default_date_min = date_now - timedelta(days=7)
    with col2:
        from_date = st.date_input(
            "From date", value=default_date_min, max_value=date_now)
        from_time = st.time_input("From time")
    with col3:
        to_date = st.date_input("To date", max_value=date_now)
        to_time = st.time_input("To time")

    set_refresh_interval(frequency)

st.markdown('---')
st.subheader('Quantitative Data')
with st.container():
    from_unix = int(datetime.timestamp(datetime.strptime(
        f"{from_date} {from_time}", "%Y-%m-%d %H:%M:%S")))
    to_unix = int(datetime.timestamp(datetime.strptime(
        f"{to_date} {to_time}", "%Y-%m-%d %H:%M:%S")))

    quantitative_df = pd.concat(
        map(lambda x: fetchers.quantitative_data(x, config.deployments[x], frequency, from_unix, to_unix), networks), axis=0
    )

    quantitative_df_columns = list(quantitative_df.columns)
    show_quantitative_columns = st.multiselect(
        'Select columns to show',
        quantitative_df_columns,
        default=['network', 'blockHeight', 'totalSupply', 'gasPrice', 'cumulativeSize', 'cumulativeUniqueAuthors', 'cumulativeRewards', 'cumulativeBurntFees', 'timestamp'])

    if 'show_block_data' not in st.session_state:
        st.session_state.show_block_data = True

    show_block_data = st.checkbox(
        'Show individual block data in time range', value=True)
    st.session_state.show_block_data = show_block_data

    AgGrid(
        quantitative_df[show_quantitative_columns],
        data_return_mode="filtered_and_sorted",
        update_mode="no_update",
        fit_columns_on_grid_load=True,
        theme="streamlit"
    )

    if show_block_data:
        st.markdown('---')
        st.subheader('Block Data')

        block_range = {}
        blockHeight_min = quantitative_df[['network', 'blockHeight']
                                          ].groupby('network').min()
        for index, row in blockHeight_min.iterrows():
            block_range[index] = {}
            block_range[index]['first'] = str(row['blockHeight'])

        blockHeight_max = quantitative_df[['network', 'blockHeight']
                                          ].groupby('network').max()
        for index, row in blockHeight_max.iterrows():
            block_range[index]['last'] = str(row['blockHeight'])

        block_df = pd.concat(
            map(lambda x: fetchers.block_data(x, config.deployments[x], block_range[x]), networks), axis=0
        )
        block_df_columns = list(block_df.columns)
        show_block_columns = st.multiselect(
            'Select columns to show',
            block_df_columns,
            default=['network', 'id', 'hash', 'author_id', 'transactionCount', 'size', 'timestamp'])

        AgGrid(
            block_df[show_block_columns],
            data_return_mode="filtered_and_sorted",
            update_mode="no_update",
            fit_columns_on_grid_load=True,
            theme="streamlit"
        )

st.markdown('---')
st.subheader('Time Series Charts')
with st.container():
    col1, col2, col3 = st.columns(3)
    with col1:
        chart_type = st.selectbox(
            'Chart Type',
            ['Bar chart', 'Line chart', 'Area chart']
        )

        if 'with_mean' not in st.session_state:
            st.session_state.with_mean = True

        with_mean = st.checkbox('With mean', value=True)
        st.session_state.with_mean = with_mean
    with col2:
        metric_on_y = st.selectbox(
            'Metric on y-axis',
            quantitative_df_columns,
            index=1
        )
    with col3:
        metric_on_x = st.selectbox(
            'Metric on x-axis',
            quantitative_df_columns,
            index=3
        )

    if chart_type == "Line chart":
        charts.plot_line(quantitative_df[['network', metric_on_y,
                                          metric_on_x]], metric_on_y, metric_on_x, with_mean)
    elif chart_type == "Bar chart":
        charts.plot_bar(quantitative_df[['network', metric_on_y,
                                         metric_on_x]], metric_on_y, metric_on_x, with_mean)
    elif chart_type == "Area chart":
        charts.plot_area(quantitative_df[['network', metric_on_y,
                                          metric_on_x]], metric_on_y, metric_on_x, with_mean)

st.markdown('---')
