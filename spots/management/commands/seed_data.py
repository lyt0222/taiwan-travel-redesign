"""
匯入全台 22 縣市示範景點資料（可重複執行，不會產生重複資料，並自動補齊照片網址）。
python manage.py seed_data

景點名稱與所在地依交通部觀光署臺灣觀光資訊網核對；
班次、票價、開放時間請以官方公告為準，這裡不填入未核對的數值。
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from spots.models import County, Spot, Theme, Town

COUNTIES = [
    ("雲林縣", 1),
    ("基隆市", 2),
    ("臺北市", 3),
    ("新北市", 4),
    ("桃園市", 5),
    ("新竹市", 6),
    ("新竹縣", 7),
    ("苗栗縣", 8),
    ("臺中市", 9),
    ("彰化縣", 10),
    ("南投縣", 11),
    ("嘉義市", 12),
    ("嘉義縣", 13),
    ("臺南市", 14),
    ("高雄市", 15),
    ("屏東縣", 16),
    ("宜蘭縣", 17),
    ("花蓮縣", 18),
    ("臺東縣", 19),
    ("澎湖縣", 20),
    ("金門縣", 21),
    ("連江縣", 22),
]

THEMES = [
    ("老街", "oldstreet", "街屋建築、在地小吃與散步路線", 1),
    ("親子共遊", "family", "適合帶孩子同行、有活動空間的景點", 2),
    ("樂齡旅遊", "senior", "步行負擔低、休息點充足，適合長者", 3),
    ("生態體驗", "eco", "濕地、賞鳥、自然景觀", 4),
    ("宗教文化", "culture", "廟宇、歷史建築與地方文化館舍", 5),
    ("山林步道", "trail", "需要一定體力的山區與步道", 6),
]

TOURISM_SEARCH = "https://www.taiwan.net.tw/m1.aspx?sNo=0000064&keyString="
TRA = "臺鐵班次請至臺灣鐵路官網查詢：https://www.railway.gov.tw/"
BUS = "客運與台灣好行路線、班次請以官方公告為準：https://www.taiwantrip.com.tw/"

PHOTO_MAP = {
    # 雲林縣 (12)
    "太平老街": "https://commons.wikimedia.org/wiki/Special:FilePath/%E6%96%97%E5%85%AD%E5%A4%AA%E5%B9%B3%E8%80%81%E8%A1%97_Douliu_Taiping_Road_-_panoramio.jpg?width=800",
    "綠色隧道景觀公園": "https://commons.wikimedia.org/wiki/Special:FilePath/%E7%B6%A0%E8%89%B2%E9%9A%A7%E9%81%93_-_panoramio.jpg?width=800",
    "椬梧滯洪池": "https://commons.wikimedia.org/wiki/Special:FilePath/%E6%88%90%E9%BE%8D%E6%BF%95%E5%9C%B020261117_%E7%A8%AE%E5%AD%90%E8%88%87%E5%A4%95%E9%99%BD.jpg?width=800",
    "北港朝天宮": "https://commons.wikimedia.org/wiki/Special:FilePath/%E5%8C%97%E6%B8%AF%E6%9C%9D%E5%A4%A9%E5%AE%AE_%E5%A4%A9%E4%B8%8A%E8%81%96%E6%AF%8D_%E5%BB%9F%E5%AE%87%E6%8B%8D%E6%94%9D.jpg?width=800",
    "西螺大橋": "https://commons.wikimedia.org/wiki/Special:FilePath/%E8%A5%BF%E8%9E%BA%E5%A4%A7%E6%A9%8B_(cropped).jpg?width=800",
    "西螺延平老街": "https://commons.wikimedia.org/wiki/Special:FilePath/%E6%96%97%E5%85%AD%E5%A4%AA%E5%B9%B3%E8%B7%AF%E8%80%81%E8%A1%97_Douliu_Taiping_Old_Street_-_panoramio.jpg?width=800",
    "劍湖山世界": "https://commons.wikimedia.org/wiki/Special:FilePath/Janfusun_Fancyworld_Sky_Wheel_20211009.jpg?width=800",
    "雲林布袋戲館": "https://commons.wikimedia.org/wiki/Special:FilePath/%E9%9B%B2%E6%9E%97%E5%B8%83%E8%A2%8B%E6%88%B2%E9%A4%A8.jpg?width=800",
    "虎尾糖廠": "https://commons.wikimedia.org/wiki/Special:FilePath/%E8%99%8E%E5%B0%BE%E7%B3%96%E5%BB%A001.JPG?width=800",
    "雲林故事館": "https://commons.wikimedia.org/wiki/Special:FilePath/Residence_of_the_Huwei_County_Magistrate_(presently_Yunlin_Story_House)_(Taiwan).jpg?width=800",
    "草嶺風景區": "https://commons.wikimedia.org/wiki/Special:FilePath/Caoling_(Yunlin_County).JPG?width=800",
    "成龍濕地": "https://commons.wikimedia.org/wiki/Special:FilePath/%E6%88%90%E9%BE%8D%E6%BF%95%E5%9C%B020261117_%E7%A8%AE%E5%AD%90%E8%88%87%E5%A4%95%E9%99%BD.jpg?width=800",
    # 全台其餘 21 縣市代表景點
    "正濱漁港色彩屋": "https://commons.wikimedia.org/wiki/Special:FilePath/Zhengbin_Fishing_Harbor_%E6%AD%A3%E6%BF%B1%E6%BC%81%E6%B8%AF_-_panoramio.jpg?width=800",
    "大稻埕碼頭": "https://commons.wikimedia.org/wiki/Special:FilePath/Dadaocheng_Wharf.jpg?width=800",
    "九份老街": "https://commons.wikimedia.org/wiki/Special:FilePath/%E4%B9%9D%E4%BB%BD%E9%87%91%E5%B1%B1%E5%B2%A9_20071203.jpg?width=800",
    "舊草嶺隧道": "https://commons.wikimedia.org/wiki/Special:FilePath/%E8%88%8A%E8%8D%89%E5%B6%BA%E9%9A%A7%E9%81%93%E7%A6%8F%E9%9A%86%E7%AB%AF_Fulong_End_of_Old_Caoling_Tunnel_-_panoramio.jpg?width=800",
    "大溪老街": "https://commons.wikimedia.org/wiki/Special:FilePath/%E5%A4%A7%E6%BA%AA%E8%80%81%E8%A1%97_Daxi_Historic_Street_-_panoramio_(1).jpg?width=800",
    "新竹都城隍廟": "https://commons.wikimedia.org/wiki/Special:FilePath/2018_Hsinchu_City_God_Temple_i_4.jpg?width=800",
    "內灣老街": "https://commons.wikimedia.org/wiki/Special:FilePath/Neiwan_Line_Monument(2).jpg?width=800",
    "勝興車站": "https://commons.wikimedia.org/wiki/Special:FilePath/%E5%8B%9D%E8%88%88%E8%BB%8A%E7%AB%99%E5%A4%96%E7%89%86.jpg?width=800",
    "高美濕地": "https://commons.wikimedia.org/wiki/Special:FilePath/Gaomei_Wetlands_%E9%AB%98%E7%BE%8E%E6%BF%95%E5%9C%B0_-_panoramio_(2).jpg?width=800",
    "鹿港老街": "https://commons.wikimedia.org/wiki/Special:FilePath/%E9%B9%BF%E6%B8%AF%E8%80%81%E8%A1%97.jpg?width=800",
    "日月潭": "https://commons.wikimedia.org/wiki/Special:FilePath/View_on_Sun_Moon_Lake,_Taiwan.jpg?width=800",
    "檜意森活村": "https://commons.wikimedia.org/wiki/Special:FilePath/Hinoki_Village_wooden_wall_by_Chiayi_Forestry_District_Office_20160326.jpg?width=800",
    "阿里山國家森林遊樂區": "https://commons.wikimedia.org/wiki/Special:FilePath/Alishan_(%E9%98%BF%E9%87%8C%E5%B1%B1)_-_panoramio.jpg?width=800",
    "安平古堡": "https://commons.wikimedia.org/wiki/Special:FilePath/%E5%AE%89%E5%B9%B3%E5%8F%A4%E5%A0%A1_-_Anping_Fortress_-_2012.02_-_panoramio.jpg?width=800",
    "蓮池潭風景區": "https://commons.wikimedia.org/wiki/Special:FilePath/%E8%93%AE%E6%B1%A0%E6%BD%AD_%E9%BE%8D%E8%99%8E%E5%A1%94_Lotus_Pond_Dragon_and_Tiger_Pagodas_-_panoramio.jpg?width=800",
    "墾丁鵝鑾鼻燈塔": "https://commons.wikimedia.org/wiki/Special:FilePath/%E5%A2%BE%E4%B8%81%E5%9C%8B%E5%AE%B6%E5%85%AC%E5%9C%92%E9%B5%9D%E9%91%BE%E9%BC%BB%E7%87%88%E5%A1%94.jpg?width=800",
    "羅東林業文化園區": "https://commons.wikimedia.org/wiki/Special:FilePath/%E7%BE%85%E6%9D%B1%E6%9E%97%E6%A5%AD%E5%9C%92%E5%8D%80_Luodong_Forestry_Park_-_panoramio.jpg?width=800",
    "太魯閣國家公園": "https://commons.wikimedia.org/wiki/Special:FilePath/Taroko_National_Park-Lin_Wen_Hung-01.jpg?width=800",
    "三仙台風景區": "https://commons.wikimedia.org/wiki/Special:FilePath/%E5%8F%B0%E6%9D%B1%E7%B8%A3%E4%B8%89%E4%BB%99%E5%8F%B0_-_panoramio.jpg?width=800",
    "七美雙心石滬": "https://commons.wikimedia.org/wiki/Special:FilePath/%E4%B8%83%E7%BE%8E%E9%9B%99%E5%BF%83%E7%9F%B3%E6%BB%AC.jpg?width=800",
    "翟山坑道": "https://commons.wikimedia.org/wiki/Special:FilePath/%E7%BF%9F%E5%B1%B1%E5%9D%91%E9%81%93.jpg?width=800",
    "南竿北海坑道": "https://commons.wikimedia.org/wiki/Special:FilePath/North_Sea_Tunnel_%E5%8C%97%E6%B5%B7%E5%9D%91%E9%81%93_-_panoramio.jpg?width=800",
}

SPOTS = [
    # --- 雲林縣 (12) ---
    {
        "name": "太平老街",
        "county": "雲林縣", "town": "斗六市",
        "themes": ["oldstreet", "senior", "culture"],
        "summary": "保存巴洛克式街屋立面的老街，從斗六車站步行可達。",
        "description": "太平老街位於斗六市區，沿街保留日治時期的巴洛克式立面街屋，山牆上的家族名號與泥塑裝飾值得細看。街上商家以在地小吃、伴手禮為主，路面平坦，適合慢慢散步。",
        "transport": "搭乘臺鐵至斗六站，出站後步行可達老街；實際距離與時間請依導航確認。\n" + TRA,
        "station": "臺鐵 斗六站",
        "friendly": "老街路面平坦，沿途有商家與座椅可休息；假日人潮較多，建議上午前往。",
        "walking": "low", "transit": True, "color": "#9a6b4f", "views": 32810,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001016&id=A12-00249",
    },
    {
        "name": "綠色隧道景觀公園",
        "county": "雲林縣", "town": "古坑鄉",
        "themes": ["family", "eco"],
        "summary": "芒果樹夾道形成的綠色隧道，適合散步、騎單車。",
        "description": "古坑綠色隧道由道路兩側的老芒果樹交織成林蔭，旁邊設有景觀公園與步道，是親子散步、騎腳踏車的熱門地點。夏天樹蔭濃密，較不炎熱。",
        "transport": "可由臺鐵斗六站轉乘客運前往古坑；自行開車者周邊設有停車空間。\n" + BUS,
        "station": "臺鐵 斗六站（轉乘客運）",
        "friendly": "公園內步道平緩，適合推嬰兒車；出發前請確認廁所與停車位置。",
        "walking": "low", "transit": False, "color": "#4f8a5b", "views": 28440,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001016&id=A12-00250",
    },
    {
        "name": "椬梧滯洪池",
        "county": "雲林縣", "town": "口湖鄉",
        "themes": ["eco", "senior"],
        "summary": "結合滯洪功能與水域景觀的濕地，適合賞鳥、看夕陽。",
        "description": "椬梧滯洪池位於口湖鄉，兼具防洪與生態功能，水面開闊，常可見到水鳥停留。周邊有環池步道，傍晚的夕陽景色很受攝影愛好者歡迎。",
        "transport": "大眾運輸班次較少，建議先查詢客運路線或自行開車前往。\n" + BUS,
        "station": "",
        "friendly": "環池步道平坦，步行負擔低；戶外缺少遮蔽，請注意防曬與補水。",
        "walking": "low", "transit": False, "color": "#5b88a6", "views": 9120,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001016&id=A12-00439",
    },
    {
        "name": "北港朝天宮",
        "county": "雲林縣", "town": "北港鎮",
        "themes": ["culture", "senior", "oldstreet"],
        "summary": "主祀媽祖的歷史古廟，周邊老街有在地小吃。",
        "description": "北港朝天宮為臺灣重要的媽祖信仰中心之一，廟宇建築雕刻精緻。廟前的中山路一帶商家林立，可品嚐北港在地小吃與伴手禮。",
        "transport": "可由臺鐵嘉義站轉乘往北港的客運，下車後步行可達。\n" + BUS,
        "station": "臺鐵 嘉義站（轉乘客運）",
        "friendly": "廟埕與周邊街道平坦；節慶期間人潮眾多，行動不便者建議避開進香高峰。",
        "walking": "low", "transit": True, "color": "#b3523d", "views": 41250,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001116&id=412",
    },
    {
        "name": "西螺大橋",
        "county": "雲林縣", "town": "西螺鎮",
        "themes": ["culture"],
        "summary": "橫跨濁水溪的紅色鋼構橋，曾被稱為遠東第一長橋。",
        "description": "西螺大橋連接彰化溪州與雲林西螺，紅色鋼桁架造型醒目，是臺灣重要的交通歷史地景。橋面可步行參觀，傍晚的光線特別適合拍照。",
        "transport": "可搭乘客運至西螺市區後步行或轉乘前往。\n" + BUS,
        "station": "",
        "friendly": "橋面為平地步行，但全長較長，可視體力走一小段即回頭。",
        "walking": "mid", "transit": True, "color": "#c0392b", "views": 22600,
        "url": "",
    },
    {
        "name": "西螺延平老街",
        "county": "雲林縣", "town": "西螺鎮",
        "themes": ["oldstreet", "culture"],
        "summary": "保留傳統街屋與醬油老店的老街，可順遊西螺大橋。",
        "description": "延平老街是西螺市區的傳統商街，沿途有許多歷史街屋，以醬油、在地小吃聞名，可與西螺大橋安排在同一天。",
        "transport": "可搭乘客運至西螺站，下車後步行前往。\n" + BUS,
        "station": "",
        "friendly": "街道平坦，但部分人行道較窄，推車通行時請留意車輛。",
        "walking": "low", "transit": True, "color": "#8c6d46", "views": 15730,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001116&id=9967",
    },
    {
        "name": "劍湖山世界",
        "county": "雲林縣", "town": "古坑鄉",
        "themes": ["family"],
        "summary": "大型主題樂園，有多項遊樂設施，適合全家出遊。",
        "description": "劍湖山世界是中部知名的主題樂園，園區內有適合不同年齡的遊樂設施與表演活動。部分設施有身高限制，出發前請先查詢官方資訊。",
        "transport": "可由臺鐵斗六站轉乘接駁或客運前往；自行開車有停車場。\n" + BUS,
        "station": "臺鐵 斗六站（轉乘）",
        "friendly": "園區範圍大，建議攜帶推車；部分設施有身高、年齡限制，請以官方公告為準。",
        "walking": "mid", "transit": False, "color": "#d9822b", "views": 56320,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001116&id=2128",
    },
    {
        "name": "雲林布袋戲館",
        "county": "雲林縣", "town": "虎尾鎮",
        "themes": ["culture", "family", "senior"],
        "summary": "由歷史建築改建的布袋戲館，認識雲林的布袋戲文化。",
        "description": "雲林布袋戲館位於虎尾鎮，由日治時期的歷史建築改建而成，展示布袋戲偶、舞台與相關文物，適合親子與長輩一同參觀。",
        "transport": "可搭乘高鐵至雲林站，再轉乘客運前往虎尾市區。\n" + BUS,
        "station": "高鐵 雲林站（轉乘客運）",
        "friendly": "室內展區，可避開日曬雨淋；開放時間與休館日請以官方公告為準。",
        "walking": "low", "transit": True, "color": "#7b4f8a", "views": 18900,
        "url": "",
    },
    {
        "name": "虎尾糖廠",
        "county": "雲林縣", "town": "虎尾鎮",
        "themes": ["culture", "family"],
        "summary": "百年糖廠與五分車鐵道，冰品是必吃點心。",
        "description": "虎尾糖廠是臺灣仍持續製糖的糖廠之一，廠區保留舊式建築與五分車鐵道，販售部的冰品很受歡迎，適合親子散步。",
        "transport": "可搭乘高鐵至雲林站，再轉乘客運前往虎尾市區。\n" + BUS,
        "station": "高鐵 雲林站（轉乘客運）",
        "friendly": "廠區平坦，步行負擔低；冰品部假日排隊人潮較多。",
        "walking": "low", "transit": True, "color": "#6a8f3a", "views": 20440,
        "url": "",
    },
    {
        "name": "雲林故事館",
        "county": "雲林縣", "town": "虎尾鎮",
        "themes": ["culture", "senior", "family"],
        "summary": "日式木造建築改建的文化館，常有說故事與手作活動。",
        "description": "雲林故事館由日治時期的官舍建築修復而成，保留木造建築之美，館方常舉辦說故事、手作等活動，適合親子與長輩參加。",
        "transport": "位於虎尾市區，可與雲林布袋戲館、虎尾糖廠排在同一天。\n" + BUS,
        "station": "高鐵 雲林站（轉乘客運）",
        "friendly": "建築為老屋，部分區域有門檻；活動時間請以官方公告為準。",
        "walking": "low", "transit": True, "color": "#a0794a", "views": 8650,
        "url": "",
    },
    {
        "name": "草嶺風景區",
        "county": "雲林縣", "town": "古坑鄉",
        "themes": ["trail", "eco"],
        "summary": "山區地質景觀與竹林步道，適合有體力的健行者。",
        "description": "草嶺位於古坑鄉山區，擁有特殊地質景觀與竹林步道。山路蜿蜒、步道有高低落差，建議安排一整天並注意天氣變化。",
        "transport": "山區大眾運輸班次有限，請先查詢台灣好行等路線班次，或自行開車前往。\n" + BUS,
        "station": "",
        "friendly": "步道有階梯與坡度，步行負擔較高；雨後路面濕滑，請穿防滑鞋。",
        "walking": "high", "transit": False, "color": "#2f6b4f", "views": 24880,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001116&id=2127",
    },
    {
        "name": "成龍濕地",
        "county": "雲林縣", "town": "口湖鄉",
        "themes": ["eco", "senior"],
        "summary": "由農地轉變而成的濕地，結合生態與地景藝術。",
        "description": "成龍濕地位於口湖鄉，因地層下陷形成，後來發展為生態與環境藝術的場域，可觀察水鳥並欣賞沿岸的藝術作品。",
        "transport": "大眾運輸班次較少，建議先查詢客運路線或自行開車前往。\n" + BUS,
        "station": "",
        "friendly": "以平地步行為主；戶外缺少遮蔽，請注意防曬。",
        "walking": "low", "transit": False, "color": "#4c7f8f", "views": 7310,
        "url": "",
    },
    # --- 北部縣市 (基隆、臺北、新北、桃園、新竹市、新竹縣、宜蘭) ---
    {
        "name": "正濱漁港色彩屋",
        "county": "基隆市", "town": "中正區",
        "themes": ["senior", "family", "culture"],
        "summary": "繽紛彩繪屋倒映港灣水面，適合散步拍照與品嚐海港美食。",
        "description": "正濱漁港位於和平島南方，是歷史悠久的舊漁港。港邊一排彩繪屋在水面形成美麗倒影，岸邊步道平緩好走，鄰近和平島地質公園。",
        "transport": "搭乘臺鐵至基隆站，轉乘基隆市公車 101、104 或台灣好行濱海奇基線至正濱漁港站。\n" + BUS,
        "station": "臺鐵 基隆站（轉乘公車）",
        "friendly": "觀景平台與港邊人行道平坦，步行距離短，適合長輩與親子輕鬆停留。",
        "walking": "low", "transit": True, "color": "#2e86ab", "views": 58400,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001105&id=A12-00348",
    },
    {
        "name": "大稻埕碼頭",
        "county": "臺北市", "town": "大同區",
        "themes": ["oldstreet", "senior", "culture"],
        "summary": "從迪化街歷史街區走向淡水河岸，欣賞河濱夕陽與城市風景。",
        "description": "大稻埕碼頭位於臺北大同區，鄰近迪化街南北貨老街與河岸空間。河濱步道全線平坦無階梯，適合傍晚散步與慢步旅行。",
        "transport": "可搭乘臺北捷運松山新店線至北門站，或中和新蘆線至大橋頭站步行前往。",
        "station": "捷運 北門站／大橋頭站",
        "friendly": "河濱廣場與老街皆為平面道路，座椅與無障礙廁所齊全。",
        "walking": "low", "transit": True, "color": "#5c6f84", "views": 72300,
        "url": "https://www.travel.taipei/zh-tw/attraction/details/1",
    },
    {
        "name": "九份老街",
        "county": "新北市", "town": "瑞芳區",
        "themes": ["oldstreet", "culture"],
        "summary": "依山傍海的山城老街，紅燈籠茶樓與海灣山景聞名國際。",
        "description": "九份老街位於新北市瑞芳區山城，保留日治時期礦業聚落的階梯巷弄與茶樓建築，可遠眺基隆嶼海景並品嚐芋圓等在地小吃。",
        "transport": "搭乘臺鐵至瑞芳站，或由捷運忠孝復興站、西門站搭乘基隆客運直達九份老街站。\n" + BUS,
        "station": "臺鐵 瑞芳站（轉乘客運）",
        "friendly": "基山街前段較平緩，但豎崎路為連續石階，輪椅或推車建議停留於汽車路與基山街平緩段。",
        "walking": "high", "transit": True, "color": "#b84a39", "views": 94200,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001091&id=290",
    },
    {
        "name": "舊草嶺隧道",
        "county": "新北市", "town": "貢寮區",
        "themes": ["family", "eco", "senior"],
        "summary": "由百年鐵路隧道改建的清涼自行車與散步廊道，出口即見龜山島海景。",
        "description": "舊草嶺隧道全長約 2.1 公里，地面仿鐵軌鋪面平坦寬敞，隧道內冬暖夏涼，出南口即可遠眺太平洋與龜山島，非常適合親子與樂齡族。",
        "transport": "搭乘臺鐵至福隆站，出站後步行或租借單車即可抵達隧道北口。\n" + TRA,
        "station": "臺鐵 福隆站",
        "friendly": "隧道內全線無階梯、照明充足且遮陽避雨，入口設有完善洗手間與休息區。",
        "walking": "low", "transit": True, "color": "#3d6b5e", "views": 51200,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001091&id=A12-00108",
    },
    {
        "name": "大溪老街",
        "county": "桃園市", "town": "大溪區",
        "themes": ["oldstreet", "family", "senior", "culture"],
        "summary": "華麗巴洛克牌樓與百年豆干名產，順遊大溪橋與木藝生態博物館。",
        "description": "大溪老街以和平路、中山路一帶的日治巴洛克式牌樓聞名，結合傳統木器行與豆干美食，周邊中正公園設有景觀電梯方便長者與推車通行。",
        "transport": "可由臺鐵桃園站、中壢站或高鐵桃園站搭乘台灣好行大溪快線直達。\n" + BUS,
        "station": "高鐵 桃園站／臺鐵 桃園站（轉乘台灣好行）",
        "friendly": "老街路面平坦，大溪橋頭至老街設有透明景觀電梯，免爬長階梯即可往返。",
        "walking": "low", "transit": True, "color": "#8f5b3c", "views": 67400,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001107&id=3215",
    },
    {
        "name": "新竹都城隍廟",
        "county": "新竹市", "town": "北區",
        "themes": ["culture", "oldstreet", "senior"],
        "summary": "超過兩百五十年歷史的官封城隍廟，廟埕匯聚新竹米粉與貢丸老店。",
        "description": "新竹都城隍廟創建於清乾隆年間，建築木雕與匾額極具歷史價值。廟前廣場與周邊街區聚集百年小吃攤商，從新竹火車站步行約 10 分鐘即可抵達。",
        "transport": "搭乘臺鐵至新竹站，出站沿中正路轉東門街步行約 10 分鐘即達。\n" + TRA,
        "station": "臺鐵 新竹站",
        "friendly": "市區人行道與廟埕全為平面動線，周邊百貨與公有市場皆有無障礙洗手間。",
        "walking": "low", "transit": True, "color": "#a63d2f", "views": 53800,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001108&id=2169",
    },
    {
        "name": "內灣老街",
        "county": "新竹縣", "town": "橫山鄉",
        "themes": ["oldstreet", "family", "culture"],
        "summary": "搭乘臺鐵內灣支線直達山城，品嚐野薑花粽與客家擂茶、漫步內灣吊橋。",
        "description": "內灣老街位於新竹縣橫山鄉，保留早期林業與礦業小鎮風情，出內灣火車站即是老街商圈，可順遊內灣戲院與橫跨油羅溪的內灣吊橋。",
        "transport": "搭乘臺鐵新竹內灣支線至終點「內灣站」，出站即達老街中心。\n" + TRA,
        "station": "臺鐵 內灣站",
        "friendly": "火車站出站直接銜接平坦老街，無須跨越多層天橋，適合全家搭乘小火車出遊。",
        "walking": "low", "transit": True, "color": "#7a6348", "views": 61500,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001109&id=9613",
    },
    {
        "name": "羅東林業文化園區",
        "county": "宜蘭縣", "town": "羅東鎮",
        "themes": ["eco", "family", "senior", "culture"],
        "summary": "昔日太平山林場貯木池與森林鐵路車站，環池木棧道綠意盎然。",
        "description": "羅東林業文化園區保留日治時期羅東出張所、貯木池、竹林車站與蒸汽火車頭，環池步道平緩舒適、樹蔭濃密，免費入園，非常適合親子與長輩。",
        "transport": "搭乘臺鐵至羅東站，由前站出口沿中正北路步行約 10 分鐘即可抵達。\n" + TRA,
        "station": "臺鐵 羅東站",
        "friendly": "園區全線為平緩木棧道與碎石步道，座椅密集且設有多處無障礙廁所，推車與輪椅皆好走。",
        "walking": "low", "transit": True, "color": "#3d7a5a", "views": 64100,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001106&id=A12-00138",
    },
    # --- 中部縣市 (苗栗、臺中、彰化、南投) ---
    {
        "name": "勝興車站",
        "county": "苗栗縣", "town": "三義鄉",
        "themes": ["culture", "family", "oldstreet"],
        "summary": "舊山線鐵道最高點木造車站，結合鐵道自行車與三義客家老街。",
        "description": "勝興車站標高 402.326 公尺，是臺鐵舊山線海拔最高的日式木造車站，整棟建築不使用一根鐵釘。周邊老街有客家擂茶與麻糬，並可預約搭乘舊山線鐵道自行車。",
        "transport": "搭乘臺鐵至三義站，轉乘計程車或接駁專車前往勝興車站。\n" + TRA,
        "station": "臺鐵 三義站（轉乘）",
        "friendly": "站前廣場與老街主幹道平緩，惟假日車流較多，建議搭乘接駁車於老街入口下車。",
        "walking": "low", "transit": False, "color": "#7c5836", "views": 59300,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001110&id=2899",
    },
    {
        "name": "高美濕地",
        "county": "臺中市", "town": "清水區",
        "themes": ["eco"],
        "summary": "風車與夕陽聞名的濕地，有木棧道可走入潮間帶。",
        "description": "高美濕地位於臺中市清水區大甲溪出海口南側，木棧道延伸至潮間帶，夕陽與風車是代表景色。當地可見珍貴的雲林莞草，也常與彰化、雲林沿海濕地一起列入中部海岸生態行程（因此關鍵字搜「雲林」會比對到此臺中景點，需搭配地區篩選）。",
        "transport": "可搭乘臺鐵海線至清水站或臺中市區公車前往。\n" + TRA,
        "station": "臺鐵 清水站（轉乘公車）",
        "friendly": "木棧道平坦；海風強勁，傍晚人潮多，請留意潮汐與保暖。",
        "walking": "low", "transit": True, "color": "#d08a3c", "views": 97793,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001112&id=2260",
    },
    {
        "name": "鹿港老街",
        "county": "彰化縣", "town": "鹿港鎮",
        "themes": ["oldstreet", "culture"],
        "summary": "紅磚老街與傳統小吃，周邊廟宇古蹟密集。",
        "description": "鹿港老街保留紅磚街道與傳統街屋，周邊有天后宮、龍山寺等古蹟，可同時體驗老街散步與在地小吃。",
        "transport": "可由臺鐵彰化站轉乘客運前往鹿港。\n" + BUS,
        "station": "臺鐵 彰化站（轉乘客運）",
        "friendly": "老街鋪面為紅磚，略有不平；假日人潮多。",
        "walking": "low", "transit": True, "color": "#a84a3a", "views": 66120,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001113&id=631",
    },
    {
        "name": "日月潭",
        "county": "南投縣", "town": "魚池鄉",
        "themes": ["eco", "senior", "family"],
        "summary": "用湖光山色作為旅程起點，挑選適合自己的環湖木棧道與停留點。",
        "description": "日月潭位於南投魚池，可從水社、向山或伊達邵等據點欣賞湖景。向山段自行車與人行步道平緩寬敞，請依同行者需求選擇目的地。",
        "transport": "可於臺鐵臺中站或高鐵臺中站轉乘台灣好行日月潭線直達。\n" + BUS,
        "station": "高鐵 臺中站（轉乘台灣好行）",
        "friendly": "向山遊客中心與水社壩步道平緩，設有完善無障礙洗手間與觀景平台。",
        "walking": "low", "transit": True, "color": "#3b7a9c", "views": 91500,
        "url": "https://www.sunmoonlake.gov.tw/zh-TW",
    },
    # --- 南部縣市 (嘉義市、嘉義縣、臺南、高雄、屏東) ---
    {
        "name": "檜意森活村",
        "county": "嘉義市", "town": "東區",
        "themes": ["culture", "family", "senior"],
        "summary": "日式木造宿舍群，結合文創商店與展覽。",
        "description": "檜意森活村由日治時期林業宿舍群修復而成，木造建築與庭園環境清幽，現有文創商店與展覽空間，適合散步拍照。",
        "transport": "由臺鐵嘉義站搭乘市區公車或計程車前往。\n" + TRA,
        "station": "臺鐵 嘉義站",
        "friendly": "園區平坦，步行負擔低；部分老屋有門檻。",
        "walking": "low", "transit": True, "color": "#8a6a3f", "views": 35210,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001121&id=11784",
    },
    {
        "name": "阿里山國家森林遊樂區",
        "county": "嘉義縣", "town": "阿里山鄉",
        "themes": ["trail", "eco"],
        "summary": "在山林與霧氣之間，認識森林鐵道、神木群與高山景觀。",
        "description": "阿里山的森林、鐵道與山景提供多樣的旅遊體驗。山區步行與氣候條件和市區不同，請事先確認適合的路線、入園資訊及交通安排。",
        "transport": "可由高鐵嘉義站或臺鐵嘉義站轉乘台灣好行阿里山線前往。\n" + BUS,
        "station": "臺鐵／高鐵 嘉義站（轉乘台灣好行）",
        "friendly": "山區步道多有坡度與階梯，氣溫較平地低，請備妥保暖衣物並評估體力。",
        "walking": "mid", "transit": True, "color": "#2d5a4c", "views": 84200,
        "url": "https://recreation.forest.gov.tw/forest/ra?typ_id=0500001",
    },
    {
        "name": "安平古堡",
        "county": "臺南市", "town": "安平區",
        "themes": ["oldstreet", "family", "culture"],
        "summary": "從荷蘭時期歷史建築出發，結合安平老街認識臺南文化故事。",
        "description": "安平古堡是認識臺灣早期歷史的重要古蹟，周邊緊鄰安平老街與延平街，可安排半日文化與美食散步行程。",
        "transport": "可由臺鐵臺南站搭乘臺南市區公車 2 路或台灣好行至安平古堡站。",
        "station": "臺鐵 臺南站（轉乘市區公車）",
        "friendly": "園區入口與平面展區平緩，惟登上瞭望臺需走階梯，長者可於平面古蹟區參觀。",
        "walking": "low", "transit": True, "color": "#a85d44", "views": 68900,
        "url": "https://historic.tainan.gov.tw/index.php?id=58&lang=cht&option=module&task=pageinfo",
    },
    {
        "name": "蓮池潭風景區",
        "county": "高雄市", "town": "左營區",
        "themes": ["culture", "senior", "family"],
        "summary": "龍虎塔與春秋閣倒映湖面，高鐵左營站旁最具代表性的環湖景區。",
        "description": "蓮池潭位於高雄市左營區，以「入龍喉、出虎口」的龍虎塔及五里亭聞名國際。環潭步道寬敞平坦，鄰近左營舊城與高鐵站，交通極為便利。",
        "transport": "搭乘高鐵、臺鐵至新左營站（左營站），步行約 10～15 分鐘或轉乘紅 35 公車即達。\n" + TRA,
        "station": "高鐵 左營站／臺鐵 新左營站",
        "friendly": "環湖步道平坦、沿途涼亭與長椅密集，非常適合長輩散步與親子推車同行。",
        "walking": "low", "transit": True, "color": "#c95b3c", "views": 78500,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001121&id=2144",
    },
    {
        "name": "墾丁鵝鑾鼻燈塔",
        "county": "屏東縣", "town": "恆春鎮",
        "themes": ["eco", "family"],
        "summary": "臺灣最南端純白武裝燈塔，碧海藍天與珊瑚礁草地視野遼闊。",
        "description": "鵝鑾鼻燈塔位於屏東縣恆春鎮墾丁國家公園內，為十九世紀末建造的純白色燈塔，園區內擁有大片綠地與珊瑚礁海岸步道，可遠眺巴士海峽。",
        "transport": "於高鐵左營站轉乘台灣好行「墾丁快線」至墾丁，再轉乘街車至鵝鑾鼻站。\n" + BUS,
        "station": "高鐵 左營站（轉乘墾丁快線）",
        "friendly": "入口至燈塔主草原步道為緩坡柏油路，適合步行拍照；海濱珊瑚礁林區則有階梯。",
        "walking": "mid", "transit": True, "color": "#2b7a9b", "views": 82600,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001122&id=421",
    },
    # --- 東部縣市 (花蓮、臺東) ---
    {
        "name": "太魯閣國家公園",
        "county": "花蓮縣", "town": "秀林鄉",
        "themes": ["trail", "eco"],
        "summary": "立霧溪切割出的壯麗大理石峽谷，世界級地質與山林景觀。",
        "description": "太魯閣國家公園以雄偉的大理石峽谷、斷崖與瀑布聞名。前往前請務必至太魯閣國家公園官網確認各步道最新開放狀況與交管資訊。",
        "transport": "搭乘臺鐵至新城（太魯閣）站或花蓮站，轉乘台灣好行太魯閣線前往遊客中心。\n" + BUS,
        "station": "臺鐵 新城（太魯閣）站",
        "friendly": "太魯閣遊客中心周邊與砂卡礑觀景台較平緩；峽谷步道請務必配戴安全帽並留意落石。",
        "walking": "high", "transit": True, "color": "#2f6858", "views": 89400,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001124&id=154",
    },
    {
        "name": "三仙台風景區",
        "county": "臺東縣", "town": "成功鎮",
        "themes": ["eco", "trail"],
        "summary": "八拱跨海步橋連接離岸小島，東海岸迎曙光與礫石海灘名勝。",
        "description": "三仙台位於臺東縣成功鎮東北方，由離岸小島與珊瑚礁海岸構成，波浪造型的八拱跨海步橋是東海岸極具代表性的地標。",
        "transport": "於臺鐵臺東站或玉里站轉乘台灣好行「東部海岸線」或興東客運至三仙台遊憩區。\n" + BUS,
        "station": "臺鐵 臺東站（轉乘台灣好行）",
        "friendly": "遊客中心至礫石海灘濱海步道平緩無障礙（適合長輩與推車）；若要登跨海八拱橋則需爬 320 階。",
        "walking": "mid", "transit": True, "color": "#247291", "views": 74100,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001123&id=759",
    },
    # --- 離島縣市 (澎湖、金門、連江) ---
    {
        "name": "七美雙心石滬",
        "county": "澎湖縣", "town": "七美鄉",
        "themes": ["eco", "culture"],
        "summary": "玄武岩與珊瑚礁砌成的雙心造型傳統捕魚石滬，澎湖離島經典地景。",
        "description": "雙心石滬位於澎湖縣七美鄉東湖村頂隙北面海崖下，是先民利用玄武岩及珊瑚礁在潮間帶築成的捕魚陷阱，退潮時雙心輪廓最為清晰。",
        "transport": "由馬公南海遊客中心搭乘交通船前往七美嶼，登島後轉乘環島公車或租車至雙心石滬。",
        "station": "澎湖 馬公南海碼頭（搭船至七美）",
        "friendly": "崖頂觀景台道路平坦、視野極佳，不需走下陡峭階梯即可完整俯瞰雙心石滬全貌。",
        "walking": "low", "transit": False, "color": "#1f6f8b", "views": 76800,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001125&id=2298",
    },
    {
        "name": "翟山坑道",
        "county": "金門縣", "town": "金城鎮",
        "themes": ["culture", "senior"],
        "summary": "鬼斧神工的花崗岩A字型水道坑道，水面倒影與戰地歷史交織。",
        "description": "翟山坑道位於金門縣金城鎮古崗湖東南側，為八二三砲戰期間開鑿供登陸小艇運補的花崗岩地下水道，坑道內水面倒影壯觀且氣溫涼爽。",
        "transport": "可由金城車站搭乘台灣好行金門線（A線水頭翟山線）直達翟山坑道站。\n" + BUS,
        "station": "金門 金城車站（轉乘台灣好行）",
        "friendly": "坑道入口至觀景台步道寬敞堅固，惟進入水道區有一段緩階梯，行走時請握扶手。",
        "walking": "mid", "transit": True, "color": "#5d6b56", "views": 63200,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001126&id=2277",
    },
    {
        "name": "南竿北海坑道",
        "county": "連江縣", "town": "南竿鄉",
        "themes": ["culture", "eco"],
        "summary": "馬祖最壯觀的花崗岩井字型地下碼頭，夜間可搭乘搖櫓船賞藍眼淚。",
        "description": "南竿北海坑道位於連江縣南竿鄉仁愛村附近，步道全長約 700 公尺，配合潮汐開放步道參觀與搖櫓船體驗，春夏季節更是無光害觀賞「藍眼淚」的熱門地點。",
        "transport": "抵達馬祖南竿機場或福澳港後，可搭乘台灣好行＠馬祖路線或公車至北海坑道（仁愛村）。",
        "station": "馬祖 南竿福澳港／南竿機場",
        "friendly": "坑道內環行步道平坦且可搭乘搖櫓船免步行；入坑道前請務必確認當日乾潮開放時段。",
        "walking": "low", "transit": True, "color": "#2c4c6b", "views": 54900,
        "url": "https://www.taiwan.net.tw/m1.aspx?sNo=0001127&id=9203",
    },
]


class Command(BaseCommand):
    help = "匯入全台 22 縣市、主題與 34 筆示範景點資料（可重複執行）"

    @transaction.atomic
    def handle(self, *args, **options):
        counties = {}
        for name, order in COUNTIES:
            counties[name], _ = County.objects.update_or_create(name=name, defaults={"order": order})

        themes = {}
        for name, slug, desc, order in THEMES:
            themes[slug], _ = Theme.objects.update_or_create(
                slug=slug, defaults={"name": name, "description": desc, "order": order}
            )

        created = 0
        for s in SPOTS:
            county = counties[s["county"]]
            town, _ = Town.objects.get_or_create(county=county, name=s["town"])
            spot, was_created = Spot.objects.get_or_create(
                name=s["name"],
                county=county,
                defaults={
                    "town": town,
                    "summary": s["summary"],
                    "description": s["description"],
                    "transport": s["transport"],
                    "nearest_station": s["station"],
                    "friendly_info": s["friendly"],
                    "walking_level": s["walking"],
                    "transit_friendly": s["transit"],
                    "cover_color": s["color"],
                    "views": s["views"],
                    "address": f"{s['county']}{s['town']}{s['name']}",
                    "official_url": s["url"] or TOURISM_SEARCH + s["name"],
                    "image_url": PHOTO_MAP.get(s["name"], ""),
                },
            )
            if was_created:
                spot.themes.set([themes[t] for t in s["themes"]])
                created += 1
            else:
                updated_fields = []
                if not spot.image_url and s["name"] in PHOTO_MAP:
                    spot.image_url = PHOTO_MAP[s["name"]]
                    updated_fields.append("image_url")
                if s["url"] and spot.official_url.startswith(TOURISM_SEARCH):
                    spot.official_url = s["url"]
                    updated_fields.append("official_url")
                if updated_fields:
                    spot.save(update_fields=updated_fields)

        self.stdout.write(
            self.style.SUCCESS(
                f"資料匯入完成：涵蓋全台 {County.objects.count()} 縣市，新增 {created} 個景點，目前共 {Spot.objects.count()} 個景點。"
            )
        )
