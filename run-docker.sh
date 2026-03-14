#!/bin/bash

docker image prune -f
docker compose run --build --rm -it -v $(pwd):/workspace ubuntu-fuzz bash