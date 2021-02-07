"""
Tests brewblox_ispindel.__main__.py
"""

import pytest

from brewblox_ispindel import __main__ as main

TESTED = main.__name__


@pytest.fixture
def m_run(mocker):
    mocker.patch(TESTED + '.service.run')


@pytest.fixture
def app(app, mocker):
    mocker.patch(TESTED + '.service.create_app', return_value=app)
    return app


def test_main(app, m_run):
    main.main()
