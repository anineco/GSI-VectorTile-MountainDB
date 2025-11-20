#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import json
import sys

pua = {"E028": "瘤", "E06E": "那", "E084": "蓮", "E093": "馿"}


def translate_gaiji(name, gaiji_flg):
    pattern = gaiji_flg.strip("()")
    i = 0
    while pattern[i : i + 2] == "*_":
        i += 2
    n = len(pattern)
    j = 0
    while pattern[n - j - 2 : n - j] == "_*":
        j += 2
    gaiji_code = pattern[i : n - j]
    if gaiji_code.startswith("E"):
        if not gaiji_code in pua:
            return name  # Private Use Area は無視
        gaiji_char = pua[gaiji_code]
    else:
        gaiji_char = chr(int(gaiji_code, 16))
    m = len(name)
    name = name[: (i // 2)] + gaiji_char + name[m - (j // 2) :]
    return name


def main():
    writer = csv.writer(sys.stdout)
    fieldnames = ["lat", "lon", "name", "kana", "lfSpanFr", "gaijiFlg", "name1"]
    writer.writerow(fieldnames)
    # 標準入力から1行ずつ読み込む
    for line in sys.stdin:
        # 改行コードや前後の空白を除去してパスを取得
        file_path = line.strip()

        # 空行はスキップ
        if not file_path:
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

                for feature in data.get("features", []):
                    geometry = feature.get("geometry", {})
                    geom_type = geometry.get("type", "")
                    if geom_type != "Point":
                        continue
                    coordinates = geometry.get("coordinates", [])
                    lon, lat = coordinates if len(coordinates) == 2 else (None, None)
                    properties = feature.get("properties", {})
                    type = properties.get("type", "")
                    if type != "山":
                        continue
                    name = properties.get("name", "")
                    kana = properties.get("kana", "")
                    lfSpanFr = properties.get("lfSpanFr", "")
                    gaijiFlg = properties.get("gaijiFlg", "")
                    if gaijiFlg != "0":
                        name1 = translate_gaiji(name, gaijiFlg)
                    else:
                        name1 = name
                    row = [lat, lon, name, kana, lfSpanFr, gaijiFlg, name1]
                    writer.writerow(row)

        except FileNotFoundError:
            print(f"❌ エラー: ファイルが見つかりません - {file_path}", file=sys.stderr)
        except json.JSONDecodeError as e:
            print(
                f"❌ エラー: JSON形式が不正です - {file_path}\n   詳細: {e}",
                file=sys.stderr,
            )
        except PermissionError:
            print(f"❌ エラー: 読み取り権限がありません - {file_path}", file=sys.stderr)
        except Exception as e:
            print(f"❌ エラー: 想定外のエラー - {file_path}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
# __END__
