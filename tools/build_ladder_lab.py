# -*- coding: utf-8 -*-
"""Тестовая страница «Блок уровней клуба — 10 вариантов» (lab-ladder.html), 13.10.2026.

Запуск из папки LK v6:   python tools/build_ladder_lab.py
Пишет lab-ladder.html (CRLF). Стили — css/lab-ladder.css, переключатели — js/lab-ladder.js.

Зачем: в профиле уровни стоят лестницей (плитки разной высоты, метки над ними) и ломают ровную блочную
сетку страницы. Здесь — 10 вариантов того же блока в рамках DS v6.1 на тех же данных, что в профиле
(tools/build_profile.py: LADDER, PROGRESS). Каждый вариант собран для всех пяти статусов; служебная полоса
сверху переключает статус и показывает вариант в блоке «Перейти на следующий уровень» целиком или отдельно.
Страница служебная, в профиль и в Битрикс не идёт.
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_profile import (BOOST, LADDER, NAV, NB, NEXT_TEXT, ORDER, PROGRESS, SPRITE, STATUS,  # noqa: E402
                           money)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATES = ["none", "l2", "l1", "vip", "svip"]
DEFAULT = "l2"
LIST_LABEL = "Уровни клуба привилегий: сумма покупок за квартал и скидка"
STATE_TEXT = {"done": "Пройден", "current": "Ваш уровень", "next": "Следующая цель", "locked": "Впереди"}
DARK_ART = ("l2", "l1", "vip")  # тёмные карты клуба (как lk-member-card--dark в профиле)
BIG = {  # крупная цифра скидки и подпись к ней (вариант 6)
    "l2": ("10%", "клубная скидка на все заказы квартала"),
    "l1": ("15%", "клубная скидка на все заказы квартала"),
    "vip": ("20%", "на 10 брендов, 15% на остальное"),
    "svip": ("25%", "на 10 брендов, 15% на остальное"),
}

VARIANTS = [
    ("Ровный ряд",
     "Минимальная правка текущего блока: четыре плитки одной высоты, метки «Ваш уровень» и «Следующая цель» – внутри плиток, "
     "а не над ними. Нижняя и верхняя граница ряда ровные, как у блоков выше и ниже."),
    ("Одна панель",
     "Уровни – не четыре отдельные карточки, а одна панель с тонкими разделителями. Цветные полосы сверху складываются в шкалу: "
     "пройдено – зелёным, ваш уровень – тёмным, цель – золотом."),
    ("Степпер",
     "Уровни как шаги маршрута: кружки с иконками лиг на одной линии, подписи под ними. Самый лёгкий по весу вариант; "
     "на телефоне шаги идут столбиком."),
    ("Таблица уровней",
     "Строгая таблица: уровень, сумма покупок за квартал, скидка и состояние. Пороги и скидки удобно сравнивать, "
     "ваш уровень и цель подсвечены."),
    ("Сколько до каждого уровня",
     "У каждого уровня своя шкала от нуля до порога и подпись «ещё N ₽». Видно, сколько не хватает не только до следующей цели, "
     "но и до VIP и Super VIP."),
    ("Сейчас → цель",
     "В фокусе только два уровня – ваш и следующий, с крупной цифрой скидки. Остальные уровни – одной строкой ниже."),
    ("Вкладки уровней",
     "Компактный переключатель из четырёх вкладок DS Tabs и под ним – подробности выбранного уровня. "
     "По умолчанию открыта следующая цель (у Super VIP – текущий уровень)."),
    ("Мини-карты клуба",
     "Каждый уровень показан своей картой клуба – той же, что в шапке профиля. Закрытые уровни – в серой гамме, "
     "все карты одного размера."),
    ("Ступени в плитках",
     "Плитки одной высоты, а «лестница» сохранена в маленькой пиктограмме из четырёх столбиков: число закрашенных столбиков – "
     "номер уровня."),
    ("Единая шкала",
     "«Текущий прогресс» и уровни объединены: на одной шкале отмечены все пороги, под ними – названия и скидки. "
     "Отдельного ряда уровней нет, блок становится заметно ниже."),
]


def ico(name, size=None, cls=""):
    c = "igro-icon" + (" igro-icon--%s" % size if size else "") + (" " + cls if cls else "")
    return '<svg class="%s" aria-hidden="true" focusable="false"><use href="#i-%s"></use></svg>' % (c, name)


def levels(status):
    """Уровни для статуса: состояние done / current / next / locked, сколько осталось до порога, доля пути от нуля."""
    cur_i = ORDER.index(status)
    cur, nxt = PROGRESS[status][2], PROGRESS[status][3]
    out = []
    for code, name, ic, thr, give in LADDER:
        i = ORDER.index(code)
        state = "current" if code == status else "next" if code == nxt else "done" if i < cur_i else "locked"
        out.append(dict(code=code, name=name.replace(" ", NB), icon=ic, thr=thr, give=give, state=state,
                        left=max(0, thr - cur), pct="%g" % min(100, round(cur * 100.0 / thr, 1))))
    return out


def perk_icon(state):
    return "check" if state in ("done", "current") else "lock"


def sr_closed(state):
    return '<span class="igro-sr-only">Пока закрыто: </span>' if state in ("next", "locked") else ""


def cur_attr(L):
    return ' aria-current="step"' if L["state"] == "current" else ""


def badge(state, on_dark=False):
    if state == "current":
        return '<span class="igro-badge igro-badge--brand">Ваш уровень</span>'
    if state == "next":
        return '<span class="igro-badge igro-badge--reward%s">Следующая цель</span>' % ("-on-dark" if on_dark else "")
    return ""


# ---------------------------------------------------------------- 1. Ровный ряд
def v1(status, uid):
    items = ""
    for L in levels(status):
        items += ('        <li class="lab-row__item lab-row__item--%(state)s"%(cur)s>\n'
                  '          <span class="lab-row__top">%(icon)s%(badge)s</span>\n'
                  '          <span class="lab-row__name">%(name)s</span>\n'
                  '          <span class="lab-row__from">от %(from)s</span>\n'
                  '          <span class="lab-row__perk">%(picon)s<span>%(sr)s%(give)s</span></span>\n'
                  '        </li>\n') % dict(state=L["state"], cur=cur_attr(L), icon=ico(L["icon"], 24, "lab-row__icon"),
                                           badge=badge(L["state"]), name=L["name"], **{"from": money(L["thr"])},
                                           picon=ico(perk_icon(L["state"])), sr=sr_closed(L["state"]), give=L["give"])
    return '      <ol class="lab-row" aria-label="%s">\n%s      </ol>\n' % (LIST_LABEL, items)


# ---------------------------------------------------------------- 2. Одна панель
def v2(status, uid):
    items = ""
    for L in levels(status):
        items += ('        <li class="lab-panel__cell lab-panel__cell--%(state)s"%(cur)s>\n'
                  '          <span class="lab-panel__state">%(stext)s</span>\n'
                  '          <span class="lab-panel__name">%(icon)s%(name)s</span>\n'
                  '          <span class="lab-panel__from">от %(from)s</span>\n'
                  '          <span class="lab-panel__perk">%(sr)s%(give)s</span>\n'
                  '        </li>\n') % dict(state=L["state"], cur=cur_attr(L), stext=STATE_TEXT[L["state"]], icon=ico(L["icon"], 18),
                                           name=L["name"], **{"from": money(L["thr"])}, sr=sr_closed(L["state"]), give=L["give"])
    return '      <ol class="lab-panel" aria-label="%s">\n%s      </ol>\n' % (LIST_LABEL, items)


# ---------------------------------------------------------------- 3. Степпер
def v3(status, uid):
    items = ""
    for L in levels(status):
        b = badge(L["state"])
        items += ('        <li class="lab-steps__item is-%(state)s"%(cur)s>\n'
                  '          <span class="lab-steps__dot">%(icon)s</span>\n'
                  '          <span class="lab-steps__name">%(name)s</span>\n'
                  '          <span class="lab-steps__from">от %(from)s</span>\n'
                  '          <span class="lab-steps__perk">%(sr)s%(give)s</span>\n'
                  '%(badge)s'
                  '        </li>\n') % dict(state=L["state"], cur=cur_attr(L), icon=ico(L["icon"], 18), name=L["name"],
                                           **{"from": money(L["thr"])}, sr=sr_closed(L["state"]), give=L["give"],
                                           badge=('          <span class="lab-steps__state">%s</span>\n' % b) if b else "")
    return '      <ol class="lab-steps" aria-label="%s">\n%s      </ol>\n' % (LIST_LABEL, items)


# ---------------------------------------------------------------- 4. Таблица уровней
def v4(status, uid):
    rows = ""
    for L in levels(status):
        if L["state"] in ("current", "next"):
            st = badge(L["state"])
        elif L["state"] == "done":
            st = '<span class="lab-table__done">%sПройден</span>' % ico("check")
        else:
            st = '<span class="lab-table__later">Впереди</span>'
        rows += ('          <tr class="lab-table__row lab-table__row--%(state)s"%(cur)s>\n'
                 '            <th scope="row"><span class="lab-table__league">%(icon)s%(name)s</span></th>\n'
                 '            <td class="lab-table__from">от %(from)s</td>\n'
                 '            <td class="lab-table__give"><span class="lab-table__perk">%(picon)s<span>%(sr)s%(give)s</span></span></td>\n'
                 '            <td class="lab-table__state">%(st)s</td>\n'
                 '          </tr>\n') % dict(state=L["state"], cur=cur_attr(L), icon=ico(L["icon"], 18), name=L["name"],
                                            **{"from": money(L["thr"])}, picon=ico(perk_icon(L["state"])), sr=sr_closed(L["state"]),
                                            give=L["give"], st=st)
    return ('      <table class="lab-table">\n'
            '        <caption class="igro-sr-only">%s</caption>\n'
            '        <thead><tr><th scope="col">Уровень</th><th scope="col">Покупки за квартал</th><th scope="col">Клубная скидка</th>'
            '<th scope="col"><span class="igro-sr-only">Состояние</span></th></tr></thead>\n'
            '        <tbody>\n%s        </tbody>\n      </table>\n') % (LIST_LABEL, rows)


# ---------------------------------------------------------------- 5. Сколько до каждого уровня
def v5(status, uid):
    items = ""
    for L in levels(status):
        if L["state"] == "done" or (L["state"] == "current" and not L["left"]):
            right = '<span class="lab-reach__left lab-reach__left--done">%s%s</span>' % (
                ico("check"), "ваш уровень" if L["state"] == "current" else "достигнут")
        elif L["state"] == "current":  # Super VIP: статус есть, но сумма для сохранения ещё не набрана
            right = '<span class="lab-reach__left">до сохранения ещё <b>%s</b></span>' % money(L["left"])
        else:
            right = '<span class="lab-reach__left">ещё <b>%s</b></span>' % money(L["left"])
        gold = " igro-progress--gold" if L["state"] in ("next", "locked") else ""
        items += ('        <li class="lab-reach__item lab-reach__item--%(state)s"%(cur)s>\n'
                  '          <span class="lab-reach__head"><span class="lab-reach__name">%(icon)s%(name)s</span>%(right)s</span>\n'
                  '          <span class="igro-progress lab-reach__bar%(gold)s" aria-hidden="true"><span class="igro-progress__track lab-reach__track">'
                  '<span class="igro-progress__fill lab-reach__progress" style="width: %(pct)s%%"></span></span></span>\n'
                  '          <span class="lab-reach__perk">%(picon)s<span>%(sr)s<b>%(give)s</b> · от %(from)s</span></span>\n'
                  '        </li>\n') % dict(state=L["state"], cur=cur_attr(L), icon=ico(L["icon"], 18), name=L["name"], right=right,
                                           gold=gold, pct=L["pct"], picon=ico(perk_icon(L["state"])), sr=sr_closed(L["state"]),
                                           give=L["give"], **{"from": money(L["thr"])})
    return '      <ol class="lab-reach" aria-label="%s">\n%s      </ol>\n' % (LIST_LABEL, items)


# ---------------------------------------------------------------- 6. Сейчас → цель
def v6(status, uid):
    lv = levels(status)
    cur = [L for L in lv if L["state"] == "current"]
    nxt = [L for L in lv if L["state"] == "next"]
    if cur:
        L = cur[0]
        big, sub = BIG[L["code"]]
        left = ('      <div class="lab-focus__card lab-focus__card--current" aria-current="step">\n'
                '        <span class="igro-eyebrow igro-eyebrow--reward-on-dark">Ваш уровень</span>\n'
                '        <span class="lab-focus__name">%s%s</span>\n'
                '        <span class="lab-focus__line"><span class="lab-focus__value">%s</span><span class="lab-focus__sub">%s</span></span>\n'
                '      </div>\n') % (ico(L["icon"], 24), L["name"], big, sub)
    else:
        left = ('      <div class="lab-focus__card lab-focus__card--none">\n'
                '        <span class="igro-eyebrow">Сейчас</span>\n'
                '        <span class="lab-focus__name">Без статуса</span>\n'
                '        <span class="lab-focus__line"><span class="lab-focus__value">0%</span><span class="lab-focus__sub">клубная скидка – после вступления в Клуб</span></span>\n'
                '      </div>\n')
    if nxt:
        L = nxt[0]
        big, sub = BIG[L["code"]]
        right = ('      <div class="lab-focus__card lab-focus__card--next">\n'
                 '        <span class="igro-eyebrow igro-eyebrow--reward">Следующая цель</span>\n'
                 '        <span class="lab-focus__name">%s%s</span>\n'
                 '        <span class="lab-focus__line"><span class="lab-focus__value"><span class="igro-sr-only">Пока закрыто: </span>%s</span><span class="lab-focus__sub">%s</span></span>\n'
                 '        <span class="lab-focus__cond">при покупках от %s за квартал · осталось %s</span>\n'
                 '      </div>\n') % (ico(L["icon"], 24), L["name"], big, sub, money(L["thr"]), money(L["left"]))
    else:  # Super VIP — выше некуда
        right = ('      <div class="lab-focus__card lab-focus__card--next">\n'
                 '        <span class="igro-eyebrow igro-eyebrow--reward">Высший уровень</span>\n'
                 '        <span class="lab-focus__name">%sСохранить Super%sVIP</span>\n'
                 '        <span class="lab-focus__line"><span class="lab-focus__value">%s</span><span class="lab-focus__sub">осталось купить в этом квартале</span></span>\n'
                 '        <span class="lab-focus__cond">статус сохраняется при покупках от %s за квартал</span>\n'
                 '      </div>\n') % (ico("gem", 24), NB, money(PROGRESS[status][1] - PROGRESS[status][2]), money(300000))
    rest = ""
    for title, group in (("Пройдены", [L for L in lv if L["state"] == "done"]), ("Дальше", [L for L in lv if L["state"] == "locked"])):
        if not group:
            continue
        rest += '        <p class="lab-focus__group"><span class="lab-focus__group-title">%s</span>%s</p>\n' % (title, "".join(
            '<span class="lab-focus__item">%s<b>%s</b> от %s – %s</span>' % (ico(L["icon"], 18), L["name"], money(L["thr"]), L["give"]) for L in group))
    return ('      <div class="lab-focus" role="group" aria-label="%s">\n%s      <span class="lab-focus__arrow" aria-hidden="true">%s</span>\n%s'
            '      <div class="lab-focus__rest">\n%s      </div>\n      </div>\n') % (LIST_LABEL, left, ico("arrow-right", 24), right, rest)


# ---------------------------------------------------------------- 7. Вкладки уровней
def v7(status, uid):
    lv = levels(status)
    pick = ([L for L in lv if L["state"] == "next"] or [L for L in lv if L["state"] == "current"])[0]["code"]
    tabs = panels = ""
    for L in lv:
        sel = L["code"] == pick
        tid, pid = "%s-%s-tab" % (uid, L["code"]), "%s-%s" % (uid, L["code"])
        mark = ico("check", None, "lab-tabs__mark") + '<span class="igro-sr-only"> – ваш уровень</span>' if L["state"] == "current" else ""
        tabs += ('          <button type="button" class="igro-tab lab-tabs__tab" role="tab" id="%s" aria-controls="%s" aria-selected="%s" tabindex="%s">%s%s%s</button>\n'
                 % (tid, pid, "true" if sel else "false", "0" if sel else "-1", ico(L["icon"], 18), L["name"], mark))
        if L["state"] == "current":
            b = badge("current")
            text = "Это ваш уровень в текущем квартале." if not L["left"] else "Это ваш уровень. Чтобы сохранить его, наберите покупки до порога до конца квартала."
        elif L["state"] == "next":
            b, text = badge("next"), NEXT_TEXT[status]
        elif L["state"] == "done":
            b, text = '<span class="igro-badge igro-badge--success">Пройден</span>', "Уровень пройден – ваш статус выше."
        else:
            b, text = '<span class="igro-badge">Впереди</span>', "До этого уровня осталось %s покупок за квартал." % money(L["left"])
        left = money(L["left"]) if L["left"] else "Порог набран"
        panels += ('        <div class="igro-tabpanel lab-tabs__panel lab-tabs__panel--%(state)s" role="tabpanel" id="%(pid)s" aria-labelledby="%(tid)s"%(hidden)s>\n'
                   '          <div class="lab-tabs__main">\n'
                   '            %(badge)s\n'
                   '            <p class="lab-tabs__title">%(icon)s%(name)s</p>\n'
                   '            <p class="lab-tabs__text">%(text)s</p>\n'
                   '          </div>\n'
                   '          <dl class="lab-tabs__facts">\n'
                   '            <div class="lab-tabs__fact"><dt>Покупки за квартал</dt><dd>от %(from)s</dd></div>\n'
                   '            <div class="lab-tabs__fact"><dt>Клубная скидка</dt><dd>%(give)s</dd></div>\n'
                   '            <div class="lab-tabs__fact"><dt>Осталось до порога</dt><dd>%(left)s</dd></div>\n'
                   '          </dl>\n'
                   '        </div>\n') % dict(state=L["state"], pid=pid, tid=tid, hidden="" if sel else " hidden", badge=b,
                                             icon=ico(L["icon"], 24), name=L["name"], text=text, give=L["give"], left=left,
                                             **{"from": money(L["thr"])})
    return ('      <div class="lab-tabs">\n'
            '        <div class="igro-tabs lab-tabs__list" role="tablist" aria-label="%s" data-tabs>\n%s        </div>\n%s'
            '      </div>\n') % (LIST_LABEL, tabs, panels)


# ---------------------------------------------------------------- 8. Мини-карты клуба
def v8(status, uid):
    items = ""
    for L in levels(status):
        lock = '<span class="lab-cards__lock">%s</span>' % ico("lock") if L["state"] in ("next", "locked") else ""
        st = badge(L["state"]) or '<span class="lab-cards__state">%s</span>' % STATE_TEXT[L["state"]]
        items += ('        <li class="lab-cards__item lab-cards__item--%(state)s"%(cur)s>\n'
                  '          <span class="lab-cards__art lab-cards__art--%(code)s"><span class="lab-cards__art-top">%(lock)s</span>'
                  '<span class="lab-cards__league">%(icon)s%(name)s</span></span>\n'
                  '          <span class="lab-cards__meta">%(st)s</span>\n'
                  '          <span class="lab-cards__from">от %(from)s</span>\n'
                  '          <span class="lab-cards__perk">%(picon)s<span>%(sr)s%(give)s</span></span>\n'
                  '        </li>\n') % dict(state=L["state"], cur=cur_attr(L), code=L["code"], lock=lock, icon=ico(L["icon"], 18),
                                           name=L["name"], st=st, **{"from": money(L["thr"])}, picon=ico(perk_icon(L["state"])),
                                           sr=sr_closed(L["state"]), give=L["give"])
    return '      <ol class="lab-cards" aria-label="%s">\n%s      </ol>\n' % (LIST_LABEL, items)


# ---------------------------------------------------------------- 9. Ступени в плитках
def v9(status, uid):
    items = ""
    for n, L in enumerate(levels(status), 1):
        bars = "".join('<span class="lab-stair__bar%s"></span>' % (" is-on" if k <= n else "") for k in range(1, 5))
        items += ('        <li class="lab-stairs__item lab-stairs__item--%(state)s"%(cur)s>\n'
                  '          <span class="lab-stairs__top"><span class="lab-stair" aria-hidden="true">%(bars)s</span>%(badge)s</span>\n'
                  '          <span class="lab-stairs__name">%(name)s</span>\n'
                  '          <span class="lab-stairs__from">от %(from)s</span>\n'
                  '          <span class="lab-stairs__perk">%(picon)s<span>%(sr)s%(give)s</span></span>\n'
                  '        </li>\n') % dict(state=L["state"], cur=cur_attr(L), bars=bars, badge=badge(L["state"]), name=L["name"],
                                           **{"from": money(L["thr"])}, picon=ico(perk_icon(L["state"])), sr=sr_closed(L["state"]),
                                           give=L["give"])
    return '      <ol class="lab-stairs" aria-label="%s">\n%s      </ol>\n' % (LIST_LABEL, items)


# ---------------------------------------------------------------- 10. Единая шкала (заменяет «Текущий прогресс»)
def route_pos(amount):
    """Положение суммы на шкале с равными отрезками: 0 → Лига II → Лига I → VIP → Super VIP (0, 25, 50, 75, 100 %)."""
    marks = [0] + [thr for _c, _n, _i, thr, _g in LADDER]
    for k in range(4):
        a, b = marks[k], marks[k + 1]
        if amount <= b:
            return round(25 * k + 25.0 * (amount - a) / (b - a), 1)
    return 100.0


def route(status, uid):
    start, end, cur, nxt, _ = PROGRESS[status]
    pos = "%g" % route_pos(cur)
    lv = levels(status)
    dots = '<span class="lab-route__dot lab-route__dot--0 is-reached%s"></span>' % (" is-current" if status == "none" else "")
    labels = ('          <li class="lab-route__label lab-route__label--start%s"><span class="lab-route__name">Старт</span>'
              '<span class="lab-route__from">0&nbsp;₽</span></li>\n') % (" is-current" if status == "none" else "")
    for k, L in enumerate(lv, 1):
        reached = " is-reached" if cur >= L["thr"] else ""
        dots += '<span class="lab-route__dot lab-route__dot--%d%s%s"></span>' % (k, reached, " is-current" if L["state"] == "current" else "")
        labels += ('          <li class="lab-route__label is-%(state)s"%(cur)s>%(icon)s<span class="lab-route__name">%(name)s</span>'
                   '<span class="lab-route__from">от %(from)s</span><span class="lab-route__perk">%(sr)s%(give)s</span></li>\n'
                   % dict(state=L["state"], cur=cur_attr(L), icon=ico(L["icon"], 18), name=L["name"], **{"from": money(L["thr"])},
                          sr=sr_closed(L["state"]), give=L["give"]))
    return ('        <div class="lk-progress lab-route">\n'
            '          <h3 class="igro-h5 lk-progress__title" id="%(uid)s-progress">Текущий прогресс</h3>\n'
            '          <div class="lk-progress__meter lab-route__meter">\n'
            '            <span class="lk-progress__here" style="left: %(pos)s%%">Вы здесь · %(cur)s<span class="lk-progress__arrow" aria-hidden="true"></span></span>\n'
            '            <div class="lk-progress__track" role="progressbar" aria-labelledby="%(uid)s-progress" aria-valuemin="0" aria-valuemax="300000" '
            'aria-valuenow="%(curn)d" aria-valuetext="%(cur)s за квартал"><span class="lk-progress__fill" style="width: %(pos)s%%"></span></div>\n'
            '            <span class="lab-route__dots" aria-hidden="true">%(dots)s</span>\n'
            '          </div>\n'
            '          <ol class="lab-route__labels" aria-label="%(label)s">\n%(labels)s          </ol>\n'
            '        </div>\n') % dict(uid=uid, pos=pos, cur=money(cur), curn=cur, dots=dots, labels=labels, label=LIST_LABEL)


BUILDERS = [v1, v2, v3, v4, v5, v6, v7, v8, v9, None]


# ---------------------------------------------------------------- блок «Перейти на следующий уровень» вокруг варианта
def section(n, status, uid):
    start, end, cur, nxt, left_code = PROGRESS[status]
    pct = "%g" % round((cur - start) * 100.0 / (end - start), 1)
    if status == "svip":
        title = "Сохранить статус"
        eyebrow = '<p class="lk-level__lead">Чтобы сохранить статус Super&nbsp;VIP в следующем расчетном периоде, совершите покупки еще на</p>'
    else:
        title = "Перейти на следующий уровень"
        eyebrow = '<span class="igro-eyebrow">Совершите покупки на</span>'
    left = STATUS[left_code]
    left_icon = ico(left["icon"], 18) if left["icon"] else ""
    right_code = nxt or "svip"
    left_label = ("<span><b>0&nbsp;₽</b></span>" if left_code == "none"
                  else "<span><b>%s</b> %s</span>" % (left["name"].replace(" ", NB), money(start)))
    goal = ('          <div class="lk-level__goal lab-ctx">\n            %s\n            <p class="lk-level__amount">%s</p>\n'
            '            <p class="lk-level__text">%s</p>\n          </div>\n') % (eyebrow, money(end - cur), NEXT_TEXT[status])
    if n == 10:
        grid = '        <div class="lk-level__grid lab-route-grid">\n' + goal + route(status, uid) + '        </div>\n'
        body = ""
    else:
        progress = ('          <div class="lk-progress">\n'
                    '            <h3 class="igro-h5 lk-progress__title" id="%(uid)s-progress">Текущий прогресс</h3>\n'
                    '            <div class="lk-progress__meter">\n'
                    '              <span class="lk-progress__here" style="left: %(pct)s%%">Вы здесь · %(cur)s<span class="lk-progress__arrow" aria-hidden="true"></span></span>\n'
                    '              <div class="lk-progress__track" role="progressbar" aria-labelledby="%(uid)s-progress" aria-valuemin="%(start)d" aria-valuemax="%(end)d" '
                    'aria-valuenow="%(curn)d"><span class="lk-progress__fill" style="width: %(pct)s%%"></span></div>\n'
                    '            </div>\n'
                    '            <div class="lk-progress__ends">\n'
                    '              <span class="lk-progress__end">%(left_icon)s%(left_label)s</span>\n'
                    '              <span class="lk-progress__end">%(right_icon)s<span><b>%(right_name)s</b> %(end_m)s</span></span>\n'
                    '            </div>\n'
                    '          </div>\n') % dict(uid=uid, pct=pct, cur=money(cur), start=start, end=end, curn=cur, left_icon=left_icon,
                                                left_label=left_label, right_icon=ico(STATUS[right_code]["icon"], 18),
                                                right_name=STATUS[right_code]["name"].replace(" ", NB), end_m=money(end))
        grid = '        <div class="lk-level__grid lab-ctx">\n' + goal + progress + '        </div>\n'
        body = BUILDERS[n - 1](status, uid)
    return ('      <section class="igro-card lk-level" aria-labelledby="%(uid)s-title">\n'
            '        <div class="lk-level__head lab-ctx">\n'
            '          <h3 class="igro-h2" id="%(uid)s-title">%(title)s</h3>\n'
            '          <span class="igro-badge igro-badge--warning">%(clock)s3&nbsp;дня до конца квартала</span>\n'
            '        </div>\n'
            '%(grid)s%(body)s'
            '        <div class="lab-ctx">\n%(boost)s        </div>\n'
            '      </section>\n') % dict(uid=uid, title=title, clock=ico("clock"), grid=grid, body=body, boost=BOOST)


def variant(n, name, idea):
    states = ""
    for st in STATES:
        uid = "v%d-%s" % (n, st)
        states += '    <div class="lab-state" data-lab-state="%s"%s>\n%s    </div>\n' % (st, "" if st == DEFAULT else " hidden", section(n, st, uid))
    return ('  <section class="lab-variant" id="v%(n)d" aria-labelledby="v%(n)d-name">\n'
            '    <header class="lab-variant__head">\n'
            '      <span class="lab-variant__num" aria-hidden="true">%(nn)02d</span>\n'
            '      <div class="lab-variant__text">\n'
            '        <h2 class="igro-h3 lab-variant__title" id="v%(n)d-name"><span class="igro-sr-only">Вариант %(n)d. </span>%(name)s</h2>\n'
            '        <p class="lab-variant__idea">%(idea)s</p>\n'
            '      </div>\n'
            '    </header>\n%(states)s  </section>\n') % dict(n=n, nn=n, name=name, idea=idea, states=states)


def proto_bar():
    opts = "".join('<option value="%s"%s>%s</option>' % (st, " selected" if st == DEFAULT else "", STATUS[st]["name"]) for st in STATES)
    return chr(10).join([
        '<div class="lk-proto lk-no-print">',
        '  <div class="lk-proto__inner">',
        '    <span class="lk-proto__tag">Прототип · тест</span>',
        '    <label class="lk-proto__label" for="labStatus">Статус участника</label>',
        '    <select class="lk-proto__select" id="labStatus">%s</select>' % opts,
        '    <label class="lk-proto__label" for="labCtx">Показать</label>',
        '    <select class="lk-proto__select" id="labCtx"><option value="full" selected>Весь блок профиля</option><option value="only">Только уровни</option></select>',
        '    <span class="lk-proto__note">Тестовая страница, на сайт не выводится</span>',
        '  </div>',
        '</div>'])


def page():
    toc = "".join('<li><a class="lab-toc__link" href="#v%d"><span class="lab-toc__num">%02d</span>%s</a></li>' % (n, n, name)
                  for n, (name, _i) in enumerate(VARIANTS, 1))
    body = "".join(variant(n, name, idea) for n, (name, idea) in enumerate(VARIANTS, 1))
    return """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Блок уровней – 10 вариантов – IGRObeauty</title>
<link rel="stylesheet" href="design-system-v6/styles.css">
<link rel="stylesheet" href="css/components.css">
<link rel="stylesheet" href="css/lk.css">
<link rel="stylesheet" href="css/lab-ladder.css">
<script src="js/lk.js" defer></script>
<script src="js/lab-ladder.js" defer></script>
</head>
<body class="igro" data-lab-ctx="full">
<!-- Собрано tools/build_ladder_lab.py: 10 вариантов блока уровней клуба. Тестовая страница; правки вносить в генератор. -->
%(sprite)s
%(proto)s
%(nav)s
  <main class="lk-main" id="main" tabindex="-1">
  <header class="lab-intro">
    <h1 class="igro-h1 lab-intro__title">Блок уровней клуба – 10 вариантов</h1>
    <p class="lab-intro__lead">Сейчас уровни стоят лестницей: плитки разной высоты и метки над ними ломают ровную блочную сетку профиля.
    Ниже – 10 вариантов того же блока в рамках DS v6.1, на тех же данных. Полоса сверху меняет статус участника
    и показывает вариант внутри блока «Перейти на следующий уровень» целиком или только сами уровни.</p>
    <nav aria-label="Варианты"><ol class="lab-toc">%(toc)s</ol></nav>
  </header>
%(body)s  </main>
</div>

<div class="lk-toasts" id="toasts"></div>
</body>
</html>
""" % dict(sprite=SPRITE, proto=proto_bar(), nav=NAV.replace(' aria-current="page"', ""), toc=toc, body=body)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    html = page().replace("\r\n", "\n").replace("\n", "\r\n")
    with open(os.path.join(ROOT, "lab-ladder.html"), "w", encoding="utf-8", newline="") as f:
        f.write(html)
    print("lab-ladder.html: %d вариантов × %d статусов" % (len(VARIANTS), len(STATES)))


if __name__ == "__main__":
    main()
