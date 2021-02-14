"""
Example on how to set up a feature that polls data, and publishes to the eventbus.
"""
# import time
import asyncio

from aiohttp import web
from brewblox_service import brewblox_logger, features, http, mqtt, repeater

LOGGER = brewblox_logger(__name__)

# def time_ms():
#     return time.time_ns() // 1000000


class PublishingFeature(repeater.RepeaterFeature):
    """
    repeater.RepeaterFeature is a base class for a common use case:
    - prepare
    - every X seconds, do Y, until the service shuts down
    """

    async def prepare(self):
        """
        This function must be implemented by child classes of RepeaterFeature.
        It is called once after the service started.
        """
        LOGGER.info(f'Starting {self}')

        # Get values from config
        # `name` and `history_topic` are defined by the brewblox-service arguments
        # `poll_interval` is defined in __main__.create_parser()
        self.name = self.app['config']['name']
        self.topic = self.app['config']['history_topic'] + '/froghop-kettles'
        self.interval = self.app['config']['poll_interval']
        self.stateTopic = self.app['config']['state_topic'] + f'/{self.name}'
        # You can prematurely exit here.
        # Raise RepeaterCancelled(), and the base class will stop without a fuss.
        # run() will not be called.
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

        # These are available because we called the setup functions in __main__
        # If you ever get a KeyError when trying to get these, you forgot to call setup()
        session = http.session(self.app)

        # jsonplaceholder does what it suggests:
        # It responds to queries with placeholder data
        url = 'https://jsonplaceholder.typicode.com/todos/1'
        response = await session.get(url)
        data = await response.json()
        LOGGER.info(data)

        # Time to send the data to the eventbus
        # For documentation on how to publish brewblox history data,
        # see https://brewblox.netlify.com/dev/reference/event_logging.html
        await mqtt.publish(self.app,
                           self.topic,
                           {
                               'key': self.name,
                               'data': data
                           })
        # timestamp = time_ms()
        colour_data = 'Test'

        await mqtt.publish(self.app,
                        self.stateTopic + "/Black",
                        {
                            "key": self.name,
                            "type": "Tilt.state",
                            "colour": "Black",
                            "timestamp": 1.000,
                            "data": colour_data,
                        },
                        err=False,
                        retain=True)


def setup(app: web.Application):
    # We register our feature here
    # It will now be automatically started when the service starts
    features.add(app, PublishingFeature(app))


def fget(app: web.Application) -> PublishingFeature:
    # Retrieve the registered instance of PublishingFeature
    return features.get(app, PublishingFeature)
