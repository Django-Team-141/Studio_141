from .i18n import DEFAULT_LANG, TEXTS


def site_language(request):
    lang = request.session.get("lang", DEFAULT_LANG)
    if lang not in TEXTS:
        lang = DEFAULT_LANG
    return {
        "lang": lang,
        "dir": "rtl" if lang == "fa" else "ltr",
        "t": TEXTS[lang],
        "other_lang": "en" if lang == "fa" else "fa",
    }