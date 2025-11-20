#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import csv
from pathlib import Path

import mysql.connector  # <-- MySQL接続ライブラリ

mycnf = Path("~/.my.cnf").expanduser()
config = configparser.ConfigParser()
config.read(mycnf, encoding="utf-8")

try:
    connection = mysql.connector.connect(
        host=config["client"]["host"],  # データベースサーバーのホスト名
        user=config["client"]["user"],  # ユーザー名
        password=config["client"]["password"],  # パスワード
        database=config["mysql"]["database"],  # データベース名
    )
    cursor = connection.cursor(dictionary=True)  # 結果を辞書型で取得
except mysql.connector.Error as err:
    print(f"MySQL エラー: {err}")
    print("DB_CONFIGの設定が正しいか確認してください。")
    exit(1)

query = """
SELECT
        id,
        sanmei.name,
        sanmei.kana,
        alt,
        lat,
        lon,
        level,
        auth,
        ST_Distance_Sphere(
            pt,
            ST_GeomFromText(%s, 4326, 'axis-order=long-lat')
        ) AS distance
    FROM
        geom
    JOIN
        sanmei
    USING (id)
    WHERE type = 1
    AND ST_Within(
        pt,
        ST_Buffer(ST_GeomFromText(%s, 4326, 'axis-order=long-lat'), %s)
    )
    ORDER BY
        distance ASC
    LIMIT 1;
"""

filename = "nnfpt_summits.csv"

try:
    # newline='' は csv を扱う際の推奨設定
    # encoding='utf-8-sig' は BOM (Excel等が付与する先頭の印) があっても
    # 正しく日本語 (Kana) を読み込むために指定します
    with open(filename, mode="r", encoding="utf-8-sig", newline="") as f:

        # DictReader は、1行目を自動的にカラム名(キー)として認識します
        reader = csv.DictReader(f)

        print(
            "gsi_lat,gsi_lon,gsi_name,gsi_kana,lfSpanFr,gaijiFlg,id,name,kana,alt,lat,lon,level,auth,distance"
        )
        # 2行目以降のデータが、1行ずつ「辞書 (dict)」として読み込まれます
        for row in reader:
            # 辞書のキー (1行目のカラム名) を使って変数に代入
            # name = compiled_pattern.sub(replacement, row['Name'].translate(tr))
            gsi_lat = row["lat"]
            gsi_lon = row["lon"]
            gsi_name = row["name"]
            gsi_kana = row["kana"]
            lfSpanFr = row["lfSpanFr"]
            gaijiFlg = row["gaijiFlg"]

            p = f"POINT({gsi_lon} {gsi_lat})"
            radius = 1000 # 1km
            cursor.execute(query, (p, p, radius))
            result = cursor.fetchone()
            if result:
                id = result["id"]
                name = result["name"]
                kana = result["kana"]
                alt = result["alt"]
                lat = result["lat"]
                lon = result["lon"]
                level = result["level"]
                auth = result["auth"]
                distance = result["distance"]
                # if name_modified == nearest_name and kana == nearest_kana and distance_meters < 40:
                #    continue
                print(
                    f"{gsi_lat},{gsi_lon},{gsi_name},{gsi_kana},{lfSpanFr},{gaijiFlg},{id},{name},{kana},{alt},{lat},{lon},{level},{auth},{distance:.2f}"
                )
            else:
                print(
                    f"{gsi_lat},{gsi_lon},{gsi_name},{gsi_kana},{lfSpanFr},{gaijiFlg},,,,,,,,,"
                )

except FileNotFoundError:
    print(f"エラー: ファイル '{filename}' が見つかりません。")
except KeyError as e:
    print(f"エラー: CSVに {e} というカラム名が見つかりません。")
except Exception as e:
    print(f"エラーが発生しました: {e}")
