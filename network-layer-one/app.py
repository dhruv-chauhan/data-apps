import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from datetime import date, datetime, timedelta
from st_aggrid import AgGrid, JsCode

import config
import fetchers
import charts


def set_refresh_interval(frequency):
    if frequency == 'Daily':
        refresh_interval = 60 * 60 * 24
    if frequency == 'Hourly':
        refresh_interval = 60 * 60

    st_autorefresh(interval=refresh_interval * 1000)


def gen_js_snippet(col_name, show_stats):
    table_rows = ''
    for stat in show_stats:
        table_rows += f'''
        '<tr>' + 
            '<td>' + '{stat}' + '</td>' + 
            '<td>' + col["{stat}"] + '</td>' + 
        '</tr>' + '''

    return '''
    function (params) {
        col = ''' + f"JSON.parse(params.data['{col_name}']);" + '''
        return (
        '<table>' + 
        ''' + table_rows + '''
        '</table>'
        );
    }'''


def build_grid_options(show_quantitative_columns, show_stats):
    columnDefs = []

    for field in config.fields_without_stats:
        columnDef = {
            "field": f"{field}"
        }
        if field not in show_quantitative_columns:
            columnDef["hide"] = True

        columnDefs.append(columnDef)

    for field in config.fields_with_stats:
        columnDef = {
            "field": f"{field}",
            "cellRenderer": JsCode(gen_js_snippet(field, show_stats)).js_code,
        }
        if field not in show_quantitative_columns:
            columnDef["hide"] = True

        columnDefs.append(columnDef)

    return {
        "rowHeight": len(show_stats) * 30 if len(show_stats) > 0 else 30,
        "columnDefs": columnDefs
    }


st.set_page_config(layout="wide")
st.title("Network Layer-1 Metrics")

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
        ['Arweave', 'Boba'])

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

    quantitative_df_columns = config.fields_with_stats + config.fields_without_stats
    show_quantitative_columns = st.multiselect(
        'Select columns to show',
        quantitative_df_columns,
        default=['network', 'blockHeight', 'totalSupply', 'gasPrice', 'Size', 'cumulativeUniqueAuthors', 'cumulativeRewards',
                 'Transactions', 'cumulativeBurntFees', 'timestamp'])

    show_stats = st.multiselect(
        'Select stats to show',
        ['count', 'sum', 'mean', 'median', 'max', 'min',
            'variance', 'upper_quartile', 'lower_quartile'],
        default=['count', 'mean'])

    AgGrid(
        quantitative_df[show_quantitative_columns],
        gridOptions=build_grid_options(show_quantitative_columns, show_stats),
        data_return_mode="filtered_and_sorted",
        update_mode="no_update",
        fit_columns_on_grid_load=True,
        theme="streamlit",
        allow_unsafe_jscode=True,
        height=600,
    )

    if 'show_block_data' not in st.session_state:
        st.session_state.show_block_data = True

    show_block_data = st.checkbox(
        'Show individual block data in time range', value=True)
    st.session_state.show_block_data = show_block_data

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
    time_series_columns = sorted(list(
        set(quantitative_df.columns) - set(config.fields_with_stats)))
    time_series_columns.remove('network')

    col1, col2, col3 = st.columns(3)
    with col1:
        chart_type = st.selectbox(
            'Chart Type',
            ['Bar chart', 'Line chart', 'Area chart']
        )

        aggregate = st.radio(
            "Aggregate on",
            ('none', 'count', 'sum', 'mean', 'median', 'min', 'max'),
            index=3,
            horizontal=True
        )
        if aggregate == 'none':
            aggregate = None

    with col2:
        metric_on_y = st.selectbox(
            'Metric on y-axis',
            time_series_columns,
            index=1
        )
    with col3:
        metric_on_x = st.selectbox(
            'Metric on x-axis',
            time_series_columns,
            index=132
        )

    if chart_type == "Line chart":
        charts.plot_line(quantitative_df[['network', metric_on_y,
                                          metric_on_x]], metric_on_y, metric_on_x, aggregate)
    elif chart_type == "Bar chart":
        charts.plot_bar(quantitative_df[['network', metric_on_y,
                                         metric_on_x]], metric_on_y, metric_on_x, aggregate)
    elif chart_type == "Area chart":
        charts.plot_area(quantitative_df[['network', metric_on_y,
                                          metric_on_x]], metric_on_y, metric_on_x, aggregate)

st.markdown('---')
