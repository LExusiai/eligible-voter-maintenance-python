#!/bin/sh

cat > user-config.py <<EOF
# -*- coding: utf-8 -*-
family = 'wikipedia'
mylang = 'zh'
usernames['wikipedia']['zh'] = '$BOTUSERNAME'
authenticate['*.wikipedia.org'] = ('$CONSUMERKEY','$CONSUMERSECRTECT', '$ACCESSKEY', '$ACCESSSECRET')
EOF

wget -qO- https://astral.sh/uv/install.sh | sh

uv run ./main.py