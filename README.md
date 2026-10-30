# 臺灣觀光資訊網 Redesign（第四組期中專題）

依「臺灣觀光資訊網介面分析」報告的 P1～P5 問題與 F1～F3 分鏡，實作成可操作的前後台網站。

- 前端：Django Templates（HTML / CSS / JavaScript）
- 後端：Django 5.2 + Django Admin
- 資料庫：Neon PostgreSQL（本機開發自動改用 SQLite）
- 部署：GitHub → Render

---

## 一、Bad UI 問題 → 網站功能對照

| 原始問題 | 網站上的改善 | 位置 |
|---|---|---|
| P1 導覽只有圖示 | 導覽列全部是文字：首頁／景點查詢／旅遊主題／我的行程；「大字模式」按鈕有文字與狀態 | 每一頁上方 |
| P2 查詢入口在長文之後 | 首頁第一屏就是查詢表單；三個情境入口（大眾運輸、親子、樂齡） | 首頁、`/search/` |
| P3 長文疊在照片上 | 白底文字；詳情頁先給一句短摘要，完整介紹可展開；分頁「景點簡介／如何前往／友善指引」；大字模式 | 詳情頁 |
| P4 兩個「全部」沒有名稱 | 結果頁條件摘要寫出「地區、鄉鎮、主題、關鍵字、交通、步行負擔、排序」等欄位名稱，並提供「修改查詢條件」 | 結果頁 |
| P5 卡片沒有所在地 | 每張卡片標出「所在地：縣市＋鄉鎮」；關鍵字輸入縣市名稱時，提示改用「地區」篩選 | 結果頁（試搜「雲林」） |

## 二、頁面與功能

| 頁面 | 網址 | 登入前 | 登入後 |
|---|---|---|---|
| 首頁 | `/` | 快速查詢、情境入口、主題、熱門景點、註冊提示 | 導覽列多出「我的行程」，不顯示註冊提示 |
| 景點查詢 | `/search/?flow=transit｜family｜senior` | 地區→鄉鎮連動選單、主題、關鍵字、大眾運輸、步行負擔、排序 | 同左 |
| 查詢結果 | `/spots/?county=…` | 條件摘要、所在地卡片 | 卡片標示「已在我的行程」 |
| 景點詳情 | `/spots/<id>/` | 三個分頁；按鈕為「登入後加入我的行程」 | 「確認目的地，加入我的行程」／移除 |
| 我的行程 | `/my-trip/` | 自動導向登入頁 | 收藏清單，可填預計出遊日與備註 |
| 登入／註冊 | `/accounts/login/`、`/accounts/register/` | | |
| 管理後台 | `/admin/` | 管理縣市、鄉鎮、主題、景點、會員收藏、使用者 | |

資料表：`County` 縣市、`Town` 鄉鎮、`Theme` 主題、`Spot` 景點、`Favorite` 會員收藏，加上 Django 內建的 `User`。

---

## 三、部署步驟（約 20 分鐘）

### 1. 上傳到 GitHub

1. 到 GitHub 建立一個新的 repository，例如 `taiwan-travel-redesign`（Public 或 Private 皆可）。
2. 在本資料夾執行：

```bash
git init
git add .
git commit -m "期中專題：臺灣觀光資訊網 Redesign"
git branch -M main
git remote add origin https://github.com/<你的帳號>/taiwan-travel-redesign.git
git push -u origin main
```

不熟指令也可以用 GitHub 網頁的「Add file → Upload files」，把整個資料夾內容拖進去。

### 2. 建立 Neon 資料庫

1. 到 https://neon.tech 註冊並建立 Project，Region 建議選 **AWS Asia Pacific (Singapore)**。
2. 在 Dashboard 按「Connect」，複製 **Connection string**，格式如下：
   `postgresql://帳號:密碼@ep-xxxx.ap-southeast-1.aws.neon.tech/neondb?sslmode=require`
3. 這串就是下一步要填的 `DATABASE_URL`（不要公開貼在報告或 GitHub 上）。

### 3. 部署到 Render

1. 到 https://render.com 用 GitHub 帳號登入。
2. 選「New → Blueprint」，選擇剛才的 repository；Render 會讀取 `render.yaml`。
   （也可以選「New → Web Service」手動設定：Runtime `Python 3`、Build Command `./build.sh`、Start Command `gunicorn config.wsgi:application`、Instance Type `Free`。）
3. 填入環境變數（Environment）：

| Key | 值 |
|---|---|
| `DATABASE_URL` | 第 2 步複製的 Neon 連線字串 |
| `DJANGO_SUPERUSER_USERNAME` | 後台管理員帳號，例如 `admin` |
| `DJANGO_SUPERUSER_PASSWORD` | 後台管理員密碼（自訂，至少 8 碼） |
| `DEMO_USERNAME` | 前台測試會員帳號，預設 `demo` |
| `DEMO_PASSWORD` | 前台測試會員密碼，例如 `Travel2026!` |
| `DEBUG` | `False` |
| `SECRET_KEY` | 用 Blueprint 會自動產生；手動建立請填一串長亂碼 |
| `PYTHON_VERSION` | `3.12.7` |

4. 按「Deploy」。`build.sh` 會自動：安裝套件 → 收集靜態檔 → 在 Neon 建資料表 → 匯入 15 個景點 → 建立管理員與測試會員。
5. 部署完成後得到網址，例如 `https://taiwan-travel-redesign.onrender.com`：
   - 前台：`https://<你的網址>/`
   - 後台：`https://<你的網址>/admin/`

> Render 免費方案閒置 15 分鐘會休眠，下次打開要等約 1 分鐘。**Demo 前與繳交前請先打開一次網站**，確認能正常載入。

### 4. 確認 Neon 有資料

到 Neon 的「Tables」頁面，可以看到 `spots_spot`、`spots_favorite`、`auth_user` 等資料表，這張截圖可以放進報告的「後台與資料庫」。

---

## 四、本機執行

```bash
python -m venv .venv
source .venv/bin/activate          # Windows：.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser   # 建立後台帳號
python manage.py ensure_accounts   # 建立前台測試會員 demo / Travel2026!
python manage.py runserver
```

開啟 http://127.0.0.1:8000/ 與 http://127.0.0.1:8000/admin/

執行測試：`python manage.py test`（11 項，涵蓋篩選、登入前後差異、收藏、註冊）

---

## 五、驗收資訊（填入報告）

| 項目 | 內容 |
|---|---|
| 前台網址 | https://＿＿＿＿＿＿.onrender.com/ |
| 後台網址 | https://＿＿＿＿＿＿.onrender.com/admin/ |
| 前台測試會員 | 帳號 `demo`／密碼：＿＿＿＿ |
| 後台管理員 | 帳號 ＿＿＿＿／密碼：＿＿＿＿ |
| GitHub | https://github.com/＿＿＿＿/taiwan-travel-redesign |

建議 Demo 路線：首頁搜尋「雲林」看到縣市提示 → 改用地區篩選 → 卡片確認所在地 → 詳情頁「如何前往」→ 未登入按鈕 → 登入 demo → 加入我的行程 → 填出遊日 → 開大字模式走一次樂齡流程 → 後台新增一個景點，回前台查得到。

## 六、資料說明

景點名稱與所在地依交通部觀光署臺灣觀光資訊網核對。班次、票價與開放時間會變動，網站只引導到官方查詢，不填入未核對的數值。卡片圖片以色塊示意，沒有使用網路上的照片。景點內容可在後台直接修改。
