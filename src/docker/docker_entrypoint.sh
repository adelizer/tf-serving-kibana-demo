#!/bin/bash

echo "Sleeping for 60 seconds to wait for Kibana to spin up"
i=0
until [ $i -gt 60 ]
do
  clear
  echo i: $i
  date
  sleep 1s
  ((i=i+1))
done

/usr/local/bin/prometheus --config.file=/etc/prometheus/prometheus.yml &
/usr/bin/tensorflow_model_server --rest_api_port="${TF_SERVE_PORT}" --model_config_file=/models/"${TF_CONFIG_DIR}"/tf_serving.config  --monitoring_config_file=/models/"${TF_CONFIG_DIR}"/monitoring.config &
flask run --host=0.0.0.0 --port=80 &
metricbeat modules enable prometheus &
metricbeat -e