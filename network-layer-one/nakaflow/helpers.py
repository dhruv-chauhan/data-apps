"""
Supporting helpers for Messari Subgraphs
"""

import pandas as pd
import requests

def get_network_subgraphs() -> pd.DataFrame:

    # TODO: make this programatic
    network_subgraphs = [
        {"name": "arweave-mainnet", "slug": "arweave", "nakamoto.ratio": 0},
        {"name": "arbitrum", "slug": "arbitrum", "nakamoto.ratio": 0},
        {"name": "aurora", "slug": "aurora-near", "nakamoto.ratio": 0},
        {"name": "avalanche", "slug": "avalanche", "nakamoto.ratio": 0},
        {"name": "boba", "slug": "boba-network", "nakamoto.ratio": 0},
        {"name": "bsc", "slug": "binance-coin", "nakamoto.ratio": 0},
        {"name": "celo", "slug": "celo", "nakamoto.ratio": 0},
        {"name": "clover", "slug": "clover-finance", "nakamoto.ratio": 0},
        {"name": "cronos", "slug": "cronos", "nakamoto.ratio": 0},
        {"name": "fantom", "slug": "fantom", "nakamoto.ratio": 0},
        {"name": "fuse", "slug": "fuse", "nakamoto.ratio": 0},
        {"name": "harmony", "slug": "harmony", "nakamoto.ratio": 0},
        {"name": "ethereum", "slug": "ethereum", "nakamoto.ratio": 0},
        {"name": "polygon", "slug": "polygon", "nakamoto.ratio": 0},
        {"name": "moonbeam", "slug": "moonbeam", "nakamoto.ratio": 0},
        {"name": "moonriver", "slug": "moonriver", "nakamoto.ratio": 0},
        {"name": "optimism", "slug": "optimism", "nakamoto.ratio": 0},
        {"name": "gnosis", "slug": "xdai", "nakamoto.ratio": 0},
        {"name": "cosmos", "slug": "cosmos", "nakamoto.ratio": 0},
        {"name": "osmosis", "slug": "osmosis", "nakamoto.ratio": 0},
        {"name": "near", "slug": "near-protocol", "nakamoto.ratio": 0},
    ]

    network_subgraphs = pd.DataFrame(network_subgraphs)
    network_subgraphs["url"] = network_subgraphs["name"].apply(
        lambda x: f"https://api.thegraph.com/subgraphs/name/messari/network-{x}"
    )
    return network_subgraphs


def date_filter_df(
    df: pd.DataFrame, start, end, col_name: str = "date"
) -> pd.DataFrame:
    """Helper for dt filtering by date column"""
    tmp_df = df[df[col_name] >= start]
    tmp_df = tmp_df[tmp_df[col_name] <= end]
    return tmp_df
