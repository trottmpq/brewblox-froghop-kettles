"""
Intermittently broadcasts temperature to the eventbus
"""

import asyncio
from dataclasses import dataclass
# from json import JSONDecodeError
import math
import time
# from os import getenv

from aiohttp import web
from brewblox_service import brewblox_logger, features, mqtt, repeater

LOGGER = brewblox_logger(__name__)


@dataclass
class TemperatureData:
    temperature: float
    temperature_unit: str
    def serialize(self):
        values = {
            f'temperature[{self.temperature_unit}]': self.temperature
        }
        return {k: (v if not isinstance(v, str) else None) for k, v in values.items()}


class TemperaturePublish(repeater.RepeaterFeature):

    def __init__(self, app: web.Application):
        super().__init__(app)

        LOGGER.info(f'Starting {self}')

        config = app['config']
        self.name = config['name']
        self.interval = config['broadcast_interval']
        self.state_topic = config['state_topic'] + f'/{self.name}'
        self.history_topic = config['history_topic'] + f'/{self.name}'

        self._will_message = {
            'key': self.name,
            'type': 'Spark.state',
            'data': {
                'status': None,
                'blocks': [],
            },
        }

        # A will is published if the client connection is broken
        mqtt.set_client_will(app,
                             self.state_topic,
                             self._will_message)

    async def prepare(self):
        if self.interval <= 0:
            raise repeater.RepeaterCancelled()

    async def before_shutdown(self, app: web.Application):
        await self.end()
        # This is an orderly shutdown - MQTT will won't be published
        await mqtt.publish(
            self.app,
            self.state_topic,
            err=False,
            retain=True,
            message=self._will_message
        )

    async def run(self):
        await asyncio.sleep(self.interval)

        seconds = time.time()
        temp_sin = math.sin(seconds * 2 * math.pi / 60 / 1) + 1
        data = TemperatureData(temp_sin, 'c')
        LOGGER.debug(data)

        await mqtt.publish(
            self.app,
            self.history_topic,
            err=False,
            message={
                'key': self.name,
                'data': data.serialize(),
            }
        )


def setup(app: web.Application):
    features.add(app, TemperaturePublish(app))


def fget(app: web.Application) -> TemperaturePublish:
    return features.get(app, TemperaturePublish)
