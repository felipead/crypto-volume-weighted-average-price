import asyncio
import json
import logging
import sys
from logging import getLogger

import websockets

from src.app.coinbase.model import Subscribe, Channel, Match
from src.app.coinbase.schema import deserialize_message, serialize_message
from src.app.model import TradingPair
from src.app.vwap import VWAP

logger = getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

WEBSOCKET_URI = 'wss://ws-feed.pro.coinbase.com'

CHANNELS = (Channel.MATCHES,)

TRADING_PAIRS = (
    TradingPair.BTC_USD,
    TradingPair.ETH_USD,
    TradingPair.ETH_BTC
)

VWAPS = tuple(VWAP(i) for i in TRADING_PAIRS)


async def event_loop():
    async with websockets.connect(WEBSOCKET_URI) as websocket:
        await subscribe(websocket)
        await listen(websocket)


async def subscribe(websocket):
    logger.info(f'Subscribing to channels {CHANNELS} and trading pairs {TRADING_PAIRS}…')
    await websocket.send(json.dumps(
        serialize_message(
            Subscribe(product_ids=TRADING_PAIRS, channels=CHANNELS)
        )
    ))


async def listen(websocket):
    logger.info('Listening to messages…')
    async for raw_message in websocket:
        message = deserialize_message(json.loads(raw_message))
        if message and isinstance(message, Match):
            process(message)


def process(point: Match):
    for vwap in VWAPS:
        if vwap.supports(point):
            vwap.add(point)
            logging.info(f'{vwap}: {vwap.current_value()}')


if __name__ == '__main__':
    asyncio.run(event_loop())
