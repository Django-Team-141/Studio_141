"""یک بار اجرا می‌شود و فونت‌های سایت را داخل static/fonts می‌ریزد.

اجرا (از ترمینال PyCharm، در ریشه‌ی پروژه):
    python scripts/fetch_fonts.py
"""
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "static" / "fonts"

VAZ_CDN = "https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/"
VAZ_RAW = "https://raw.githubusercontent.com/rastikerdar/vazirmatn/v33.003/"
JB_CDN = "https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono@master/"
JB_RAW = "https://raw.githubusercontent.com/JetBrains/JetBrainsMono/master/"
FS = "https://cdn.jsdelivr.net/npm/@fontsource/jetbrains-mono/files/"

FONTS = {
    "Vazirmatn-Light.woff2": [
        VAZ_CDN + "fonts/webfonts/Vazirmatn-Light.woff2",
        VAZ_RAW + "fonts/webfonts/Vazirmatn-Light.woff2",
    ],
    "Vazirmatn-Medium.woff2": [
        VAZ_CDN + "fonts/webfonts/Vazirmatn-Medium.woff2",
        VAZ_RAW + "fonts/webfonts/Vazirmatn-Medium.woff2",
    ],
    "Vazirmatn-ExtraBold.woff2": [
        VAZ_CDN + "fonts/webfonts/Vazirmatn-ExtraBold.woff2",
        VAZ_RAW + "fonts/webfonts/Vazirmatn-ExtraBold.woff2",
    ],
    "JetBrainsMono-Regular.woff2": [
        JB_CDN + "fonts/webfonts/JetBrainsMono-Regular.woff2",
        JB_RAW + "fonts/webfonts/JetBrainsMono-Regular.woff2",
        FS + "jetbrains-mono-latin-400-normal.woff2",
    ],
    "JetBrainsMono-Bold.woff2": [
        JB_CDN + "fonts/webfonts/JetBrainsMono-Bold.woff2",
        JB_RAW + "fonts/webfonts/JetBrainsMono-Bold.woff2",
        FS + "jetbrains-mono-latin-700-normal.woff2",
    ],
}

# مجوز OFL باید کنار فونت‌ها بماند
LICENSES = {
    "OFL-Vazirmatn.txt": [VAZ_CDN + "OFL.txt", VAZ_RAW + "OFL.txt"],
    "OFL-JetBrainsMono.txt": [JB_CDN + "OFL.txt", JB_RAW + "OFL.txt"],
}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def is_font(data):
    return data[:4] == b"wOF2" and len(data) > 5000


def is_license(data):
    return len(data) > 500 and b"OPEN FONT LICENSE" in data.upper()


def fetch(name, urls, check):
    target = OUT / name
    if target.exists() and target.stat().st_size > 0:
        print("از قبل هست:", name)
        return True
    for url in urls:
        try:
            data = get(url)
        except Exception as exc:
            print("  نشد (%s): %s" % (type(exc).__name__, url))
            continue
        if check(data):
            target.write_bytes(data)
            print("دانلود شد:", name)
            return True
        print("  فایل درست نبود:", url)
    return False


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    failed = []

    for name, urls in FONTS.items():
        if not fetch(name, urls, is_font):
            failed.append((name, urls))
    for name, urls in LICENSES.items():
        if not fetch(name, urls, is_license):
            failed.append((name, urls))

    print()
    if not failed:
        print("همه‌ی فایل‌ها آماده است. حالا سرور را بالا بیاورید و Ctrl+F5 بزنید.")
        return

    print("این فایل‌ها دانلود نشد. VPN را روشن کنید و دوباره اجرا کنید.")
    print("اگر باز هم نشد، لینک اولِ هرکدام را در مرورگر باز کنید و فایل را")
    print("با همان اسم داخل static/fonts ذخیره کنید:\n")
    for name, urls in failed:
        print(" ", name)
        print("   ", urls[0])


if __name__ == "__main__":
    main()