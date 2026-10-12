// این فایل کوچک در head می‌آید تا قبل از نمایش صفحه اجرا شود
document.documentElement.classList.add("js");
setTimeout(function () {
  if (!window.__revealReady) document.documentElement.classList.add("no-reveal");
}, 3000);