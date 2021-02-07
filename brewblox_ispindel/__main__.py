"""
ISpindel brewblox service
"""

from argparse import ArgumentParser

from brewblox_service import http, mqtt, scheduler, service

from brewblox_ispindel import ispindel_service


def create_parser(default_name='ispindel') -> ArgumentParser:
    parser: ArgumentParser = service.create_parser(default_name=default_name)
    return parser


def main():
    app = service.create_app(parser=create_parser())
    scheduler.setup(app)
    mqtt.setup(app)
    http.setup(app)
    ispindel_service.setup(app)
    service.furnish(app)
    service.run(app)


if __name__ == '__main__':
    main()
