"""
Example on how to set up a feature that polls data, and publishes to the eventbus.
"""
import time
import asyncio
import math

from dataclasses import dataclass

from aiohttp import web
from brewblox_service import brewblox_logger, features, http, mqtt, repeater

LOGGER = brewblox_logger(__name__)

# def time_ms():
#     return time.time_ns() // 1000000


@dataclass
class TemperatureData:
    temperature: float
    temperature_unit: str

    def serialize(self):
        values = {
            f'temperature[{self.temperature_unit}]': self.temperature
        }
        return {k: (v if not isinstance(v, str) else None) for k, v in values.items()}


class PublishingFeature(repeater.RepeaterFeature):
    """
    repeater.RepeaterFeature is a base class for a common use case:
    - prepare
    - every X seconds, do Y, until the service shuts down
    """
    def __init__(self, app: web.Application):
        super().__init__(app)

        LOGGER.info(f'Starting {self}')

        config = app['config']
        self.name = config['name']
        self.interval = config['poll_interval']
        self.state_topic = config['state_topic'] + f'/{self.name}'
        self.history_topic = config['history_topic'] + f'/{self.name}'

    async def prepare(self):
        """
        This function must be implemented by child classes of RepeaterFeature.
        It is called once after the service started.
        """
        if self.interval <= 0:
            raise repeater.RepeaterCancelled()

    async def run(self):
        """
        This function must be implemented by child classes of RepeaterFeature.
        After prepare(), the base class keeps calling run() until the service shuts down.

        To prevent spam, it is strongly recommended to use asyncio.sleep().
        asyncio.sleep() is non-blocking - other services and endpoint handlers will run.
        """
        await asyncio.sleep(self.interval)

        # # These are available because we called the setup functions in __main__
        # # If you ever get a KeyError when trying to get these, you forgot to call setup()
        # session = http.session(self.app)

        # # jsonplaceholder does what it suggests:
        # # It responds to queries with placeholder data
        # url = 'https://jsonplaceholder.typicode.com/todos/1'
        # response = await session.get(url)
        # data = await response.json()
        # LOGGER.info(data)
        seconds = time.time()
        temp_sin = math.sin(seconds * 2 * math.pi / 60 / 1) + 1
        data = TemperatureData(temp_sin, 'c')
        LOGGER.debug(data)

        # Time to send the data to the eventbus
        # For documentation on how to publish brewblox history data,
        # see https://brewblox.netlify.com/dev/reference/event_logging.html
        await mqtt.publish(
            self.app,
            self.history_topic,
            {
                'key': 'tempsensor1',
                'data': data.serialize()
            })

        # timestamp = time_ms()

        await mqtt.publish(
            self.app,
            self.state_topic,
            err=False,
            retain=True,
            message={
                'key': self.name,
                'type': 'Spark.state',
                'data': {
                    'status': {
                        'device_address': 'froghop_controller1',
                        'connection_kind': 'wifi',
                        'service_info': {
                            'name': 'froghop-kettles'
                        },
                        'device_info': {
                            'system_version': '1.0',
                            'platform': 'armv7',
                            'reset_reason': 'string',
                        },
                        'handshake_info': {
                            'is_compatible_firmware': True,
                            'is_latest_firmware': True,
                            'is_valid_device_id': True
                        },
                        'is_autoconnecting': True,
                        'is_connected': True,
                        'is_acknowledged': True,
                        'is_synchronized': True,
                        'is_updating': True
                    },
                    'blocks': [
                        {
                            'id': 'temp1',
                            'nid': 1,
                            'serviceId': 'string',
                            'groups': [],
                            'type': 'TempSensorOneWire',
                            'data': {
                                'offset': '1',
                                'address': 'string',
                                'value': data.temperature
                            }
                        }],
                },
            }
        )


def setup(app: web.Application):
    # We register our feature here
    # It will now be automatically started when the service starts
    features.add(app, PublishingFeature(app))


def fget(app: web.Application) -> PublishingFeature:
    # Retrieve the registered instance of PublishingFeature
    return features.get(app, PublishingFeature)
