schema = "https://github.com/messari/subgraphs/blob/master/subgraphs/network/schema.graphql"
deployments = {
    "Arbitrum One":
        "https://api.thegraph.com/subgraphs/name/messari/network-arbitrum",
    "Arweave":
        "https://api.thegraph.com/subgraphs/name/messari/network-arweave-mainnet",
    "Aurora":
        "https://api.thegraph.com/subgraphs/name/messari/network-aurora",
    "Avalanche":
        "https://api.thegraph.com/subgraphs/name/messari/network-avalanche",
    "Boba":
        "https://api.thegraph.com/subgraphs/name/messari/network-boba",
    "BSC":
        "https://api.thegraph.com/subgraphs/name/messari/network-bsc",
    "Celo":
        "https://api.thegraph.com/subgraphs/name/messari/network-celo",
    # "Clover":
    #     "https://api.thegraph.com/subgraphs/name/messari/network-clover",
    "Cosmos":
        "https://api.thegraph.com/subgraphs/name/messari/network-cosmos",
    "Ethereum":
        "https://api.thegraph.com/subgraphs/name/messari/network-ethereum",
    "Fantom":
        "https://api.thegraph.com/subgraphs/name/messari/network-fantom",
    "Fuse":
        "https://api.thegraph.com/subgraphs/name/messari/network-fuse",
    "Harmony":
        "https://api.thegraph.com/subgraphs/name/messari/network-harmony",
    "Matic":
        "https://api.thegraph.com/subgraphs/name/messari/network-polygon",
    "Moonbeam":
        "https://api.thegraph.com/subgraphs/name/messari/network-moonbeam",
    "Moonriver":
        "https://api.thegraph.com/subgraphs/name/messari/network-moonriver",
    "NEAR":
        "https://api.thegraph.com/subgraphs/name/messari/network-near",
    "Optimism":
        "https://api.thegraph.com/subgraphs/name/messari/network-optimism",
    "Osmosis":
        "https://api.thegraph.com/subgraphs/name/messari/network-osmosis",
    "xDai":
        "https://api.thegraph.com/subgraphs/name/messari/network-gnosis"
}

metrics_without_stats = ["network", "blockHeight",
                         "blocks", "timestamp", "datetime", "totalSupply", "gasPrice"]
metrics_with_stats = ["UniqueAuthors", "Difficulty", "GasUsed", "GasLimit", "BurntFees", "Rewards",
                      "Size", "Chunks", "Supply", "Transactions", "BlockInterval", "GasPrice"]
