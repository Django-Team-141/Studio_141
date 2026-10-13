(function () {
  var toast = document.getElementById("toast");
  if (!toast) return;

  var timer = 0;

  function show(msg) {
    toast.textContent = msg;
    toast.classList.add("show");
    clearTimeout(timer);
    timer = setTimeout(hide, 4200);
  }
  function hide() {
    toast.classList.remove("show");
  }

  // هر لینکی که data-soon دارد، به‌جای باز شدن یک پیام کوتاه نشان می‌دهد
  document.addEventListener("click", function (e) {
    var soon = e.target.closest("[data-soon]");
    if (soon) {
      e.preventDefault();
      show(soon.getAttribute("data-soon"));
      return;
    }
    if (toast.classList.contains("show") && !e.target.closest("#toast")) hide();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") hide();
  });
})();