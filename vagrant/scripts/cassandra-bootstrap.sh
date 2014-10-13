#!/bin/bash

java_file="jre-7u67-linux-i586.rpm"

java_install="/opt/support/$java_file"

cp "$java_install" /home/$java_file

yum -y install /home/$java_file

yum -y install jna

datastax_repo_file="/etc/yum.repos.d/datastax.repo"

if [ ! -f "$datastax_repo_file" ]; then
    echo "
[datastax]
name= DataStax Repo for Apache Cassandra
baseurl=http://rpm.datastax.com/community
enabled=0
gpgcheck=0
" > /etc/yum.repos.d/datastax.repo
fi

yum --enablerepo=datastax install -y dsc21