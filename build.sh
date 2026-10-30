#!/usr/bin/env bash
# Render 建置腳本：安裝套件 → 收集靜態檔 → 建立資料表 → 匯入資料 → 建立驗收帳號
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_data
python manage.py ensure_accounts
