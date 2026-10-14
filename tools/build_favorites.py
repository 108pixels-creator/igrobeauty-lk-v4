# -*- coding: utf-8 -*-
"""Страница «Избранное» (favorites.html): карточки как в каталоге v5 + сердечко, удаление, подборки.

Запуск из LK v6:  python tools/build_favorites.py
Карточка повторяет каталог v5 (igro-design-pages/catalog/v5, render.js cardHTML и styles.css .ig-card,
макет Figma «IB – my DESIGN», узел 2481:2340): картинка 208×220, бренд, серия (линия), название,
«Арт: …», цена 20 px с подписью «Проф. цена», кнопка 44 px во всю ширину → счётчик «− 1 +», «нет в наличии».
Поле под фото белое (13.10): серое #F5F5F5 в макете — заглушка вместо фото, сами фото — на белом.
Бренд — как в справочнике каталога v5 (поле g), серия — оттуда же (поле l). Бренд и серия — одной строкой
«NIRVEL PROFESSIONAL · ArtX»; не влезает в ширину карточки — серия целиком переносится на новую строку (13.10).
Добавлено для ЛК: сердечко в правом верхнем углу (активно; при наведении превращается в корзину;
по нажатию — окно «Убрать из избранного?»). Отдельной кнопки удаления у корзины нет (13.10).
«Отправить в корзину» в шапке (13.10) — кладёт в корзину всё, что сейчас на экране: выбранную подборку
с учётом фильтров; «нет в наличии» пропускается, уже добавленные товары не меняются.
Подборки: по умолчанию одна — «Все товары»; можно создать новую, переключаться, удалить (кроме основной).
Демо: подборка «Для кабинета» из трёх товаров. Поведение — js/lk.js, initFavorites.
Файл пишется с CRLF, как остальные страницы v5.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB = "&nbsp;"

# порядок — по дате добавления, новые сверху (БТ)
ITEMS = [
    dict(img="levissime", brand="Levissime", line="", name="Маска альгинатная, 500" + NB + "г", art="65112", price="2" + NB + "700", cat="Уход за лицом", type="Маска", use="Для салона", colls="c1"),
    dict(img="nirvel", brand="Nirvel Professional", line="ArtX", name="Pastel ArtX, серебристый, 100" + NB + "мл", art="14003", price="1" + NB + "080", cat="Окрашивание", type="Краска", use="Для салона", colls=""),
    dict(img="iuver", brand="Iuver", line="", name="Флюид увлажняющий для волос, 150" + NB + "мл", art="72840", price="2" + NB + "385", cat="Уход за волосами", type="Флюид", use="Для домашнего ухода", colls=""),
    dict(img="lashcolor", brand="Levissime", line="Lash Color", name="Воск плёночный в гранулах, 100" + NB + "г", art="31596", price="396", cat="Депиляция", type="Воск", use="Для салона", colls="c1"),
    dict(img="refectocil", brand="RefectoCil", line="RefectoCil", name="Краска для бровей и ресниц №" + NB + "3.1, 15" + NB + "мл", art="15277", price="765", cat="Брови и ресницы", type="Краска", use="Для салона", colls="c1"),
    dict(img="soleo", brand="Soleo", line="Classic", name="Lolli Pop, ускоритель загара, 150" + NB + "мл", art="20775", price="558", cat="Загар", type="Крем", use="Для домашнего ухода", colls="", out=True),
    dict(img="levis-hydrage", brand="Levissime", line="Hydrage", name="Hydrage, крем увлажняющий, 50" + NB + "мл", art="48310", price="1" + NB + "188", cat="Уход за лицом", type="Крем", use="Для домашнего ухода", colls=""),
    dict(img="levis-younglife", brand="Levissime", line="Glass skin", name="Young Life, крем для лица, 50" + NB + "мл", art="15290", price="1" + NB + "710", cat="Уход за лицом", type="Крем", use="Для салона", colls="", out=True),
]
COLLS = [("all", "Все товары"), ("c1", "Для кабинета")]


def icon(name, size=None, cls=""):
    c = "igro-icon" + (" igro-icon--%s" % size if size else "") + (" " + cls if cls else "")
    return '<svg class="%s" aria-hidden="true" focusable="false"><use href="#i-%s"></use></svg>' % (c, name)


def plain(s):
    return s.replace(NB, " ").replace("&nbsp;", " ")


def line(it):
    if not it["line"]:
        return ""
    return '<span class="lk-pcard__line" title="%s"><span class="lk-pcard__line-text">%s</span></span>' % (it["line"], it["line"])


def card(it):
    full = "%s %s" % (it["brand"], it["name"])
    if it.get("out"):
        action = '<div class="lk-pcard__nostock">%s<span>нет в наличии</span></div>' % icon("close", 18)
    else:
        action = '<button type="button" class="lk-pcard__btn" data-cart-add aria-label="В корзину: %s">В корзину</button>' % plain(full)
    return f'''      <li data-item data-brand="{it["brand"]}" data-cat="{it["cat"]}" data-type="{it["type"]}" data-use="{it["use"]}" data-colls="{it["colls"]}">
        <article class="lk-pcard" aria-label="{plain(full)}">
          <div class="lk-pcard__media">
            <img class="lk-pcard__img" src="assets/products/{it["img"]}.webp" alt="{plain(full)}" width="208" height="220" loading="lazy">
            <button type="button" class="lk-pcard__fav" aria-pressed="true" aria-label="В избранном. Убрать из избранного: {plain(full)}" data-fav-heart>{icon("heart-fill", 24, "lk-pcard__fav-heart")}{icon("trash", 24, "lk-pcard__fav-trash")}</button>
          </div>
          <div class="lk-pcard__body">
            <div class="lk-pcard__brandline"><span class="lk-pcard__brand">{it["brand"]}</span>{line(it)}</div>
            <h2 class="lk-pcard__name"><a href="#product">{it["name"]}</a></h2>
            <div class="lk-pcard__art">Арт:{NB}{it["art"]}</div>
            <div class="lk-pcard__pricerow"><span class="lk-pcard__price" data-price="{it["price"].replace(NB, "")}">{it["price"]}{NB}₽</span><span class="lk-pcard__pricenote">Проф.{NB}цена</span></div>
          </div>
          <div class="lk-pcard__controls">{action}</div>
        </article>
      </li>
'''


def colls_nav():
    out = ""
    for cid, name in COLLS:
        n = len(ITEMS) if cid == "all" else sum(1 for i in ITEMS if cid in i["colls"].split())
        on = cid == "all"
        btn = ('<button type="button" class="lk-coll%s" aria-pressed="%s" data-coll="%s"><span class="lk-coll__name">%s</span>'
               '<span class="lk-coll__count">%d</span></button>' % (" is-active" if on else "", "true" if on else "false", cid, name, n))
        dele = "" if cid == "all" else ('<button type="button" class="lk-coll__del" aria-label="Удалить подборку «%s»" data-coll-del="%s">%s</button>'
                                         % (name, cid, icon("close", 18)))
        out += '        <li class="lk-colls__item">%s%s</li>\n' % (btn, dele)
    return out


SELECT = '''      <div class="igro-select" data-dropdown><div class="igro-select__control"><label class="igro-select__label" for="{id}">{label}</label><select class="igro-select__input" id="{id}" name="{key}" data-key="{key}"><option value="all" selected>{all}</option>{opts}</select>{chev}</div></div>
'''


def select(id_, key, label, all_, values):
    return SELECT.format(id=id_, key=key, label=label, all=all_, opts="".join("<option>%s</option>" % v for v in values),
                         chev=icon("chevron-down", cls="igro-select__chevron"))


SPRITE = '''<svg class="lk-sprite" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">
  <symbol id="i-cart" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 4h2l2.2 10.2a1.5 1.5 0 0 0 1.5 1.2h8.6a1.5 1.5 0 0 0 1.5-1.1L20.5 8H6"/><circle cx="9.5" cy="19.5" r="1.3"/><circle cx="17" cy="19.5" r="1.3"/></symbol>
  <symbol id="i-chevron-down" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></symbol>
  <symbol id="i-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 6l12 12M18 6L6 18"/></symbol>
  <symbol id="i-education" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5l8 3.5-8 3.5-8-3.5L12 5z"/><path d="M6 11v4.2c0 1 2.7 2.3 6 2.3s6-1.3 6-2.3V11"/></symbol>
  <symbol id="i-heart" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20s-7-4.35-7-9.5A3.5 3.5 0 0 1 12 7a3.5 3.5 0 0 1 7 3.5C19 15.65 12 20 12 20z"/></symbol>
  <symbol id="i-heart-fill" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20s-7-4.35-7-9.5A3.5 3.5 0 0 1 12 7a3.5 3.5 0 0 1 7 3.5C19 15.65 12 20 12 20z"/></symbol>
  <symbol id="i-info" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></symbol>
  <symbol id="i-logout" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5H7a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h8"/><path d="M18 15l3-3-3-3M10 12h11"/></symbol>
  <symbol id="i-minus" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/></symbol>
  <symbol id="i-orders" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4.5h6a1 1 0 0 1 1 1V7H8V5.5a1 1 0 0 1 1-1zM9 12h6M9 16h4"/></symbol>
  <symbol id="i-plus" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></symbol>
  <symbol id="i-trash" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 7h14M9 7V5h6v2M7 7l1 13h8l1-13"/></symbol>
  <symbol id="i-user" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="3.5"/><path d="M5 20c0-3.5 3.1-5.5 7-5.5s7 2 7 5.5"/></symbol>
  <symbol id="i-promo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 12.6V5a1.5 1.5 0 0 1 1.5-1.5h7.6a1.5 1.5 0 0 1 1.06.44l7.4 7.4a1.5 1.5 0 0 1 0 2.12l-7.6 7.6a1.5 1.5 0 0 1-2.12 0l-7.4-7.4a1.5 1.5 0 0 1-.44-1.06z"/><circle cx="8.5" cy="8.5" r="1.5"/></symbol>
  <symbol id="i-user-circle" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="10" r="2.5"/><path d="M7.5 17.5c.6-2 2.4-3 4.5-3s3.9 1 4.5 3"/></symbol>
</svg>'''


def nav():
    items = [("index.html", "user", "Мой профиль"), ("orders.html", "orders", "Мои заказы"), ("favorites.html", "heart", "Избранное"),
             ("promo.html", "promo", "Акции"), ("education.html", "education", "Мое обучение"), ("data.html", "user-circle", "Мои данные")]
    lis = "".join('      <li><a class="lk-nav__item" href="%s"%s>%s<span class="lk-nav__label">%s</span></a></li>\n'
                  % (h, ' aria-current="page"' if h == "favorites.html" else "", icon(i), t) for h, i, t in items)
    return ('<a class="igro-btn igro-btn--dark lk-skip" href="#main">Перейти к содержимому</a>\n<div class="lk-shell">\n  <aside class="lk-aside">\n'
            '    <nav class="igro-card lk-nav" aria-label="Личный кабинет">\n      <ul class="lk-nav__list">\n' + lis +
            '      <li class="lk-nav__divider" aria-hidden="true"></li>\n'
            '      <li><a class="lk-nav__item" href="#logout">%s<span class="lk-nav__label">Выйти</span></a></li>\n'
            '      </ul>\n    </nav>\n  </aside>' % icon("logout"))


def page():
    brands = sorted({i["brand"] for i in ITEMS}, key=str.lower)
    cats = ["Уход за лицом", "Уход за волосами", "Окрашивание", "Брови и ресницы", "Депиляция", "Загар"]
    types = ["Крем", "Маска", "Флюид", "Краска", "Воск"]
    uses = ["Для салона", "Для домашнего ухода"]
    filters = (select("ff-brand", "brand", "Бренд", "Все бренды", brands) + select("ff-cat", "cat", "Категория", "Все категории", cats) +
               select("ff-type", "type", "Тип продукта", "Все типы", types) + select("ff-use", "use", "Назначение", "Любое", uses))
    cards = "".join(card(i) for i in ITEMS)
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Избранное — IGRObeauty</title>
<link rel="stylesheet" href="design-system-v6/styles.css">
<link rel="stylesheet" href="css/components.css">
<link rel="stylesheet" href="css/lk.css">
<script src="js/lk.js" defer></script>
</head>
<body class="igro">
<!-- Собрано tools/build_favorites.py. Правки вносить в генератор. -->
{SPRITE}
{nav()}
  <main class="lk-main" id="main" tabindex="-1">
    <div class="lk-fav-head">
      <div class="lk-fav-head__titles">
        <h1 class="igro-h1 lk-title lk-title--with-lead">Избранное</h1>
        <p class="lk-lead" id="fav-count" aria-live="polite">У вас {len(ITEMS)} товаров в избранном</p>
      </div>
      <button type="button" class="igro-btn igro-btn--primary lk-fav-head__cart" data-fav-to-cart>{icon("cart")}Отправить в корзину</button>
    </div>

    <nav class="lk-colls" aria-label="Подборки избранного">
      <ul class="lk-colls__list" id="favColls">
{colls_nav()}      </ul>
      <button type="button" class="igro-btn igro-btn--ghost igro-btn--sm lk-colls__add" data-coll-add>{icon("plus")}Новая подборка</button>
    </nav>

    <form class="lk-filters lk-filters--4" id="fav-filters" aria-label="Фильтры избранного" data-filter="#fav-grid" data-filter-empty="#fav-filter-empty">
{filters}    </form>
    <ul class="lk-pgrid" id="fav-grid">
{cards}    </ul>
    <div class="igro-empty lk-filter-empty" id="fav-filter-empty" hidden>
      <span class="igro-empty__icon">{icon("heart")}</span>
      <p class="igro-empty__title">Ничего не нашлось</p>
      <p class="igro-empty__text">Под эти фильтры нет товаров. Измените их или сбросьте.</p>
      <div class="igro-empty__action"><button type="button" class="igro-btn igro-btn--dark" data-filter-reset="#fav-filters">Сбросить фильтры</button></div>
    </div>
    <div class="igro-empty" id="fav-coll-empty" hidden>
      <span class="igro-empty__icon">{icon("heart")}</span>
      <p class="igro-empty__title">В подборке пока нет товаров</p>
      <p class="igro-empty__text">Здесь появятся товары, которые вы добавите в эту подборку.</p>
    </div>
    <div class="igro-empty" id="fav-empty" hidden>
      <span class="igro-empty__icon">{icon("heart")}</span>
      <p class="igro-empty__title">В избранном пока пусто</p>
      <p class="igro-empty__text">Нажмите на сердечко в каталоге – товар появится здесь.</p>
    </div>
    <div class="lk-fav-hint"><div class="igro-alert" role="status"><svg class="igro-icon igro-icon--24 igro-alert__icon" aria-hidden="true" focusable="false"><use href="#i-info"></use></svg><div class="igro-alert__body"><div class="igro-alert__text">Вы можете добавить до 100 товаров в избранное</div></div></div></div>
  </main>
</div>

<div class="igro-dialog-scrim" id="favConfirm" hidden>
  <div class="igro-dialog lk-confirm" role="alertdialog" aria-modal="true" aria-labelledby="favConfirmTitle" aria-describedby="favConfirmSub" tabindex="-1">
    <div class="igro-dialog__head">
      <div class="igro-dialog__titles"><h2 class="igro-dialog__title" id="favConfirmTitle">Убрать из избранного?</h2><p class="igro-dialog__subtitle" id="favConfirmSub"></p></div>
      <button type="button" class="igro-dialog__close" aria-label="Закрыть" data-dialog-close>{icon("close")}</button>
    </div>
    <div class="igro-dialog__footer">
      <button type="button" class="igro-btn igro-btn--danger igro-btn--lg igro-dialog__primary" id="favConfirmOk">Убрать</button>
      <button type="button" class="igro-btn igro-btn--secondary igro-btn--lg igro-dialog__secondary" data-dialog-close>Отмена</button>
    </div>
  </div>
</div>

<div class="igro-dialog-scrim" id="collDialog" hidden>
  <div class="igro-dialog lk-confirm" role="dialog" aria-modal="true" aria-labelledby="collDialogTitle" tabindex="-1">
    <div class="igro-dialog__head">
      <div class="igro-dialog__titles"><h2 class="igro-dialog__title" id="collDialogTitle">Новая подборка</h2></div>
      <button type="button" class="igro-dialog__close" aria-label="Закрыть" data-dialog-close>{icon("close")}</button>
    </div>
    <div class="igro-dialog__body">
      <form id="collForm" novalidate>
        <div class="igro-field"><div class="igro-field__control"><input class="igro-field__input" id="collName" name="collName" type="text" value="" placeholder=" " required maxlength="40" autocomplete="off" aria-describedby="collName-hint"><label class="igro-field__label" for="collName">Название подборки<b class="igro-field__req" aria-hidden="true">*</b></label></div><p class="igro-field__hint" id="collName-hint" data-default="Например, «Для кабинета» или «Заказ на осень»">Например, «Для кабинета» или «Заказ на осень»</p></div>
      </form>
    </div>
    <div class="igro-dialog__footer">
      <button type="submit" class="igro-btn igro-btn--primary igro-btn--lg igro-dialog__primary" form="collForm">Создать подборку</button>
      <button type="button" class="igro-btn igro-btn--secondary igro-btn--lg igro-dialog__secondary" data-dialog-close>Отмена</button>
    </div>
  </div>
</div>

<div class="lk-toasts" id="toasts"></div>
</body>
</html>
'''


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    html = page().replace("\r\n", "\n").replace("\n", "\r\n")
    with open(os.path.join(ROOT, "favorites.html"), "w", encoding="utf-8", newline="") as f:
        f.write(html)
    print("favorites.html: %d товаров, подборок %d" % (len(ITEMS), len(COLLS)))


if __name__ == "__main__":
    main()
