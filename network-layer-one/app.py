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
st.title("Network Metrics")

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
            ('Daily', 'Hourly'))

    date_now = date.today()
    if frequency == 'Daily':
        default_date_min = date(2021,1,1)
    elif frequency == 'Hourly':
        default_date_min = date_now - timedelta(days=120)

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

    if frequency == 'Hourly':
        nakamoto_df = pd.concat(
            map(lambda x: fetchers.quantitative_data(x, config.deployments[x], 'Daily', from_unix, to_unix), networks), axis=0
        )
    else:
        nakamoto_df = quantitative_df

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
                f'##### {frequency} average (mean) Blocks')

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
                f'{prefix}_lower_quartile', f'{prefix}_upper_quartile']
        if f'{prefix}_cumulative' in quantitative_df.columns:
            cols.append(f'{prefix}_cumulative')

        tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
        with tab1:
            col1, col2 = st.columns([3, 1])
            with col1:
                charts.plot_box(quantitative_df[cols], prefix, 'timestamp', 'count')
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


with st.expander("Nakamoto Coefficients"):
    with st.container():
        data = nakamoto_df[['blockHeight', 'timestamp']]

        data['day'] = data["timestamp"].apply(lambda x: x.strftime("%d"))
        blocks = data[data["day"] == '01']["blockHeight"].tolist()

        author_df = pd.concat(
            map(lambda x: fetchers.author_data(x, config.deployments[x], blocks), networks), axis=0
        )

        block_timestamp_dict = (
            data[["blockHeight", "timestamp"]]
            .set_index("blockHeight")
            .to_dict()
        )
        author_df["timestamp"] = author_df["height"].apply(
            lambda x: block_timestamp_dict["timestamp"][x]
        )

        author_df = author_df.set_index(["network", "height", "timestamp", "id"])  # set index as (height, id)
        author_df = author_df.unstack()  # Move index id to columns
        author_df = author_df.swaplevel(axis=1).sort_index(axis=1)  # swap & sort column
        author_df = author_df.diff()  # get diff over time
        author_df = author_df.xs("cumulativeBlocksCreated", axis=1, level=1)  # grab blocks created
        author_df = author_df.iloc[1:]  # drop the first one

        tmp_list = []
        for idx, row in author_df.iterrows():
            # TODO, drop 0s from row
            row = row[row > 0]

            author_count = len(row)

            # get stats about block mining
            blocks_mined_total = row.sum()
            blocks_mined_median = row.median()
            blocks_mined_mean = row.mean()

            blocks_mined_max = row.max()
            blocks_mined_min = row.min()

            blocks_mined_std = row.std()

            blocks_mined_q3 = row.quantile(0.75)
            blocks_mined_q1 = row.quantile(0.25)

            # Getting realized nakamoto
            authored = row.sort_values(ascending=False).to_frame(name="authored")
            authored["authored.cumulative"] = authored["authored"].cumsum()
            authored["pct"] = authored["authored"] / blocks_mined_total
            authored["pct.cumulative"] = authored["pct"].cumsum()

            realized_nakamoto = (
                len(authored[authored["pct.cumulative"] < 0.33]) + 1
            )

            # NOTE: consider normalizing this to pct so the charts are simplier
            tmp_dict = {
                "network": idx[0],
                "date": idx[2].strftime("%Y-%m-%d"),
                "author_count": author_count,
                "nakamoto_realized": realized_nakamoto,
                "blocksAuthored_sum": blocks_mined_total,
                "blocksAuthored_mean": blocks_mined_mean,
                "blocksAuthored_median": blocks_mined_median,
                "blocksAuthored_max": blocks_mined_max,
                "blocksAuthored_min": blocks_mined_min,
                "blocksAuthored_std": blocks_mined_std,
                "blocksAuthored_upper_quartile": blocks_mined_q3,
                "blocksAuthored_lower_quartile": blocks_mined_q1,
            }
            tmp_list.append(tmp_dict)

        author_stats = pd.DataFrame(tmp_list)

        with st.container():
            st.markdown('##### Blocks Authored Distribution')

            tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
            with tab1:
                # author_stats_fig = charts.plotly_box_plot(
                #     author_stats.set_index('date'),
                #     'blocksAuthored',
                #     mean=False,
                #     upper=False,
                #     lower=False
                # )
                # st.plotly_chart(author_stats_fig, use_container_width=True)

                charts.plot_box(author_stats, 'blocksAuthored', 'date', 'sum')

            with tab2:
                AgGrid(
                    author_stats,
                    data_return_mode="filtered_and_sorted",
                    update_mode="no_update",
                    fit_columns_on_grid_load=True,
                    theme="streamlit"
                )

                col1, col2 = st.columns([12, 1])
                with col2:
                    st.download_button(
                        label="Export as CSV",
                        data=df_to_csv(author_stats),
                        file_name=f'author_stats.csv',
                        mime='text/csv',
                    )

        st.markdown('---')
        with st.container():
            st.markdown('##### Custom Charts')

            cols = [
                "date",
                "author_count",
                "nakamoto_realized",
                "blocksAuthored_sum",
                "blocksAuthored_mean",
                "blocksAuthored_median",
                "blocksAuthored_max",
                "blocksAuthored_min",
                "blocksAuthored_std",
                "blocksAuthored_upper_quartile",
                "blocksAuthored_lower_quartile",
            ]

            col1, col2, col3 = st.columns(3)
            with col1:
                chart_type = st.selectbox(
                    'Chart Type',
                    ['Line chart', 'Bar chart', 'Area chart'],
                    key='author_stats_chart_type'
                )

                aggregators = ['none', 'count', 'sum',
                               'mean', 'median', 'min', 'max']
                default_index = aggregators.index('none')
                aggregate = st.radio(
                    "Mark Aggregator",
                    aggregators,
                    index=default_index,
                    horizontal=True
                )
                if aggregate == 'none':
                    aggregate = None

            with col2:
                default_index = cols.index('nakamoto_realized')
                metric_on_y = st.selectbox(
                    'Metric on y-axis',
                    cols,
                    index=default_index
                )
            with col3:
                default_index = cols.index('date')
                metric_on_x = st.selectbox(
                    'Metric on x-axis',
                    cols,
                    index=default_index
                )

            tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
            with tab1:
                if chart_type == "Line chart":
                    charts.plot_line(author_stats[['network', metric_on_y,
                                                   metric_on_x]], metric_on_y, metric_on_x, aggregate)
                elif chart_type == "Bar chart":
                    charts.plot_bar(author_stats[['network', metric_on_y,
                                                  metric_on_x]], metric_on_y, metric_on_x, aggregate)
                elif chart_type == "Area chart":
                    charts.plot_area(author_stats[['network', metric_on_y,
                                                   metric_on_x]], metric_on_y, metric_on_x, aggregate)

            with tab2:
                AgGrid(
                    author_stats[['network', metric_on_y, metric_on_x]],
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
                            author_stats[['network', metric_on_y, metric_on_x]]),
                        file_name=f'{metric_on_y}_vs_{metric_on_x}.csv',
                        mime='text/csv',
                    )
