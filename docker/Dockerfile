FROM ubuntu:18.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install wget sudo lsb-release netcat
RUN apt install -y vim gnupg2  
RUN apt-get -y install postgresql

RUN wget -qO - https://packages.irods.org/irods-signing-key.asc | sudo apt-key add -
RUN echo "deb [arch=amd64] https://packages.irods.org/apt/ $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/renci-irods.list
RUN apt update

RUN apt-get -y install irods-runtime=4.2.12-1~bionic
RUN apt-get -y install irods-icommands=4.2.12-1~bionic
RUN apt-get -y install irods-server=4.2.12-1~bionic
RUN apt-get -y install irods-database-plugin-postgres=4.2.12-1~bionic

COPY ICAT.sql /tmp/
RUN service postgresql start &&\
    psql -f /tmp/ICAT.sql
RUN exit


CMD ["bash"]
#docker build --platform linux/amd64 -t irods:v2 -f Dockerfile .
