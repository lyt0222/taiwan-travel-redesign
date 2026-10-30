from django.contrib import admin
from .models import County, Favorite, Spot, Theme, Town

admin.site.site_header = "臺灣觀光資訊網 Redesign｜管理後台"
admin.site.site_title = "觀光資訊網後台"
admin.site.index_title = "資料管理（整合組員 A 與組員 B 專案）"


class TownInline(admin.TabularInline):
    model = Town
    extra = 0


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "town_count", "spot_count")
    list_editable = ("order",)
    inlines = [TownInline]

    @admin.display(description="鄉鎮數")
    def town_count(self, obj):
        return obj.towns.count()

    @admin.display(description="景點數")
    def spot_count(self, obj):
        return obj.spots.count()


@admin.register(Town)
class TownAdmin(admin.ModelAdmin):
    list_display = ("name", "county")
    list_filter = ("county",)
    search_fields = ("name",)


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order", "description")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    class Media:
        css = {"all": ("admin_custom/admin.css",)}

    list_display = (
        "name", "county", "town", "theme_list",
        "transit_friendly", "walking_level", "is_featured", "views", "is_published"
    )
    list_filter = ("county", "themes", "transit_friendly", "walking_level", "is_featured", "is_published")
    list_editable = ("is_featured", "is_published")
    search_fields = ("name", "county__name", "town__name", "summary", "description", "address")
    filter_horizontal = ("themes",)
    autocomplete_fields = ("town",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("基本資料", {"fields": ("name", ("county", "town"), "themes", "summary", ("is_featured", "is_published"))}),
        ("詳情分頁與出遊資訊", {"fields": ("description", "address", "opening_hours", "transport", "nearest_station", "friendly_info")}),
        ("篩選條件", {"fields": (("transit_friendly", "walking_level"),)}),
        ("視覺與統計", {"fields": ("official_url", "image_url", "cover_color", "views", ("created_at", "updated_at"))}),
    )

    @admin.display(description="主題")
    def theme_list(self, obj):
        return "、".join(t.name for t in obj.themes.all())

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("county", "town").prefetch_related("themes")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "spot", "planned_date", "note", "created_at")
    list_filter = ("spot__county", "created_at")
    search_fields = ("user__username", "spot__name", "note")
