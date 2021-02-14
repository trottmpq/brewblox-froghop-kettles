import asyncio
import random
from aiohttp import web
from brewblox_service import scheduler
from brewblox_service.features import ServiceFeature


class MyFeature(ServiceFeature):

    def __init__(self, app: web.Application):
        super().__init__(app)
        self._task: asyncio.Task = None

    async def startup(self, app: web.Application):
        # Schedule a long-running background task
        self._task = await scheduler.create(app, self._hello())

    async def before_shutdown(self, app: web.Application):
        print('Any minute now...')

    async def shutdown(self, app: web.Application):
        # Orderly cancel the background task
        await scheduler.cancel(app, self._task)

    async def _hello(self):
        while True:
            await asyncio.sleep(5)
            print(random.choice([
                'Hellooo',
                'Searching',
                'Sentry mode activated',
                'Is anyone there?',
                'Could you come over here?',
            ]))
