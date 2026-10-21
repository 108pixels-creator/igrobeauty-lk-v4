# -*- coding: utf-8 -*-
"""Сборка страниц «Мой профиль» для всех состояний по БТ из одного шаблона.

Запуск из папки LK v4:   python tools/build_profile.py
Пишет index.html (Лига II) и profile-<код>.html для остальных состояний.
Коды: p1–p5 — статусы: без статуса, Лига II, Лига I, VIP, Super VIP.

Модель с 13.10.2026 (решение Антона): в ЛК нет уровня «Партнёр» — кабинет показывает только контрагентов,
партнёр остаётся сущностью 1С. Лига, текущий прогресс, сумма до сохранения или повышения статуса и ретро-бонус
общие для всех контрагентов одного партнёра: все их покупки идут в общий прогресс, и каждый контрагент видит
одно и то же. Поэтому профиль один для всех — бывший вариант «партнёр»; состояния «контрагент» (k1–k5, урезанный
профиль по БТ с. 11–14) убраны, страницы перенесены в _archive/. Ретро-бонус списывается только по телефону через менеджера.
Переключатель состояний — служебная полоса «Прототип» сверху с системным <select>; в Битрикс не идёт.
Файлы пишутся с CRLF, как остальные страницы v5.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB = "&nbsp;"


def money(n):
    return "{:,}".format(n).replace(",", NB) + NB + "₽"


def icon(name, size=None):
    cls = "igro-icon" + (" igro-icon--%s" % size if size else "")
    return '<svg class="%s" aria-hidden="true" focusable="false"><use href="#i-%s"></use></svg>' % (cls, name)


# Актуальный логотип ИГРО из Figma «IB – my DESIGN», node 538:2578 (assets/logo/igro-logo.svg, цвет — currentColor).
# Встраивается в разметку: <img> не красится токеном, а <use> и mask на внешний файл не работают при открытии с диска.
def _logo():
    import re as _re
    with open(os.path.join(ROOT, "assets", "logo", "igro-logo.svg"), encoding="utf-8") as f:
        svg = f.read().strip()
    svg = svg.replace('role="img" aria-label="ИГРО"', 'class="lk-member-card__logo" role="img" aria-label="ИГРО" focusable="false"')
    return _re.sub(r">\s+<", "><", svg)


LOGO = _logo()

STATUS = {  # gen — родительный падеж («скидка Лиги I», «от Лиги II»)
    "none": dict(name="Без статуса", gen="без статуса", icon=None),
    "l2": dict(name="Лига II", gen="Лиги II", icon="star", pct="10%"),
    "l1": dict(name="Лига I", gen="Лиги I", icon="crown", pct="15%"),
    "vip": dict(name="VIP", gen="VIP", icon="gem", pct="20%", rest="15%"),
    "svip": dict(name="Super VIP", gen="Super VIP", icon="gem", pct="25%", rest="15%"),
}
BRANDS = ["Nirvel", "Levissime", "Iuver", "Depilflax 100", "Starpil", "Lash Color", "Refectocil", "Soleo", "Comair", "ИГРОbeauty"]
LADDER = [  # код, имя, иконка, порог, что даёт
    ("l2", "Лига II", "star", 30000, "Скидка 10%"),
    ("l1", "Лига I", "crown", 60000, "Скидка 15%"),
    ("vip", "VIP", "gem", 90000, "20% на 10 брендов, 15% на остальное"),
    ("svip", "Super VIP", "gem", 300000, "25% на 10 брендов, 15% на остальное"),
]
ORDER = ["none", "l2", "l1", "vip", "svip"]
# шкала «Текущий прогресс» (БТ с. 6): начало, конец, текущая сумма, следующий уровень, уровень в начале шкалы
# у Super VIP шкала та же, что у VIP: от VIP 90 000 до Super VIP 300 000
PROGRESS = {
    "none": (0, 30000, 20000, "l2", "none"),
    "l2": (30000, 60000, 45000, "l1", "l2"),
    "l1": (60000, 90000, 70000, "vip", "l1"),
    "vip": (90000, 300000, 150000, "svip", "vip"),
    "svip": (90000, 300000, 250000, None, "vip"),
}
# демо-данные: ретро-бонус (None — участник без бонуса) и экономия за квартал
RETRO = {"none": None, "l2": None, "l1": None, "vip": 6000, "svip": 15000}
SAVED = {"none": None, "l2": 4500, "l1": 6900, "vip": 21000, "svip": 48000}
NEXT_TEXT = {  # текст карточки 1 (демо; «3 дня до конца квартала» считаются от 27.09.2026)
    "none": "Успейте до 30 сентября — и с 1 октября вы в Лиге&nbsp;II: клубная скидка 10% на все заказы квартала.",
    "l2": "Успейте до 30 сентября — и с 1 октября вы в Лиге&nbsp;I: клубная скидка вырастет с 10 до 15%.",
    "l1": "Успейте до 30 сентября — и с 1 октября вы в VIP: 20% на 10 брендов и 15% на остальной ассортимент.",
    "vip": "Успейте до 30 сентября — и с 1 октября вы в Super VIP: 25% на 10 брендов.",
    "svip": "Успейте до 30 сентября — и статус Super VIP сохранится на следующий квартал.",
}

STATES = [("p1", "none"), ("p2", "l2"), ("p3", "l1"), ("p4", "vip"), ("p5", "svip")]


def file_for(code):
    return "index.html" if code == "p2" else "profile-%s.html" % code


FAQ = [
    ("Что дает клубная скидка?", "Клубная скидка — это фиксированная скидка, которая применяется ко всем заказам в течение квартала и зависит от вашего статуса в программе лояльности.", True),
    ("Как перейти на следующий уровень?", "Статус повышается по итогам квартала в зависимости от общей суммы ваших покупок. Чем выше объем покупок, тем выше статус в следующем периоде.", True),
    ("Как рассчитывается текущий прогресс?", "Текущий прогресс рассчитывается как сумма всех ваших покупок за текущий расчетный период (квартал или первые 3 месяца с момента первого заказа для новых клиентов). Учитываются все оплаченные заказы, включая заказы через сайт и колл-центр.", False),
    ("Я уже набрал нужную сумму, почему у меня не разблокировалась клубная скидка?", "Статус обновляется по итогам расчетного периода. Даже при достижении нужной суммы он начнет действовать только в следующем квартале.", True),
    ("Когда обновится мой статус?", "Статус пересчитывается по итогам каждого квартала и начинает действовать в следующем расчетном периоде.", True),
    ("Какой срок действия клубной скидки?", "Клубная скидка действует в течение одного расчетного квартала и обновляется по итогам нового периода.", True),
    ("Как продлить текущий статус?", "Для сохранения статуса необходимо поддерживать нужный объем покупок каждый квартал. Если по итогам квартала объем покупок ниже минимального порога вашего уровня, статус будет понижен в следующем периоде.", False),
]

SPRITE = """<svg class="lk-sprite" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">
  <symbol id="i-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></symbol>
  <symbol id="i-crown" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7l4 5 5-7 5 7 4-5-2 11H5L3 7z"/><path d="M5 21h14"/></symbol>
  <symbol id="i-gem" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12l4 6-10 12L2 9l4-6z"/><path d="M2 9h20M11 3L8 9l4 12 4-12-3-6"/></symbol>
  <symbol id="i-star" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 17l-5.2 2.6 1-5.8L3.5 9.7l5.9-.9L12 3.5z"/></symbol>
  <symbol id="i-chevron-down" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></symbol>
  <symbol id="i-chevron-right" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></symbol>
  <symbol id="i-arrow-right" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>
  <symbol id="i-clock" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></symbol>
  <symbol id="i-coins" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="9" cy="7" rx="5.5" ry="2.5"/><path d="M3.5 7v4c0 1.4 2.5 2.5 5.5 2.5s5.5-1.1 5.5-2.5V7"/><path d="M9.5 16.4c.6.1 1.3.1 2 .1 3 0 5.5-1.1 5.5-2.5"/><path d="M14.5 11.8c2.5.3 6 .9 6 2.2v4c0 1.4-2.5 2.5-5.5 2.5S9.5 19.4 9.5 18v-1.6"/></symbol>
  <symbol id="i-discount" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17L17 7"/><circle cx="8.5" cy="8.5" r="1.7" fill="currentColor" stroke="none"/><circle cx="15.5" cy="15.5" r="1.7" fill="currentColor" stroke="none"/></symbol>
  <symbol id="i-education" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5l8 3.5-8 3.5-8-3.5L12 5z"/><path d="M6 11v4.2c0 1 2.7 2.3 6 2.3s6-1.3 6-2.3V11"/></symbol>
  <symbol id="i-gift" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="9" width="16" height="11" rx="1.5"/><path d="M3 9h18M12 9v11"/><path d="M12 9S11 5 8.5 5A2 2 0 0 0 8.5 9M12 9s1-4 3.5-4a2 2 0 0 1 0 4"/></symbol>
  <symbol id="i-heart" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20s-7-4.35-7-9.5A3.5 3.5 0 0 1 12 7a3.5 3.5 0 0 1 7 3.5C19 15.65 12 20 12 20z"/></symbol>
  <symbol id="i-lock" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="14" height="9" rx="1.5"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></symbol>
  <symbol id="i-logout" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5H7a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h8"/><path d="M18 15l3-3-3-3M10 12h11"/></symbol>
  <symbol id="i-orders" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4.5h6a1 1 0 0 1 1 1V7H8V5.5a1 1 0 0 1 1-1zM9 12h6M9 16h4"/></symbol>
  <symbol id="i-plus" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></symbol>
  <symbol id="i-sliders" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h10M18 7h2M4 17h4M12 17h8"/><circle cx="16" cy="7" r="2"/><circle cx="10" cy="17" r="2"/></symbol>
  <symbol id="i-user" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="3.5"/><path d="M5 20c0-3.5 3.1-5.5 7-5.5s7 2 7 5.5"/></symbol>
  <symbol id="i-promo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 12.6V5a1.5 1.5 0 0 1 1.5-1.5h7.6a1.5 1.5 0 0 1 1.06.44l7.4 7.4a1.5 1.5 0 0 1 0 2.12l-7.6 7.6a1.5 1.5 0 0 1-2.12 0l-7.4-7.4a1.5 1.5 0 0 1-.44-1.06z"/><circle cx="8.5" cy="8.5" r="1.5"/></symbol>
  <symbol id="i-user-circle" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="10" r="2.5"/><path d="M7.5 17.5c.6-2 2.4-3 4.5-3s3.9 1 4.5 3"/></symbol>
</svg>"""

NAV = """<a class="igro-btn igro-btn--dark lk-skip" href="#main">Перейти к содержимому</a>
<div class="lk-shell">
  <aside class="lk-aside">
    <nav class="igro-card lk-nav" aria-label="Личный кабинет">
      <ul class="lk-nav__list">
      <li><a class="lk-nav__item" href="index.html" aria-current="page">%(user)s<span class="lk-nav__label">Мой профиль</span></a></li>
      <li><a class="lk-nav__item" href="orders.html">%(orders)s<span class="lk-nav__label">Мои заказы</span></a></li>
      <li><a class="lk-nav__item" href="favorites.html">%(heart)s<span class="lk-nav__label">Избранное</span></a></li>
      <li><a class="lk-nav__item" href="promo.html">%(promo)s<span class="lk-nav__label">Акции</span></a></li>
      <li><a class="lk-nav__item" href="education.html">%(education)s<span class="lk-nav__label">Мое обучение</span></a></li>
      <li><a class="lk-nav__item" href="data.html">%(usercircle)s<span class="lk-nav__label">Мои данные</span></a></li>
      <li class="lk-nav__divider" aria-hidden="true"></li>
      <li><a class="lk-nav__item" href="#logout">%(logout)s<span class="lk-nav__label">Выйти</span></a></li>
      </ul>
    </nav>
  </aside>""" % dict(user=icon("user"), orders=icon("orders"), heart=icon("heart"), education=icon("education"), usercircle=icon("user-circle"), logout=icon("logout"), promo=icon("promo"))

BOOST = """      <div class="lk-boost">
        <div class="lk-boost__head">
          <h3 class="igro-h5">Быстрее добрать помогут ваши частые покупки</h3>
          <a class="igro-link" href="favorites.html"><span class="igro-link__text">Всё избранное</span>%(chev)s</a>
        </div>
        <ul class="lk-boost__list">
          <li class="lk-boost__item">
            <span class="lk-boost__thumb"><img src="assets/products/nirvel.webp" alt=""></span>
            <span class="lk-boost__text"><span class="lk-boost__name">Nirvel Pastel ArtX, серебристый, 100&nbsp;мл</span><span class="lk-boost__price">1&nbsp;080&nbsp;₽</span></span>
            <button type="button" class="igro-icon-btn igro-icon-btn--outline igro-icon-btn--sm" aria-label="В корзину: Nirvel Pastel ArtX, серебристый" data-toast="Добавлено в корзину|Nirvel Pastel ArtX, серебристый, 1 шт.">%(plus)s</button>
          </li>
          <li class="lk-boost__item">
            <span class="lk-boost__thumb"><img src="assets/products/refectocil.webp" alt=""></span>
            <span class="lk-boost__text"><span class="lk-boost__name">RefectoCil №&nbsp;3.1, краска для бровей и ресниц</span><span class="lk-boost__price">765&nbsp;₽</span></span>
            <button type="button" class="igro-icon-btn igro-icon-btn--outline igro-icon-btn--sm" aria-label="В корзину: RefectoCil №&nbsp;3.1" data-toast="Добавлено в корзину|RefectoCil №&nbsp;3.1, 1 шт.">%(plus)s</button>
          </li>
          <li class="lk-boost__item">
            <span class="lk-boost__thumb"><img src="assets/products/lashcolor.webp" alt=""></span>
            <span class="lk-boost__text"><span class="lk-boost__name">Lash Color, воск плёночный в гранулах, 100&nbsp;г</span><span class="lk-boost__price">396&nbsp;₽</span></span>
            <button type="button" class="igro-icon-btn igro-icon-btn--outline igro-icon-btn--sm" aria-label="В корзину: воск плёночный Lash Color" data-toast="Добавлено в корзину|Воск плёночный Lash Color, 1 шт.">%(plus)s</button>
          </li>
        </ul>
      </div>
""" % dict(chev=icon("chevron-right", 18), plus=icon("plus"))


def perk(icon_name, value, label, locked=False, wide=False, extra="", value_text=False):
    cls = "lk-perk" + (" lk-perk--locked" if locked else "") + (" lk-perk--wide" if wide else "")
    vcls = "lk-perk__value" + (" lk-perk__value--text" if value_text else "")
    sr = '<span class="igro-sr-only">Пока закрыто: </span>' if locked else ""
    label_html = '            <span class="lk-perk__label">%s</span>\n' % label if label else ""
    return ('          <li class="%s">\n            %s\n            <span class="%s">%s%s</span>\n%s%s          </li>\n'
            % (cls, icon(icon_name, 24).replace('class="igro-icon igro-icon--24"', 'class="igro-icon igro-icon--24 lk-perk__icon"'), vcls, sr, value, label_html, extra))


def discount_perk(status):
    s = STATUS[status]
    if status == "none":
        return perk("lock", "Клубная скидка", "Доступно после вступления в Клуб", locked=True, value_text=True)
    if status in ("vip", "svip"):
        tags = "".join('<span class="lk-perk__tag">%s</span>' % b for b in BRANDS)
        extra = ('            <span class="igro-sr-only">Бренды со скидкой %s: </span><span class="lk-perk__tags">%s</span>\n'
                 '            <span class="lk-perk__rest"><b>%s</b> скидка на остальной ассортимент</span>\n' % (s["pct"], tags, s["rest"]))
        return perk("discount", s["pct"], "моя клубная скидка — %s, на бренды из списка" % s["name"].replace(" ", NB), wide=True, extra=extra)  # подпись идёт до тегов
    return perk("discount", s["pct"], "моя клубная скидка — %s, на все заказы квартала" % s["name"].replace(" ", NB))


def retro_head(status):
    """13.10: ретро-бонус — без плашки, в правом верхнем углу шапки вместо кнопки «Перейти в каталог».
    Всегда две строки (значение и пояснение), поэтому высота одна во всех состояниях."""
    bonus = RETRO[status]
    if bonus is None:
        main = '<b class="lk-retro__value">5%</b> бонус · мой ретро-бонус'
        note = "Доступно после вступления в Клуб" if status == "none" else "В этом периоде пока не начислен"
        mod, ic, sr = " lk-retro--locked", "lock", "Пока закрыто: "
    else:
        main = '<b class="lk-retro__value">%s</b> бонусов доступно · ретро-бонус 5%%' % "{:,}".format(bonus).replace(",", NB)
        note = "Списать бонус можно только по телефону, через менеджера"
        mod, ic, sr = "", "gift", ""
    return ('<p class="lk-retro%s">%s<span class="lk-retro__text"><span class="lk-retro__main">%s%s</span>'
            '<span class="lk-retro__note">%s</span></span></p>' % (mod, icon(ic, 24).replace('class="igro-icon igro-icon--24"', 'class="igro-icon igro-icon--24 lk-retro__icon"'),
               '<span class="igro-sr-only">%s</span>' % sr if sr else "", main, note))


def next_perk(status):
    start, end, cur, nxt, _left = PROGRESS[status]
    if nxt is None:
        return perk("gem", "Super VIP", "высший статус Клуба — сохраняется при покупках от 300&nbsp;000&nbsp;₽ за квартал", value_text=True)
    thr = dict((c, t) for c, _n, _i, t, _g in LADDER)[nxt]
    gen = STATUS[nxt]["gen"].replace(" ", NB)
    pct = STATUS[nxt]["pct"]
    what = "скидка %s" % gen if nxt in ("l2", "l1") else "скидка %s на 10 брендов" % gen
    return perk("lock", pct, "%s — при покупках от %s за квартал" % (what, money(thr)), locked=True)


def saved_perk(status):
    v = SAVED[status]
    if v is None:
        return ""
    return perk("coins", money(v), "вы сэкономили в этом квартале")


def hero(status):
    s = STATUS[status]
    if s["icon"]:
        league = '<span class="lk-member-card__league">%s%s</span>' % (icon(s["icon"], 24), s["name"])
    else:
        league = '<span class="lk-member-card__league lk-member-card__league--none">Без статуса</span>'
    lead = "Екатерина Иванова · Студия красоты Красота · частный специалист"
    perks = discount_perk(status) + saved_perk(status) + next_perk(status)
    return """    <section class="lk-hero lk-hero--scene lk-hero--scene-%(status)s" aria-labelledby="hero-title">
      <svg class="lk-hero__rings" viewBox="0 0 560 560" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true" focusable="false"><circle cx="280" cy="280" r="279"/><circle cx="280" cy="280" r="219"/><circle cx="280" cy="280" r="159"/><circle cx="280" cy="280" r="99"/></svg>
      <div class="lk-hero__head">
        <div class="lk-hero__hello">
          <span class="igro-eyebrow igro-eyebrow--reward-on-dark">Клуб привилегий IGRO</span>
          <h1 class="lk-hero__title" id="hero-title"><span class="igro-sr-only">Мой профиль. </span>Добрый день, Екатерина</h1>
          <p class="lk-hero__lead">%(lead)s</p>
        </div>
      </div>
      <div class="lk-hero__body">
        <article class="lk-member-card lk-member-card--skin lk-member-card--%(status)s%(dark)s" aria-labelledby="card-title">
          <svg class="lk-member-card__rings" viewBox="0 0 280 280" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" focusable="false"><circle cx="140" cy="140" r="138"/><circle cx="140" cy="140" r="108"/><circle cx="140" cy="140" r="78"/><circle cx="140" cy="140" r="48"/></svg>
          <h2 class="igro-sr-only" id="card-title">Моя карта</h2>
          %(logo)s
          <div class="lk-member-card__tier">
            <span class="igro-eyebrow igro-eyebrow--reward">Клуб привилегий</span>
            %(league)s
          </div>
          <div class="lk-member-card__tier">
            <span class="lk-member-card__number"><span class="igro-sr-only">Номер карты </span>5020 4827 1136 0045</span>
            <span class="lk-member-card__foot"><span class="lk-member-card__owner">Екатерина Иванова</span>%(since)s</span>
          </div>
        </article>
        <span class="lk-member-card__shadow" aria-hidden="true"></span>
        <div class="lk-perks-block">
        <h2 class="igro-eyebrow igro-eyebrow--reward-on-dark lk-perks-block__title" id="perks-title">Ваши привилегии</h2>
        <p class="lk-perks-block__note">В этом квартале</p>
        <ul class="lk-perks" aria-labelledby="perks-title">
%(perks)s        </ul>
        </div>
        <!-- 13.10: ретро-бонус в разметке — после привилегий. На десктопе сетка ставит его в правый верхний угол
             (область retro), ниже 1024 px он идёт в самом низу блока, после экономии и следующего статуса -->
        %(retro)s
      </div>
    </section>
""" % dict(lead=lead, retro=retro_head(status), league=league, perks=perks, status=status,
           # не участник Клуба (БТ с. 3) — без «В клубе с…»
           since="" if status == "none" else '<span class="lk-member-card__since">В клубе с&nbsp;2024 года</span>',
           # фон карты по статусу — из референса refs/«ИГРО_ Коллекция VIP-карт привилегий.png»; на тёмных картах светлый текст
           dark=" lk-member-card--dark" if status in ("l2", "l1", "vip") else "",
           logo=LOGO)


def level_block(status):
    start, end, cur, nxt, left_code = PROGRESS[status]
    s = STATUS[status]
    pct = round((cur - start) * 100.0 / (end - start), 1)
    pct_s = ("%g" % pct)
    if status == "svip":
        title = "Сохранить статус"
        # длинный текст БТ (с. 5) — обычной строкой, не прописными: eyebrow в три строки читается тяжело
        eyebrow = '<p class="lk-level__lead">Чтобы сохранить статус Super&nbsp;VIP в следующем расчетном периоде, совершите покупки еще на</p>'
    else:
        title = "Перейти на следующий уровень"
        eyebrow = '<span class="igro-eyebrow">Совершите покупки на</span>'
    goal = money(end - cur)
    left = STATUS[left_code]
    left_icon = icon(left["icon"], 18) if left["icon"] else ""
    right_code = nxt or "svip"
    right_name = STATUS[right_code]["name"]
    right_icon = icon(STATUS[right_code]["icon"], 18)
    left_label = ("<span><b>0&nbsp;₽</b></span>" if left_code == "none"
                  else "<span><b>%s</b> %s</span>" % (left["name"].replace(" ", NB), money(start)))
    valuetext = "%s: от %s (%s) до %s (%s)" % (money(cur), "нуля" if left_code == "none" else left["gen"], money(start), STATUS[right_code]["gen"], money(end))
    # 20.10: ряд уровней по макету Figma «IB – my DESIGN», node 2707:6442 — мини-карты клуба одной высоты,
    # поверх них степпер: круги по центру карт и линии между ними. Состояния: done — пройден (цветная карта, тёмный круг),
    # current — ваш уровень (рамка, золотой круг, бейдж), next — следующая цель (серая карта 50 %, тёмный бейдж),
    # locked — впереди (серая карта 50 %). Линия к пройденному и текущему — золотая 2 px, от текущего к цели — 4 px
    # с переходом золото → серый (assets/tier-link-next.svg), дальше — серая 2 px.
    cur_i = ORDER.index(status)
    tiers = []
    for code, name, ic, thr, give in LADDER:
        i = ORDER.index(code)
        st = "current" if code == status else "next" if code == nxt else "done" if i < cur_i else "locked"
        tiers.append((code, name, ic, thr, st))
    steps = ""
    for k, (code, name, ic, thr, st) in enumerate(tiers):
        link = ""
        if k < len(tiers) - 1:
            to = tiers[k + 1][4]
            kind = "next" if (st == "current" and to == "next") else "reached" if to in ("done", "current") else "ahead"
            link = '<span class="lk-tier__link lk-tier__link--%s" aria-hidden="true"></span>' % kind
        badge = {"current": '<span class="igro-badge lk-tier__badge lk-tier__badge--current">Ваш уровень</span>',
                 "next": '<span class="igro-badge lk-tier__badge lk-tier__badge--next">Следующая цель</span>'}.get(st, "")
        lock = icon("lock").replace('class="igro-icon"', 'class="igro-icon lk-tier__lock"') if st in ("next", "locked") else ""
        label = "SUPER VIP" if code == "svip" else name.replace(" ", NB)  # как в макете
        perk_icon = icon("check" if st in ("done", "current") else "lock").replace('class="igro-icon"', 'class="igro-icon lk-tier__perk-icon"')
        sr = '<span class="igro-sr-only">Пока закрыто: </span>' if st in ("next", "locked") else ""
        pct = STATUS[code]["pct"]
        mark = '<span class="lk-tier__mark" aria-hidden="true">*</span>' if code == "svip" else ""
        rest = ('<p class="lk-tier__rest">на 10 брендов<br>%s на остальное</p>' % STATUS[code]["rest"]) if code in ("vip", "svip") else ""
        steps += ("        <li class=\"lk-tier lk-tier--%(st)s\"%(cur)s>\n"
                  "          <div class=\"lk-tier__card\">%(link)s<span class=\"lk-tier__art lk-tier__art--%(code)s\" aria-hidden=\"true\"></span>%(badge)s"
                  "<span class=\"lk-tier__dot\" aria-hidden=\"true\">%(dot)s</span>"
                  "<span class=\"lk-tier__name%(nmod)s\">%(nicon)s%(label)s</span>%(lock)s</div>\n"
                  "          <div class=\"lk-tier__info\"><div class=\"lk-tier__main\"><p class=\"lk-tier__perk\">%(picon)s<span>%(sr)sСкидка %(pct)s%(mark)s</span></p>"
                  "<p class=\"lk-tier__from\">от %(thr)s</p></div>%(rest)s</div>\n"
                  "        </li>\n") % dict(
            st=st, cur=' aria-current="step"' if st == "current" else "", link=link, code=code, badge=badge,
            dot=icon(ic, 18), nicon=icon(ic, 18).replace('class="igro-icon igro-icon--18"', 'class="igro-icon igro-icon--18 lk-tier__name-icon"'),
            label=label, nmod=" lk-tier__name--svip" if code == "svip" else "", lock=lock, picon=perk_icon, sr=sr, pct=pct, mark=mark, thr=money(thr), rest=rest)
    return """    <section class="igro-card lk-level lk-section" aria-labelledby="level-title">
      <div class="lk-level__head">
        <h2 class="igro-h2" id="level-title">%(title)s</h2>
        <span class="igro-badge igro-badge--warning">%(clock)s3&nbsp;дня до конца квартала</span>
      </div>
      <div class="lk-level__grid">
        <div class="lk-level__goal">
          %(eyebrow)s
          <p class="lk-level__amount">%(goal)s</p>
          <p class="lk-level__text">%(text)s</p>
        </div>
        <div class="lk-progress">
          <h3 class="igro-h5 lk-progress__title" id="progress-title">Текущий прогресс</h3>
          <div class="lk-progress__meter">
            <span class="lk-progress__here" style="left: %(pct)s%%">Вы здесь · %(cur)s<span class="lk-progress__arrow" aria-hidden="true"></span></span>
            <div class="lk-progress__track" role="progressbar" aria-labelledby="progress-title" aria-valuemin="%(start)d" aria-valuemax="%(end)d" aria-valuenow="%(curn)d" aria-valuetext="%(valuetext)s"><span class="lk-progress__fill" style="width: %(pct)s%%"></span></div>
          </div>
          <div class="lk-progress__ends">
            <span class="lk-progress__end">%(left_icon)s%(left_label)s</span>
            <span class="lk-progress__end">%(right_icon)s<span><b>%(right_name)s</b> %(end_m)s</span></span>
          </div>
        </div>
      </div>
      <ol class="lk-tiers" aria-label="Уровни клуба привилегий: сумма покупок за квартал и скидка">
%(steps)s      </ol>
%(boost)s    </section>
""" % dict(title=title, clock=icon("clock"), eyebrow=eyebrow, goal=goal, text=NEXT_TEXT[status], pct=pct_s, cur=money(cur), start=start, end=end, curn=cur,
           valuetext=valuetext, left_icon=left_icon, left_label=left_label, right_icon=right_icon, right_name=right_name.replace(" ", NB), end_m=money(end), steps=steps, boost=BOOST)


def faq_block():
    out = ""
    for n, (q, a, link) in enumerate(FAQ, 1):
        link_html = ' <a href="#loyalty">Узнать больше<span class="igro-sr-only"> о Клубе привилегий ИГРО</span></a>' if link else ""
        out += ('        <div class="igro-accordion__item">\n'
                '          <h3 class="igro-accordion__heading"><button type="button" class="igro-accordion__trigger" id="faq-h%(n)d" aria-expanded="%(exp)s" aria-controls="faq-p%(n)d"><span class="igro-accordion__title">%(q)s</span><span class="igro-accordion__chevron">%(chev)s</span></button></h3>\n'
                '          <div class="igro-accordion__panel" id="faq-p%(n)d" role="region" aria-labelledby="faq-h%(n)d"%(hidden)s>%(a)s%(link)s</div>\n'
                '        </div>\n') % dict(n=n, exp="true" if n == 1 else "false", q=q, chev=icon("chevron-down"), hidden="" if n == 1 else " hidden", a=a, link=link_html)
    return """    <section class="lk-section" aria-labelledby="faq-title">
      <h2 class="igro-h2 lk-section__title" id="faq-title">Частые вопросы</h2>
      <div class="igro-accordion" data-accordion>
%s      </div>
    </section>
""" % out


def proto_bar(code):
    """Служебная полоса прототипа сверху: системный <select> состояний «Моего профиля». В Битрикс не идёт."""
    groups = "".join('<option value="%s"%s>%s</option>' % (file_for(c), " selected" if c == code else "", STATUS[st]["name"]) for c, st in STATES)
    return chr(10).join([
        '<div class="lk-proto lk-no-print">',
        '  <div class="lk-proto__inner">',
        '    <span class="lk-proto__tag">Прототип</span>',
        '    <label class="lk-proto__label" for="lkProtoState">Состояние экрана «Мой профиль»</label>',
        '    <select class="lk-proto__select" id="lkProtoState" data-proto-switch>%s</select>' % groups,
        '    <span class="lk-proto__note">Служебная полоса, на сайт не выводится</span>',
        '  </div>',
        '</div>'])


def page(code, status):
    body = hero(status) + "\n" + level_block(status) + "\n" + faq_block()
    return """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Мой профиль — IGRObeauty</title>
<link rel="stylesheet" href="design-system-v6/styles.css">
<link rel="stylesheet" href="css/components.css">
<link rel="stylesheet" href="css/lk.css">
<script src="js/lk.js" defer></script>
</head>
<body class="igro" data-lk-state="%(code)s" data-lk-status="%(status)s">
<!-- Собрано tools/build_profile.py: состояние %(code)s — %(statusname)s. Правки вносить в генератор. -->
%(sprite)s
%(proto)s
%(nav)s
  <main class="lk-main" id="main" tabindex="-1">

%(body)s  </main>
</div>

<div class="lk-toasts" id="toasts"></div>
</body>
</html>
""" % dict(code=code, status=status, statusname=STATUS[status]["name"], sprite=SPRITE, nav=NAV, body=body, proto=proto_bar(code))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # консоль Windows в cp1252 не печатает кириллицу
    for code, status in STATES:
        html = page(code, status).replace("\r\n", "\n").replace("\n", "\r\n")
        path = os.path.join(ROOT, file_for(code))
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(html)
        print("%-18s %s" % (file_for(code), STATUS[status]["name"]))


if __name__ == "__main__":
    main()
