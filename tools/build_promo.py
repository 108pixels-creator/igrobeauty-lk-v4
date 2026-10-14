# -*- coding: utf-8 -*-
"""Раздел «Акции» (promo.html и promo-<код>.html) — копия раздела действующего сайта
https://igrobeauty.ru/personal/promo/ (снят 13.10.2026 в авторизованном кабинете) в оформлении DS v6.1.

Запуск из LK v6:  python tools/build_promo.py

Что взято с сайта: 22 акции в том же порядке, названия, картинки и тексты условий дословно
(поправлена только типографика: кавычки «», короткое тире, неразрывные пробелы, «1351р.» → «1 351 ₽»).
Ссылки «Перейти» ведут в каталог действующего сайта. У четырёх «Стартовых наборов» на странице акции
вместо текста — вертикальный плакат 1305×1819; у трёх акций страница — одна картинка без текста.
Картинки: если в assets/promo/ есть локальная копия (<код>.webp, у плакатов <код>-poster.webp),
берётся она, иначе — ссылка на файл на igrobeauty.ru.
Битрикс: список — компонент списка инфоблока, страница акции — детальная страница; блоки условий —
из поля «Детальное описание», ссылки «Перейти» — в каталог.
Файлы пишутся с CRLF, как остальные страницы.
"""
import html
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = "https://igrobeauty.ru"
NB = " "
NOTES = ["Уточняйте при оформлении заказа", "Данная акция только для Москвы и МО"]
CONSUMABLES = "Скидка 25% на одноразовые расходные материалы для парикмахерского зала и косметолгии IGRObeauty"
GLOVES = "/catalog/odnorazovaya_produktsiya_1/perchatki_odnorazovye_i_narukavniki/"

# blocks: ("p", текст) · ("deal", крупная строка скидки) · ("ul", [пункты]) · ("ul-links", [(текст, ссылка)])
PROMOS = [
    dict(slug="aktsiya-na-krasitel-nature-10-2", title="Акция на краситель Nature 10 + 2", img="/upload/iblock/416/g68q1h8indoyp72w0fkk3i0aoa03eb9b.jpg",
         blocks=[("p", "При покупке 10 красителей NATURE 100" + NB + "мл + 2 красителя в подарок")],
         links=[("Каталог NATURE", "/catalog/dlya_volos/okrashivanie_volos/bivalentnyy_krasitel_nature/")], notes=NOTES),
    dict(slug="aktsiya-na-krasitel-artx-10-2", title="Акция на краситель ARTX 10 + 2", img="/upload/iblock/7e2/drv0jpnsoqh2rjsbva1h4ja93ipel0ft.jpg",
         blocks=[("p", "При покупке 10 красителей ARTX 100" + NB + "мл + 2 красителя в подарок")],
         links=[("Каталог ARTX", "/catalog/dlya_volos/okrashivanie_volos/permanentnyy_krasitel_artx/")], notes=NOTES),
    dict(slug="startovyy-nabor-s-krasitelem-nature", title="Стартовый набор с красителем NATURE", img="/upload/iblock/555/zv2jmx2bors8r8nvep3m2ydg4ff40zwo.jpg",
         poster="/upload/iblock/129/aa9w3ix3tyaw3ar5w679ca4xmom8wbrb.jpg"),
    dict(slug="startovyy-nabor-kosmetologa-levissime", title="Стартовый набор косметолога LevisSime", img="/upload/iblock/359/lfvzy9fz6pfial85ug2mpi8tk5wum6b3.jpg",
         poster="/upload/iblock/d52/j2gnirvis9xpxiwd336mwti97ql7qq07.jpg"),
    dict(slug="startovyy-nabor-kosmetologa-depilflax", title="Стартовый набор косметолога Depilflax", img="/upload/iblock/85e/b9n82di4y52kk7jpwokm9ry1bgow059v.jpg",
         poster="/upload/iblock/438/xe7wdcejjhwyl673lam70636o046cq9y.jpg"),
    dict(slug="startovyy-nabor-kosmetologa-silver", title="Стартовый набор косметолога Silver", img="/upload/iblock/9a4/3azdduym94r2xhu4kiqx7c10kah5pbm1.jpg",
         poster="/upload/iblock/bcc/4hzspybjfhl7ppz3z10f4alvubdm5lr2.jpg"),
    dict(slug="skidka-na-krasitel-dlya-brovey-lashcolor-15", title="Скидка на краситель для бровей LashColor – 15%", img="/upload/iblock/2ee/22rgx0sft146l6gpg9th3d6hnknsix6k.jpg",
         blocks=[("p", "Скидка на краску Lash Color для бровей и ресниц."),
                 ("p", "При покупке 3-x любых цветов + Оксидант (1,8%) или 3% объем 90" + NB + "мл"),
                 ("deal", "СКИДКА НА НАБОР 15%")],
         links=[("Каталог Lash Color", "/catalog/brovi_i_resnitsy/krasitel_lashcolor/")], notes=NOTES),
    dict(slug="aktsiya-na-nabor-s-ukhodami-15", title="Акция на набор с уходами -15%", img="/upload/iblock/dd0/6avjn0oultxpnfwe3by3b0pfq4mjt1jq.jpg",
         blocks=[("p", "При покупке «Шампуня для объема волос Nirvel Professional Shampoo Volume & Texture Chitosan & Panthenol, 1000" + NB + "мл» "
                       "и «Спрея для объема волос Volume Spray BasiCare, Nirvel, 200" + NB + "мл»"),
                 ("deal", "СКИДКА 15% – стоимость набора 1" + NB + "351" + NB + "₽")],
         links=[("Шампуня для объема волос BASIC PRO", "/catalog/dlya_volos/ukhod_za_volosami/basic_pro/shampun_dlya_volos_s_khitozanom_i_pantenolom_chitosan_panthenol_nirvel_basic_pro_1000_ml/"),
                ("Спрей для объема волос Volume Spray BasiCare", "/catalog/dlya_volos/ukhod_za_volosami/basicare/dlya_obema_1/sprey_dlya_obema_volos_volume_spray_nirvel_200_ml_/")],
         notes=NOTES),
    dict(slug="aktsiya-na-ukhody-basic-pro-15", title="Акция на уходы Basic Pro – 15%", img="/upload/iblock/e6a/lus8kfelmh4s3mg7it6n8z3dls0pkn0q.jpg",
         blocks=[("p", "При покупке Шампуня 250" + NB + "мл, Кондиционера 250" + NB + "мл и Двухфазного спрей-кондиционера 200" + NB + "мл (в ассортименте) из линейки Basic Pro"),
                 ("deal", "СКИДКА 15%")],
         links=[("Каталог BASIC PRO", "/catalog/dlya_volos/ukhod_za_volosami/basic_pro/")], notes=NOTES),
    dict(slug="aktsiya-na-dvukhfaznyy-sprey-s-maslom-argany-2-1", title="Акция на двухфазный спрей с маслом арганы 2+1", img="/upload/iblock/758/fvmybvq07lvdw4e5cyoantm3p4co1b7e.jpg",
         blocks=[("p", "При покупке двух «Спрей двухфазный с маслом арганы Argan Biphase, Nirvel Professional, 250" + NB + "мл»"),
                 ("deal", "2 + 1 в ПОДАРОК")],
         links=[("Купить Argan Biphase", "/catalog/dlya_volos/vosstanovlenie_volos/programma_spa_ukhoda_za_volosami_s_arganovym_maslom/dvukhfaznyy_nesmyvaemyy_sprey_s_maslom_argany_d_uvlazhneniya_i_vosstanovleniya_volos_biphase_argan_n/")],
         notes=NOTES),
    dict(slug="skidka-na-vosk-v-kartridzhakh-starpil-15", title="Скидка на воск в картриджах Starpil -15%", img="/upload/iblock/62a/56p4bsreseo1c0cmi6t6xqq02ywmfvp7.jpg",
         blocks=[("p", "При покупке 20 картриджей воска Depilflax100 или Starpil"), ("deal", "СКИДКА 15%")],
         links=[("Картриджи Starpil", "/catalog/depilyatsiya/vosk_dlya_depilyatsii/vosk_v_kartridzhakh/?set_filter=y&searchFilter_3353_3729572004=Y")], notes=NOTES),
    dict(slug="skidka-na-vosk-v-kartridzhakh-depilflax-15", title="Скидка на воск в картриджах Depilflax -15%", img="/upload/iblock/5c5/7s89o3zsq0qc0037e3uogv08so59kljl.jpg",
         blocks=[("p", "При покупке 20 картриджей воска Depilflax100 или Starpil"), ("deal", "СКИДКА 15%")],
         links=[("Картриджи Depilflax100", "/catalog/depilyatsiya/vosk_dlya_depilyatsii/vosk_v_kartridzhakh/?set_filter=y&searchFilter_3353_2839649921=Y")], notes=NOTES),
    dict(slug="skidka-na-goryachiy-vosk-v-briketakh-starpil-15", title="Скидка на горячий воск в брикетах Starpil – 15%", img="/upload/iblock/7b1/492vpj433xa5nakdc2jw9rj42u38axjv.jpg",
         blocks=[("p", "При покупке трех пакетов горячего воска в брикетах DEPILFLAX100 и STARPIL 1000" + NB + "гр. (любой цвет на выбор)"), ("deal", "СКИДКА 15%")],
         links=[("Картриджи Starpil", "/catalog/depilyatsiya/vosk_dlya_depilyatsii/vosk_goryachiy_nizkotemperaturnyy_v_briketakh/?set_filter=y&searchFilter_3353_3729572004=Y")], notes=NOTES),
    dict(slug="skidka-na-goryachiy-vosk-v-briketakh-depilflax-15", title="Скидка на горячий воск в брикетах Depilflax – 15%", img="/upload/iblock/c92/x08yb5fhthiooiyxyi9nb3fbct6jn5yv.jpg",
         blocks=[("p", "При покупке трех пакетов горячего воска в брикетах DEPILFLAX100 и STARPIL 1000" + NB + "гр. (любой цвет на выбор)"), ("deal", "СКИДКА 15%")],
         links=[("Depilflax100", "/catalog/depilyatsiya/vosk_dlya_depilyatsii/vosk_goryachiy_nizkotemperaturnyy_v_briketakh/?set_filter=y&searchFilter_3353_2839649921=Y")], notes=NOTES),
    dict(slug="skidka-na-odnorazovye-prostyni-15", title="Скидка на одноразовые простыни – 15%", img="/upload/iblock/c08/9srdtw8x0bu9p17ikb1l6uz6tj20ytbi.jpg",
         blocks=[("p-strong", CONSUMABLES),
                 ("ul-links", [("Простыня 80 х 200 см, СМС, 20г/м2, Зеленый, в Рулоне с перфорацией, NUUMA, 75шт",
                                "/catalog/odnorazovaya_produktsiya_1/prostyni_odnorazovye/prostynya_80_kh_200_sm_sms_20g_m2_zelenyy_myatnyy_v_rulone_s_perforatsiey_nuuma_75sht/"),
                               ("Простыня 80 х 200 см, СМС, 20г/м2, Фиолетовый, в Рулоне с перфорацией, NUUMA 75шт",
                                "/catalog/odnorazovaya_produktsiya_1/prostyni_odnorazovye/prostynya_80_kh_200_sm_sms_20g_m2_fioletovyy_v_rulone_s_perforatsiey_nuuma_75sht/")])],
         links=[], notes=NOTES),
    dict(slug="skidka-na-polotentsa-i-folgu-15", title="Скидка на полотенца и фольгу – 15%", img="/upload/iblock/16f/padccykbkyd2ue3bf0lnt08zwucpzjpq.jpg"),
    dict(slug="skidka-na-nirvel-rizos", title="Скидка на Nirvel Rizos", img="/upload/iblock/a3f/ka4v4og613k2mpad44o4iikgg4fw3i4z.jpg"),
    dict(slug="skidka-na-polotentsa-15", title="Скидка на полотенца 15%", img="/upload/iblock/7cf/7pos73gmpdjd60glkaqcc94519mzgkpk.jpg"),
    dict(slug="skidka-na-perchatki-matrix-benovy-25", title="Скидка на перчатки MATRIX BENOVY 25%", img="/upload/iblock/bf7/jx7jspp1gdfbhoy3jinubiwwuobnp6ox.jpg",
         blocks=[("p-strong", CONSUMABLES), ("ul", ["Перчатки неопудренные, текстурированные, латекс 5,2 гр, полимерное покрытие, S, M, L"])],
         links=[("Каталог IGRObeauty", GLOVES)], notes=NOTES),
    dict(slug="skidka-na-perchatki-25", title="Скидка на перчатки 25%", img="/upload/iblock/79c/1hpgqtuu07d9m2go4v62siw0bwl4lkry.jpg",
         blocks=[("p-strong", CONSUMABLES), ("ul", ["Перчатки НИТРИЛОВЫЕ, цвет ГОЛУБОЙ, размеры S-M", "Перчатки НИТРИЛОВЫЕ, цвет в ассортименте, все размеры"])],
         links=[("Каталог IGRObeauty", GLOVES)], notes=NOTES),
    dict(slug="skidka-na-perchatki-nitrilovye-25", title="Скидка на перчатки нитриловые – 25%", img="/upload/iblock/28d/3wkzidqk8m00wocugy0kofkukclkwpwk.jpg",
         blocks=[("p-strong", CONSUMABLES)], links=[("Каталог IGRObeauty", GLOVES)], notes=NOTES),
    dict(slug="skidka-na-perchatki-neopudrennye-25", title="Скидка на перчатки неопудренные – 25%", img="/upload/iblock/77f/dc4u9l5fdq1qh94ereu0hm5yma3fb9jn.jpg",
         blocks=[("p-strong", CONSUMABLES)], links=[("Каталог IGRObeauty", GLOVES)], notes=NOTES),
]

E = html.escape


def icon(name, size=None, cls=""):
    c = "igro-icon" + (" igro-icon--%s" % size if size else "") + (" " + cls if cls else "")
    return '<svg class="%s" aria-hidden="true" focusable="false"><use href="#i-%s"></use></svg>' % (c, name)


def plural(n, one, few, many):
    if n % 10 == 1 and n % 100 != 11:
        return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        return few
    return many


def src(slug, live_path, poster=False):
    local = "assets/promo/%s%s.webp" % (slug, "-poster" if poster else "")
    return local if os.path.isfile(os.path.join(ROOT, local)) else LIVE + live_path


SPRITE = '''<svg class="lk-sprite" aria-hidden="true" focusable="false" xmlns="http://www.w3.org/2000/svg">
  <symbol id="i-arrow-right" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>
  <symbol id="i-chevron-left" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></symbol>
  <symbol id="i-education" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5l8 3.5-8 3.5-8-3.5L12 5z"/><path d="M6 11v4.2c0 1 2.7 2.3 6 2.3s6-1.3 6-2.3V11"/></symbol>
  <symbol id="i-heart" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20s-7-4.35-7-9.5A3.5 3.5 0 0 1 12 7a3.5 3.5 0 0 1 7 3.5C19 15.65 12 20 12 20z"/></symbol>
  <symbol id="i-info" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></symbol>
  <symbol id="i-logout" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5H7a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h8"/><path d="M18 15l3-3-3-3M10 12h11"/></symbol>
  <symbol id="i-orders" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4.5h6a1 1 0 0 1 1 1V7H8V5.5a1 1 0 0 1 1-1zM9 12h6M9 16h4"/></symbol>
  <symbol id="i-promo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 12.6V5a1.5 1.5 0 0 1 1.5-1.5h7.6a1.5 1.5 0 0 1 1.06.44l7.4 7.4a1.5 1.5 0 0 1 0 2.12l-7.6 7.6a1.5 1.5 0 0 1-2.12 0l-7.4-7.4a1.5 1.5 0 0 1-.44-1.06z"/><circle cx="8.5" cy="8.5" r="1.5"/></symbol>
  <symbol id="i-user" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="3.5"/><path d="M5 20c0-3.5 3.1-5.5 7-5.5s7 2 7 5.5"/></symbol>
  <symbol id="i-user-circle" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="10" r="2.5"/><path d="M7.5 17.5c.6-2 2.4-3 4.5-3s3.9 1 4.5 3"/></symbol>
</svg>'''

def nav():
    items = [("index.html", "user", "Мой профиль"), ("orders.html", "orders", "Мои заказы"), ("favorites.html", "heart", "Избранное"),
             ("promo.html", "promo", "Акции"), ("education.html", "education", "Мое обучение"), ("data.html", "user-circle", "Мои данные")]
    lis = "".join('      <li><a class="lk-nav__item" href="%s"%s>%s<span class="lk-nav__label">%s</span></a></li>\n'
                  % (h, ' aria-current="page"' if h == "promo.html" else "", icon(i), t) for h, i, t in items)
    return ('<a class="igro-btn igro-btn--dark lk-skip" href="#main">Перейти к содержимому</a>\n<div class="lk-shell">\n  <aside class="lk-aside">\n'
            '    <nav class="igro-card lk-nav" aria-label="Личный кабинет">\n      <ul class="lk-nav__list">\n' + lis +
            '      <li class="lk-nav__divider" aria-hidden="true"></li>\n'
            '      <li><a class="lk-nav__item" href="#logout">%s<span class="lk-nav__label">Выйти</span></a></li>\n'
            '      </ul>\n    </nav>\n  </aside>' % icon("logout"))


def page(title, main):
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)} — IGRObeauty</title>
<link rel="stylesheet" href="design-system-v6/styles.css">
<link rel="stylesheet" href="css/components.css">
<link rel="stylesheet" href="css/lk.css">
<script src="js/lk.js" defer></script>
</head>
<body class="igro">
<!-- Собрано tools/build_promo.py. Правки вносить в генератор. -->
{SPRITE}
{nav()}
  <main class="lk-main" id="main" tabindex="-1">
{main}  </main>
</div>
<div class="lk-toasts" id="toasts"></div>
</body>
</html>
'''


def list_page():
    n = len(PROMOS)
    cards = "".join(
        '      <li><a class="lk-promo" href="promo-%s.html"><span class="lk-promo__media"><img class="lk-promo__img" src="%s" alt="" width="1000" height="625" loading="lazy"></span>'
        '<span class="lk-promo__title">%s</span></a></li>\n' % (p["slug"], src(p["slug"], p["img"]), E(p["title"])) for p in PROMOS)
    main = f'''    <h1 class="igro-h1 lk-title lk-title--with-lead">Акции</h1>
    <p class="lk-lead">Сейчас {plural(n, "действует", "действуют", "действуют")} {n} {plural(n, "акция", "акции", "акций")}</p>
    <ul class="lk-promo-grid">
{cards}    </ul>
'''
    return page("Акции", main)


def block(b):
    kind, val = b
    if kind == "p":
        return '<p>%s</p>' % E(val)
    if kind == "p-strong":
        return '<p class="lk-promo-terms__lead">%s</p>' % E(val)
    if kind == "deal":
        return '<p class="lk-promo-terms__deal">%s</p>' % E(val)
    if kind == "ul":
        return '<ul class="lk-promo-terms__list">%s</ul>' % "".join("<li>%s</li>" % E(x) for x in val)
    if kind == "ul-links":
        return '<ul class="lk-promo-terms__list">%s</ul>' % "".join(
            '<li><a class="lk-promo-link" href="%s">%s%s</a></li>' % (E(LIVE + u), E(t), icon("arrow-right", 18)) for t, u in val)
    raise ValueError(kind)


def detail_page(p):
    blocks = p.get("blocks")
    if p.get("poster"):
        mod, img, w, h = " lk-promo-doc--poster", src(p["slug"], p["poster"], True), 1305, 1819
    elif not blocks:
        mod, img, w, h = " lk-promo-doc--image", src(p["slug"], p["img"]), 1000, 625
    else:
        mod, img, w, h = "", src(p["slug"], p["img"]), 1000, 625
    # на плакате мелкая таблица цен — открыть его целиком в новой вкладке
    full = ('      <p class="lk-promo-doc__full"><a class="lk-promo-link" href="%s" target="_blank" rel="noopener">Открыть плакат целиком%s</a></p>\n'
            % (img, icon("arrow-right", 18))) if p.get("poster") else ""
    terms = ""
    if blocks:
        body = "\n".join("          " + block(b) for b in blocks)
        links = ""
        if p.get("links"):
            links = '        <ul class="lk-promo-terms__links">%s</ul>\n' % "".join(
                '<li><a class="lk-promo-link" href="%s">%s%s</a></li>' % (E(LIVE + u), E(t), icon("arrow-right", 18)) for t, u in p["links"])
        notes = ""
        if p.get("notes"):
            notes = ('        <div class="igro-alert lk-promo-terms__note" role="note">%s<div class="igro-alert__body"><div class="igro-alert__text">%s</div></div></div>\n'
                     % (icon("info", 24, "igro-alert__icon"), "<br>".join(E(x) for x in p["notes"])))
        terms = f'''      <section class="igro-card lk-promo-terms" aria-labelledby="promo-terms">
        <h2 class="lk-promo-terms__title" id="promo-terms">Условия</h2>
        <div class="lk-promo-terms__body">
{body}
        </div>
{links}{notes}      </section>
'''
    main = f'''    <nav class="igro-breadcrumb lk-crumbs" aria-label="Навигационная цепочка">
      <ol><li><a href="promo.html">Акции</a></li><li><span aria-current="page">{E(p["title"])}</span></li></ol>
    </nav>
    <h1 class="igro-h1 lk-title">{E(p["title"])}</h1>
    <div class="lk-promo-doc{mod}">
      <div class="lk-promo-doc__media"><img class="lk-promo-doc__img" src="{img}" alt="{E(p["title"])}" width="{w}" height="{h}"></div>
{full}{terms}    </div>
    <p class="lk-promo-doc__back"><a class="igro-btn igro-btn--secondary" href="promo.html">{icon("chevron-left")}Все акции</a></p>
'''
    return page(p["title"], main)


def write(name, text):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="") as f:
        f.write(text.replace("\r\n", "\n").replace("\n", "\r\n"))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    write("promo.html", list_page())
    for p in PROMOS:
        write("promo-%s.html" % p["slug"], detail_page(p))
    local = sum(1 for p in PROMOS if not src(p["slug"], p["img"]).startswith("http"))
    print("promo.html + %d страниц акций; картинок локально: %d из %d" % (len(PROMOS), local, len(PROMOS)))


if __name__ == "__main__":
    main()
