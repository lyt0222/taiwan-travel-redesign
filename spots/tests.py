from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import County, Favorite, Spot


class SiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_data", verbosity=0)
        cls.yunlin = County.objects.get(name="雲林縣")
        cls.user = User.objects.create_user("tester", password="Pass12345!x")

    def test_pages_load(self):
        spot = Spot.objects.first()
        for url in [
            reverse("spots:home"),
            reverse("spots:search"),
            reverse("spots:search") + "?flow=family",
            reverse("spots:search") + "?flow=senior",
            reverse("spots:results"),
            reverse("spots:detail", args=[spot.pk]),
            reverse("spots:detail", args=[spot.pk]) + "?tab=transport",
            reverse("spots:detail", args=[spot.pk]) + "?tab=friendly",
            reverse("accounts:login"),
            reverse("accounts:register"),
        ]:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_county_filter_only_returns_that_county(self):
        r = self.client.get(reverse("spots:results"), {"county": self.yunlin.pk})
        self.assertTrue(r.context["spots"])
        self.assertTrue(all(s.county_id == self.yunlin.pk for s in r.context["spots"]))
        self.assertIn(("地區", "雲林縣"), r.context["conditions"])

    def test_county_name_keyword_shows_hint(self):
        # P5：輸入「雲林」當關鍵字，會出現跨縣市結果與改用地區篩選的提示
        r = self.client.get(reverse("spots:results"), {"q": "雲林"})
        self.assertEqual(r.context["county_hint"], self.yunlin)
        self.assertContains(r, "改為只看 雲林縣")
        self.assertContains(r, "臺中市 清水區")

    def test_theme_and_transit_filters(self):
        r = self.client.get(reverse("spots:results"), {"theme": "family", "transit": "1"})
        for s in r.context["spots"]:
            self.assertTrue(s.transit_friendly)
            self.assertIn("family", [t.slug for t in s.themes.all()])

    def test_walking_filter(self):
        r = self.client.get(reverse("spots:results"), {"walking": "low"})
        self.assertTrue(all(s.walking_level == "low" for s in r.context["spots"]))

    def test_my_trip_requires_login(self):
        r = self.client.get(reverse("spots:my_trip"))
        self.assertEqual(r.status_code, 302)
        self.assertIn(reverse("accounts:login"), r["Location"])

    def test_detail_differs_before_and_after_login(self):
        spot = Spot.objects.first()
        url = reverse("spots:detail", args=[spot.pk])
        self.assertContains(self.client.get(url), "登入後加入我的行程")
        self.client.login(username="tester", password="Pass12345!x")
        self.assertContains(self.client.get(url), "確認目的地，加入我的行程")

    def test_favorite_toggle_and_update(self):
        self.client.login(username="tester", password="Pass12345!x")
        spot = Spot.objects.first()
        self.client.post(reverse("spots:toggle_favorite", args=[spot.pk]))
        fav = Favorite.objects.get(user=self.user, spot=spot)
        self.client.post(reverse("spots:update_favorite", args=[fav.pk]), {"note": "早上出發", "planned_date": "2026-11-08"})
        fav.refresh_from_db()
        self.assertEqual(fav.note, "早上出發")
        self.assertContains(self.client.get(reverse("spots:my_trip")), spot.name)
        self.client.post(reverse("spots:toggle_favorite", args=[spot.pk]))
        self.assertFalse(Favorite.objects.filter(user=self.user, spot=spot).exists())

    def test_register(self):
        r = self.client.post(
            reverse("accounts:register"),
            {"username": "newbie", "email": "", "password1": "Travel!2026abc", "password2": "Travel!2026abc"},
        )
        self.assertEqual(r.status_code, 302)
        self.assertTrue(User.objects.filter(username="newbie").exists())

    def test_views_increment(self):
        spot = Spot.objects.first()
        before = spot.views
        self.client.get(reverse("spots:detail", args=[spot.pk]))
        spot.refresh_from_db()
        self.assertEqual(spot.views, before + 1)

    def test_seed_is_idempotent(self):
        n = Spot.objects.count()
        call_command("seed_data", verbosity=0)
        self.assertEqual(Spot.objects.count(), n)
