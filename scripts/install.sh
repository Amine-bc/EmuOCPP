#!/bin/sh

python3 -m venv "$(dirname "$0")"/../venv
"$(dirname "$0")"/../venv/bin/pip install -r "$(dirname "$0")"/../requirements.txt
"$(dirname "$0")"/../venv/bin/pip install --upgrade git+https://github.com/cnp3/ipmininet.git@v1.1
