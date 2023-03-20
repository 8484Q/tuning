FROM openanolis/anolisos:8.4-aarch64

# add repo
COPY epel.repo /etc/yum.repos.d/
RUN yum clean all
RUN yum makecache

# install package
RUN yum install -y unzip polkit vim net-tools which openssl-devel bzip2-devel libffi-devel zlib-devel make cmake gcc gcc-c++

# install nginx
RUN yum install -y nginx
RUN sed -i "s/access_log.*/access_log off;/g" /etc/nginx/nginx.conf

# install python
RUN yum -y install python36 python36-devel rust
RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install wheel
RUN pip3 install matplotlib
RUN pip3 install numpy
RUN pip3 install pandas
RUN pip3 install scikit_learn==0.24.2 
RUN pip3 install ultraopt==0.1.1
RUN pip3 install tornado==6.1
RUN pip3 install pynginxconfig
RUN pip3 install requests==2.25.1 
RUN pip3 install pySOT==0.3.3 
RUN pip3 install POAP==0.1.26
RUN pip3 install hyperopt==0.2.5
RUN pip3 install xgboost
RUN pip3 install shap==0.35.0
RUN pip3 install pyudev

# create folder
RUN mkdir /var/keentune
RUN mkdir /var/keentune/wrk-master
RUN mkdir /var/keentune/profile
RUN mkdir /var/keentune/data
RUN mkdir /var/keentune/data/tuning_data
RUN mkdir /var/keentune/tuning_workspace
RUN mkdir /var/keentune/tuning_workspace/http_long

# install wrk
COPY wrk-master /var/keentune/wrk-master
WORKDIR /var/keentune/wrk-master
RUN make
RUN cp /var/keentune/wrk-master/wrk /usr/bin

# install keentuned
RUN yum install -y keentuned keentune-target keentune-bench
COPY ./keentuned/daemon/examples/benchmark/wrk/* /etc/keentune/benchmark/wrk
RUN sed -i "s/PARAMETER.*=.*/PARAMETER = sysctl.json, nginx.json/g" /etc/keentune/conf/keentuned.conf

# install brain
RUN mkdir -p /var/keentune/python-brain/
COPY brain/ /var/keentune/python-brain/
COPY brain/keentune-brain.service /usr/lib/systemd/system
WORKDIR /var/keentune/python-brain/
RUN python3 setup.py install
RUN cp /usr/local/bin/keentune-brain /usr/bin

# # install target
# RUN mkdir -p /var/keentune/python-target/
# COPY target/ /var/keentune/python-target/
# COPY target/keentune-target.service /usr/lib/systemd/system
# WORKDIR /var/keentune/python-target/
# RUN python3 setup.py install
# RUN cp /usr/local/bin/keentune-target /usr/bin

# # install bench
# RUN mkdir -p /var/keentune/python-bench/
# COPY bench/ /var/keentune/python-bench/
# COPY bench/keentune-bench.service /usr/lib/systemd/system
# WORKDIR /var/keentune/python-bench/
# RUN python3 setup.py install
# RUN cp /usr/local/bin/keentune-bench /usr/bin

# get preset files
COPY preset_files/sysctl.json /etc/keentune/parameter
COPY preset_files/tuning_jobs.csv /var/keentune
COPY preset_files/http_long_group1.conf /var/keentune/profile
COPY preset_files/http_long/* /var/keentune/data/tuning_data

WORKDIR /etc/keentune

ENTRYPOINT ["/lib/systemd/systemd"]


