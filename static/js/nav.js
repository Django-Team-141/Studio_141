(function () {
  var toggle = document.getElementById("navtoggle");
  var menu = document.getElementById("menu");
  if (!toggle || !menu) return;

  function close() { toggle.checked = false; }

  // با زدن روی یک لینک منو بسته می‌شود
  menu.addEventListener("click", function (e) {
    if (e.target.closest("a")) close();
  });

  // کلیک بیرون از منو یا زدن Esc هم آن را می‌بندد
  document.addEventListener("click", function (e) {
    if (toggle.checked && !e.target.closest("nav")) close();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && toggle.checked) close();
  });

  // لینک بخشی که الان وسط صفحه است روشن می‌شود
  if (!("IntersectionObserver" in window)) return;

  var links = menu.querySelectorAll("a.l");
  var targets = [];
  links.forEach(function (a) {
    var id = (a.getAttribute("href") || "").split("#")[1];
    var el = id && document.getElementById(id);
    if (el) targets.push({ el: el, link: a });
  });
  if (!targets.length) return;

  // هدر هم دیده می‌شود تا وقتی بالای صفحه‌ایم هیچ لینکی روشن نباشد
  var hero = document.getElementById("hero");
  if (hero) targets.push({ el: hero, link: null });

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      links.forEach(function (l) { l.classList.remove("on"); });
      targets.forEach(function (t) {
        if (t.el === en.target && t.link) t.link.classList.add("on");
      });
    });
  }, { rootMargin: "-40% 0px -55% 0px" });

  targets.forEach(function (t) { io.observe(t.el); });
})();