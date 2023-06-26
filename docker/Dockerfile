FROM centos:7
LABEL description="Docker container iRODS 4.3.12 iCAT"

RUN yum -y install epel-release wget curl nc which
RUN rpm --import https://packages.irods.org/irods-signing-key.asc \
 && wget --no-check-certificate -qO - https://packages.irods.org/renci-irods.yum.repo | tee /etc/yum.repos.d/renci-irods.yum.repo
RUN yum -y install irods-server irods-database-plugin-postgres \
 && useradd -d /var/lib/irods irods \
 && yum clean all \
 && rm -rf /var/cache/yum/* \
 && rm -rf /tmp/*
RUN yum -y install sudo

ENV IRODS_ADMIN_USER=irods
ENV IRODS_ADMIN_PASS=test123
ENV IRODS_ZONE_NAME=testZone
ENV IRODS_ZONE_KEY=TEMPORARY_zone_key
ENV IRODS_ZONE_PORT=1247
ENV IRODS_NEGOTIATION_KEY=TEMPORARY_32byte_negotiation_key
ENV IRODS_ICAT_DBSERVER=icat-db
ENV IRODS_ICAT_DBPORT=5432
ENV IRODS_ICAT_DBNAME=ICAT
ENV IRODS_ICAT_DBUSER=irods
ENV IRODS_ICAT_DBPASS=test123
ENV IRODS_CONTROLPLANE_PORT=1248
ENV IRODS_CONTROLPLANE_KEY=TEMPORARY__32byte_ctrl_plane_key
ENV IRODS_DATA_PORT_RANGE_BEG=20000
ENV IRODS_DATA_PORT_RANGE_END=20199

COPY genresp.sh docker-entrypoint.sh irods_login.sh /
RUN chmod +x /genresp.sh /docker-entrypoint.sh /irods_login.sh

## data volumes
VOLUME "/etc/irods" "/var/lib/irods/iRODS/server/log" "/var/lib/irods/Vault"

EXPOSE $IRODS_ZONE_PORT $IRODS_CONTROLPLANE_PORT $IRODS_DATA_PORT_RANGE_BEG-$IRODS_DATA_PORT_RANGE_END

## entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["irods"]
