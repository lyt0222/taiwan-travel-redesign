import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='County',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True, verbose_name='縣市')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='排序')),
            ],
            options={
                'verbose_name': '縣市',
                'verbose_name_plural': '縣市',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True, verbose_name='主題')),
                ('slug', models.SlugField(allow_unicode=True, max_length=30, unique=True, verbose_name='代號')),
                ('description', models.CharField(blank=True, max_length=100, verbose_name='說明')),
                ('order', models.PositiveSmallIntegerField(default=0, verbose_name='排序')),
            ],
            options={
                'verbose_name': '旅遊主題',
                'verbose_name_plural': '旅遊主題',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Town',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, verbose_name='鄉鎮市區')),
                ('county', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='towns', to='spots.county', verbose_name='縣市')),
            ],
            options={
                'verbose_name': '鄉鎮市區',
                'verbose_name_plural': '鄉鎮市區',
                'ordering': ['county__order', 'name'],
                'unique_together': {('county', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Spot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='景點名稱')),
                ('summary', models.CharField(help_text='結果卡片與詳情頁最上方的一句話（對應 P3：先給短摘要）', max_length=150, verbose_name='短摘要')),
                ('description', models.TextField(blank=True, help_text='詳情頁可展開的完整內容', verbose_name='完整介紹')),
                ('address', models.CharField(blank=True, help_text='整合自組員 A 景點位置欄位', max_length=200, verbose_name='地址或位置說明')),
                ('opening_hours', models.CharField(blank=True, default='請以官方最新公告為準。', max_length=200, verbose_name='開放時間資訊')),
                ('transport', models.TextField(blank=True, help_text='大眾運輸方式；班次請引導至官方查詢，勿填未核對的時刻', verbose_name='如何前往')),
                ('nearest_station', models.CharField(blank=True, max_length=50, verbose_name='鄰近車站')),
                ('friendly_info', models.TextField(blank=True, help_text='無障礙、廁所、停車、步道難度等', verbose_name='友善指引')),
                ('walking_level', models.CharField(choices=[('low', '輕鬆'), ('mid', '中等'), ('high', '較費力')], default='low', max_length=10, verbose_name='步行負擔')),
                ('transit_friendly', models.BooleanField(default=False, verbose_name='大眾運輸可達')),
                ('official_url', models.URLField(blank=True, max_length=500, verbose_name='官方景點頁')),
                ('image_url', models.CharField(blank=True, max_length=500, verbose_name='圖片網址或靜態路徑')),
                ('cover_color', models.CharField(default='#3f7f74', help_text='無照片時卡片示意圖使用的顏色', max_length=7, verbose_name='卡片色調')),
                ('is_featured', models.BooleanField(default=True, verbose_name='首頁推薦')),
                ('views', models.PositiveIntegerField(default=0, verbose_name='點閱數')),
                ('is_published', models.BooleanField(default=True, verbose_name='上架')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='建立時間')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新時間')),
                ('county', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='spots', to='spots.county', verbose_name='縣市')),
                ('themes', models.ManyToManyField(blank=True, related_name='spots', to='spots.theme', verbose_name='主題')),
                ('town', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='spots', to='spots.town', verbose_name='鄉鎮市區')),
            ],
            options={
                'verbose_name': '景點',
                'verbose_name_plural': '景點',
                'ordering': ['-views', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.CharField(blank=True, max_length=100, verbose_name='備註')),
                ('planned_date', models.DateField(blank=True, null=True, verbose_name='預計出遊日')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='加入時間')),
                ('spot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='spots.spot', verbose_name='景點')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to=settings.AUTH_USER_MODEL, verbose_name='會員')),
            ],
            options={
                'verbose_name': '會員收藏',
                'verbose_name_plural': '會員收藏',
                'ordering': ['planned_date', '-created_at'],
                'unique_together': {('user', 'spot')},
            },
        ),
    ]
