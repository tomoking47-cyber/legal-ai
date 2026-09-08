#!/bin/bash
cd "$(dirname "$0")"
echo "============================================"
echo "  VV 質問候補の抽出をはじめます"
echo "============================================"
echo
python3 question_miner.py --config config.json --days 90
echo
echo "終了しました。output フォルダを見てください。"
