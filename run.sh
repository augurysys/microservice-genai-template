#! /bin/bash
set -e

export PYTHONPATH=$PYTHONPATH:/src

if [ $# -eq 0 ]; then
  echo "No arguments supplied. Expecting one of: [async, api]"
  exit 1
fi

if [ $1 = "async" ]; then
  python -u asynchronous/nsq/nsq_consumer.py
elif [ $1 = "api" ]; then
  python -u api/app.py
else
  echo "Unknown argument ${1}. Expecting one of: [async, api]"
  exit 1
fi
