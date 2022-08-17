import streamlit as st
import pandas as pd
from PIL import Image
import datetime
import asyncio
import os

# Local imports
from network import Network
from helpers import (
    get_network_subgraphs,
    date_filter_df,
)
from charting import (
    plotly_box_plot,
    plotly_lines,
    clean_plotly_fig,
)

#### Helpers ####

#***** Config *****
st.set_page_config (
    page_icon="🚂",
    layout="wide"
)
st.title("Decentralization-Station 🚂")
st.caption('built by [@mikeykremer](https://twitter.com/mikeykremer) using [Messari Subgraphs](https://github.com/messari/subgraphs)')

with st.sidebar:
    st.write('Network Selection')

    network_subgraphs = get_network_subgraphs()
    networks = tuple(network_subgraphs['name'].tolist())

    network = st.selectbox('Network', networks)
    url = network_subgraphs[network_subgraphs['name']==network].get('url').iloc[0]
    messari_asset_slug = network_subgraphs[network_subgraphs['name']==network].get('slug').iloc[0]

    #***** Filters *****
    st.write('Filters')
    col1, col2 = st.columns(2)
    start_date = col1.date_input('start date', datetime.date(2021,1,1))
    end_date = col2.date_input('end date', datetime.datetime.now().date())

# Handling nework storage
if network not in st.session_state:
    nw = Network(url)
    st.session_state[network] = nw
else:
    nw = st.session_state[network]

st.write('### Daily Snapshots')
if nw.daily_snapshots.empty:
    with st.spinner(f'Getting {network} daily snapshots'):
        asyncio.run(nw.get_snapshots())
        st.session_state[network] = nw

col1, col2, col3 = st.columns(3)
daily_snaps = date_filter_df(nw.daily_snapshots, start_date, end_date)
col1.dataframe(daily_snaps)

gas_df = daily_snaps[['date', 'dailyMeanGasUsed', 'dailyMeanGasLimit']]
gas_df['gas.used.pct'] = gas_df['dailyMeanGasUsed'].astype(float) / gas_df['dailyMeanGasLimit'].astype(float)
gas_fig = plotly_lines(gas_df[['date','gas.used.pct']].set_index('date'))
gas_fig = clean_plotly_fig(gas_fig)
gas_fig.update_layout(title='<b>Gas Limit / Gas Used</b>')
col2.plotly_chart(gas_fig, use_container_width=True)

block_interval_fig = plotly_lines(daily_snaps[['date','dailyMeanBlockInterval']].set_index('date'))
block_interval_fig = clean_plotly_fig(block_interval_fig)
block_interval_fig.update_layout(title='<b>Mean Block interval</b>')
col3.plotly_chart(block_interval_fig, use_container_width=True)

col1, col2, col3 = st.columns(3)
daa_fig = plotly_lines(daily_snaps[['date','dailyActiveAuthors']].set_index('date'))
daa_fig = clean_plotly_fig(daa_fig)
daa_fig.update_layout(title='<b>Daily Active Authors</b>')
col1.plotly_chart(daa_fig, use_container_width=True)

rewards_fig = plotly_lines(daily_snaps[['date','dailyMeanRewards']].set_index('date'))
rewards_fig = clean_plotly_fig(rewards_fig)
rewards_fig.update_layout(title='<b>Daily Mean Rewards</b>')
col2.plotly_chart(rewards_fig, use_container_width=True)

image = Image.open(os.path.join(os.path.dirname(__file__), 'media/loser.jpeg'))
col3.image(image, caption='Winners care about decentralization')

# Active authors
# txn count
# mean block interval
# mean gas used
# Burnt fees
# mean difficulty
# mean rewards
# cum size
# mean rewards
# cum size
# mean block size


st.write('### Nakamoto Analysis')
if nw.author_stats.empty:
    with st.spinner(f'Getting {network} author stats, be patient. The longer this takes the more decentralized the project (typically).'):
        asyncio.run(nw.get_author_stats())
        st.session_state[network] = nw

col1, col2, col3 = st.columns(3)
author_stats = date_filter_df(nw.author_stats, start_date, end_date)
col1.dataframe(author_stats)

real_nak_fig = plotly_lines(author_stats.set_index('date')[['nakamoto.realized']])
real_nak_fig = clean_plotly_fig(real_nak_fig)
real_nak_fig.update_layout(
    title='<b>Realized Nakamoto Coefficient</b>',
)
col2.plotly_chart(real_nak_fig, use_container_width=True)

author_stats_fig = plotly_box_plot(
    author_stats.set_index('date'),
    'blocks.authored',
    mean=False,
    upper=False,
    lower=False
)
author_stats_fig = clean_plotly_fig(author_stats_fig)
author_stats_fig.update_layout(
    title='<b>Blocks Authored Distribution</b>',
)
col3.plotly_chart(author_stats_fig, use_container_width=True)

st.write('### Glossary')

col1, col2 = st.columns(2)
col1.dataframe(network_subgraphs)
col1.markdown("""
##### further reading
[The Economics of Proof-of-Stake Rewards](https://messari.io/article/the-economics-of-proof-of-stake-rewards) By Florent Moulin

[What's at Stake in Staking-as-a-Service](https://messari.io/article/what-s-at-stake-in-staking-as-a-service) By Chase Devens & Rasheed Saleuddin

[Nakamoto Consesnus](https://messari.io/article/nakamoto-consensus) By Messari

[Why Decentralization Matters](https://onezero.medium.com/why-decentralization-matters-5e3f79f7638e) By Chris Dixon

[The Meaning of Decentralization](https://medium.com/@VitalikButerin/the-meaning-of-decentralization-a0c92b76a274) By Vitalik Buterin
""")

col2.markdown('''
**Nakamoto Coefficient:**
The Nakamoto coefficient is the minimum number of authors which can conspire to create a critical majority.
While there is more nuance to decentralization than Nakamoto Coefficient (blockchain design really matters),
this is a decent enough proxy for decentralization.
However, it's safe to say the bigger the nakamoto coefficient the better.
I'm also going to make a personal interjection here that no chain is sufficiently decentralized.
Any Nakamoto Coefficient below 1000 is too small,
notice how abysmally far away we all are from this.

**Nakamoto Ratio:** 
The Nakamoto Ratio is the percantage (as a decimal) of validation/mining power required to create a critical majority.
This number is dependent on blockchain design.

**Realized Nakamoto:** 
In many cases it can be difficult to get the historical state of network stake.
Realized Nakamoto coefficient is my workaround for this problem.
Using the law of large numbers, if N authors added X% of new blocks to the chain,
then this number should approximately be the Nakamoto Coefficient over this period of time.

**Slug:**
This is the Messari asset slug for the base asset of the network.
Use these to do your own experimentation :)

**Author:**
Because we want to cover chains with different consensus mechanisms,
'author' is the catch all term for an entity which commits blocks to the chain.
Think miner, verifier, sequencer, etc...

**Distribution:**
You should have paid more attention in math class.
tldr, distribution is the spread of any metric.
In the case of the 'Blocks Authored Distribution' chart,
the dristribution is basically a spread of how many blocks where commited by each author.
In the specific case of blocks authors,
we want a small-tight distribution.
A smaller distribution means that all the authors are authoring similar numbers of blocks.
Wide distributions, especially to the upside, 
means a subset of authors are responsible for a majority of blocks.

**Block Interval:**
This is the amount of time inbetween blocks.
Some blockchains create blocks in an 'on-demand' basis so they get a pass here.
However, most blockchains try to create blocks on a regular schedule.
The more flat this line is, the more stable the network is.
''')

