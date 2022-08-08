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


def gen_js_snippet(metric, stats):
    table_rows = ''
    for stat in stats:
        table_rows += f'''
        '<tr>' + 
            '<td>' + '{stat}' + '</td>' + 
            '<td>' + col["{stat}"] + '</td>' + 
        '</tr>' + '''

    return '''
    function (params) {
        col = ''' + f"JSON.parse(params.data['{metric}']);" + '''
        return (
        '<table>' + 
        ''' + table_rows + '''
        '</table>'
        );
    }'''


def build_grid_options(cols, stats):
    columnDefs = []

    for metric in config.metrics_without_stats:
        columnDef = {
            "field": f"{metric}",
            "resizable": True,
        }
        if metric not in cols:
            columnDef["hide"] = True

        columnDefs.append(columnDef)

    for metric in config.metrics_with_stats:
        columnDef = {
            "field": f"{metric}",
            "cellRenderer": JsCode(gen_js_snippet(metric, stats)).js_code,
            "resizable": True,
        }
        if metric not in cols:
            columnDef["hide"] = True

        columnDefs.append(columnDef)

    return {
        "rowHeight": len(stats) * 30 if len(stats) > 0 else 30,
        "columnDefs": columnDefs,
        "defaultColDef": {
            "filter": True,
        }
    }


@st.cache
def df_to_csv(df):
    return df.to_csv().encode('utf-8')


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
        st.json(config.deployments, expanded=False)

st.markdown('---')
st.subheader('Query Parameters')
with st.container():
    networks = st.multiselect(
        'Select networks',
        config.deployments.keys(),
        ['Arweave'])

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

    from_unix = int(datetime.timestamp(datetime.strptime(
        f"{from_date} {from_time}", "%Y-%m-%d %H:%M:%S")))
    to_unix = int(datetime.timestamp(datetime.strptime(
        f"{to_date} {to_time}", "%Y-%m-%d %H:%M:%S")))

    quantitative_df = pd.concat(
        map(lambda x: fetchers.quantitative_data(x, config.deployments[x], frequency, from_unix, to_unix), networks), axis=0
    )

with st.expander("Metrics"):
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('##### Block Height')

            data = quantitative_df[['network', 'blockHeight']
                                   ].groupby('network').max().reset_index()
            for index, row in data.iterrows():
                st.metric(label=row['network'], value=row['blockHeight'])
        with col2:
            st.markdown('##### Total Supply')

            data = quantitative_df[['network', 'totalSupply']
                                   ].groupby('network').max().reset_index()
            for index, row in data.iterrows():
                st.metric(label=row['network'], value=row['totalSupply'])
        with col3:
            st.markdown('##### Gas Price')

            data = quantitative_df[['network', 'gasPrice']
                                   ].groupby('network').max().reset_index()
            for index, row in data.iterrows():
                st.metric(label=row['network'],
                          value=row['gasPrice'])
        with col4:
            st.markdown(
                f'##### Average (mean) Blocks per {frequency.replace("ly", "")}')

            data = quantitative_df[['network', 'blocks']
                                   ].groupby('network').mean().reset_index()
            data = data.rename(columns={'blocks': 'blocks_mean'})

            charts.plot_bar(data, 'network', 'blocks_mean',
                            None, {'height': 100*len(data) if len(data) > 1 else 125})

    st.markdown('---')
    with st.container():
        st.markdown('##### Stats')

        default_index = config.metrics_with_stats.index(
            f'Transactions')
        metric = st.selectbox(
            'Metric',
            config.metrics_with_stats,
            index=default_index)

        prefix = frequency.lower() + metric
        cols = ['network', 'timestamp', f'{prefix}_count', f'{prefix}_sum',
                f'{prefix}_mean', f'{prefix}_variance',
                f'{prefix}_max', f'{prefix}_min',
                f'{prefix}_q1', f'{prefix}_q3']
        if f'{prefix}_cumulative' in quantitative_df.columns:
            cols.append(f'{prefix}_cumulative')

        tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
        with tab1:
            col1, col2 = st.columns([3, 1])
            with col1:
                charts.plot_box(prefix, quantitative_df[cols])
            with col2:
                if f'{prefix}_cumulative' in quantitative_df.columns:
                    data = quantitative_df[['network', f'{prefix}_cumulative']
                                           ].groupby('network').max().reset_index()

                    charts.plot_bar(data, 'network', f'{prefix}_cumulative', None, {
                                    'height': 100*len(data) if len(data) > 1 else 125})

        with tab2:
            AgGrid(
                quantitative_df[cols],
                data_return_mode="filtered_and_sorted",
                update_mode="no_update",
                fit_columns_on_grid_load=True,
                theme="streamlit"
            )

            col1, col2 = st.columns([12, 1])
            with col2:
                st.download_button(
                    label="Export as CSV",
                    data=df_to_csv(quantitative_df[cols]),
                    file_name=f'{prefix}.csv',
                    mime='text/csv',
                )

    st.markdown('---')
    with st.container():
        st.markdown('##### Custom Charts')

        cols = sorted(set(quantitative_df.columns.values) -
                      set(config.metrics_with_stats))

        col1, col2, col3 = st.columns(3)
        with col1:
            chart_type = st.selectbox(
                'Chart Type',
                ['Line chart', 'Bar chart', 'Area chart']
            )

            aggregators = ['none', 'count', 'sum',
                           'mean', 'median', 'min', 'max']
            default_index = aggregators.index('mean')
            aggregate = st.radio(
                "Mark Aggregator",
                aggregators,
                index=default_index,
                horizontal=True
            )
            if aggregate == 'none':
                aggregate = None

        with col2:
            default_index = cols.index('blocks')
            metric_on_y = st.selectbox(
                'Metric on y-axis',
                cols,
                index=default_index
            )
        with col3:
            default_index = cols.index('timestamp')
            metric_on_x = st.selectbox(
                'Metric on x-axis',
                cols,
                index=default_index
            )

        tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
        with tab1:
            if chart_type == "Line chart":
                charts.plot_line(quantitative_df[['network', metric_on_y,
                                                  metric_on_x]], metric_on_y, metric_on_x, aggregate)
            elif chart_type == "Bar chart":
                charts.plot_bar(quantitative_df[['network', metric_on_y,
                                                metric_on_x]], metric_on_y, metric_on_x, aggregate)
            elif chart_type == "Area chart":
                charts.plot_area(quantitative_df[['network', metric_on_y,
                                                  metric_on_x]], metric_on_y, metric_on_x, aggregate)

        with tab2:
            AgGrid(
                quantitative_df[['network', metric_on_y, metric_on_x]],
                data_return_mode="filtered_and_sorted",
                update_mode="no_update",
                fit_columns_on_grid_load=True,
                theme="streamlit"
            )

            col1, col2 = st.columns([12, 1])
            with col2:
                st.download_button(
                    label="Export as CSV",
                    data=df_to_csv(
                        quantitative_df[['network', metric_on_y, metric_on_x]]),
                    file_name=f'{metric_on_y}_vs_{metric_on_x}.csv',
                    mime='text/csv',
                )

with st.expander("Data"):
    cols = st.multiselect(
        'Metrics',
        config.metrics_with_stats + config.metrics_without_stats,
        default=['network', 'blockHeight', 'totalSupply', 'gasPrice', 'Size', 'Transactions', 'timestamp'])

    stats = st.multiselect(
        'Stats',
        ['count', 'sum', 'mean', 'max', 'min',
            'variance', 'upper_quartile', 'lower_quartile', 'cumulative'],
        default=['count', 'mean'])

    if 'show_block_data' not in st.session_state:
        st.session_state.show_block_data = False

    show_block_data = st.checkbox(
        'Show individual block data in time range', value=True)
    st.session_state.show_block_data = show_block_data

    AgGrid(
        quantitative_df[cols],
        gridOptions=build_grid_options(cols, stats),
        data_return_mode="filtered_and_sorted",
        update_mode="no_update",
        fit_columns_on_grid_load=True,
        theme="streamlit",
        allow_unsafe_jscode=True,
        height=600,
    )

    col1, col2 = st.columns([12, 1])
    with col2:
        st.download_button(
            label="Export as CSV",
            data=df_to_csv(
                quantitative_df[cols]),
            file_name='quantitative_data.csv',
            mime='text/csv',
        )

    if show_block_data:
        st.markdown('---')
        st.markdown('##### Block Data')

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

        cols = st.multiselect(
            'Columns',
            block_df.columns.values,
            default=['network', 'id', 'hash', 'author_id', 'transactionCount', 'size', 'timestamp'])

        AgGrid(
            block_df[cols],
            data_return_mode="filtered_and_sorted",
            update_mode="no_update",
            fit_columns_on_grid_load=True,
            theme="streamlit"
        )

        col1, col2 = st.columns([12, 1])
        with col2:
            st.download_button(
                label="Export as CSV",
                data=df_to_csv(
                    block_df[cols]),
                file_name='quantitative_data.csv',
                mime='text/csv',
            )
