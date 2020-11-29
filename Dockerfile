FROM python:3.7-slim

# Install SMSTP + use it as a "sendmail" replacement
RUN apt update && apt install -y \
	msmtp \
	msmtp-mta \
	openssl \
	ca-certificates
RUN update-ca-certificates

# equivalent of installing msmtp-mta:
# RUN ln -sf /usr/bin/msmtp /usr/sbin/sendmail

WORKDIR /srv/app

# Install app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY ikeawatcher ikeawatcher

COPY msmtprc /etc
COPY run.sh .
RUN chmod +x run.sh

ENTRYPOINT ["./run.sh"]