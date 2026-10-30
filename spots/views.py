from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .models import County, Favorite, Spot, Theme, Town

# 三條任務流程（對應報告 F1～F3）的預設條件
FLOWS = {
    "transit": {
        "title": "大眾運輸旅遊",
        "heading": "查找旅遊景點",
        "lead": "沒有汽車也能去：先選地區，再確認交通方式。",
        "theme": "",
        "transit": True,
        "persona": "F1",
    },
    "family": {
        "title": "親子出遊",
        "heading": "親子出遊",
        "lead": "用地區與親子主題篩選，再比較設施與開放資訊。",
        "theme": "family",
        "transit": False,
        "persona": "F2",
    },
    "senior": {
        "title": "樂齡輕鬆遊",
        "heading": "樂齡輕鬆遊",
        "lead": "大字顯示、步行負擔低的景點，閱讀短摘要即可決定。",
        "theme": "senior",
        "transit": False,
        "persona": "F3",
    },
}

SORTS = {
    "popular": ("熱門程度", ["-views", "name"]),
    "name": ("名稱", ["name"]),
    "new": ("最新上架", ["-created_at"]),
}

WALKING = {"low": "輕鬆", "mid": "中等", "high": "較費力"}


def _published():
    return Spot.objects.filter(is_published=True).select_related("county", "town").prefetch_related("themes")


def home(request):
    popular = _published()[:6]
    return render(
        request,
        "spots/home.html",
        {
            "counties": County.objects.all(),
            "themes": Theme.objects.all(),
            "popular": popular,
            "flows": FLOWS,
        },
    )


def search(request):
    """查詢頁（F1-1／F2-1／F3-1）：條件欄位都有文字名稱，先查詢、再閱讀介紹"""
    flow_key = request.GET.get("flow", "transit")
    flow = FLOWS.get(flow_key, FLOWS["transit"])
    return render(
        request,
        "spots/search.html",
        {
            "flow_key": flow_key,
            "flow": flow,
            "counties": County.objects.all(),
            "themes": Theme.objects.all(),
            "sorts": SORTS,
            "walking": WALKING,
            "selected_county": request.GET.get("county", ""),
            "selected_theme": request.GET.get("theme", flow["theme"]),
        },
    )


def results(request):
    """結果頁（F1-2／F2-2／F3-2）：條件摘要有名稱、卡片列出縣市與鄉鎮"""
    qs = _published()
    params = request.GET
    county_id = params.get("county", "")
    town_id = params.get("town", "")
    theme_slug = params.get("theme", "")
    keyword = params.get("q", "").strip()
    transit = params.get("transit") == "1"
    walking = params.get("walking", "")
    sort = params.get("sort", "popular")
    flow_key = params.get("flow", "")

    conditions = []  # 給條件摘要使用：(欄位名稱, 值)
    county = town = theme = None

    if county_id:
        county = County.objects.filter(pk=county_id).first()
        if county:
            qs = qs.filter(county=county)
            conditions.append(("地區", county.name))
    if town_id:
        town = Town.objects.filter(pk=town_id).first()
        if town:
            qs = qs.filter(town=town)
            conditions.append(("鄉鎮", town.name))
    if theme_slug:
        theme = Theme.objects.filter(slug=theme_slug).first()
        if theme:
            qs = qs.filter(themes=theme)
            conditions.append(("主題", theme.name))
    if keyword:
        qs = qs.filter(
            Q(name__icontains=keyword)
            | Q(summary__icontains=keyword)
            | Q(description__icontains=keyword)
            | Q(themes__name__icontains=keyword)
        ).distinct()
        conditions.append(("關鍵字", keyword))
    if transit:
        qs = qs.filter(transit_friendly=True)
        conditions.append(("交通", "大眾運輸可達"))
    if walking in WALKING:
        order = list(WALKING)
        qs = qs.filter(walking_level__in=order[: order.index(walking) + 1])
        conditions.append(("步行負擔", f"{WALKING[walking]}以內"))

    sort_label, sort_order = SORTS.get(sort, SORTS["popular"])
    qs = qs.order_by(*sort_order)
    conditions.append(("排序", sort_label))

    # P5：關鍵字其實是縣市名稱時，提示改用「地區」篩選，避免跨縣市結果混在一起
    county_hint = None
    if keyword and not county:
        for c in County.objects.all():
            if keyword in (c.name, c.name.rstrip("縣市")):
                county_hint = c
                break

    spots = list(qs)
    fav_ids = set()
    if request.user.is_authenticated:
        fav_ids = set(request.user.favorites.values_list("spot_id", flat=True))

    other_counties = sorted({s.county.name for s in spots})

    return render(
        request,
        "spots/results.html",
        {
            "spots": spots,
            "conditions": conditions,
            "county_hint": county_hint,
            "keyword": keyword,
            "fav_ids": fav_ids,
            "query_string": params.urlencode(),
            "edit_url": f"{reverse('spots:search')}?{params.urlencode()}",
            "flow": FLOWS.get(flow_key),
            "result_counties": other_counties,
        },
    )


def detail(request, pk):
    """詳情頁（F1-3／F2-3／F3-3）：短摘要＋分頁（簡介／如何前往／友善指引）"""
    spot = get_object_or_404(_published(), pk=pk)
    Spot.objects.filter(pk=pk).update(views=F("views") + 1)

    tab = request.GET.get("tab", "intro")
    if tab not in ("intro", "transport", "friendly"):
        tab = "intro"

    back = request.GET.get("back", "")
    back_url = f"{reverse('spots:results')}?{back}" if back else reverse("spots:search")

    is_fav = request.user.is_authenticated and Favorite.objects.filter(user=request.user, spot=spot).exists()
    nearby = _published().filter(county=spot.county).exclude(pk=spot.pk)[:3]

    return render(
        request,
        "spots/detail.html",
        {
            "spot": spot,
            "tab": tab,
            "back": back,
            "back_url": back_url,
            "is_fav": is_fav,
            "nearby": nearby,
            "walking_label": WALKING.get(spot.walking_level, ""),
        },
    )


def _safe_next(request, fallback):
    nxt = request.POST.get("next") or request.GET.get("next")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}):
        return nxt
    return fallback


@login_required
@require_POST
def toggle_favorite(request, pk):
    spot = get_object_or_404(Spot, pk=pk)
    action = request.POST.get("action", "toggle")
    if action == "remove":
        Favorite.objects.filter(user=request.user, spot=spot).delete()
        messages.info(request, f"已將「{spot.name}」移出我的行程。")
    elif action == "add":
        Favorite.objects.get_or_create(user=request.user, spot=spot)
        messages.success(request, f"已將「{spot.name}」加入我的行程。")
    else:
        fav, created = Favorite.objects.get_or_create(user=request.user, spot=spot)
        if created:
            messages.success(request, f"已將「{spot.name}」加入我的行程。")
        else:
            fav.delete()
            messages.info(request, f"已將「{spot.name}」移出我的行程。")
    return redirect(_safe_next(request, reverse("spots:detail", args=[pk])))


@login_required
def my_trip(request):
    """我的行程：登入後才看得到（會員登入前後的功能差異）"""
    favorites = request.user.favorites.select_related("spot", "spot__county", "spot__town")
    return render(request, "spots/my_trip.html", {"favorites": favorites})


@login_required
@require_POST
def update_favorite(request, pk):
    fav = get_object_or_404(Favorite, pk=pk, user=request.user)
    fav.note = request.POST.get("note", "")[:100]
    date = request.POST.get("planned_date") or None
    fav.planned_date = date
    try:
        fav.full_clean(exclude=["user", "spot"])
        fav.save()
        messages.success(request, f"已更新「{fav.spot.name}」的行程備註。")
    except Exception:
        messages.error(request, "日期格式不正確，請重新選擇。")
    return redirect("spots:my_trip")


def towns_api(request):
    """依縣市回傳鄉鎮清單，給查詢表單的連動選單使用"""
    county_id = request.GET.get("county")
    towns = Town.objects.filter(county_id=county_id).values("id", "name") if county_id else []
    return JsonResponse({"towns": list(towns)})
