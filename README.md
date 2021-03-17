# Crypto VWAP Feed

This is a real-time _Volume Weighted Average Price_ or [VWAP](https://en.wikipedia.org/wiki/Volume-weighted_average_price) calculation engine for some common cryptocurrency trading pairs, such as:

- `BTC-USD` (Bitcoin to USD)
- `ETH-USD` (Ethereum to USD)
- `ETH-BTC` (Ethereum to Bitcoin)
- ...

## How it works

It connects to the [Coinbase WebSocket](https://docs.pro.coinbase.com/#the-matches-channel) feed and listens to messages that represent trades. Coinbase call these [_matches_](https://docs.pro.coinbase.com/#match):

> A trade occurred between two orders. The aggressor or taker order is the one executing immediately after being received and the maker order is a resting order on the book. The side field indicates the maker order side. If the side is sell this indicates the maker was a sell order and the match is considered an up-tick. A buy side match is a down-tick.

For every trading pair we're interested about (eg: `BTC-USD`), we compute the VWAP with at most 200 data points. It is computed as:

![VWAP formula](https://wikimedia.org/api/rest_v1/media/math/render/svg/6c0a822a0a9e58a127105e818a07061a02851685)

where:

- <img src="https://render.githubusercontent.com/render/math?math=P_{VWAP}"> is the Volume Weighted Average Price;
- <img src="https://render.githubusercontent.com/render/math?math=P_{j}"> is price of trade <img src="https://render.githubusercontent.com/render/math?math=j">;
- <img src="https://render.githubusercontent.com/render/math?math=Q_{j}"> is quantity of trade <img src="https://render.githubusercontent.com/render/math?math=j">;
- <img src="https://render.githubusercontent.com/render/math?math=j"> is each individual trade that takes place over the defined period of time, excluding cross trades and basket cross trades.

### Out-of-order messages

According to Coinbase:

> While a websocket connection is over TCP, the websocket servers receive market data in a manner which can result in dropped messages. Your feed consumer should either be designed to expect and handle sequence gaps and out-of-order messages, or use channels that guarantee delivery of messages.

To handle out-of-order messages, we use the [_sequence numbers_](https://docs.pro.coinbase.com/#sequence-numbers) provided by Coinbase. We store messages in a priority queue or list that is sorted by these sequences. As messages arrive, the oldest messages, i.e., those with smaller sequences, are dropped.

## Limitations and future improvements

We're currently storing these data points _in memory_. That means, if the application crashes all data points will be lost and it will take a while to accumulate this data again.

As an improvement, we can store this data in a Redis queue. More specifically, we can use Redis to create a [time series that is sorted by lexicographic order](https://redislabs.com/redis-best-practices/time-series/lexicographic-sorted-set-time-series/). This will allow us to efficiently iterate over the time series sorted by the [_sequence numbers_](https://docs.pro.coinbase.com/#sequence-numbers) provided by Coinbase.

We also need to have better error support and fault tolerance, in case Coinbase sends us ["error" messages](https://docs.pro.coinbase.com/#protocol-overview) or the WebSocket connection simply drops because of a [TCP timeout](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing).

## Requirements

- `docker` or [Docker Desktop](https://docs.docker.com/desktop/)
- `docker-compose` (included with _Docker Desktop_)
- `make` or [GNU Make](https://www.gnu.org/software/make/) (probably already installed in your OS). It is being used to build the Docker container dependencies. 

## Setup

This will build the necessary Docker images:

```
./build.sh
```

## Run the test suite

Tests are run by [`pytest`](https://docs.pytest.org/en/stable/) within the CI Docker containers.

```
./test.sh
```

## Run lint (code style checks)

Checks are run by [`Flake8`](https://flake8.pycqa.org/en/latest/) within the CI Docker containers.

```
./lint.sh
```

## Run the application

```
./run.sh
```
