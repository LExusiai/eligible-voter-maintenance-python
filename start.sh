#!/bin/sh

curl -LsSf https://astral.sh/uv/install.sh | sh

cat > user-config.py <<EOF
# -*- coding: utf-8 -*-
family = 'wikipedia'
mylang = 'zh'
usernames['wikipedia']['zh'] = '$BOTUSERNAME'
authenticate['*.wikipedia.org'] = ('$CONSUMERKEY','$CONSUMERSECRTECT', '$ACCESSKEY', '$ACCESSSECRET')
EOF

uv run ./main.py
