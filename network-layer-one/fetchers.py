import os
import time
import asyncio
import logging
import pandas as pd
import streamlit as st
from threading import Thread
from datetime import datetime
from aiohttp import ClientSession
from subgrounds.subgrounds import Subgrounds
from streamlit.runtime.scriptrunner.script_run_context import add_script_run_ctx

import config
import helpers


async def loop_query(session, network, query):
    start_time = time.time()

    url = config.deployments[network]
    data = []

    continue_loop = True
    while continue_loop:
        async with session.post(url, json=query) as response:
            response = await response.json()
            if "data" not in response:
                logging.error(f">> no data,\n response: {response}\n query: {query}")
                return data

            response_data = response["data"]["data"]
            data.extend(response_data)

            if len(response_data) != query["variables"]["first"]:
                continue_loop = False
            else:
                df = pd.DataFrame(response_data)
                query["variables"]["id"] = df["id"].max()

    logging.info(">> query %s\n took %s seconds" %
                 (query, time.time() - start_time))

    return data


# Quantitative Data

async def get_daily_quantitative_data(session, network):
    q = """
    query($first: Int, $id: ID!) {
        data: dailySnapshots (first: $first, orderBy: id, orderDirection: asc, where: {id_gt: $id}) {
            id,
            blockHeight,
            dailyBlocks,
            timestamp,
            cumulativeUniqueAuthors,
            cumulativeDifficulty,
            cumulativeGasUsed,
            cumulativeBurntFees,
            cumulativeRewards,
            cumulativeSize,
            totalSupply,
            cumulativeTransactions,
            gasPrice,
            dailyUniqueAuthors {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            dailyDifficulty {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            dailyGasUsed {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            dailyGasLimit {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            dailyBurntFees {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            dailyRewards {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            dailySize {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            dailyChunks {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            dailySupply {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            dailyBlockInterval {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            dailyGasPrice {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            dailyTransactions {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            }
        }
    }
    """

    query = {
        "query": q,
        "variables": {
            "first": 1000,
            "id": "0",
        },
    }

    data = await loop_query(session, network, query)

    return (network, 'daily', data)


async def get_hourly_quantitative_data(session, network):
    q = """
    query($first: Int, $id: ID!) {
        data: hourlySnapshots (first: $first, orderBy: id, orderDirection: asc, where: {id_gt: $id}) {
            id,
            blockHeight,
            hourlyBlocks,
            timestamp,
            cumulativeUniqueAuthors,
            cumulativeDifficulty,
            cumulativeGasUsed,
            cumulativeBurntFees,
            cumulativeRewards,
            cumulativeSize,
            totalSupply,
            cumulativeTransactions,
            gasPrice,
            hourlyUniqueAuthors {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            hourlyDifficulty {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            hourlyGasUsed {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            hourlyGasLimit {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            hourlyBurntFees {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            hourlyRewards {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            hourlySize {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            hourlyChunks {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            hourlySupply {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            hourlyBlockInterval {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            hourlyGasPrice {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            },
            hourlyTransactions {
                count
                mean
                max
                min
                sum
                variance
                q3
                q1
            }
        }
    }
    """

    query = {
        "query": q,
        "variables": {
            "first": 1000,
            "id": "0",
        },
    }

    data = await loop_query(session, network, query)

    return (network, 'hourly', data)


async def update_snapshots(network, frequency):
    logging.info(f">> updating {network} {frequency} snapshots")

    async with ClientSession() as session:
        if frequency == 'hourly':
            res = await get_hourly_quantitative_data(session, network)
        else:
            res = await get_daily_quantitative_data(session, network)

        file_path = f"snapshots/{res[1]}/{res[0]}.json"
        helpers.write_to_file(file_path, res[2])

        return file_path


async def get_snapshots(network, frequency, from_unix, to_unix):
    start_time = time.time()

    file_path = f"snapshots/{frequency}/{network}.json"
    if not os.path.isfile(file_path):
        file_path = await update_snapshots(network, frequency)

    df = pd.json_normalize(helpers.read_from_file(file_path))
    if len(df.index) == 0 or df.empty:
        return df

    df = helpers.date_filter_df(df, from_unix, to_unix)
    if len(df.index) == 0 or df.empty:
        return df

    df = df.sort_values(by=['timestamp'], ascending=False)
    df = df.reset_index(drop=True)
    df = df.iloc[1:, :]
    df = df.fillna(0)

    df = df.rename({
        f'{frequency}Blocks': 'blocks',
        'cumulativeUniqueAuthors': f'{frequency}UniqueAuthors_cumulative',
        'cumulativeDifficulty': f'{frequency}Difficulty_cumulative',
        'cumulativeGasUsed': f'{frequency}GasUsed_cumulative',
        'cumulativeBurntFees': f'{frequency}BurntFees_cumulative',
        'cumulativeRewards': f'{frequency}Rewards_cumulative',
        'cumulativeSize': f'{frequency}Size_cumulative',
        'cumulativeTransactions': f'{frequency}Transactions_cumulative',
    }, axis='columns')

    for metric in config.metrics_with_stats:
        df[metric] = df.apply(
            lambda x: helpers.create_stats_obj(
                x[f'{frequency}{metric}.count'] if f'{frequency}{metric}.count' in df.columns else None,
                x[f'{frequency}{metric}.mean'] if f'{frequency}{metric}.mean' in df.columns else None,
                x[f'{frequency}{metric}.max'] if f'{frequency}{metric}.max' in df.columns else None,
                x[f'{frequency}{metric}.min'] if f'{frequency}{metric}.min' in df.columns else None,
                x[f'{frequency}{metric}.sum'] if f'{frequency}{metric}.sum' in df.columns else None,
                x[f'{frequency}{metric}.variance'] if f'{frequency}{metric}.variance' in df.columns else None,
                x[f'{frequency}{metric}.q1'] if f'{frequency}{metric}.q1' in df.columns else None,
                x[f'{frequency}{metric}.q3'] if f'{frequency}{metric}.q3' in df.columns else None,
                x[f'{frequency}{metric}_cumulative'] if f'{frequency}{metric}_cumulative' in df.columns else None,
            ), axis=1
        )

        if f'{frequency}{metric}.count' in df.columns:
            df = df.rename(
                {f'{frequency}{metric}.count': f'{frequency}{metric}_count'}, axis='columns')
            df = df.astype({f'{frequency}{metric}_count': 'int'})
        if f'{frequency}{metric}.mean' in df.columns:
            df = df.rename(
                {f'{frequency}{metric}.mean': f'{frequency}{metric}_mean'}, axis='columns')
            df = df.astype({f'{frequency}{metric}_mean': 'float'})
        if f'{frequency}{metric}.max' in df.columns:
            df = df.rename({f'{frequency}{metric}.max': f'{frequency}{metric}_max'}, axis='columns')
            df = df.astype({f'{frequency}{metric}_max': 'float'})
        if f'{frequency}{metric}.min' in df.columns:
            df = df.rename({f'{frequency}{metric}.min': f'{frequency}{metric}_min'}, axis='columns')
            df = df.astype({f'{frequency}{metric}_min': 'float'})
        if f'{frequency}{metric}.sum' in df.columns:
            df = df.rename({f'{frequency}{metric}.sum': f'{frequency}{metric}_sum'}, axis='columns')
            df = df.astype({f'{frequency}{metric}_sum': 'float'})
        if f'{frequency}{metric}.variance' in df.columns:
            df = df.rename(
                {f'{frequency}{metric}.variance': f'{frequency}{metric}_variance'}, axis='columns')
            df = df.astype({f'{frequency}{metric}_variance': 'float'})
        if f'{frequency}{metric}.q1' in df.columns:
            df = df.rename({f'{frequency}{metric}.q1': f'{frequency}{metric}_q1'}, axis='columns')
            df = df.astype({f'{frequency}{metric}_q1': 'float'})
        if f'{frequency}{metric}.q3' in df.columns:
            df = df.rename({f'{frequency}{metric}.q3': f'{frequency}{metric}_q3'}, axis='columns')
            df = df.astype({f'{frequency}{metric}_q3': 'float'})
        if f'{frequency}{metric}_cumulative' in df.columns:
            df = df.astype({f'{frequency}{metric}_cumulative': 'float'})

    df = df.astype({
        'blockHeight': 'int',
        'blocks': 'int',
        'totalSupply': 'float',
        'gasPrice': 'float'
    })

    df["network"] = network
    df["datetime"] = df["timestamp"].apply(
        lambda x: datetime.fromtimestamp(int(x)))

    logging.info(">> %s %s quantitative data took %s seconds" % (network, frequency, time.time() - start_time))

    return df


async def update_snapshots_all_networks():
    start_time = time.time()

    logging.info(">> updating all network daily and hourly snapshots in background")
    st.session_state['are_snapshots_updated'] = 0

    async with ClientSession() as session:
        networks = config.deployments.keys()
        tasks = []
        for network in networks:
            tasks.append(asyncio.ensure_future(get_daily_quantitative_data(session, network)))
            tasks.append(asyncio.ensure_future(get_hourly_quantitative_data(session, network)))

        res = await asyncio.gather(*tasks)
        for r in res:
            file_path = f"snapshots/{r[1]}/{r[0]}.json"
            helpers.write_to_file(file_path, r[2])

        st.session_state['are_snapshots_updated'] = 1

        logging.info(">> refreshing all network quantitative data took %s seconds" % (time.time() - start_time))

        return


def refresh_snapshots():
    thread = Thread(target=asyncio.run, args=(update_snapshots_all_networks(),), daemon=True)
    add_script_run_ctx(thread)
    thread.start()

    return


# Block Data

async def get_block_data(session, network, block_id):
    q = """
    query($first: Int, $id: ID!) {
        data: blocks (first: $first, orderBy: id, orderDirection: desc, where: {id: $id}) {
            id,
            hash,
            timestamp,
            author {
                id
                cumulativeDifficulty
                cumulativeBlocksCreated
            },
            size,
            baseFeePerGas,
            difficulty,
            gasLimit,
            gasUsed,
            blockUtilization,
            gasPrice,
            burntFees,
            chunkCount,
            transactionCount,
            rewards,
        }
    }
    """

    query = {
        "query": q,
        "variables": {
            "first": 1000,
            "id": int(block_id),
        },
    }

    data = await loop_query(session, network, query)

    return data


async def get_block_snapshot(network, block_id):
    start_time = time.time()

    df = pd.DataFrame()

    async with ClientSession() as session:
        data = await get_block_data(session, network, block_id)
        df = pd.json_normalize(data)

        logging.info(">> block data took %s seconds for block_id: %s" %
                     (time.time() - start_time, block_id))

        return df


# Author Data

async def get_author_data(session, network, author_id):
    q = """
    query($first: Int, $author_id: String!) {
        data: authors(first: $first, orderBy: id, orderDirection: asc, where: {id: $author_id}) {
            id
            cumulativeDifficulty
            cumulativeBlocksCreated
        }
    }
    """

    query = {
        "query": q,
        "variables": {
            "first": 1000,
            "author_id": author_id,
        },
    }

    data = await loop_query(session, network, query)

    return data


async def get_author_snapshot(network, author_id):
    start_time = time.time()

    df = pd.DataFrame()

    async with ClientSession() as session:
        data = await get_author_data(session, network, author_id)
        df = pd.json_normalize(data)

        logging.info(">> author data took %s seconds for author_id: %s" %
                     (time.time() - start_time, author_id))

        return df


# async def get_author_snapshots(network, blocks):
#     start_time = time.time()

#     df = pd.DataFrame()

#     async with ClientSession() as session:
#         for block_id in blocks:
#             data = await get_block_data(session, network, block_id)
#             df_block = pd.json_normalize(data)

#             df_block = df_block[['author.id', 'author.cumulativeDifficulty', 'author.cumulativeBlocksCreated']]
#             df_block["height"] = block_id
#             df = pd.concat([df, df_block], axis=0)

#         df = df.reset_index(drop=True)
#         df = df.rename({
#             'author.id': 'id',
#             'author.cumulativeDifficulty': 'cumulativeDifficulty',
#             'author.cumulativeBlocksCreated': 'cumulativeBlocksCreated',
#         }, axis='columns')

#         df["network"] = network

#         df = df.fillna(0)
#         df = df.astype({
#             'id': 'str',
#             'cumulativeDifficulty': 'float',
#             'cumulativeBlocksCreated': 'float'
#         })

#         logging.info(">> author data took %s seconds for blocks: %s" %
#                      (time.time() - start_time, blocks))

#         return df


# Nakamoto Coefficient Data

sg = Subgrounds()


@st.cache(allow_output_mutation=True)
def author_data(network, deployment, blocks):
    df = pd.DataFrame()
    for block in blocks:
        subgraph = sg.load_subgraph(deployment)
        records = subgraph.Query.authors(
            orderBy=subgraph.Author.cumulativeBlocksCreated,
            orderDirection='desc',
            block={'number': block},
            first=5000
        )

        authors = sg.query_df([
            records.id,
            records.cumulativeDifficulty,
            records.cumulativeBlocksCreated,
        ])
        authors = authors.rename(columns=lambda x: x[len("authors_"):])

        authors["height"] = block

        df = pd.concat([df, authors]).reset_index(drop=True)

    df["network"] = network

    df = df.fillna(0)
    df = df.astype({
        'cumulativeDifficulty': 'float',
        'cumulativeBlocksCreated': 'float'
    })

    return df
