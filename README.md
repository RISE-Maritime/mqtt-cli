# mqtt-cli
A command-line tool for publishing and subscribing to mqtt. 

Use cases:
* Trials
* As part of a bash pipeline

## Installation
`pip install mqtt-cli`

## Usage
```
$ mqtt --help

usage: mqtt [-h] [--host HOST] [--port PORT] [--transport {tcp,websockets}] [--clientid CLIENTID] [--user USER] [--password PASSWORD] [--protocol {3,4,5}] [--path PATH] [--tls] [--clean-start] [--log-level LOG_LEVEL]
            {publish,subscribe} ...

MQTT command-line client application

positional arguments:
  {publish,subscribe}

options:
  -h, --help            show this help message and exit
  --host HOST
  --port PORT
  --transport {tcp,websockets}
  --clientid CLIENTID
  --user USER
  --password PASSWORD
  --protocol {3,4,5}
  --path PATH
  --tls
  --clean-start
  --log-level LOG_LEVEL
```

```
$ mqtt publish --help

usage: mqtt publish [-h] [--qos {0,1,2}] [-t TOPIC] [-m MESSAGE] [--line LINE] [--retain] [--queue QUEUE]

options:
  -h, --help            show this help message and exit
  --qos {0,1,2}
  -t TOPIC, --topic TOPIC
  -m MESSAGE, --message MESSAGE
  --line LINE
  --retain
  --queue QUEUE
```

```
$ mqtt subscribe --help

usage: mqtt subscribe [-h] [--qos {0,1,2}] -t TOPIC [--line LINE] [--json]

options:
  -h, --help            show this help message and exit
  --qos {0,1,2}
  -t TOPIC, --topic TOPIC
  --line LINE
  --json
```


TBC
