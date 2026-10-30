from django.conf import settings
from django.db import models


class County(models.Model):
    """縣市（對應 P5：卡片需列出縣市）"""

    name = models.CharField("縣市", max_length=10, unique=True)
    order = models.PositiveSmallIntegerField("排序", default=0)

    class Meta:
        verbose_name = "縣市"
        verbose_name_plural = "縣市"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Town(models.Model):
    """鄉鎮市區"""

    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name="towns", verbose_name="縣市")
    name = models.CharField("鄉鎮市區", max_length=10)

    class Meta:
        verbose_name = "鄉鎮市區"
        verbose_name_plural = "鄉鎮市區"
        ordering = ["county__order", "name"]
        unique_together = [("county", "name")]

    def __str__(self):
        return f"{self.county.name} {self.name}"


class Theme(models.Model):
    """旅遊主題（老街、親子共遊、樂齡旅遊、自然生態…）"""

    name = models.CharField("主題", max_length=20, unique=True)
    slug = models.SlugField("代號", max_length=30, unique=True, allow_unicode=True)
    description = models.CharField("說明", max_length=100, blank=True)
    order = models.PositiveSmallIntegerField("排序", default=0)

    class Meta:
        verbose_name = "旅遊主題"
        verbose_name_plural = "旅遊主題"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Spot(models.Model):
    """景點（整合組員 B 分鏡欄位與組員 A 地址／開放時間／首頁推薦欄位）"""

    name = models.CharField("景點名稱", max_length=80)
    county = models.ForeignKey(County, on_delete=models.PROTECT, related_name="spots", verbose_name="縣市")
    town = models.ForeignKey(Town, on_delete=models.PROTECT, related_name="spots", verbose_name="鄉鎮市區")
    themes = models.ManyToManyField(Theme, related_name="spots", verbose_name="主題", blank=True)
    summary = models.CharField("短摘要", max_length=150, help_text="結果卡片與詳情頁最上方的一句話（對應 P3：先給短摘要）")
    description = models.TextField("完整介紹", blank=True, help_text="詳情頁可展開的完整內容")
    address = models.CharField("地址或位置說明", max_length=200, blank=True, help_text="整合自組員 A 景點位置欄位")
    opening_hours = models.CharField("開放時間資訊", max_length=200, blank=True, default="請以官方最新公告為準。")
    transport = models.TextField("如何前往", blank=True, help_text="大眾運輸方式；班次請引導至官方查詢，勿填未核對的時刻")
    nearest_station = models.CharField("鄰近車站", max_length=50, blank=True)
    friendly_info = models.TextField("友善指引", blank=True, help_text="無障礙、廁所、停車、步道難度等")
    walking_level = models.CharField(
        "步行負擔",
        max_length=10,
        choices=[("low", "輕鬆"), ("mid", "中等"), ("high", "較費力")],
        default="low",
    )
    transit_friendly = models.BooleanField("大眾運輸可達", default=False)
    official_url = models.URLField("官方景點頁", max_length=500, blank=True)
    image_url = models.CharField("圖片網址或靜態路徑", max_length=500, blank=True)
    cover_color = models.CharField("卡片色調", max_length=7, default="#3f7f74", help_text="無照片時卡片示意圖使用的顏色")
    is_featured = models.BooleanField("首頁推薦", default=True)
    views = models.PositiveIntegerField("點閱數", default=0)
    is_published = models.BooleanField("上架", default=True)
    created_at = models.DateTimeField("建立時間", auto_now_add=True)
    updated_at = models.DateTimeField("更新時間", auto_now=True)

    class Meta:
        verbose_name = "景點"
        verbose_name_plural = "景點"
        ordering = ["-views", "name"]

    def __str__(self):
        return f"{self.name}（{self.county.name}{self.town.name}）"

    @property
    def location(self):
        return f"{self.county.name} {self.town.name}"


class Favorite(models.Model):
    """會員收藏／我的行程（登入後才有的功能）"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites", verbose_name="會員")
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name="favorited_by", verbose_name="景點")
    note = models.CharField("備註", max_length=100, blank=True)
    planned_date = models.DateField("預計出遊日", null=True, blank=True)
    created_at = models.DateTimeField("加入時間", auto_now_add=True)

    class Meta:
        verbose_name = "會員收藏"
        verbose_name_plural = "會員收藏"
        ordering = ["planned_date", "-created_at"]
        unique_together = [("user", "spot")]

    def __str__(self):
        return f"{self.user} → {self.spot.name}"
