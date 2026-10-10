(function () {
  var cv = document.getElementById("sky");
  var hero = document.getElementById("hero");
  if (!cv || !hero) return;

  var cx = cv.getContext("2d");
  var still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  var W = 0, H = 0, lastW = 0;
  var stars = [];
  var mouse = { x: -999, y: -999, on: false };

  function build() {
    var r = cv.getBoundingClientRect();
    W = r.width;
    H = r.height;
    cv.width = W * dpr;
    cv.height = H * dpr;
    cx.setTransform(dpr, 0, 0, dpr, 0, 0);

    var n = Math.min(260, Math.floor((W * H) / 5500));
    stars = [];
    for (var i = 0; i < n; i++) {
      var z = Math.random();
      stars.push({
        x: Math.random() * W,
        y: Math.random() * H,
        dx: 0, dy: 0,
        vx: 0, vy: 0,
        z: z,
        r: 0.4 + z * 1.7,
        c: Math.random() < 0.5 ? "0,212,255" : "0,230,118",
        t: Math.random() * 6
      });
    }
  }

  function frame(t) {
    cx.clearRect(0, 0, W, H);

    var px = mouse.on ? mouse.x / W - 0.5 : 0;
    var py = mouse.on ? mouse.y / H - 0.5 : 0;

    for (var i = 0; i < stars.length; i++) {
      var s = stars[i];

      s.x += s.z * 0.12 + s.vx;
      s.y += s.vy;
      if (s.x > W + 5) s.x = -5;
      if (s.x < -5) s.x = W + 5;
      if (s.y > H + 5) s.y = -5;
      if (s.y < -5) s.y = H + 5;
      s.vx *= 0.92;
      s.vy *= 0.92;

      // ستاره‌های نزدیک موس عقب می‌روند
      var ddx = s.x - mouse.x;
      var ddy = s.y - mouse.y;
      var d = Math.hypot(ddx, ddy);
      if (d < 150 && d > 0) {
        var f = (1 - d / 150) * (0.5 + s.z) * 2.2;
        s.vx += (ddx / d) * f * 0.35;
        s.vy += (ddy / d) * f * 0.35;
      }

      // لایه‌های عمق (پارالاکس)
      s.dx = s.x - px * s.z * 40;
      s.dy = s.y - py * s.z * 40;

      var tw = 0.55 + 0.45 * Math.sin(t / 700 + s.t);
      cx.beginPath();
      cx.arc(s.dx, s.dy, s.r, 0, 6.283);
      cx.fillStyle = "rgba(" + s.c + "," + (0.35 + s.z * 0.6) * tw + ")";
      cx.shadowColor = "rgb(" + s.c + ")";
      cx.shadowBlur = s.r * 4;
      cx.fill();
    }

    // خط‌های اتصال بین ستاره‌های نزدیک؛ نزدیک موس پررنگ‌ترند
    cx.shadowBlur = 0;
    cx.lineWidth = 0.7;
    for (var a = 0; a < stars.length; a++) {
      var sa = stars[a];
      if (sa.z < 0.35) continue;
      for (var b = a + 1; b < stars.length; b++) {
        var sb = stars[b];
        if (sb.z < 0.35) continue;
        var dist = Math.hypot(sa.dx - sb.dx, sa.dy - sb.dy);
        if (dist < 88) {
          var near = Math.hypot(sa.dx - mouse.x, sa.dy - mouse.y) < 190;
          cx.strokeStyle = "rgba(0,212,255," + (1 - dist / 88) * (near ? 0.6 : 0.12) + ")";
          cx.beginPath();
          cx.moveTo(sa.dx, sa.dy);
          cx.lineTo(sb.dx, sb.dy);
          cx.stroke();
        }
      }
    }

    if (!still) requestAnimationFrame(frame);
  }

  hero.addEventListener("pointermove", function (e) {
    var r = cv.getBoundingClientRect();
    mouse.x = e.clientX - r.left;
    mouse.y = e.clientY - r.top;
    mouse.on = true;
  });
  hero.addEventListener("pointerleave", function () {
    mouse.x = mouse.y = -999;
    mouse.on = false;
  });

  // فقط وقتی عرض عوض شد دوباره می‌سازیم، تا با بالا و پایین شدن نوار مرورگر موبایل ستاره‌ها نپرند
  window.addEventListener("resize", function () {
    if (hero.clientWidth !== lastW) {
      lastW = hero.clientWidth;
      build();
      if (still) frame(0);
    }
  });

  lastW = hero.clientWidth;
  build();
  if (still) {
    frame(0);
  } else {
    requestAnimationFrame(frame);
  }
})();