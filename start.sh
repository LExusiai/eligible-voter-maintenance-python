#!/bin/sh

python3 -m venv ./pwbvenv
source ./pwbvenv/bin/activate
pip install uv

cat > user-config.py <<EOF
# -*- coding: utf-8 -*-
family = 'wikipedia'
mylang = 'zh'
usernames['wikipedia']['zh'] = '$BOTUSERNAME'
authenticate['*.wikipedia.org'] = ('$CONSUMERKEY','$CONSUMERSECRTECT', '$ACCESSKEY', '$ACCESSSECRET')
EOF

uv run ./main.py