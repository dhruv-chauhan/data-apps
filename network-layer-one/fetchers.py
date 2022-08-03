import streamlit as st
from subgrounds.subgrounds import Subgrounds
from datetime import datetime
import json

import config

sg = Subgrounds()


def create_stats_obj(count, mean, median, max, min, sum, variance, upper_quartile, lower_quartile):
    return json.dumps({
        "count": count,
        "mean": mean,
        "median": median,
        "max": max,
        "min": min,
        "sum": sum,
        "variance": variance,
        "upper_quartile": upper_quartile,
        "lower_quartile": lower_quartile
    })


@st.cache
def quantitative_data(network, deployment, frequency, from_unix, to_unix):
    subgraph = sg.load_subgraph(deployment)
    if frequency == 'Daily':
        records = subgraph.Query.dailySnapshots(
            orderBy=subgraph.DailySnapshot.timestamp,
            orderDirection='desc',
            where=[subgraph.DailySnapshot.timestamp >= from_unix,
                   subgraph.DailySnapshot.timestamp <= to_unix]
        )

        df = sg.query_df([
            records.id,
            records.blockHeight,
            records.dailyBlocks,
            records.timestamp,
            records.cumulativeUniqueAuthors,
            records.cumulativeDifficulty,
            records.cumulativeGasUsed,
            records.cumulativeBurntFees,
            records.cumulativeRewards,
            records.cumulativeSize,
            records.totalSupply,
            records.cumulativeTransactions,
            records.gasPrice,

            records.dailyUniqueAuthors,
            records.dailyDifficulty,
            records.dailyGasUsed,
            records.dailyGasLimit,
            records.dailyBurntFees,
            records.dailyRewards,
            records.dailySize,
            records.dailyChunks,
            records.dailySupply,
            records.dailyTransactions,
            records.dailyBlockInterval,
            records.dailyGasPrice,
        ])

        df = df.rename(columns=lambda x: x[len("dailySnapshots_"):])
        for field in config.fields_with_stats:
            df[field] = df.apply(
                lambda x: create_stats_obj(
                    x[f'daily{field}_count'],
                    x[f'daily{field}_mean'],
                    x[f'daily{field}_median'],
                    x[f'daily{field}_max'],
                    x[f'daily{field}_min'],
                    x[f'daily{field}_sum'],
                    x[f'daily{field}_variance'],
                    x[f'daily{field}_q1'],
                    x[f'daily{field}_q3']
                ), axis=1
            )
        df["blocks"] = df['dailyBlocks']

    if frequency == 'Hourly':
        records = subgraph.Query.hourlySnapshots(
            orderBy=subgraph.HourlySnapshot.timestamp,
            orderDirection='desc',
            where=[subgraph.HourlySnapshot.timestamp >= from_unix,
                   subgraph.HourlySnapshot.timestamp <= to_unix]
        )

        df = sg.query_df([
            records.id,
            records.blockHeight,
            records.hourlyBlocks,
            records.timestamp,
            records.cumulativeUniqueAuthors,
            records.cumulativeDifficulty,
            records.cumulativeGasUsed,
            records.cumulativeBurntFees,
            records.cumulativeRewards,
            records.cumulativeSize,
            records.totalSupply,
            records.cumulativeTransactions,
            records.gasPrice,

            records.hourlyUniqueAuthors,
            records.hourlyDifficulty,
            records.hourlyGasUsed,
            records.hourlyGasLimit,
            records.hourlyBurntFees,
            records.hourlyRewards,
            records.hourlySize,
            records.hourlyChunks,
            records.hourlySupply,
            records.hourlyTransactions,
            records.hourlyBlockInterval,
            records.hourlyGasPrice,
        ])

        df = df.rename(columns=lambda x: x[len("hourlySnapshots_"):])
        for field in config.fields_with_stats:
            df[field] = df.apply(
                lambda x: create_stats_obj(
                    x[f'hourly{field}_count'],
                    x[f'hourly{field}_mean'],
                    x[f'hourly{field}_median'],
                    x[f'hourly{field}_max'],
                    x[f'hourly{field}_min'],
                    x[f'hourly{field}_sum'],
                    x[f'hourly{field}_variance'],
                    x[f'hourly{field}_q1'],
                    x[f'hourly{field}_q3']
                ), axis=1
            )
        df["blocks"] = df['hourlyBlocks']

    df["network"] = network
    df["timestamp"] = df["timestamp"].apply(
        lambda x: datetime.fromtimestamp(x))

    df = df.fillna(0)
    df = df.astype({
        'blockHeight': 'int',
        'blocks': 'int',
        'cumulativeUniqueAuthors': 'int',
        'cumulativeDifficulty': 'float',
        'cumulativeGasUsed': 'float',
        'cumulativeBurntFees': 'float',
        'cumulativeRewards': 'float',
        'cumulativeSize': 'float',
        'totalSupply': 'float',
        'cumulativeTransactions': 'float',
        'gasPrice': 'float'
    })

    return df


@st.cache
def block_data(network, deployment, block_range):
    subgraph = sg.load_subgraph(deployment)
    records = subgraph.Query.blocks(
        orderBy=subgraph.Block.id,
        orderDirection='desc',
        where=[subgraph.Block.id > block_range['first'],
               subgraph.Block.id <= block_range['last']]
    )

    df = sg.query_df([
        records.id,
        records.hash,
        records.timestamp,
        records.author.id,
        records.size,
        records.baseFeePerGas,
        records.difficulty,
        records.gasLimit,
        records.gasUsed,
        records.blockUtilization,
        records.gasPrice,
        records.burntFees,
        records.chunkCount,
        records.transactionCount,
        records.rewards
    ])
    df = df.rename(columns=lambda x: x[len("blocks_"):])

    df["network"] = network
    df["timestamp"] = df["timestamp"].apply(
        lambda x: datetime.fromtimestamp(x))

    df = df.fillna(0)
    df = df.astype({
        'size': 'float',
        'baseFeePerGas': 'float',
        'difficulty': 'float',
        'gasLimit': 'float',
        'gasUsed': 'float',
        'blockUtilization': 'float',
        'gasPrice': 'float',
        'burntFees': 'float',
        'chunkCount': 'int',
        'transactionCount': 'int',
        'rewards': 'float'
    })

    return df
