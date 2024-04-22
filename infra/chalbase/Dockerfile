FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y gcc socat python3 locales

# Set the locale
RUN locale-gen en_US.UTF-8  
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8  

COPY ./dropflag /usr/local/bin/
RUN chmod +x /usr/local/bin/dropflag
