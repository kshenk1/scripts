#!/bin/bash

## Add this hostname to the end of the ipv4 localhost line in /etc/hosts
_hostname="$(hostname)"
[ -z "$(egrep "$_hostname$" /etc/hosts)" ] && {
    sed -i '/^127\.0\.0\.1/ s/$/ '$_hostname'/' /etc/hosts
}

## TODO: works for now, but currently using a 64bit VM...
yum -y install glibc-2.17-55.el7_0.1.i686 libgcc-4.8.2-16.2.el7_0.i686

[ -f "/opt/support/jre-7u67-linux-i586.rpm" ] && {
    rpm -ivh /opt/support/jre-7u67-linux-i586.rpm || {
        echo "Java Installation failed" && exit 1
    }
}

#yum -y install jna

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