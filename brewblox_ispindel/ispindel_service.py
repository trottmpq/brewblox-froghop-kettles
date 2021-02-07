"""
ISpindel http endpoint
"""

from aiohttp import web
from aiohttp_apispec import docs, request_schema
from brewblox_service import brewblox_logger, mqtt
from marshmallow import Schema, fields

routes = web.RouteTableDef()

LOGGER = brewblox_logger(__name__)


def setup(app: web.Application):
    app.router.add_routes(routes)
    LOGGER.info('Setup iSpindel register endpoint')


class ISpindelSchema(Schema):
    name = fields.String(required=True)
    temperature = fields.Float(required=True)
    battery = fields.Float(required=False)
    gravity = fields.Float(required=False)
    RSSI = fields.Float(required=False)
    angle = fields.Float(required=False)


@docs(
    tags=['iSpindel'],
    summary='Endpoint to receive iSpindel metrics.',
    description='The iSpindel wake up and send an HTTP POST request to this endpoint.',
)
@routes.post('/ispindel')
@request_schema(ISpindelSchema(unknown='exclude'))
async def ispindel_handler(request: web.Request) -> web.Response:
    """
    This endpoint accepts request from iSpindel when configured to use the Generic HTTP POST.
    """
    # Contains input data after validation
    data = request['data']

    name = data.get('name')
    temperature = data.get('temperature')
    battery = data.get('battery')
    gravity = data.get('gravity')
    rssi = data.get('RSSI')
    angle = data.get('angle')

    topic = request.app['config']['history_topic']
    await mqtt.publish(request.app,
                       topic,
                       {'key': name,
                        'data': {'temperature': temperature,
                                 'battery': battery,
                                 'angle': angle,
                                 'rssi': rssi,
                                 'gravity': gravity}})
    LOGGER.info(f'iSpindel {name}, temp: {temperature}, gravity: {gravity}')
    return web.Response(status=200)
