def site_nav(request):
    """大字模式：用 cookie 記住，伺服器端直接套用 class，避免頁面閃爍（對應 P3、Persona 3）"""
    return {"big_font": request.COOKIES.get("bigfont") == "1"}
