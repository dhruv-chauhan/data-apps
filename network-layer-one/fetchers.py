import pandas as pd
import streamlit as st
from subgrounds.subgrounds import Subgrounds
from datetime import datetime
import json

import config

sg = Subgrounds()


def create_stats_obj(count, mean, max, min, sum, variance, upper_quartile, lower_quartile, cumulative=None):
    return json.dumps({
        "count": count,
        "mean": mean,
        "max": max,
        "min": min,
        "sum": sum,
        "variance": variance,
        "upper_quartile": upper_quartile,
        "lower_quartile": lower_quartile,
        "cumulative": cumulative
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

        df = df.fillna(0)
        df = df.rename(columns=lambda x: x[len("dailySnapshots_"):])
        df = df.rename({
            'dailyBlocks': 'blocks',
            'cumulativeUniqueAuthors': 'dailyUniqueAuthors_cumulative',
            'cumulativeDifficulty': 'dailyDifficulty_cumulative',
            'cumulativeGasUsed': 'dailyGasUsed_cumulative',
            'cumulativeBurntFees': 'dailyBurntFees_cumulative',
            'cumulativeRewards': 'dailyRewards_cumulative',
            'cumulativeSize': 'dailySize_cumulative',
            'cumulativeTransactions': 'dailyTransactions_cumulative',
        }, axis='columns')

        for metric in config.metrics_with_stats:
            df[metric] = df.apply(
                lambda x: create_stats_obj(
                    x[f'daily{metric}_count'],
                    x[f'daily{metric}_mean'],
                    x[f'daily{metric}_max'],
                    x[f'daily{metric}_min'],
                    x[f'daily{metric}_sum'],
                    x[f'daily{metric}_variance'],
                    x[f'daily{metric}_q1'],
                    x[f'daily{metric}_q3'],
                    x[f'daily{metric}_cumulative'] if f'daily{metric}_cumulative' in df.columns else None,
                ), axis=1
            )
            df = df.rename({
                f'daily{metric}_q1': f'daily{metric}_lower_quartile',
                f'daily{metric}_q3': f'daily{metric}_upper_quartile'
            }, axis='columns')
            df = df.astype({
                f'daily{metric}_count': 'int',
                f'daily{metric}_mean': 'float',
                f'daily{metric}_max': 'float',
                f'daily{metric}_min': 'float',
                f'daily{metric}_sum': 'float',
                f'daily{metric}_variance': 'float',
                f'daily{metric}_lower_quartile': 'float',
                f'daily{metric}_upper_quartile': 'float'
            })
        df = df.astype({
            'dailyUniqueAuthors_cumulative': 'int',
            'dailyDifficulty_cumulative': 'float',
            'dailyGasUsed_cumulative': 'float',
            'dailyBurntFees_cumulative': 'float',
            'dailyRewards_cumulative': 'float',
            'dailySize_cumulative': 'float',
            'dailyTransactions_cumulative': 'float',
        })

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

        df = df.fillna(0)
        df = df.rename(columns=lambda x: x[len("hourlySnapshots_"):])
        df = df.rename({
            'hourlyBlocks': 'blocks',
            'cumulativeUniqueAuthors': 'hourlyUniqueAuthors_cumulative',
            'cumulativeDifficulty': 'hourlyDifficulty_cumulative',
            'cumulativeGasUsed': 'hourlyGasUsed_cumulative',
            'cumulativeBurntFees': 'hourlyBurntFees_cumulative',
            'cumulativeRewards': 'hourlyRewards_cumulative',
            'cumulativeSize': 'hourlySize_cumulative',
            'cumulativeTransactions': 'hourlyTransactions_cumulative',
        }, axis='columns')

        for metric in config.metrics_with_stats:
            df[metric] = df.apply(
                lambda x: create_stats_obj(
                    x[f'hourly{metric}_count'],
                    x[f'hourly{metric}_mean'],
                    x[f'hourly{metric}_max'],
                    x[f'hourly{metric}_min'],
                    x[f'hourly{metric}_sum'],
                    x[f'hourly{metric}_variance'],
                    x[f'hourly{metric}_q1'],
                    x[f'hourly{metric}_q3'],
                    x[f'hourly{metric}_cumulative'] if f'hourly{metric}_cumulative' in df.columns else None,
                ), axis=1
            )
            df = df.rename({
                f'hourly{metric}_q1': f'hourly{metric}_lower_quartile',
                f'hourly{metric}_q3': f'hourly{metric}_upper_quartile'
            }, axis='columns')
            df = df.astype({
                f'hourly{metric}_count': 'int',
                f'hourly{metric}_mean': 'float',
                f'hourly{metric}_max': 'float',
                f'hourly{metric}_min': 'float',
                f'hourly{metric}_sum': 'float',
                f'hourly{metric}_variance': 'float',
                f'hourly{metric}_lower_quartile': 'float',
                f'hourly{metric}_upper_quartile': 'float'
            })
        df = df.astype({
            'hourlyUniqueAuthors_cumulative': 'int',
            'hourlyDifficulty_cumulative': 'float',
            'hourlyGasUsed_cumulative': 'float',
            'hourlyBurntFees_cumulative': 'float',
            'hourlyRewards_cumulative': 'float',
            'hourlySize_cumulative': 'float',
            'hourlyTransactions_cumulative': 'float',
        })
    df = df.astype({
        'blockHeight': 'int',
        'blocks': 'int',
        'totalSupply': 'float',
        'gasPrice': 'float'
    })

    df["network"] = network
    df["timestamp"] = df["timestamp"].apply(
        lambda x: datetime.fromtimestamp(x))

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


@st.cache
def author_data(network, deployment, blocks):
    df = pd.DataFrame()
    for block in blocks:
        subgraph = sg.load_subgraph(deployment)
        records = subgraph.Query.authors(
            orderBy=subgraph.Author.cumulativeBlocksCreated,
            orderDirection='desc',
            block={'number': block}
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
