#!/bin/sh
docker logs --follow --tail 1 guacamole|./auto_guac_for_docker.py &
