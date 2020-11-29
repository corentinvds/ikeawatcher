# IKEA Watcher

This script periodically polls the Ikea API until a given articles list is available to delivery or to "click and collect".

An email is sent when the articles are available for the specified locations.

# Python usage (one shot, no email):
```bash
pip install -r requirements.txt
python -m ikeawatcher [--help] --country=BE [--delivery <zip-code>] [--collect <location>] [--try-all]  <article>:<quantity> [<article>:<quantity> ...]
```
- `country`: country of delivery (only tested with `be`)
- You can provide as much as `--delivery <zip-code>` or `-- <collect-location>` as you want
- `collect-location` is a substring of one of the collect locations available the the selected country (example: `--collect arlon` will select the `IKEA Arlon` collect location)
- use `--try-all` to force the script to test all delivery/collect locations instead of stopping on the first successful request

# Docker usage

You can use the provided Dockerfile to run the script inside a container.
The container entrypoint periodically run the python script and sends an email when the shopping list is available.

To configure the email you can either
 - provide `FROM_EMAIL` and `SMTP_PASSWORD` environment variables to use GMAIL config
 - erase the `/etc/msmtp` config file via a volume mount

Usage with docker-compose:
```bash
cp .env.example .env
nano .env
# edit .env to fit your needs
docker-compose up --build -d
docker-compose logs -tf
```
 