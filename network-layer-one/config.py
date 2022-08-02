schema = "https://github.com/messari/subgraphs/blob/master/subgraphs/network/schema.graphql"
deployments = {
    "Arbitrum One":
        "https://api.thegraph.com/subgraphs/name/messari/network-arbitrum",
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
    "Fantom":
        "https://api.thegraph.com/subgraphs/name/messari/network-fantom",
    "Fuse":
        "https://api.thegraph.com/subgraphs/name/messari/network-fuse",
    "Harmony":
        "https://api.thegraph.com/subgraphs/name/messari/network-harmony",
    # "Mainnet":
    #     "https://api.thegraph.com/subgraphs/name/messari/network-ethereum",               [OLD SCHEMA]
    "Matic":
        "https://api.thegraph.com/subgraphs/name/messari/network-polygon",
    # "Moonbeam":
    #     "https://api.thegraph.com/subgraphs/name/messari/network-moonbeam",               [OLD SCHEMA]
    "Moonriver":
        "https://api.thegraph.com/subgraphs/name/messari/network-moonriver",
    "Optimism":
        "https://api.thegraph.com/subgraphs/name/messari/network-optimism",
    "xDai":
        "https://api.thegraph.com/subgraphs/name/messari/network-gnosis",
    "Arweave":
        "https://api.thegraph.com/subgraphs/name/messari/network-arweave-mainnet",
    # "Cosmos":
    #     "https://api.thegraph.com/subgraphs/name/messari/network-cosmos",                 [OLD SCHEMA]
    "Osmosis":
        "https://api.thegraph.com/subgraphs/name/messari/network-osmosis",
    "NEAR":
        "https://api.thegraph.com/subgraphs/name/messari/network-near"
}

fields_without_stats = ["network", "blockHeight", "blocks", "timestamp", "cumulativeUniqueAuthors", "cumulativeDifficulty",
                        "cumulativeGasUsed", "cumulativeBurntFees", "cumulativeRewards", "cumulativeSize", "totalSupply", "cumulativeTransactions", "gasPrice"]
fields_with_stats = ["UniqueAuthors", "Difficulty", "GasUsed", "GasLimit", "BurntFees", "Rewards",
                     "Size", "Chunks", "Supply", "Transactions", "BlockInterval", "BlockInterval", "GasPrice"]
