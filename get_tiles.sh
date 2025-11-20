#!/bin/bash

mysql --skip-column-names --batch < get_zxy.sql > ZXY_LIST

cat ZXY_LIST | while IFS=/ read -r z x y; do
    echo "Downloading tile z=$z, x=$x, y=$y"
    mkdir -p tiles/$z/$x
    wget -q -O tiles/$z/$x/$y.geojson "https://cyberjapandata.gsi.go.jp/xyz/experimental_nnfpt/$z/$x/$y.geojson"
done

find tiles -name "*.geojson" | ./extract_summits.py > nnfpt_summits.csv
