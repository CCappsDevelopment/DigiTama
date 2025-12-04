#!/usr/bin/env bash

PORT="/dev/ttyACM0"

for i in $(seq -w 0 19); do
    src="water_${i}.raw"
    dst=":water_${i}.raw"
    echo "Copying $src -> $dst"
    mpremote connect "$PORT" cp "$src" "$dst"
done

