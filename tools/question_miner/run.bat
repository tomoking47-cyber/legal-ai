@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo ============================================
echo   VV 質問候補の抽出をはじめます
echo ============================================
echo.
python question_miner.py --config config.json --days 90
echo.
echo 終了しました。output フォルダを見てください。
pause
