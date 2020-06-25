import os
import sys
import logging


LOGLEVEL = os.environ.get('LOGLEVEL') if os.environ.get('LOGLEVEL') is not None else logging.INFO
LOGFORMAT = '%(asctime)s | %(levelname)s | [%(filename)s:%(lineno)s - %(funcName)s] %(message)s'
logging.basicConfig(format=LOGFORMAT, level=LOGLEVEL, stream=sys.stdout)
logging.root.setLevel(LOGLEVEL)

PROJECT_NAME = 'tf_serving_demo'

LOGGER_NAME = 'tf_serving_demo'
TF_CONFIG_DIR = os.environ.get('TF_CONFIG_DIR', 'mnist_classifier')

# elasticsearch
ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', 'localhost')
ELASTICSEARCH_PORT = int(os.environ.get('ELASTICSEARCH_PORT', 9200))
ELASTICSEARCH_INDEX = "logstash."
ENVIRONMENT = 'dev'