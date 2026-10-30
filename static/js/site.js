// 整合組員 A 與組員 B 前端互動腳本：大字模式（Cookie + localStorage）、縣市鄉鎮連動、手機選單、密碼顯示切換
(function () {
  var btn = document.getElementById("fontToggle");
  var root = document.documentElement;

  function applyBigFont(on) {
    root.classList.toggle("big-font", on);
    if (btn) {
      btn.setAttribute("aria-pressed", on ? "true" : "false");
      var stateEl = btn.querySelector(".font-state");
      if (stateEl) stateEl.textContent = on ? "已開" : "關";
    }
  }

  try {
    if (!root.classList.contains("big-font") && localStorage.getItem("travel-large-text") === "true") {
      applyBigFont(true);
    }
  } catch (_) {}

  if (btn) {
    btn.addEventListener("click", function () {
      var on = !root.classList.contains("big-font");
      applyBigFont(on);
      document.cookie = "bigfont=" + (on ? "1" : "0") + "; path=/; max-age=31536000; SameSite=Lax";
      try { localStorage.setItem("travel-large-text", String(on)); } catch (_) {}
    });
  }

  // 手機選單收合與 Escape 關閉（整合自組員 A）
  var menuBtn = document.getElementById("menuToggle");
  var mainNav = document.getElementById("main-nav");
  if (menuBtn && mainNav) {
    menuBtn.addEventListener("click", function () {
      var open = menuBtn.getAttribute("aria-expanded") !== "true";
      mainNav.classList.toggle("is-open", open);
      menuBtn.setAttribute("aria-expanded", String(open));
      menuBtn.textContent = open ? "關閉" : "選單";
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && mainNav.classList.contains("is-open")) {
        mainNav.classList.remove("is-open");
        menuBtn.setAttribute("aria-expanded", "false");
        menuBtn.textContent = "選單";
        menuBtn.focus();
      }
    });
  }

  // 密碼顯示／隱藏切換（整合自組員 A）
  document.querySelectorAll(".password-toggle").forEach(function (toggleBtn) {
    var input = document.getElementById(toggleBtn.getAttribute("data-target"));
    if (!input) return;
    toggleBtn.addEventListener("click", function () {
      var show = input.type === "password";
      input.type = show ? "text" : "password";
      toggleBtn.textContent = show ? "隱藏" : "顯示";
      toggleBtn.setAttribute("aria-label", show ? "隱藏密碼" : "顯示密碼");
      toggleBtn.setAttribute("aria-pressed", String(show));
    });
  });

  // 地區 → 鄉鎮 連動選單（整合自組員 B）
  var county = document.getElementById("county");
  var town = document.getElementById("town");
  if (county && town) {
    var url = county.getAttribute("data-towns-url");
    var load = function () {
      var selected = town.getAttribute("data-selected") || "";
      town.innerHTML = "";
      var first = document.createElement("option");
      first.value = "";
      first.textContent = county.value ? "全部鄉鎮" : "全部鄉鎮（請先選地區）";
      town.appendChild(first);
      if (!county.value) return;
      fetch(url + "?county=" + encodeURIComponent(county.value))
        .then(function (r) { return r.json(); })
        .then(function (data) {
          data.towns.forEach(function (t) {
            var o = document.createElement("option");
            o.value = t.id;
            o.textContent = t.name;
            if (String(t.id) === selected) o.selected = true;
            town.appendChild(o);
          });
        });
    };
    county.addEventListener("change", function () {
      town.setAttribute("data-selected", "");
      load();
    });
    load();
  }
})();
