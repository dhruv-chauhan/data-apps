import streamlit as st
from subgrounds.subgrounds import Subgrounds
from datetime import datetime

sg = Subgrounds()


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
            records.firstTimestamp,
            records.timestamp,
            records.cumulativeUniqueAuthors,
            records.cumulativeDifficulty,
            records.cumulativeBurntFees,
            records.cumulativeRewards,
            records.cumulativeSize,
            records.totalSupply,
            records.gasPrice,
            records.dailyActiveAuthors,
            records.dailyBlocks,
            records.dailyDifficulty,
            records.dailyMeanDifficulty,
            records.dailyCumulativeGasUsed,
            records.dailyCumulativeGasLimit,
            records.dailyBlockUtilization,
            records.dailyMeanGasUsed,
            records.dailyMeanGasLimit,
            records.dailyBurntFees,
            records.dailyRewards,
            records.dailyMeanRewards,
            records.dailySupplyIncrease,
            records.dailyMeanBlockInterval,
            records.dailyCumulativeSize,
            records.dailyMeanBlockSize,
            records.dailyChunkCount,
            records.dailyTransactionCount,
            records.firstSupply
        ])
        df = df.rename(columns=lambda x: x[len("dailySnapshots_"):])
        df.astype({
            'dailyActiveAuthors': 'int',
            'dailyBlocks': 'int',
            'dailyDifficulty': 'float',
            'dailyMeanDifficulty': 'float',
            'dailyCumulativeGasUsed': 'float',
            'dailyCumulativeGasLimit': 'float',
            'dailyBlockUtilization': 'float',
            'dailyMeanGasUsed': 'float',
            'dailyMeanGasLimit': 'float',
            'dailyBurntFees': 'float',
            'dailyRewards': 'float',
            'dailyMeanRewards': 'float',
            'dailySupplyIncrease': 'float',
            'dailyMeanBlockInterval': 'float',
            'dailyCumulativeSize': 'float',
            'dailyMeanBlockSize': 'float',
            'dailyChunkCount': 'int',
            'dailyTransactionCount': 'int'
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
            records.firstTimestamp,
            records.timestamp,
            records.cumulativeUniqueAuthors,
            records.cumulativeDifficulty,
            records.cumulativeBurntFees,
            records.cumulativeRewards,
            records.cumulativeSize,
            records.totalSupply,
            records.gasPrice,
            records.hourlyActiveAuthors,
            records.hourlyBlocks,
            records.hourlyDifficulty,
            records.hourlyMeanDifficulty,
            records.hourlyCumulativeGasUsed,
            records.hourlyCumulativeGasLimit,
            records.hourlyBlockUtilization,
            records.hourlyMeanGasUsed,
            records.hourlyMeanGasLimit,
            records.hourlyBurntFees,
            records.hourlyRewards,
            records.hourlyMeanRewards,
            records.hourlySupplyIncrease,
            records.hourlyMeanBlockInterval,
            records.hourlyCumulativeSize,
            records.hourlyMeanBlockSize,
            records.hourlyChunkCount,
            records.hourlyTransactionCount,
            records.firstSupply
        ])
        df = df.rename(columns=lambda x: x[len("hourlySnapshots_"):])
        df.astype({
            'hourlyActiveAuthors': 'int',
            'hourlyBlocks': 'int',
            'hourlyDifficulty': 'float',
            'hourlyMeanDifficulty': 'float',
            'hourlyCumulativeGasUsed': 'float',
            'hourlyCumulativeGasLimit': 'float',
            'hourlyBlockUtilization': 'float',
            'hourlyMeanGasUsed': 'float',
            'hourlyMeanGasLimit': 'float',
            'hourlyBurntFees': 'float',
            'hourlyRewards': 'float',
            'hourlyMeanRewards': 'float',
            'hourlySupplyIncrease': 'float',
            'hourlyMeanBlockInterval': 'float',
            'hourlyCumulativeSize': 'float',
            'hourlyMeanBlockSize': 'float',
            'hourlyChunkCount': 'int',
            'hourlyTransactionCount': 'int'
        })

    df["network"] = network
    df["timestamp"] = df["timestamp"].apply(
        lambda x: datetime.fromtimestamp(x))
    df["firstTimestamp"] = df["firstTimestamp"].apply(
        lambda x: datetime.fromtimestamp(x))
    df.astype({
        'blockHeight': 'int',
        'cumulativeUniqueAuthors': 'int',
        'cumulativeDifficulty': 'float',
        'cumulativeBurntFees': 'float',
        'cumulativeRewards': 'float',
        'cumulativeSize': 'float',
        'totalSupply': 'float',
        'gasPrice': 'float',
        'firstSupply': 'float'
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
    df.astype({
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
