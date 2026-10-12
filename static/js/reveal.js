(function () {
  window.__revealReady = true;

  var els = document.querySelectorAll(".reveal");
  if (!els.length) return;

  if (!("IntersectionObserver" in window)) {
    els.forEach(function (el) { el.classList.add("in"); });
    return;
  }

  // بین عنصرهای هم‌ردیف کمی فاصله می‌اندازیم تا پشت‌سرهم بیایند
  var counts = new Map();
  els.forEach(function (el) {
    var n = counts.get(el.parentNode) || 0;
    el.style.setProperty("--d", Math.min(n, 5) * 0.08 + "s");
    counts.set(el.parentNode, n + 1);
  });

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) {
        en.target.classList.add("in");
        io.unobserve(en.target);
      }
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });

  els.forEach(function (el) { io.observe(el); });
})();