import time
import asyncio
import os
import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta

import config
import fetchers
import charts
import helpers
from header.header import header


st.set_page_config(page_icon="⛓️", layout="wide")
header(
    title="Network Metrics",
    img_src="https://pbs.twimg.com/profile_images/1460309230271942656/2axFof4c_400x400.jpg",
    author_url="https://twitter.com/_dhruv_chauhan_",
    author="Dhruv Chauhan",
)

helpers.local_css(os.path.join(os.path.dirname(__file__), "style.css"))

with st.expander("⚙️ Query Parameters", expanded=False):
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            network = st.selectbox(
                'Select network',
                config.deployments.keys(),
                index=1)
            frequency = st.selectbox(
                'Select frequency of snapshots',
                ('Daily', 'Hourly')).lower()

        date_now = date.today()
        if frequency == 'daily':
            default_date_min = date_now - timedelta(days=365)
        elif frequency == 'hourly':
            default_date_min = date_now - timedelta(days=16)  # ~365 hours

        with col2:
            from_date = st.date_input(
                "From date", value=default_date_min, max_value=date_now)
            from_time = st.time_input("From time")
        with col3:
            to_date = st.date_input("To date", max_value=date_now)
            to_time = st.time_input("To time")

        from_unix = int(datetime.timestamp(datetime.strptime(
            f"{from_date} {from_time}", "%Y-%m-%d %H:%M:%S")))
        to_unix = int(datetime.timestamp(datetime.strptime(
            f"{to_date} {to_time}", "%Y-%m-%d %H:%M:%S")))

quantitative_df = asyncio.run(fetchers.get_snapshots(network, frequency, from_unix, to_unix))

if len(quantitative_df.index) != 0:
    with st.container():
        with st.container():
            if 'are_snapshots_updated' not in st.session_state:
                st.session_state['are_snapshots_updated'] = -1

            if st.session_state['are_snapshots_updated'] == -1:
                btn_text = '🔄 Refresh network snapshots'
                btn_disabled = False
            elif st.session_state['are_snapshots_updated'] == 0:
                btn_text = '⏳ Updating in background...'
                btn_disabled = True
            elif st.session_state['are_snapshots_updated'] == 1:
                btn_text = '✨ Snapshots up to date!'
                btn_disabled = True

            col1, col2, col3 = st.columns([5, 1, 1])
            with col1:
                st.markdown(f'#### Network: {network}')
            with col2:
                helpers.data_download_button(
                    quantitative_df, f"{network}_{frequency}", label=f"📥 Download {network} snapshot")
            with col3:
                st.button(btn_text, disabled=btn_disabled, on_click=fetchers.refresh_snapshots)

            st.markdown('---')

        with st.container():
            latest_snapshot = quantitative_df[quantitative_df['timestamp'] == quantitative_df['timestamp'].max()]
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown('##### Supply')
                st.metric(label="Total Supply", value=latest_snapshot['totalSupply'].iloc[0])
            with col2:
                st.markdown('##### Gas')
                if f'{frequency}GasUsed_count' in latest_snapshot.columns:
                    st.metric(label=f"{frequency} Gas Used", value=latest_snapshot[f'{frequency}GasUsed_count'].iloc[0])
                if f'{frequency}GasLimit_count' in latest_snapshot.columns:
                    st.metric(label=f"{frequency} Gas Limit",
                              value=latest_snapshot[f'{frequency}GasLimit_count'].iloc[0])
                st.metric(label="Gas Price", value=latest_snapshot['gasPrice'].iloc[0])
            with col3:
                st.markdown('##### Authors')
                if f'{frequency}UniqueAuthors_count' in latest_snapshot.columns:
                    st.metric(label=f"{frequency} Unique Authors",
                              value=latest_snapshot[f'{frequency}UniqueAuthors_count'].iloc[0])
                if f'{frequency}UniqueAuthors_cumulative' in latest_snapshot.columns:
                    st.metric(label=f"Cumulative Unique Authors",
                              value=latest_snapshot[f'{frequency}UniqueAuthors_cumulative'].iloc[0])
            with col4:
                st.markdown('##### Burnt Fees')
                if f'{frequency}BurntFees_count' in latest_snapshot.columns:
                    st.metric(label=f"{frequency} Burnt Fees",
                              value=latest_snapshot[f'{frequency}BurntFees_count'].iloc[0])
                if f'{frequency}BurntFees_cumulative' in latest_snapshot.columns:
                    st.metric(label=f"Cumulative Burnt Fees",
                              value=latest_snapshot[f'{frequency}BurntFees_cumulative'].iloc[0])
            with col5:
                st.markdown('##### Transactions')
                if f'{frequency}Transactions_count' in latest_snapshot.columns:
                    st.metric(label=f"{frequency} Transactions",
                              value=latest_snapshot[f'{frequency}Transactions_count'].iloc[0])
                if f'{frequency}Transactions_cumulative' in latest_snapshot.columns:
                    st.metric(label=f"Cumulative Transactions",
                              value=latest_snapshot[f'{frequency}Transactions_cumulative'].iloc[0])

            st.markdown('  ')

            col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
            with col1:
                st.markdown('##### Block')
                st.metric(label="Block Height", value=latest_snapshot['blockHeight'].iloc[0])
                st.metric(label=f"{frequency} Blocks", value=latest_snapshot['blocks'].iloc[0])
                if f'{frequency}BlockInterval_count' in latest_snapshot.columns:
                    st.metric(label=f"{frequency} Block Interval",
                              value=latest_snapshot[f'{frequency}BlockInterval_count'].iloc[0])
            with col2:
                st.markdown('##### Difficulty')
                if f'{frequency}Difficulty_mean' in latest_snapshot.columns:
                    st.metric(label=f"{frequency} Average Difficulty",
                              value=latest_snapshot[f'{frequency}Difficulty_mean'].iloc[0])
                if f'{frequency}Difficulty_cumulative' in latest_snapshot.columns:
                    st.metric(label=f"Cumulative Difficulty",
                              value=latest_snapshot[f'{frequency}Difficulty_cumulative'].iloc[0])
            with col3:
                st.markdown('##### Rewards')
                if f'{frequency}Rewards_count' in latest_snapshot.columns:
                    st.metric(label=f"{frequency} Rewards", value=latest_snapshot[f'{frequency}Rewards_count'].iloc[0])
                if f'{frequency}Rewards_cumulative' in latest_snapshot.columns:
                    st.metric(label=f"Cumulative Rewards",
                              value=latest_snapshot[f'{frequency}Rewards_cumulative'].iloc[0])
            with col4:
                st.markdown('##### Block Size')
                if f'{frequency}Size_mean' in latest_snapshot.columns:
                    st.metric(label=f"{frequency} Average Block Size",
                              value=latest_snapshot[f'{frequency}Size_mean'].iloc[0])
                if f'{frequency}Size_cumulative' in latest_snapshot.columns:
                    st.metric(label=f"Cumulative Block Size",
                              value=latest_snapshot[f'{frequency}Size_cumulative'].iloc[0])

    with st.expander("📊 Time-series Plots"):
        chart_type = st.selectbox(
            'Chart Type',
            ['Line chart', 'Bar chart', 'Area chart']
        )

        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                metric_on_y = 'blockHeight'
                metric_on_x = 'datetime'
                data = quantitative_df[['network', metric_on_y, metric_on_x]]

                tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
                with tab1:
                    if chart_type == "Line chart":
                        charts.plot_line(data, metric_on_y, metric_on_x, None)
                    elif chart_type == "Bar chart":
                        charts.plot_bar(data, metric_on_y, metric_on_x, None)
                    elif chart_type == "Area chart":
                        charts.plot_area(data, metric_on_y, metric_on_x, None)

                with tab2:
                    helpers.data_grid(data)
                    helpers.data_download_button(data, f"{metric_on_y}_vs_{metric_on_x}")
            with col2:
                metric_on_y = 'blocks'
                metric_on_x = 'datetime'
                data = quantitative_df[['network', metric_on_y, metric_on_x]]

                tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
                with tab1:
                    if chart_type == "Line chart":
                        charts.plot_line(data, metric_on_y, metric_on_x, None)
                    elif chart_type == "Bar chart":
                        charts.plot_bar(data, metric_on_y, metric_on_x, None)
                    elif chart_type == "Area chart":
                        charts.plot_area(data, metric_on_y, metric_on_x, None)

                with tab2:
                    helpers.data_grid(data)
                    helpers.data_download_button(data, f"{metric_on_y}_vs_{metric_on_x}")

            col1, col2 = st.columns(2)
            with col1:
                metric_on_y = 'totalSupply'
                metric_on_x = 'datetime'
                data = quantitative_df[['network', metric_on_y, metric_on_x]]

                tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
                with tab1:
                    if chart_type == "Line chart":
                        charts.plot_line(data, metric_on_y, metric_on_x, None)
                    elif chart_type == "Bar chart":
                        charts.plot_bar(data, metric_on_y, metric_on_x, None)
                    elif chart_type == "Area chart":
                        charts.plot_area(data, metric_on_y, metric_on_x, None)

                with tab2:
                    helpers.data_grid(data)
                    helpers.data_download_button(data, f"{metric_on_y}_vs_{metric_on_x}")
            with col2:
                metric_on_y = 'gasPrice'
                metric_on_x = 'datetime'
                data = quantitative_df[['network', metric_on_y, metric_on_x]]

                tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
                with tab1:
                    if chart_type == "Line chart":
                        charts.plot_line(data, metric_on_y, metric_on_x, None)
                    elif chart_type == "Bar chart":
                        charts.plot_bar(data, metric_on_y, metric_on_x, None)
                    elif chart_type == "Area chart":
                        charts.plot_area(data, metric_on_y, metric_on_x, None)

                with tab2:
                    helpers.data_grid(data)
                    helpers.data_download_button(data, f"{metric_on_y}_vs_{metric_on_x}")

        with st.container():
            st.markdown('---')
            st.markdown('##### Stats')

            default_index = config.metrics_with_stats.index('Transactions')
            metric = st.selectbox(
                'Metric',
                config.metrics_with_stats,
                index=default_index)

            # try:
            prefix = frequency + metric
            cols = ['network', 'datetime', f'{prefix}_count', f'{prefix}_sum',
                    f'{prefix}_mean', f'{prefix}_variance',
                    f'{prefix}_max', f'{prefix}_min',
                    f'{prefix}_q1', f'{prefix}_q3']
            if f'{prefix}_cumulative' in quantitative_df.columns:
                cols.append(f'{prefix}_cumulative')

            data = quantitative_df[cols]

            tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
            with tab1:
                if f'{prefix}_cumulative' in quantitative_df.columns:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        charts.plot_box(data, prefix, 'datetime', 'count')
                    with col2:
                        charts.plot_bar(
                            quantitative_df[['network', f'{prefix}_cumulative', 'datetime']], f'{prefix}_cumulative', 'datetime', None)
                else:
                    charts.plot_box(data, prefix, 'datetime', 'count')

            with tab2:
                helpers.data_grid(data, grid_height=320)
                helpers.data_download_button(data, prefix)
            # except:
            #     st.warning('No Data')

        with st.container():
            st.markdown('---')
            st.markdown('##### Or, plot any other metrics!')

            cols = sorted(config.metrics_without_stats + config.metrics_with_stats)

            col1, col2 = st.columns(2)
            with col1:
                default_index = cols.index('UniqueAuthors')
                metric_on_y = st.selectbox(
                    'Metric on y-axis',
                    cols,
                    index=default_index
                )
                if metric_on_y in config.metrics_with_stats:
                    stat = st.radio(
                        "Aggregate on",
                        ('count', 'mean', 'max', 'min', 'sum', 'variance', 'q1', 'q3', 'cumulative'),
                        horizontal=True,
                        key=time.time())
                    metric_on_y = f"{frequency}{metric_on_y}_{stat}"
            with col2:
                default_index = cols.index('blockHeight')
                metric_on_x = st.selectbox(
                    'Metric on x-axis',
                    cols,
                    index=default_index
                )
                if metric_on_x in config.metrics_with_stats:
                    stat = st.radio(
                        "Aggregate on",
                        ('count', 'mean', 'max', 'min', 'sum', 'variance', 'q1', 'q3', 'cumulative'),
                        horizontal=True,
                        key=time.time())
                    metric_on_x = f"{frequency}{metric_on_x}_{stat}"

            try:
                data = quantitative_df[['network', metric_on_y, metric_on_x]]

                tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
                with tab1:
                    if chart_type == "Line chart":
                        charts.plot_line(data, metric_on_y, metric_on_x, None)
                    elif chart_type == "Bar chart":
                        charts.plot_bar(data, metric_on_y, metric_on_x, None)
                    elif chart_type == "Area chart":
                        charts.plot_area(data, metric_on_y, metric_on_x, None)

                with tab2:
                    helpers.data_grid(data)
                    helpers.data_download_button(data, f"{metric_on_y}_vs_{metric_on_x}")
            except:
                st.warning('No Data')

    with st.expander("🔍 Explorers"):
        with st.container():
            st.markdown('##### Block Data')

            block_number = st.text_input('Enter block number', latest_snapshot['blockHeight'].iloc[0])
            block_author = ''
            if block_number != "" and block_number.isnumeric():
                block_df = asyncio.run(fetchers.get_block_snapshot(network, block_number))

                if not block_df.empty:
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        st.metric(label="ID", value=block_df['id'].iloc[0])
                    with col2:
                        st.metric(label="Hash", value=block_df['hash'].iloc[0])

                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric(label="Block Size", value=block_df['size'].iloc[0])
                        st.metric(label="Timestamp", value=block_df['timestamp'].iloc[0])
                    with col2:
                        st.metric(label="Gas Used", value=block_df['gasUsed'].iloc[0])
                        st.metric(label="Gas Limit", value=block_df['gasLimit'].iloc[0])
                        st.metric(label="Gas Price", value=block_df['gasPrice'].iloc[0])
                    with col3:
                        st.metric(label="Base Fee per Gas", value=block_df['baseFeePerGas'].iloc[0])
                        st.metric(label="Burnt Fee", value=block_df['burntFees'].iloc[0])
                    with col4:
                        st.metric(label="Author", value=block_df['author.id'].iloc[0])
                        st.metric(label="Difficulty", value=block_df['difficulty'].iloc[0])
                        st.metric(label="Rewards", value=block_df['rewards'].iloc[0])
                    with col5:
                        st.metric(label="Block Utilization", value=block_df['blockUtilization'].iloc[0])
                        st.metric(label="Transaction Count", value=block_df['transactionCount'].iloc[0])
                        st.metric(label="Chunk Count", value=block_df['chunkCount'].iloc[0])

                    block_author = block_df['author.id'].iloc[0]
                else:
                    st.warning('No Data')
            else:
                st.error('Invalid Input')

        with st.container():
            st.markdown('---')
            st.markdown('##### Author Data')

            author_id = st.text_input('Enter author address', block_author)
            if author_id != "":
                author_df = asyncio.run(fetchers.get_author_snapshot(network, author_id))

                if not author_df.empty:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.metric(label="ID", value=author_df['id'].iloc[0])
                    with col2:
                        st.metric(label="Cumulative Difficulty", value=author_df['cumulativeDifficulty'].iloc[0])
                        st.metric(label="Cumulative Blocks Created", value=author_df['cumulativeBlocksCreated'].iloc[0])
                else:
                    st.warning('No Data')

    holder = st.empty()
    try:
        with holder.expander("✳️ Nakamoto Coefficients"):
            with st.container():
                data = quantitative_df[['blockHeight', 'datetime']]

                data['day'] = data["datetime"].apply(lambda x: x.strftime("%d"))
                blocks = data[data["day"] == '01']["blockHeight"].tolist()

                author_df = fetchers.author_data(network, config.deployments[network], blocks)
                # st.write(author_df)

                # author_df = asyncio.run(fetchers.get_author_snapshots(network, blocks))
                # st.write(author_df)

                block_timestamp_dict = (
                    data[["blockHeight", "datetime"]]
                    .set_index("blockHeight")
                    .to_dict()
                )
                author_df["datetime"] = author_df["height"].apply(
                    lambda x: block_timestamp_dict["datetime"][x]
                )

                author_df = author_df.set_index(["network", "height", "datetime", "id"])  # set index as (height, id)
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
                        "blocksAuthored_q3": blocks_mined_q3,
                        "blocksAuthored_q1": blocks_mined_q1,
                    }
                    tmp_list.append(tmp_dict)

                author_stats = pd.DataFrame(tmp_list)

            with st.container():
                tab1, tab2 = st.tabs(["📈 Chart", "🗃 Data"])
                with tab1:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('##### Realized Nakamoto')

                        metric_on_y = 'nakamoto_realized'
                        metric_on_x = 'date'
                        data = author_stats[['network', metric_on_y, metric_on_x]]

                        charts.plot_line(data, metric_on_y, metric_on_x, None)
                    with col2:
                        st.markdown('##### Blocks Authored')

                        charts.plot_box(author_stats, 'blocksAuthored', 'date', 'sum')
                with tab2:
                    helpers.data_grid(author_stats)
                    helpers.data_download_button(author_stats, 'prefix')
    except:
        holder.empty()
else:
    st.warning('No Data in Time Range')
