"""Main entrypoint for this application"""
import sys
import logging
import warnings
import argparse

from parse import compile
from paho.mqtt.client import Client, MQTTv31, MQTTv311, MQTTv5

logger = logging.getLogger("mqtt")


def connect(mq: Client, args: argparse.Namespace):
    @mq.disconnect_callback()
    def _(
        client, userdata, flags, reason_code, props=None
    ):  # pylint: disable=unused-argument
        """Subscribe on connect"""
        if reason_code != 0:
            logger.error(
                "Disconnected from %s with reason code: %s", client, reason_code
            )

    # Keyword argument handling
    kwargs = {}
    if args.protocol == 5:
        kwargs["clean_start"] = args.clean_start

    # Connect!
    mq.connect(args.host, args.port, **kwargs)


def publish(mq: Client, parser: argparse.ArgumentParser, args: argparse.Namespace):
    # Validation
    if pattern := args.line:
        if "topic" not in pattern and not args.topic:
            parser.error(
                "A topic must be specified either on the command line or as a pattern parameter."
            )
        elif "message" not in pattern and not args.message:
            parser.error(
                "A message must be specified either on the command line or as a pattern parameter."
            )
    else:
        if not args.topic or not args.message:
            parser.error("A topic and a message must be specified on the command line.")

    # Connect and start loop
    connect(mq, args)
    mq.loop_start()

    if pattern := args.line:
        parser = compile(pattern)

        for line in sys.stdin:
            result = parser.parse(line)
            mq.publish(
                topic=args.topic or result["topic"],
                payload=args.message or result["message"],
                qos=args.qos,
                retain=args.retain,
            )
    else:
        mq.publish(
            topic=args.topic,
            payload=args.message,
            qos=args.qos,
            retain=args.retain,
        )


def subscribe(mq: Client, parser: argparse.ArgumentParser, args: argparse.Namespace):
    @mq.connect_callback()
    def _(client, userdata, flags, reason_code, props=None):
        """Subscribe on connect"""
        if reason_code != 0:
            logger.error(
                "Connection failed to %s with reason code: %s", client, reason_code
            )
            return

        for topic in args.topic:
            mq.subscribe(topic, qos=args.qos)

    @mq.message_callback()
    def _(client, userdata, message):
        """Print received message to stdout according to specified format"""
        topic = message.topic

        try:
            payload = message.payload.decode()
        except UnicodeDecodeError:
            logger.exception(f"Could not decode payload: {message.payload}")
            return

        sys.stdout.write(f"{args.line.format(topic=topic, message=payload)}\n")
        sys.stdout.flush()

    connect(mq, args)
    mq.loop_forever()


def main():
    parser = argparse.ArgumentParser(
        prog="mqtt",
        description="MQTT command-line client application",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--host", type=str, default="localhost")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--transport", choices=["tcp", "websockets"], default="tcp")
    parser.add_argument("--clientid", type=str, default=None)
    parser.add_argument("--user", type=str, default=None)
    parser.add_argument("--password", type=str, default=None)
    parser.add_argument(
        "--protocol", type=int, choices=[MQTTv31, MQTTv311, MQTTv5], default=MQTTv5
    )
    parser.add_argument("--tls", action="store_true", default=False)
    parser.add_argument("--clean-start", action="store_true", default=False)
    parser.add_argument("--log-level", type=int, default=logging.WARNING)

    ## Subcommands
    subparsers = parser.add_subparsers(required=True)

    ## Common parser for all subcommands
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--qos", choices=[0, 1, 2], default=0)

    ## Publish subcommand
    publish_parser = subparsers.add_parser("publish", parents=[common_parser])
    publish_parser.add_argument("-t", "--topic", type=str, default=None)
    publish_parser.add_argument("-m", "--message", type=str, default=None)
    publish_parser.add_argument("--line", type=str, default=None)
    publish_parser.add_argument("--retain", action="store_true", default=False)

    publish_parser.set_defaults(func=publish)

    ## Subscribe subcommand
    subscribe_parser = subparsers.add_parser("subscribe", parents=[common_parser])
    subscribe_parser.add_argument(
        "-t", "--topic", type=str, action="append", required=True
    )
    subscribe_parser.add_argument("--line", type=str, default="{message}")
    subscribe_parser.set_defaults(func=subscribe)

    ## Parse arguments and start doing our thing
    args = parser.parse_args()

    # Setup logger
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s %(message)s", level=args.log_level
    )
    logging.captureWarnings(True)
    warnings.filterwarnings("once")

    ## Construct client
    mq = Client(
        client_id=args.clientid, transport=args.transport, protocol=args.protocol
    )
    mq.username_pw_set(args.user, args.password)
    if args.tls:
        mq.tls_set()

    mq.enable_logger(logger.getChild("paho.client"))

    # Dispatch to correct function
    try:
        args.func(mq, parser, args)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
