"""
建立（或更新）驗收用帳號，可重複執行。部署時由 build.sh 自動呼叫。

環境變數：
  DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_PASSWORD → Django 後台管理員（預設 admin / Admin2026!）
  DEMO_USERNAME / DEMO_PASSWORD → 前台測試會員（預設 demo / Travel2026!）
"""
import os
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from spots.models import Favorite, Spot


class Command(BaseCommand):
    help = "建立後台管理員與前台測試會員"

    def handle(self, *args, **options):
        admin_user = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        admin_pw = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "Admin2026!")
        user, _ = User.objects.get_or_create(username=admin_user)
        user.email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        user.is_staff = True
        user.is_superuser = True
        user.set_password(admin_pw)
        user.save()
        self.stdout.write(self.style.SUCCESS(f"後台管理員：{admin_user}"))

        demo_user = os.environ.get("DEMO_USERNAME", "demo")
        demo_pw = os.environ.get("DEMO_PASSWORD", "Travel2026!")
        user, created = User.objects.get_or_create(username=demo_user)
        user.set_password(demo_pw)
        user.save()
        if created:
            for name in ("太平老街", "雲林布袋戲館", "綠色隧道景觀公園"):
                spot = Spot.objects.filter(name=name).first()
                if spot:
                    Favorite.objects.get_or_create(user=user, spot=spot, defaults={"note": "示範收藏行程"})
        self.stdout.write(self.style.SUCCESS(f"前台測試會員：{demo_user}"))
