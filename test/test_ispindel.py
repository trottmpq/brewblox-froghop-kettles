"""
Tests the iSpindel endpoint
"""
import json

import pytest
from brewblox_service import brewblox_logger
from brewblox_service.testing import response
from mock import AsyncMock

from brewblox_ispindel import ispindel_service as ispindel

LOGGER = brewblox_logger(__name__)

TESTED = ispindel.__name__

BODY_OK = '{"name":"iSpindel000","ID":4974097,"angle":83.49442,"temperature":21.4375,"temp_units":"C",' + \
          '"battery":4.035453,"gravity":30.29128,"interval":60,"RSSI":-76}'

EVENT_OK = {'angle': 83.49442, 'temperature': 21.4375, 'battery': 4.035453, 'gravity': 30.29128, 'rssi': -76}


@pytest.fixture
def m_publisher(mocker):
    m = mocker.patch(TESTED + '.mqtt.publish', AsyncMock())
    return m


@pytest.fixture
def app(app):
    ispindel.setup(app)
    return app


async def test_ispindel(app, client, m_publisher):
    await response(client.post('/ispindel', json=json.loads(BODY_OK)))
    m_publisher.assert_awaited_once_with(
        app,
        'brewcast/history',
        {
            'key': 'iSpindel000',
            'data': EVENT_OK,
        })


async def test_invalid(app, client, m_publisher):
    await response(client.post('/ispindel', json={}), status=422)
    m_publisher.assert_not_awaited()
