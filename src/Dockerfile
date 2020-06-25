FROM tensorflow/serving:1.14.0

# Install OS dependencies
RUN apt-get update -y \
	&& apt-get upgrade -y \
	&& apt-get install -y \
		apt-utils \
		python3 \
		python3-pip \
    libpng-dev \
		libsm6 libxext6 libxrender-dev libglib2.0-0 \
		curl \
		vim \
		tree \
		htop \
		zip gzip tar

ENV HOME=/home
ENV PROJECT_NAME=tf-serving-kibana-demo
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV SHELL=/bin/bash
ENV FLASK_APP=/$PROJECT_NAME/src/api/app.py
ENV prometheus_multiproc_dir=/$PROJECT_NAME/src/api/

# Copy config files
RUN mkdir /var/lib/prometheus
RUN mkdir /etc/prometheus
COPY src/api/config/prometheus.yml /etc/prometheus/

# install prometheus
RUN curl -LO https://github.com/prometheus/prometheus/releases/download/v2.0.0/prometheus-2.0.0.linux-amd64.tar.gz
RUN sha256sum prometheus-2.0.0.linux-amd64.tar.gz
RUN tar xvf prometheus-2.0.0.linux-amd64.tar.gz
RUN cp prometheus-2.0.0.linux-amd64/prometheus /usr/local/bin/
RUN cp prometheus-2.0.0.linux-amd64/promtool /usr/local/bin/
RUN cp -r prometheus-2.0.0.linux-amd64/consoles /etc/prometheus
RUN cp -r prometheus-2.0.0.linux-amd64/console_libraries /etc/prometheus

# install metricbeat for prometheus metrics export to Kibana
RUN curl -L -O https://artifacts.elastic.co/downloads/beats/metricbeat/metricbeat-7.6.0-amd64.deb
RUN dpkg -i metricbeat-7.6.0-amd64.deb
RUN metricbeat modules enable prometheus

COPY src/api/config/metricbeat/metricbeat.yml /etc/metricbeat/
COPY src/api/config/metricbeat/prometheus.yml /etc/metricbeat/modules.d
RUN chmod go-w /etc/metricbeat/metricbeat.yml
RUN chmod go-w /etc/metricbeat/modules.d/prometheus.yml

# Navigate to the base folder of the container.
WORKDIR /
# Fetch model through AWS using a key & id


COPY /src/ /$PROJECT_NAME/src/
# Add production requirements
COPY requirements_prod.txt requirements_prod.txt
# Install python dependencies
RUN pip3 install -r requirements_prod.txt

COPY src/docker/docker_entrypoint.sh /usr/bin/docker_entrypoint.sh
# Create executable script for the application
RUN chmod +x /usr/bin/docker_entrypoint.sh
ENTRYPOINT ["/usr/bin/docker_entrypoint.sh"]
