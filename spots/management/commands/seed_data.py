"""
匯入示範資料（可重複執行，不會產生重複資料）。
python manage.py seed_data

景點名稱與所在地依交通部觀光署臺灣觀光資訊網核對；
班次、票價、開放時間請以官方公告為準，這裡不填入未核對的數值。
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from spots.models import County, Spot, Theme, Town

COUNTIES = [("雲林縣", 1), ("臺中市", 2), ("彰化縣", 3), ("嘉義市", 4), ("嘉義縣", 5), ("南投縣", 6), ("臺北市", 7), ("臺南市", 8)]

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

PHOTO_MAP = {'太平老街': 'https://commons.wikimedia.org/wiki/Special:FilePath/%E6%96%97%E5%85%AD%E5%A4%AA%E5%B9%B3%E8%80%81%E8%A1%97_Douliu_Taiping_Road_-_panoramio.jpg?width=800', '綠色隧道景觀公園': 'https://commons.wikimedia.org/wiki/Special:FilePath/%E7%B6%A0%E8%89%B2%E9%9A%A7%E9%81%93_-_panoramio.jpg?width=800', '椬梧滯洪池': 'https://commons.wikimedia.org/wiki/Special:FilePath/%E6%88%90%E9%BE%8D%E6%BF%95%E5%9C%B020261117_%E7%A8%AE%E5%AD%90%E8%88%87%E5%A4%95%E9%99%BD.jpg?width=800', '北港朝天宮': 'https://commons.wikimedia.org/wiki/Special:FilePath/%E5%8C%97%E6%B8%AF%E6%9C%9D%E5%A4%A9%E5%AE%AE_%E5%A4%A9%E4%B8%8A%E8%81%96%E6%AF%8D_%E5%BB%9F%E5%AE%87%E6%8B%8D%E6%94%9D.jpg?width=800', '西螺大橋': 'https://commons.wikimedia.org/wiki/Special:FilePath/%E8%A5%BF%E8%9E%BA%E5%A4%A7%E6%A9%8B_(cropped).jpg?width=800', '西螺延平老街': 'https://commons.wikimedia.org/wiki/Special:FilePath/%E6%96%97%E5%85%AD%E5%A4%AA%E5%B9%B3%E8%B7%AF%E8%80%81%E8%A1%97_Douliu_Taiping_Old_Street_-_panoramio.jpg?width=800', '劍湖山世界': 'https://commons.wikimedia.org/wiki/Special:FilePath/Janfusun_Fancyworld_Sky_Wheel_20211009.jpg?width=800', '雲林布袋戲館': 'https://commons.wikimedia.org/wiki/Special:FilePath/%E9%9B%B2%E6%9E%97%E5%B8%83%E8%A2%8B%E6%88%B2%E9%A4%A8.jpg?width=800', '虎尾糖廠': 'https://commons.wikimedia.org/wiki/Special:FilePath/%E8%99%8E%E5%B0%BE%E7%B3%96%E5%BB%A001.JPG?width=800', '雲林故事館': 'https://commons.wikimedia.org/wiki/Special:FilePath/Residence_of_the_Huwei_County_Magistrate_(presently_Yunlin_Story_House)_(Taiwan).jpg?width=800', '草嶺風景區': 'https://commons.wikimedia.org/wiki/Special:FilePath/Caoling_(Yunlin_County).JPG?width=800', '成龍濕地': 'https://commons.wikimedia.org/wiki/Special:FilePath/%E6%88%90%E9%BE%8D%E6%BF%95%E5%9C%B020261117_%E7%A8%AE%E5%AD%90%E8%88%87%E5%A4%95%E9%99%BD.jpg?width=800', '高美濕地': 'https://commons.wikimedia.org/wiki/Special:FilePath/Gaomei_Wetlands_%E9%AB%98%E7%BE%8E%E6%BF%95%E5%9C%B0_-_panoramio_(2).jpg?width=800', '鹿港老街': 'https://commons.wikimedia.org/wiki/Special:FilePath/%E9%B9%BF%E6%B8%AF%E8%80%81%E8%A1%97.jpg?width=800', '檜意森活村': 'https://commons.wikimedia.org/wiki/Special:FilePath/Hinoki_Village_wooden_wall_by_Chiayi_Forestry_District_Office_20160326.jpg?width=800', '阿里山國家森林遊樂區': 'https://commons.wikimedia.org/wiki/Special:FilePath/Alishan_(%E9%98%BF%E9%87%8C%E5%B1%B1)_-_panoramio.jpg?width=800', '日月潭': 'https://commons.wikimedia.org/wiki/Special:FilePath/View_on_Sun_Moon_Lake,_Taiwan.jpg?width=800', '大稻埕碼頭': 'https://commons.wikimedia.org/wiki/Special:FilePath/Dadaocheng_Wharf.jpg?width=800', '安平古堡': 'https://commons.wikimedia.org/wiki/Special:FilePath/%E5%AE%89%E5%B9%B3%E5%8F%A4%E5%A0%A1_-_Anping_Fortress_-_2012.02_-_panoramio.jpg?width=800'}

SPOTS = [
    {
        "name": "太平老街",
        "county": "雲林縣", "town": "斗六市",
        "themes": ["oldstreet", "senior", "culture"],
        "summary": "保存巴洛克式街屋立面的老街，從斗六車站步行可達。",
        "description": "太平老街位於斗六市區，沿街保留日治時期的巴洛克式立面街屋，山牆上的家族名號與泥塑裝飾值得細看。"
                       "街上商家以在地小吃、伴手禮為主，路面平坦，適合慢慢散步。",
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
        "description": "古坑綠色隧道由道路兩側的老芒果樹交織成林蔭，旁邊設有景觀公園與步道，"
                       "是親子散步、騎腳踏車的熱門地點。夏天樹蔭濃密，較不炎熱。",
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
        "description": "椬梧滯洪池位於口湖鄉，兼具防洪與生態功能，水面開闊，常可見到水鳥停留。"
                       "周邊有環池步道，傍晚的夕陽景色很受攝影愛好者歡迎。",
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
        "description": "北港朝天宮為臺灣重要的媽祖信仰中心之一，廟宇建築雕刻精緻。"
                       "廟前的中山路一帶商家林立，可品嚐北港在地小吃與伴手禮。",
        "transport": "可由臺鐵嘉義站轉乘往北港的客運，下車後步行可達。\n" + BUS,
        "station": "臺鐵 嘉義站（轉乘客運）",
        "friendly": "廟埕與周邊街道平坦；節慶期間人潮眾多，行動不便者建議避開進香高峰。",
        "walking": "low", "transit": True, "color": "#b3523d", "views": 41250,
        "url": "",
    },
    {
        "name": "西螺大橋",
        "county": "雲林縣", "town": "西螺鎮",
        "themes": ["culture"],
        "summary": "橫跨濁水溪的紅色鋼構橋，曾被稱為遠東第一長橋。",
        "description": "西螺大橋連接彰化溪州與雲林西螺，紅色鋼桁架造型醒目，是臺灣重要的交通歷史地景。"
                       "橋面可步行參觀，傍晚的光線特別適合拍照。",
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
        "description": "延平老街是西螺市區的傳統商街，沿途有許多歷史街屋，"
                       "以醬油、在地小吃聞名，可與西螺大橋安排在同一天。",
        "transport": "可搭乘客運至西螺站，下車後步行前往。\n" + BUS,
        "station": "",
        "friendly": "街道平坦，但部分人行道較窄，推車通行時請留意車輛。",
        "walking": "low", "transit": True, "color": "#8c6d46", "views": 15730,
        "url": "",
    },
    {
        "name": "劍湖山世界",
        "county": "雲林縣", "town": "古坑鄉",
        "themes": ["family"],
        "summary": "大型主題樂園，有多項遊樂設施，適合全家出遊。",
        "description": "劍湖山世界是中部知名的主題樂園，園區內有適合不同年齡的遊樂設施與表演活動。"
                       "部分設施有身高限制，出發前請先查詢官方資訊。",
        "transport": "可由臺鐵斗六站轉乘接駁或客運前往；自行開車有停車場。\n" + BUS,
        "station": "臺鐵 斗六站（轉乘）",
        "friendly": "園區範圍大，建議攜帶推車；部分設施有身高、年齡限制，請以官方公告為準。",
        "walking": "mid", "transit": False, "color": "#d9822b", "views": 56320,
        "url": "",
    },
    {
        "name": "雲林布袋戲館",
        "county": "雲林縣", "town": "虎尾鎮",
        "themes": ["culture", "family", "senior"],
        "summary": "由歷史建築改建的布袋戲館，認識雲林的布袋戲文化。",
        "description": "雲林布袋戲館位於虎尾鎮，由日治時期的歷史建築改建而成，"
                       "展示布袋戲偶、舞台與相關文物，適合親子與長輩一同參觀。",
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
        "description": "虎尾糖廠是臺灣仍持續製糖的糖廠之一，廠區保留舊式建築與五分車鐵道，"
                       "販售部的冰品很受歡迎，適合親子散步。",
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
        "description": "雲林故事館由日治時期的官舍建築修復而成，保留木造建築之美，"
                       "館方常舉辦說故事、手作等活動，適合親子與長輩參加。",
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
        "description": "草嶺位於古坑鄉山區，擁有特殊地質景觀與竹林步道。"
                       "山路蜿蜒、步道有高低落差，建議安排一整天並注意天氣變化。",
        "transport": "山區大眾運輸班次有限，請先查詢台灣好行等路線班次，或自行開車前往。\n" + BUS,
        "station": "",
        "friendly": "步道有階梯與坡度，步行負擔較高；雨後路面濕滑，請穿防滑鞋。",
        "walking": "high", "transit": False, "color": "#2f6b4f", "views": 24880,
        "url": "",
    },
    {
        "name": "成龍濕地",
        "county": "雲林縣", "town": "口湖鄉",
        "themes": ["eco", "senior"],
        "summary": "由農地轉變而成的濕地，結合生態與地景藝術。",
        "description": "成龍濕地位於口湖鄉，因地層下陷形成，後來發展為生態與環境藝術的場域，"
                       "可觀察水鳥並欣賞沿岸的藝術作品。",
        "transport": "大眾運輸班次較少，建議先查詢客運路線或自行開車前往。\n" + BUS,
        "station": "",
        "friendly": "以平地步行為主；戶外缺少遮蔽，請注意防曬。",
        "walking": "low", "transit": False, "color": "#4c7f8f", "views": 7310,
        "url": "",
    },
    {
        "name": "高美濕地",
        "county": "臺中市", "town": "清水區",
        "themes": ["eco"],
        "summary": "風車與夕陽聞名的濕地，有木棧道可走入潮間帶。",
        "description": "高美濕地位於臺中市清水區大甲溪出海口南側，木棧道延伸至潮間帶，"
                       "夕陽與風車是代表景色。當地可見珍貴的雲林莞草，也常與彰化、雲林沿海濕地一起列入中部海岸生態行程（因此關鍵字搜「雲林」會比對到此臺中景點，需搭配地區篩選）。",
        "transport": "可搭乘臺鐵海線至清水站或臺中市區公車前往。\n" + TRA,
        "station": "臺鐵 清水站（轉乘公車）",
        "friendly": "木棧道平坦；海風強勁，傍晚人潮多，請留意潮汐與保暖。",
        "walking": "low", "transit": True, "color": "#d08a3c", "views": 97793,
        "url": "",
    },
    {
        "name": "鹿港老街",
        "county": "彰化縣", "town": "鹿港鎮",
        "themes": ["oldstreet", "culture"],
        "summary": "紅磚老街與傳統小吃，周邊廟宇古蹟密集。",
        "description": "鹿港老街保留紅磚街道與傳統街屋，周邊有天后宮、龍山寺等古蹟，"
                       "可同時體驗老街散步與在地小吃。",
        "transport": "可由臺鐵彰化站轉乘客運前往鹿港。\n" + BUS,
        "station": "臺鐵 彰化站（轉乘客運）",
        "friendly": "老街鋪面為紅磚，略有不平；假日人潮多。",
        "walking": "low", "transit": True, "color": "#a84a3a", "views": 66120,
        "url": "",
    },
    {
        "name": "檜意森活村",
        "county": "嘉義市", "town": "東區",
        "themes": ["culture", "family", "senior"],
        "summary": "日式木造宿舍群，結合文創商店與展覽。",
        "description": "檜意森活村由日治時期林業宿舍群修復而成，木造建築與庭園環境清幽，"
                       "現有文創商店與展覽空間，適合散步拍照。",
        "transport": "由臺鐵嘉義站搭乘市區公車或計程車前往。\n" + TRA,
        "station": "臺鐵 嘉義站",
        "friendly": "園區平坦，步行負擔低；部分老屋有門檻。",
        "walking": "low", "transit": True, "color": "#8a6a3f", "views": 35210,
        "url": "",
    },
    {
        "name": "阿里山國家森林遊樂區",
        "county": "嘉義縣", "town": "阿里山鄉",
        "themes": ["trail", "eco"],
        "summary": "在山林與霧氣之間，認識森林鐵道、神木群與高山景觀。",
        "description": "阿里山的森林、鐵道與山景提供多樣的旅遊體驗。山區步行與氣候條件和市區不同，請事先確認適合的路線、入園資訊及交通安排（整合自組員 A 核對景點）。",
        "transport": "可由高鐵嘉義站或臺鐵嘉義站轉乘台灣好行阿里山線前往。\n" + BUS,
        "station": "臺鐵／高鐵 嘉義站（轉乘台灣好行）",
        "friendly": "山區步道多有坡度與階梯，氣溫較平地低，請備妥保暖衣物並評估體力。",
        "walking": "mid", "transit": True, "color": "#2d5a4c", "views": 84200,
        "url": "https://recreation.forest.gov.tw/forest/ra?typ_id=0500001",
    },
    {
        "name": "日月潭",
        "county": "南投縣", "town": "魚池鄉",
        "themes": ["eco", "senior", "family"],
        "summary": "用湖光山色作為旅程起點，挑選適合自己的環湖木棧道與停留點。",
        "description": "日月潭位於南投魚池，可從水社、向山或伊達邵等據點欣賞湖景。向山段自行車與人行步道平緩寬敞，請依同行者需求選擇目的地（整合自組員 A 核對景點）。",
        "transport": "可於臺鐵臺中站或高鐵臺中站轉乘台灣好行日月潭線直達。\n" + BUS,
        "station": "高鐵 臺中站（轉乘台灣好行）",
        "friendly": "向山遊客中心與水社壩步道平緩，設有完善無障礙洗手間與觀景平台。",
        "walking": "low", "transit": True, "color": "#3b7a9c", "views": 91500,
        "url": "https://www.sunmoonlake.gov.tw/zh-TW",
    },
    {
        "name": "大稻埕碼頭",
        "county": "臺北市", "town": "大同區",
        "themes": ["oldstreet", "senior", "culture"],
        "summary": "從迪化街歷史街區走向淡水河岸，欣賞河濱夕陽與城市風景。",
        "description": "大稻埕碼頭位於臺北大同區，鄰近迪化街南北貨老街與河岸空間。河濱步道全線平坦無階梯，適合傍晚散步與慢步旅行（整合自組員 A 核對景點）。",
        "transport": "可搭乘臺北捷運松山新店線至北門站，或中和新蘆線至大橋頭站步行前往。",
        "station": "捷運 北門站／大橋頭站",
        "friendly": "河濱廣場與老街皆為平面道路，座椅與無障礙廁所齊全。",
        "walking": "low", "transit": True, "color": "#5c6f84", "views": 72300,
        "url": "https://www.travel.taipei/zh-tw/attraction/details/1",
    },
    {
        "name": "安平古堡",
        "county": "臺南市", "town": "安平區",
        "themes": ["oldstreet", "family", "culture"],
        "summary": "從荷蘭時期歷史建築出發，結合安平老街認識臺南文化故事。",
        "description": "安平古堡是認識臺灣早期歷史的重要古蹟，周邊緊鄰安平老街與延平街，可安排半日文化與美食散步行程（整合自組員 A 核對景點）。",
        "transport": "可由臺鐵臺南站搭乘臺南市區公車 2 路或台灣好行至安平古堡站。",
        "station": "臺鐵 臺南站（轉乘市區公車）",
        "friendly": "園區入口與平面展區平緩，惟登上瞭望臺需走階梯，長者可於平面古蹟區參觀。",
        "walking": "low", "transit": True, "color": "#a85d44", "views": 68900,
        "url": "https://historic.tainan.gov.tw/index.php?id=58&lang=cht&option=module&task=pageinfo",
    },
]


class Command(BaseCommand):
    help = "匯入縣市、主題與示範景點資料（可重複執行）"

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
            elif not spot.image_url and s["name"] in PHOTO_MAP:
                spot.image_url = PHOTO_MAP[s["name"]]
                spot.save(update_fields=["image_url"])

        self.stdout.write(self.style.SUCCESS(f"資料匯入完成：新增 {created} 個景點，目前共 {Spot.objects.count()} 個。"))
