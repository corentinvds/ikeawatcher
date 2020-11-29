#!/usr/bin/env bash
CONFIG_FILE_PATH=/etc/msmtprc

if [[ "$FROM_EMAIL" != "" ]]; then
  echo "Replacing __FROM_EMAIL__ by FROM_EMAIL var in $CONFIG_FILE_PATH ..."
  sed -i "s|__FROM_EMAIL__|$FROM_EMAIL|g" $CONFIG_FILE_PATH
fi;

if [[ "$SMTP_PASSWORD" != "" ]]; then
  echo "Replacing __SMTP_PASSWORD__ by SMTP_PASSWORD var in $CONFIG_FILE_PATH ..."
  sed -i "s|__SMTP_PASSWORD__|$SMTP_PASSWORD|g" $CONFIG_FILE_PATH
fi;

grep -e "__SMTP_PASSWORD__" -e "__FROM_EMAIL__" $CONFIG_FILE_PATH
if [[ "$?" == "0" ]]; then
  echo "There are remaining placeholders in $CONFIG_FILE_PATH"
  exit 1
fi

if [[ -z "$TO_EMAIL" ]]; then
  echo "Missing TO_EMAIL var"
  exit 0
fi;

if [[ -z "$WAIT_DURATION" ]]; then
  echo "Missing WAIT_DURATION var"
  exit 0
fi;


ret=-1
while [[ "$ret" != "0" ]]; do
  echo "$(date) New try with $@"
  python -m ikeawatcher $@ > result.txt 2>&1
  ret=$?
  echo "$(date) >>>>>APP LOGS:"
  cat result.txt
  if [[ "$ret" != "0" ]]; then
    echo "$(date) wait ${WAIT_DURATION} ..."
    sleep "${WAIT_DURATION}"
  fi
done

echo "$(date) Sending email ..."
(echo -e "Subject: IKEA COMMAND AVAILABLE!\n" ; cat result.txt) \
  | msmtp \
    --tls-trust-file=/etc/ssl/certs/ca-certificates.crt \
    --logfile=- \
    "$TO_EMAIL"

#echo "$(date) >>>>>EMAIL LOGS:"
#cat /var/log/sendmail.log

echo "FINISHED"
