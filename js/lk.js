/* ==========================================================================
   IGRObeauty — Личный кабинет v5 · behaviour for the DS v6.1 class layer.
   Keyboard and ARIA patterns follow readme §7 (Tabs, Accordion, Dialog,
   Autocomplete, forms) and the WAI-ARIA select-only combobox. No dependencies.
   ========================================================================== */
(function () {
  "use strict";

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };
  var isShown = function (el) { return !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length); };
  var isSheetWidth = function () { return window.matchMedia("(max-width: 767px)").matches; };
  var CLOSE_SVG = '<svg class="igro-icon igro-icon--18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true" focusable="false"><path d="M6 6l12 12M18 6L6 18"/></svg>';

  function plural(n, one, few, many) {
    var n10 = n % 10, n100 = n % 100;
    if (n10 === 1 && n100 !== 11) return one;
    if (n10 >= 2 && n10 <= 4 && (n100 < 12 || n100 > 14)) return few;
    return many;
  }
  function svgIcon(name, size) {
    return '<svg class="igro-icon' + (size ? " igro-icon--" + size : "") + '" aria-hidden="true" focusable="false"><use href="#i-' + name + '"></use></svg>';
  }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; });
  }

  /* Page scroll lock shared by dialogs and bottom sheets */
  var locks = 0;
  function lockScroll(on) {
    locks = Math.max(0, locks + (on ? 1 : -1));
    document.documentElement.classList.toggle("igro-scroll-locked", locks > 0);
  }

  /* ---------------------------------------------------------------- Tabs (DS Tabs)
     Roving tabindex; ←/→ and Home/End move and select; panels are role="tabpanel". */
  function initTabs(list) {
    var tabs = $$('[role="tab"]', list);
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.getAttribute("aria-controls"));
        if (panel) panel.hidden = !on;
      });
      if (focus) tab.focus();
    }
    tabs.forEach(function (tab, i) {
      tab.addEventListener("click", function () { select(tab, false); });
      tab.addEventListener("keydown", function (e) {
        var n = tabs.length, to = null;
        if (e.key === "ArrowRight") to = (i + 1) % n;
        else if (e.key === "ArrowLeft") to = (i - 1 + n) % n;
        else if (e.key === "Home") to = 0;
        else if (e.key === "End") to = n - 1;
        if (to !== null) { e.preventDefault(); select(tabs[to], true); }
      });
    });
    // Deep link: data.html#addr opens the «Адреса доставки» tab.
    var hash = location.hash.replace("#", "");
    var fromHash = hash && tabs.filter(function (t) { return t.getAttribute("aria-controls") === "panel-" + hash; })[0];
    if (fromHash) select(fromHash, false);
  }

  /* ---------------------------------------------------------------- Accordion (DS Accordion)
     One open item at a time (DS default); buttons carry aria-expanded / aria-controls. */
  function initAccordion(root) {
    var triggers = $$(".igro-accordion__trigger", root);
    var multiple = root.hasAttribute("data-multiple");
    function setOpen(btn, on) {
      btn.setAttribute("aria-expanded", on ? "true" : "false");
      var panel = document.getElementById(btn.getAttribute("aria-controls"));
      if (panel) panel.hidden = !on;
    }
    triggers.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var open = btn.getAttribute("aria-expanded") === "true";
        if (!multiple) triggers.forEach(function (b) { if (b !== btn) setOpen(b, false); });
        setOpen(btn, !open);
      });
    });
  }

  /* ---------------------------------------------------------------- Dialog (DS Dialog)
     Labelled by its title, focus moves in and stays in, Esc closes, focus returns
     to the opener, page scroll is locked while open. */
  var FOCUSABLE = 'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';
  var stack = [];

  function openDialog(scrim, opener, focusEl) {
    var dialog = $(".igro-dialog", scrim);
    closeAllDropdowns(false);
    scrim.hidden = false;
    lockScroll(true);
    stack.push({ scrim: scrim, dialog: dialog, opener: opener || document.activeElement });
    (focusEl || dialog).focus();
  }
  function closeDialog(scrim) {
    for (var i = stack.length - 1; i >= 0; i--) {
      if (stack[i].scrim !== scrim) continue;
      var entry = stack.splice(i, 1)[0];
      scrim.hidden = true;
      lockScroll(false);
      var back = entry.opener;
      if (back && document.body.contains(back) && isShown(back)) back.focus();
      else if (stack.length) stack[stack.length - 1].dialog.focus();
      else { var main = $("#main"); if (main) main.focus(); }
      scrim.dispatchEvent(new CustomEvent("dialog:close"));
      return;
    }
  }
  document.addEventListener("keydown", function (e) {
    var top = stack[stack.length - 1];
    if (!top) return;
    if (e.key === "Escape") { e.preventDefault(); closeDialog(top.scrim); return; }
    if (e.key !== "Tab") return;
    var list = $$(FOCUSABLE, top.dialog).filter(isShown);
    if (!list.length) { e.preventDefault(); return; }
    var first = list[0], last = list[list.length - 1], active = document.activeElement;
    if (e.shiftKey && (active === first || active === top.dialog)) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && active === last) { e.preventDefault(); first.focus(); }
    else if (!top.dialog.contains(active)) { e.preventDefault(); first.focus(); }
  });
  document.addEventListener("click", function (e) {
    var closer = e.target.closest("[data-dialog-close]");
    if (closer) { closeDialog(closer.closest(".igro-dialog-scrim")); return; }
    if (e.target.classList && e.target.classList.contains("igro-dialog-scrim")) closeDialog(e.target);
  });

  /* ---------------------------------------------------------------- Toast (DS Toast) */
  function toast(title, message, status) {
    var host = $("#toasts");
    if (!host) return;
    var el = document.createElement("div");
    el.className = "igro-toast igro-toast--" + (status || "success");
    el.setAttribute("role", status === "error" ? "alert" : "status");
    host.appendChild(el);
    // Fill after insertion so the live region announces the text.
    window.setTimeout(function () {
      el.innerHTML = '<div class="igro-toast__body"><div class="igro-toast__title">' + escapeHtml(title) + "</div>" +
        (message ? '<div class="igro-toast__message">' + escapeHtml(message) + "</div>" : "") + "</div>" +
        '<button type="button" class="igro-toast__close" aria-label="Закрыть">' + CLOSE_SVG + "</button>";
      $(".igro-toast__close", el).addEventListener("click", function () { el.remove(); });
    }, 30);
    window.setTimeout(function () { if (el.parentNode) el.remove(); }, 6000);
  }

  /* ---------------------------------------------------------------- Dropdown
     DS Select field + the checkout picker popover. The native <select> stays in the form
     (value, reset, server-side rendering in Bitrix); JS adds a select-only combobox:
     ↓/↑ open and move, Home/End, PageUp/PageDown, Enter/Space pick, Esc closes,
     Tab picks and moves on, typing jumps to an option. ≤767px the list is a bottom sheet. */
  var dropdowns = [];
  function closeAllDropdowns(focus, except) {
    dropdowns.forEach(function (d) { if (d !== except) d.close(focus); });
  }

  function initDropdown(root) {
    var select = $("select", root);
    if (!select || root.__dropdown) return;
    var control = $(".igro-select__control", root);
    var label = $(".igro-select__label", root);
    var base = select.id || "dd" + dropdowns.length;
    if (label && !label.id) label.id = base + "-label";
    var labelText = "";
    if (label) { var copy = label.cloneNode(true); $$('[aria-hidden="true"]', copy).forEach(function (n) { n.remove(); }); labelText = copy.textContent.trim(); }

    var trigger = document.createElement("div");
    trigger.className = "igro-dropdown__trigger";
    trigger.id = base + "-combo";
    trigger.tabIndex = 0;
    trigger.setAttribute("role", "combobox");
    trigger.setAttribute("aria-haspopup", "listbox");
    trigger.setAttribute("aria-expanded", "false");
    trigger.setAttribute("aria-controls", base + "-listbox");
    if (label) trigger.setAttribute("aria-labelledby", label.id);
    if (select.required) trigger.setAttribute("aria-required", "true");
    if (select.getAttribute("aria-describedby")) trigger.setAttribute("aria-describedby", select.getAttribute("aria-describedby"));
    trigger.innerHTML = '<span class="igro-dropdown__value"></span>';
    var valueEl = trigger.firstChild;

    var panel = document.createElement("div");
    panel.className = "igro-dropdown__panel";
    panel.hidden = true;
    panel.innerHTML = '<span class="igro-dropdown__handle" aria-hidden="true"></span>' +
      '<button type="button" class="igro-dropdown__close" tabindex="-1" aria-label="Закрыть">' + CLOSE_SVG + "</button>" +
      '<p class="igro-dropdown__head" aria-hidden="true">' + escapeHtml(labelText) + "</p>" +
      '<ul class="igro-dropdown__list" role="listbox" id="' + base + '-listbox" tabindex="-1"' + (label ? ' aria-labelledby="' + label.id + '"' : "") + "></ul>";
    var list = $(".igro-dropdown__list", panel);
    list.innerHTML = Array.prototype.map.call(select.options, function (o, i) {
      var sub = o.getAttribute("data-sub");
      return '<li class="igro-list-row igro-list-row--compact" role="option" id="' + base + "-opt-" + i + '" data-index="' + i + '" aria-selected="false">' +
        '<span class="igro-list-row__text"><span class="igro-list-row__title">' + escapeHtml(o.text) + "</span>" +
        (sub ? '<span class="igro-list-row__sub">' + escapeHtml(sub) + "</span>" : "") + "</span></li>";
    }).join("");
    var scrim = document.createElement("div");
    scrim.className = "igro-dropdown__scrim";
    scrim.hidden = true;

    control.appendChild(trigger);
    control.appendChild(panel);
    root.appendChild(scrim);
    root.classList.add("igro-dropdown");
    select.tabIndex = -1;
    select.__trigger = trigger;

    var items = $$('[role="option"]', list), active = -1, sheet = false, typed = "", typedAt = 0;

    function sync() {
      var i = select.selectedIndex;
      valueEl.textContent = i >= 0 ? select.options[i].text : "";
      items.forEach(function (li, k) { li.setAttribute("aria-selected", k === i ? "true" : "false"); });
    }
    function setActive(i, scroll) {
      active = Math.max(0, Math.min(items.length - 1, i));
      items.forEach(function (li, k) { li.classList.toggle("is-active", k === active); });
      trigger.setAttribute("aria-activedescendant", items[active].id);
      if (scroll) items[active].scrollIntoView({ block: "nearest" });
    }
    function open() {
      if (!panel.hidden) return;
      closeAllDropdowns(false, api);
      panel.hidden = false;
      panel.classList.remove("is-up");
      root.classList.add("is-open");
      trigger.setAttribute("aria-expanded", "true");
      sheet = isSheetWidth();
      if (sheet) { scrim.hidden = false; lockScroll(true); }
      else {
        var r = panel.getBoundingClientRect(), c = control.getBoundingClientRect();
        if (r.bottom > window.innerHeight - 8 && c.top > r.height + 16) panel.classList.add("is-up");
      }
      setActive(select.selectedIndex >= 0 ? select.selectedIndex : 0, true);
    }
    function close(focus) {
      if (panel.hidden) return;
      panel.hidden = true;
      scrim.hidden = true;
      root.classList.remove("is-open");
      trigger.setAttribute("aria-expanded", "false");
      trigger.removeAttribute("aria-activedescendant");
      items.forEach(function (li) { li.classList.remove("is-active"); });
      if (sheet) { lockScroll(false); sheet = false; }
      if (focus) trigger.focus();
    }
    function choose(i, focus) {
      if (i < 0 || i >= items.length) return;
      var changed = select.selectedIndex !== i;
      select.selectedIndex = i;
      sync();
      close(focus);
      if (changed) select.dispatchEvent(new Event("change", { bubbles: true }));
    }
    function typeahead(ch) {
      var now = Date.now();
      typed = now - typedAt > 600 ? ch : typed + ch;
      typedAt = now;
      var q = typed.toLowerCase(), from = typed.length === 1 ? active + 1 : active;
      for (var k = 0; k < items.length; k++) {
        var idx = (from + k + items.length) % items.length;
        if (select.options[idx].text.toLowerCase().indexOf(q) === 0) { if (panel.hidden) open(); setActive(idx, true); return; }
      }
    }

    trigger.addEventListener("keydown", function (e) {
      var isOpen = !panel.hidden;
      switch (e.key) {
        case "ArrowDown": e.preventDefault(); if (!isOpen) open(); else if (!e.altKey) setActive(active + 1, true); break;
        case "ArrowUp": e.preventDefault(); if (!isOpen) open(); else if (e.altKey) choose(active, true); else setActive(active - 1, true); break;
        case "Home": e.preventDefault(); if (!isOpen) open(); setActive(0, true); break;
        case "End": e.preventDefault(); if (!isOpen) open(); setActive(items.length - 1, true); break;
        case "PageDown": if (isOpen) { e.preventDefault(); setActive(active + 10, true); } break;
        case "PageUp": if (isOpen) { e.preventDefault(); setActive(active - 10, true); } break;
        case "Enter": case " ": e.preventDefault(); if (isOpen) choose(active, true); else open(); break;
        case "Escape": if (isOpen) { e.preventDefault(); e.stopPropagation(); close(true); } break;
        case "Tab": if (isOpen) choose(active, false); break;
        default:
          if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) { e.preventDefault(); typeahead(e.key); }
      }
    });
    trigger.addEventListener("click", function () { if (panel.hidden) open(); else close(true); });
    trigger.addEventListener("blur", function () { window.setTimeout(function () { if (document.activeElement !== trigger) close(false); }, 0); });
    list.addEventListener("mousedown", function (e) { e.preventDefault(); });
    list.addEventListener("click", function (e) { var li = e.target.closest('[role="option"]'); if (li) choose(Number(li.getAttribute("data-index")), true); });
    list.addEventListener("mousemove", function (e) { var li = e.target.closest('[role="option"]'); if (li && Number(li.getAttribute("data-index")) !== active) setActive(Number(li.getAttribute("data-index")), false); });
    scrim.addEventListener("click", function () { close(true); });
    $(".igro-dropdown__close", panel).addEventListener("mousedown", function (e) { e.preventDefault(); });
    $(".igro-dropdown__close", panel).addEventListener("click", function () { close(true); });
    select.addEventListener("change", sync);
    if (select.form) select.form.addEventListener("reset", function () { window.setTimeout(sync, 0); });

    var api = { close: close, sync: sync, trigger: trigger };
    root.__dropdown = api;
    dropdowns.push(api);
    sync();
  }
  window.addEventListener("resize", function () { closeAllDropdowns(false); });

  /* ---------------------------------------------------------------- Filters (orders, favorites)
     A form with data-filter="#list": every select with data-key hides list items whose
     data-<key> differs; the first option means «all». In Bitrix this is a GET form. */
  function initFilter(form) {
    var target = $(form.getAttribute("data-filter"));
    if (!target) return;
    var empty = $(form.getAttribute("data-filter-empty"));
    var selects = $$("select[data-key]", form);
    function apply() {
      var shown = 0;
      $$("[data-item]", target).forEach(function (item) {
        // is-out-coll: товар вне выбранной подборки «Избранного» (initFavorites)
        var ok = !item.classList.contains("is-out-coll") && selects.every(function (s) { return s.selectedIndex === 0 || item.getAttribute("data-" + s.getAttribute("data-key")) === s.value; });
        item.hidden = !ok;
        if (ok) shown++;
      });
      target.hidden = shown === 0;
      if (empty) empty.hidden = shown > 0;
      form.dispatchEvent(new CustomEvent("filter:applied", { detail: { shown: shown } }));
    }
    form.addEventListener("change", apply);
    form.addEventListener("reset", function () { window.setTimeout(apply, 0); });
    form.addEventListener("submit", function (e) { e.preventDefault(); });
    $$("[data-filter-reset]").forEach(function (btn) {
      if (btn.getAttribute("data-filter-reset") !== "#" + form.id) return;
      btn.addEventListener("click", function () { form.reset(); var first = $(".igro-dropdown__trigger", form); if (first) first.focus(); });
    });
    apply();
  }

  /* ---------------------------------------------------------------- Fields */
  // DS formatPhone: +7 (XXX) XXX-XX-XX while typing, pasting or deleting; 8… and 7… read as the prefix.
  function formatPhone(raw) {
    var s = String(raw || "").trim();
    var d = s.replace(/\D/g, "");
    var prefixOnly = false;
    if (s.indexOf("+7") === 0) d = d.slice(1);
    else if (/^[78]/.test(d) && (d.length === 1 || d.length >= 11)) { d = d.slice(1); prefixOnly = !d; }
    d = d.slice(0, 10);
    if (!d) return prefixOnly ? "+7 (" : "";
    var out = "+7 (" + d.slice(0, 3);
    if (d.length > 3) out += ") " + d.slice(3, 6);
    if (d.length > 6) out += "-" + d.slice(6, 8);
    if (d.length > 8) out += "-" + d.slice(8, 10);
    return out;
  }
  var phoneDigits = function (v) { return formatPhone(v).replace(/\D/g, "").slice(1); };

  function fieldRoot(input) { return input.closest(".igro-field, .igro-select, .igro-textarea"); }
  function setError(input, message) {
    var root = fieldRoot(input);
    var hint = document.getElementById(input.id + "-hint");
    var mod = root.classList.contains("igro-select") ? "igro-select--invalid" : "igro-field--invalid";
    var targets = input.__trigger ? [input, input.__trigger] : [input];
    if (message) {
      targets.forEach(function (t) { t.setAttribute("aria-invalid", "true"); });
      root.classList.add(mod);
      if (hint) { hint.textContent = message; hint.hidden = false; }
    } else {
      targets.forEach(function (t) { t.removeAttribute("aria-invalid"); });
      root.classList.remove(mod);
      if (hint) { var def = hint.getAttribute("data-default") || ""; hint.textContent = def; hint.hidden = !def; }
    }
  }
  function validate(input) {
    var v = input.value.trim();
    if (input.required && !v) return input.tagName === "SELECT" ? "Выберите значение" : "Заполните поле";
    if (input.type === "email" && v && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)) return "Проверьте адрес почты: например, name@mail.ru";
    if (input.hasAttribute("data-phone") && v && phoneDigits(v).length !== 10) return "Введите номер полностью";
    return "";
  }
  function validateForm(form) {
    var firstBad = null;
    $$("input, select, textarea", form).forEach(function (el) {
      if (el.type === "checkbox" || el.disabled) return;
      var msg = validate(el);
      setError(el, msg);
      if (msg && !firstBad) firstBad = el;
    });
    if (firstBad) (firstBad.__trigger || firstBad).focus();
    return !firstBad;
  }
  function syncClear(input) {
    var btn = $('[data-clear="' + input.id + '"]');
    if (btn) btn.hidden = !input.value;
  }

  function initFields(root) {
    $$("[data-phone]", root).forEach(function (input) {
      input.addEventListener("input", function () { input.value = formatPhone(input.value); syncClear(input); });
    });
    $$(".igro-field__input, .igro-select__input, .igro-textarea__input", root).forEach(function (input) {
      var evt = input.tagName === "SELECT" ? "change" : "input";
      input.addEventListener(evt, function () {
        syncClear(input);
        if (input.getAttribute("aria-invalid") === "true" && !validate(input)) setError(input, "");
      });
    });
    $$("[data-clear]", root).forEach(function (btn) {
      btn.addEventListener("click", function () {
        var input = document.getElementById(btn.getAttribute("data-clear"));
        input.value = "";
        input.dispatchEvent(new Event("input", { bubbles: true }));
        btn.hidden = true;
        input.focus();
      });
    });
    $$("[data-count-for]", root).forEach(function (counter) {
      var ta = document.getElementById(counter.getAttribute("data-count-for"));
      var max = ta.getAttribute("maxlength");
      var sync = function () { counter.textContent = ta.value.length + " / " + max; };
      ta.addEventListener("input", sync);
      sync();
    });
  }

  /* ---------------------------------------------------------------- Address suggestions
     Demo source in the shape of DaData «suggest address»: label + sub line, street-level
     results until a house number is typed. Bitrix: replace IGRO_LK.suggestAddress. */
  var STREETS = [
    ["Москва", "ул. Лесная", "127047"], ["Москва", "ул. Тверская", "125009"], ["Москва", "ул. Мельникова", "109316"],
    ["Москва", "Ленинский пр-т", "119049"], ["Москва", "ул. Баумана", "105005"], ["Москва", "ул. Новый Арбат", "119019"],
    ["Москва", "Кутузовский пр-т", "121165"], ["Москва", "ул. Профсоюзная", "117292"], ["Москва", "ул. Пятницкая", "115035"],
    ["Москва", "пр-т Мира", "129090"], ["Москва", "ул. Лесные Поляны", "141011"], ["Химки", "ул. Лесная", "141400"],
    ["Санкт-Петербург", "Невский пр-т", "191025"], ["Санкт-Петербург", "ул. Марата", "191002"], ["Санкт-Петербург", "Лесной пр-т", "194100"],
    ["Казань", "ул. Баумана", "420111"], ["Казань", "ул. Пушкина", "420015"], ["Екатеринбург", "ул. Малышева", "620014"],
    ["Екатеринбург", "ул. Вайнера", "620014"], ["Новосибирск", "Красный пр-т", "630007"], ["Краснодар", "ул. Красная", "350000"],
    ["Нижний Новгород", "ул. Большая Покровская", "603005"]
  ];
  var STOP = { "ул": 1, "улица": 1, "д": 1, "дом": 1, "г": 1, "город": 1, "пр": 1, "пр-т": 1, "проспект": 1, "кв": 1, "офис": 1, "корп": 1, "стр": 1, "россия": 1 };
  var norm = function (s) { return String(s).toLowerCase().replace(/ё/g, "е"); };
  function tokenize(q) {
    var words = [], house = "";
    norm(q).split(/[\s,.;]+/).forEach(function (t) {
      if (!t || STOP[t]) return;
      if (/^\d/.test(t)) { if (!house) house = t; return; }
      words.push(t);
    });
    return { words: words, house: house };
  }
  function suggestAddress(query, done) {
    var tk = tokenize(query), out = [];
    if (!tk.words.length) { done([], tk); return; }
    var hits = STREETS.filter(function (s) {
      var hay = norm(s[0] + " " + s[1]).split(/[\s.,-]+/);
      return tk.words.every(function (w) { return hay.some(function (h) { return h.indexOf(w) === 0; }); });
    });
    hits.forEach(function (s, i) {
      var street = s[0] + ", " + s[1];
      if (tk.house) {
        out.push({ label: street + ", д. " + tk.house, sub: s[2] + ", " + s[0], complete: true });
        if (i === 0) {
          out.push({ label: street + ", д. " + tk.house + ", корп. 1", sub: s[2] + ", " + s[0], complete: true });
          out.push({ label: street + ", д. " + tk.house + ", стр. 2", sub: s[2] + ", " + s[0], complete: true });
        }
      } else {
        out.push({ label: street, sub: "Улица · " + s[0] + ", " + s[2], complete: false });
      }
    });
    done(out.slice(0, 6), tk);
  }
  // Bold the typed part of every word, as the checkout city search does.
  function highlight(label, tk) {
    var terms = tk.words.concat(tk.house ? [tk.house] : []);
    return label.split(/([\s,.]+)/).map(function (seg) {
      var n = norm(seg), best = "";
      terms.forEach(function (t) { if (n.indexOf(t) === 0 && t.length > best.length) best = t; });
      return best ? "<b>" + escapeHtml(seg.slice(0, best.length)) + "</b>" + escapeHtml(seg.slice(best.length)) : escapeHtml(seg);
    }).join("");
  }

  /* ---------------------------------------------------------------- Autocomplete (DS Autocomplete v6.1)
     ARIA combobox: opens on focus and while typing, ↑/↓ move the highlight
     (aria-activedescendant), Enter picks, Esc closes. */
  function initAutocomplete(root, onPick) {
    var input = $('[role="combobox"]', root);
    var list = $('[role="listbox"]', root);
    var items = [], hi = -1;
    function close() { list.hidden = true; input.setAttribute("aria-expanded", "false"); input.removeAttribute("aria-activedescendant"); hi = -1; }
    function highlightRow(i) {
      hi = i;
      $$('[role="option"]', list).forEach(function (o, k) { o.setAttribute("aria-selected", k === i ? "true" : "false"); });
      if (i >= 0) { input.setAttribute("aria-activedescendant", list.id + "-" + i); var opt = document.getElementById(list.id + "-" + i); if (opt) opt.scrollIntoView({ block: "nearest" }); }
      else input.removeAttribute("aria-activedescendant");
    }
    function render(values, tk) {
      items = values;
      hi = -1;
      if (!items.length) {
        list.innerHTML = '<li class="igro-autocomplete__empty" role="option" aria-disabled="true" aria-selected="false" id="' + list.id + '-none">Ничего не найдено. Проверьте написание адреса</li>';
      } else {
        list.innerHTML = items.map(function (it, i) {
          return '<li class="igro-autocomplete__option" role="option" id="' + list.id + "-" + i + '" aria-selected="false">' +
            svgIcon("pin").replace('class="igro-icon"', 'class="igro-icon igro-autocomplete__pin"') +
            '<span class="igro-autocomplete__text"><span class="igro-autocomplete__label">' + highlight(it.label, tk) + "</span>" +
            (it.sub ? '<span class="igro-autocomplete__sub">' + escapeHtml(it.sub) + "</span>" : "") + "</span></li>";
        }).join("");
      }
      list.hidden = false;
      input.setAttribute("aria-expanded", "true");
    }
    function refresh() {
      var v = input.value.trim();
      if (v.length < 2) { close(); return; }
      api.source(v, render);
    }
    function pick(i) {
      var it = items[i];
      if (!it) return;
      close();
      if (it.complete) { onPick(it.label); return; }
      // Street only: keep typing the house number.
      input.value = it.label + ", д. ";
      input.dispatchEvent(new Event("input", { bubbles: true }));
      input.focus();
      input.setSelectionRange(input.value.length, input.value.length);
    }
    input.addEventListener("input", refresh);
    input.addEventListener("focus", refresh);
    input.addEventListener("keydown", function (e) {
      var shown = !list.hidden && items.length > 0;
      if (e.key === "ArrowDown") {
        e.preventDefault();
        if (list.hidden) { refresh(); if (!list.hidden && items.length) highlightRow(0); return; }
        if (shown) highlightRow(Math.min(items.length - 1, hi + 1));
      } else if (e.key === "ArrowUp" && shown) { e.preventDefault(); highlightRow(Math.max(0, hi - 1)); }
      else if (e.key === "Enter" && shown && hi >= 0) { e.preventDefault(); pick(hi); }
      else if (e.key === "Escape" && !list.hidden) { e.preventDefault(); e.stopPropagation(); close(); }
    });
    input.addEventListener("blur", function () { window.setTimeout(function () { if (document.activeElement !== input) close(); }, 120); });
    list.addEventListener("mousedown", function (e) { e.preventDefault(); });
    list.addEventListener("click", function (e) { var o = e.target.closest('.igro-autocomplete__option'); if (o) pick(Number(o.id.split("-").pop())); });
    list.addEventListener("mousemove", function (e) { var o = e.target.closest('.igro-autocomplete__option'); if (o && Number(o.id.split("-").pop()) !== hi) highlightRow(Number(o.id.split("-").pop())); });
    var api = { close: close, source: function (q, cb) { window.IGRO_LK.suggestAddress(q, cb); } };
    return api;
  }

  /* ---------------------------------------------------------------- Page: Мои данные */
  function initProfileForm() {
    var form = $("#profileForm");
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (validateForm(form)) toast("Изменения сохранены", "Данные профиля обновлены", "success");
    });
  }

  function initNotifications() {
    var sw = $("#ntMkt");
    if (!sw) return;
    sw.addEventListener("change", function () {
      toast(sw.checked ? "Рассылка включена" : "Рассылка отключена", sw.checked ? "Будем присылать новости и предложения" : "Письма с акциями больше не придут", "success");
    });
  }

  function initAddresses() {
    var listEl = $("#addrList");
    if (!listEl) return;
    var LIST = [
      { id: "a1", text: "Москва, ул. Лесная, д. 10", flat: "офис 305", salon: "Студия красоты Красота", recipient: "Екатерина Иванова", phone: "+7 (900) 123-45-67", comment: "" },
      { id: "a2", text: "Санкт-Петербург, Невский пр-т, д. 15", flat: "офис 210", salon: "", recipient: "Ольга Смирнова", phone: "+7 (978) 999-99-98", comment: "" },
      { id: "a3", text: "Казань, ул. Баумана, д. 23", flat: "офис 12", salon: "", recipient: "", phone: "", comment: "" }
    ];
    var dialog = $("#addrDialog"), confirm = $("#confirmDialog"), form = $("#addrForm");
    var f = {
      addr: $("#addrInput"), flat: $("#addrFlat"), salon: $("#addrSalon"), recipient: $("#addrRecipient"), phone: $("#addrPhone"),
      comment: $("#addrComment"), primary: $("#addrDefault")
    };
    var editId = null, pendingDelete = null;
    var find = function (id) { return LIST.filter(function (a) { return a.id === id; })[0] || null; };
    var full = function (a) { return a.text + (a.flat ? ", " + a.flat : ""); };

    function render() {
      listEl.innerHTML = LIST.map(function (a, i) {
        var comma = a.text.indexOf(",");
        var city = comma === -1 ? a.text : a.text.slice(0, comma).trim();
        var street = [comma === -1 ? "" : a.text.slice(comma + 1).trim(), a.flat].filter(Boolean).join(", ") || "—";
        var rows = "<dt>Город</dt><dd>" + escapeHtml(city) + "</dd><dt>Адрес</dt><dd>" + escapeHtml(street) + "</dd>" +
          (a.salon ? "<dt>Салон</dt><dd>" + escapeHtml(a.salon) + "</dd>" : "") +
          (a.recipient ? "<dt>Получатель</dt><dd>" + escapeHtml(a.recipient) + "</dd>" : "") +
          (a.phone ? "<dt>Телефон</dt><dd>" + escapeHtml(a.phone) + "</dd>" : "");
        var label = escapeHtml(full(a));
        return '<li class="lk-addr" data-addr="' + a.id + '"><div class="lk-addr__head">' +
          (i === 0 ? '<span class="igro-badge igro-badge--brand">Основной адрес</span>' : "") +
          '<div class="lk-addr__tools">' +
          '<button type="button" class="igro-btn igro-btn--ghost igro-btn--sm lk-addr__edit" data-addr-edit="' + a.id + '" aria-label="Редактировать адрес: ' + label + '">' + svgIcon("pencil") + '<span class="lk-addr__edit-label">Редактировать</span></button>' +
          '<button type="button" class="igro-icon-btn igro-icon-btn--danger igro-icon-btn--sm" data-addr-del="' + a.id + '" aria-label="Удалить адрес: ' + label + '">' + svgIcon("trash") + "</button>" +
          '</div></div><dl class="lk-addr__grid">' + rows + "</dl></li>";
      }).join("");
      listEl.hidden = !LIST.length;
      $("#addrEmpty").hidden = LIST.length > 0;
    }

    var ac = initAutocomplete($("[data-autocomplete]", dialog), function (value) {
      f.addr.value = value;
      syncClear(f.addr);
      setError(f.addr, "");
      showOnMap(value);
      if (isSheetWidth() && step() === "1") { $(".lk-addr-next", dialog).focus({ preventScroll: true }); return; }
      f.flat.focus();
    });

    /* v6, 13.10 · Телефон (≤767 px): окно — нижняя шторка поверх карты, в два шага, как в чекауте v4.
       Шаг 1 — карта и поле адреса с подсказками, «Далее»; шаг 2 — строка с адресом («Изменить» → шаг 1)
       и остальные поля. Новый адрес открывается на шаге 1, сохранённый — сразу на шаге 2.
       На десктопе шаги не видны: CSS прячет их только в шторке. */
    var sheet = $(".lk-addr-dialog", dialog), picked = "";
    var step = function () { return dialog.getAttribute("data-step"); };
    function showOnMap(text) {
      picked = text || "";
      $$("[data-map-label]", dialog).forEach(function (l) { l.textContent = picked; l.hidden = !picked; });
      if (!picked) return;
      $$(".lk-map__pin", dialog).forEach(function (pin) { pin.classList.remove("is-drop"); void pin.offsetWidth; pin.classList.add("is-drop"); });
    }
    f.addr.addEventListener("input", function () { if (picked && f.addr.value.trim() !== picked) showOnMap(""); });
    // Смена шага: высота шторки меняется плавно (старая → новая), как в чекауте
    function setStep(n, animate) {
      var from = animate && isSheetWidth() ? sheet.getBoundingClientRect().height : 0;
      dialog.setAttribute("data-step", String(n));
      $("#addrRecapText").textContent = f.addr.value.trim();
      if (!from) return;
      var to = sheet.getBoundingClientRect().height;
      if (Math.abs(to - from) < 2) return;
      sheet.style.height = from + "px";
      void sheet.offsetHeight;
      sheet.classList.add("is-resizing");
      sheet.style.height = to + "px";
      window.setTimeout(function () { sheet.classList.remove("is-resizing"); sheet.style.height = ""; }, 320);
    }
    function toStep2() {
      var msg = f.addr.value.trim() ? "" : "Начните вводить адрес и выберите его из подсказок";
      setError(f.addr, msg);
      if (msg) { f.addr.focus(); return; }
      ac.close();
      setStep(2, true);
      $(".lk-addr-recap", dialog).focus({ preventScroll: true }); // без клавиатуры: сначала видно, что дальше
    }
    function toStep1() {
      setStep(1, true);
      f.addr.focus();
    }
    dialog.addEventListener("click", function (e) {
      var b = e.target.closest("[data-addr-step]");
      if (b) { if (b.getAttribute("data-addr-step") === "2") toStep2(); else toStep1(); }
    });

    // Свайп вниз за заголовок или ручку закрывает шторку (как нижние листы чекаута)
    function resetSheet() { sheet.classList.remove("is-settling"); sheet.style.transform = ""; sheet.style.animation = ""; }
    (function () {
      var startY = 0, dy = 0, lastY = 0, lastT = 0, v = 0, drag = false;
      function down(e) {
        if (!isSheetWidth() || e.target.closest("button")) return;
        drag = true; dy = 0; v = 0; startY = lastY = e.clientY; lastT = e.timeStamp;
        sheet.classList.remove("is-settling");
        sheet.style.animation = "none";
        e.currentTarget.setPointerCapture(e.pointerId);
      }
      function move(e) {
        if (!drag) return;
        dy = Math.max(0, e.clientY - startY);
        var dt = e.timeStamp - lastT;
        if (dt > 0) v = (e.clientY - lastY) / dt;
        lastY = e.clientY; lastT = e.timeStamp;
        sheet.style.transform = "translateY(" + dy + "px)";
      }
      function up() {
        if (!drag) return;
        drag = false;
        var h = sheet.getBoundingClientRect().height;
        sheet.classList.add("is-settling");
        if (dy > Math.min(140, h * 0.28) || v > 0.9) {
          sheet.style.transform = "translateY(" + Math.round(h + 48) + "px)";
          window.setTimeout(function () { closeDialog(dialog); resetSheet(); }, 200);
        } else {
          sheet.style.transform = "";
          window.setTimeout(resetSheet, 220);
        }
      }
      [$(".igro-dialog__head", sheet), $(".lk-sheet-handle", sheet)].filter(Boolean).forEach(function (g) {
        g.addEventListener("pointerdown", down);
        g.addEventListener("pointermove", move);
        g.addEventListener("pointerup", up);
        g.addEventListener("pointercancel", up);
      });
    })();

    // Клавиатура телефона: шторка поднимается над ней и не выше видимой области (visualViewport)
    var vv = window.visualViewport;
    function fitViewport() {
      if (dialog.hidden || !isSheetWidth() || !vv) { dialog.style.paddingBottom = ""; sheet.style.maxHeight = ""; return; }
      var kb = Math.max(0, window.innerHeight - (vv.height + vv.offsetTop));
      dialog.style.paddingBottom = kb ? Math.round(kb) + "px" : "";
      sheet.style.maxHeight = Math.round(vv.height * 0.88) + "px";
    }
    if (vv) { vv.addEventListener("resize", fitViewport); vv.addEventListener("scroll", fitViewport); }
    dialog.addEventListener("dialog:close", function () { ac.close(); resetSheet(); fitViewport(); });

    function openEditor(id, opener) {
      var rec = id ? find(id) : null;
      editId = rec ? rec.id : "new";
      $("#addrDialogTitle").textContent = rec ? "Адрес доставки" : "Новый адрес доставки";
      f.addr.value = rec ? rec.text : "";
      f.flat.value = rec ? rec.flat : "";
      f.salon.value = rec ? rec.salon : "";
      f.recipient.value = rec ? rec.recipient || "" : "";
      f.phone.value = rec ? rec.phone : "";
      f.comment.value = rec ? rec.comment : "";
      f.comment.dispatchEvent(new Event("input"));
      f.primary.checked = !!rec && LIST.indexOf(rec) === 0;
      [f.addr, f.flat, f.phone].forEach(function (el) { setError(el, ""); syncClear(el); });
      $("#addrDelete").hidden = !rec;
      ac.close();
      resetSheet();
      setStep(rec ? 2 : 1, false);
      openDialog(dialog, opener); // as DS Dialog: focus goes to the dialog itself, Tab moves into it
      showOnMap(rec ? rec.text : "");
      fitViewport();
    }

    function askDelete(rec, opener) {
      pendingDelete = rec.id;
      $("#confirmSub").textContent = full(rec);
      openDialog(confirm, opener); // not on «Удалить»: Enter must not delete by accident
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (isSheetWidth() && step() === "1") { toStep2(); return; }
      var addrMsg = f.addr.value.trim() ? "" : "Начните вводить адрес и выберите его из подсказок";
      var flatMsg = f.flat.value.trim() ? "" : "Укажите квартиру или офис";
      var phoneMsg = f.phone.value && phoneDigits(f.phone.value).length !== 10 ? "Введите номер полностью" : "";
      setError(f.addr, addrMsg); setError(f.flat, flatMsg); setError(f.phone, phoneMsg);
      var bad = addrMsg ? f.addr : flatMsg ? f.flat : phoneMsg ? f.phone : null;
      if (bad === f.addr && step() === "2") setStep(1, true);
      if (bad) { bad.focus(); return; }
      var data = { text: f.addr.value.trim(), flat: f.flat.value.trim(), salon: f.salon.value.trim(), recipient: f.recipient.value.trim(), phone: f.phone.value.trim(), comment: f.comment.value.trim() };
      var rec = editId === "new" ? { id: "a" + Date.now() } : find(editId);
      Object.keys(data).forEach(function (k) { rec[k] = data[k]; });
      if (editId === "new") LIST.push(rec);
      if (f.primary.checked) { LIST = LIST.filter(function (x) { return x !== rec; }); LIST.unshift(rec); }
      var isNew = editId === "new";
      render();
      closeDialog(dialog);
      var editBtn = $('[data-addr-edit="' + rec.id + '"]');
      if (editBtn) editBtn.focus();
      toast(isNew ? "Адрес добавлен" : "Адрес сохранён", full(rec), "success");
    });

    $("#addrDelete").addEventListener("click", function () {
      var rec = find(editId);
      if (rec) askDelete(rec, $("#addrDelete"));
    });
    $("#confirmDelete").addEventListener("click", function () {
      var rec = find(pendingDelete);
      LIST = LIST.filter(function (a) { return a.id !== pendingDelete; });
      pendingDelete = null;
      closeDialog(confirm);
      if (!dialog.hidden) closeDialog(dialog);
      render();
      var next = $("[data-addr-edit]") || $("#addrEmpty [data-addr-add]");
      if (next) next.focus();
      if (rec) toast("Адрес удалён", full(rec), "success");
    });

    document.addEventListener("click", function (e) {
      var add = e.target.closest("[data-addr-add]");
      if (add) { openEditor(null, add); return; }
      var ed = e.target.closest("[data-addr-edit]");
      if (ed) { openEditor(ed.getAttribute("data-addr-edit"), ed); return; }
      var del = e.target.closest("[data-addr-del]");
      if (del) { var r = find(del.getAttribute("data-addr-del")); if (r) askDelete(r, del); }
    });

    render();
  }

  /* ---------------------------------------------------------------- Page: Избранное (v6, 12.10)
     Подборки: по умолчанию одна — «Все товары» (показывает всё избранное, не удаляется); можно создать
     новую, переключаться, удалить. Сердечко в карточке (при наведении — корзина) → окно «Убрать из
     избранного?». Демо: всё в памяти страницы; в Битриксе каждое действие — запрос на сервер. */
  function initFavorites() {
    var grid = $("#fav-grid");
    if (!grid) return;
    var form = $("#fav-filters"), count = $("#fav-count"), collList = $("#favColls");
    var collEmpty = $("#fav-coll-empty"), favEmpty = $("#fav-empty"), filterEmpty = $("#fav-filter-empty");
    var confirmBox = $("#favConfirm"), collDialog = $("#collDialog"), collForm = $("#collForm"), collInput = $("#collName");
    var current = "all", pendingItem = null, pendingColl = null, nextId = 1;
    var toCart = $("[data-fav-to-cart]");

    var items = function () { return $$("[data-item]", grid); };
    var inColl = function (li, id) { return id === "all" || (" " + (li.getAttribute("data-colls") || "") + " ").indexOf(" " + id + " ") > -1; };
    var collBtn = function (id) { return $('[data-coll="' + id + '"]', collList); };
    var collName = function (id) { var b = collBtn(id); return b ? $(".lk-coll__name", b).textContent : ""; };
    var itemName = function (li) { return $(".lk-pcard", li).getAttribute("aria-label"); };
    var goods = function (n) { return n + " " + plural(n, "товар", "товара", "товаров"); };

    function refreshCounts() {
      $$("[data-coll]", collList).forEach(function (b) {
        var id = b.getAttribute("data-coll");
        $(".lk-coll__count", b).textContent = items().filter(function (li) { return inColl(li, id); }).length;
      });
      var all = items().length, inC = items().filter(function (li) { return inColl(li, current); }).length;
      count.textContent = !all ? "В избранном нет товаров"
        : current === "all" ? "У вас " + goods(all) + " в избранном"
        : "В подборке «" + collName(current) + "» " + goods(inC);
    }
    // Товары вне текущей подборки помечаются, фильтр (initFilter) их не показывает.
    function apply() {
      items().forEach(function (li) { li.classList.toggle("is-out-coll", !inColl(li, current)); });
      form.dispatchEvent(new Event("change"));
    }
    form.addEventListener("filter:applied", function () {
      var all = items().length, inC = items().filter(function (li) { return inColl(li, current); }).length;
      if (toCart) toCart.hidden = !items().some(function (li) { return !li.hidden; });
      favEmpty.hidden = all > 0;
      collEmpty.hidden = !(all > 0 && inC === 0);
      form.hidden = inC === 0;
      if (inC === 0) { grid.hidden = true; filterEmpty.hidden = true; }
      refreshCounts();
    });

    function selectColl(id, focus) {
      current = id;
      $$("[data-coll]", collList).forEach(function (b) {
        var on = b.getAttribute("data-coll") === id;
        b.classList.toggle("is-active", on);
        b.setAttribute("aria-pressed", on ? "true" : "false");
      });
      apply();
      if (focus) collBtn(id).focus();
    }

    function removeItem(li) {
      var name = itemName(li);
      var sib = function (dir) { for (var n = li[dir]; n; n = n[dir]) if (!n.hidden) return n; return null; };
      var next = sib("nextElementSibling") || sib("previousElementSibling");
      li.remove();
      apply(); // повторно применить фильтр: под фильтром может не остаться товаров (QA В4)
      var target = next && !next.hidden ? $("[data-fav-heart]", next) : null;
      if (!target && !filterEmpty.hidden) target = $("[data-filter-reset]", filterEmpty);
      (target || $("#main")).focus();
      toast("Товар убран из избранного", name, "success");
    }

    function askConfirm(title, sub, okText, opener) {
      $("#favConfirmTitle").textContent = title;
      $("#favConfirmSub").textContent = sub;
      $("#favConfirmOk").textContent = okText;
      openDialog(confirmBox, opener); // фокус — на окно, не на «Убрать»: Enter не удаляет случайно
    }

    grid.addEventListener("click", function (e) {
      var heart = e.target.closest("[data-fav-heart]");
      if (heart) {
        pendingItem = heart.closest("li"); pendingColl = null;
        askConfirm("Убрать из избранного?", itemName(pendingItem), "Убрать", heart);
      }
    });

    collList.addEventListener("click", function (e) {
      var del = e.target.closest("[data-coll-del]");
      if (del) {
        pendingColl = del.getAttribute("data-coll-del"); pendingItem = null;
        askConfirm("Удалить подборку «" + collName(pendingColl) + "»?", "Товары останутся в избранном, в подборке «Все товары».", "Удалить", del);
        return;
      }
      var b = e.target.closest("[data-coll]");
      if (b) selectColl(b.getAttribute("data-coll"), false);
    });

    $("#favConfirmOk").addEventListener("click", function () {
      var li = pendingItem, cid = pendingColl;
      pendingItem = pendingColl = null;
      closeDialog(confirmBox);
      if (li) { removeItem(li); return; }
      if (!cid) return;
      var name = collName(cid);
      collBtn(cid).closest("li").remove();
      items().forEach(function (it) {
        var rest = (it.getAttribute("data-colls") || "").split(/\s+/).filter(function (x) { return x && x !== cid; });
        it.setAttribute("data-colls", rest.join(" "));
      });
      selectColl(current === cid ? "all" : current, false);
      collBtn(current).focus();
      toast("Подборка удалена", name, "success");
    });

    // «Отправить в корзину» — всё, что сейчас на экране (подборка с учётом фильтров): товары в наличии уходят
    // в корзину по 1 шт., уже добавленные не меняются, «нет в наличии» пропускаются. Демо: в Битриксе — один запрос.
    if (toCart) toCart.addEventListener("click", function () {
      var shown = items().filter(function (li) { return !li.hidden; });
      var btns = shown.map(function (li) { return $("[data-cart-add]", li); }).filter(Boolean);
      var already = shown.filter(function (li) { return $(".lk-stepper", li); }).length;
      var out = shown.filter(function (li) { return $(".lk-pcard__nostock", li); }).length;
      btns.forEach(cartAdd);
      var notes = [];
      if (already) notes.push("Уже были в корзине: " + goods(already));
      if (out) notes.push("Нет в наличии: " + goods(out));
      if (btns.length) toast("В корзину добавлено " + goods(btns.length), notes.join(" · "), "success");
      else toast(already ? "Все товары уже в корзине" : "Нечего добавить в корзину", notes.join(" · "), already ? "success" : "error");
    });

    // Новая подборка: окно с названием, фокус сразу в поле.
    $$("[data-coll-add]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        collForm.reset();
        setError(collInput, "");
        openDialog(collDialog, btn, collInput);
      });
    });
    collForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = collInput.value.trim().replace(/\s+/g, " ");
      var taken = $$(".lk-coll__name", collList).some(function (n) { return n.textContent.toLowerCase() === name.toLowerCase(); });
      var msg = !name ? "Введите название подборки" : taken ? "Подборка с таким названием уже есть" : "";
      setError(collInput, msg);
      if (msg) { collInput.focus(); return; }
      var id = "u" + nextId++;
      var li = document.createElement("li");
      li.className = "lk-colls__item";
      li.innerHTML = '<button type="button" class="lk-coll" aria-pressed="false" data-coll="' + id + '"><span class="lk-coll__name">' + escapeHtml(name) +
        '</span><span class="lk-coll__count">0</span></button><button type="button" class="lk-coll__del" aria-label="Удалить подборку «' + escapeHtml(name) +
        '»" data-coll-del="' + id + '">' + svgIcon("close", 18) + "</button>";
      collList.appendChild(li);
      closeDialog(collDialog);
      selectColl(id, true);
      toast("Подборка создана", name, "success");
    });

    apply();
  }

  /* ---------------------------------------------------------------- «В корзину» → счётчик (как в каталоге v5)
     Кнопка [data-cart-add] превращается в «− 1 +»; цена в карточке пересчитывается на количество;
     ниже единицы — снова кнопка. Демо: в Битриксе каждое изменение — запрос к корзине. */
  function price(card, qty) {
    var el = card && $(".lk-pcard__price", card);
    if (!el) return;
    var unit = parseInt(el.getAttribute("data-price"), 10);
    el.textContent = String(unit * qty).replace(/\B(?=(\d{3})+(?!\d))/g, " ") + " ₽";
  }
  // Кнопка → счётчик с единицей; общая для кнопки в карточке и «Отправить в корзину» в «Избранном»
  function cartAdd(btn) {
    var name = (btn.getAttribute("aria-label") || "").replace(/^В корзину: /, "");
    var st = document.createElement("div");
    st.className = "lk-stepper";
    st.setAttribute("role", "group");
    st.setAttribute("aria-label", "Количество в корзине: " + name);
    st.setAttribute("data-name", name);
    st.innerHTML = '<button type="button" class="lk-stepper__btn" data-step="-1" aria-label="Уменьшить">' + svgIcon("minus", 18) + "</button>" +
      '<span class="lk-stepper__val" aria-live="polite">1</span>' +
      '<button type="button" class="lk-stepper__btn" data-step="1" aria-label="Увеличить">' + svgIcon("plus", 18) + "</button>";
    var card = btn.closest(".lk-pcard");
    btn.replaceWith(st);
    price(card, 1);
    return st;
  }
  function initCartSteppers() {
    document.addEventListener("click", function (e) {
      var add = e.target.closest("[data-cart-add]");
      if (add) {
        var st = cartAdd(add);
        $('[data-step="1"]', st).focus({ preventScroll: true });
        toast("Добавлено в корзину", st.getAttribute("data-name") + ", 1 шт.", "success");
        return;
      }
      var step = e.target.closest(".lk-stepper [data-step]");
      if (!step) return;
      var stepper = step.parentNode, val = $(".lk-stepper__val", stepper), card2 = stepper.closest(".lk-pcard");
      var n = parseInt(val.textContent, 10) + parseInt(step.getAttribute("data-step"), 10);
      if (n < 1) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "lk-pcard__btn";
        b.setAttribute("data-cart-add", "");
        b.setAttribute("aria-label", "В корзину: " + stepper.getAttribute("data-name"));
        b.textContent = "В корзину";
        stepper.replaceWith(b);
        price(card2, 1);
        b.focus({ preventScroll: true });
      } else {
        val.textContent = n;
        price(card2, n);
      }
    });
  }

  /* ---------------------------------------------------------------- «Акции»: фильтр по направлению (14.10)
     Переключатели над сеткой — как подборки «Избранного»: «Все акции» или одно направление (раздел каталога).
     Выбор пишется в адрес (?dir=hair), поэтому «Назад» со страницы акции возвращает к тому же списку.
     Битрикс: направление — свойство элемента инфоблока «Направление», фильтр — по нему. */
  function initPromoDirs() {
    var list = $("#promoDirs"), grid = $(".lk-promo-grid"), status = $("#promoStatus");
    if (!list || !grid) return;
    var btns = $$("[data-dir]", list);
    function select(dir, announce) {
      var shown = 0, name = "";
      btns.forEach(function (b) {
        var on = b.getAttribute("data-dir") === dir;
        b.setAttribute("aria-pressed", on ? "true" : "false");
        b.classList.toggle("is-active", on);
        if (on) name = $(".lk-coll__name", b).textContent;
      });
      $$("li[data-dir]", grid).forEach(function (li) {
        var show = dir === "all" || li.getAttribute("data-dir") === dir;
        li.hidden = !show;
        if (show) shown++;
      });
      if (announce && status) status.textContent = name + ": " + shown + " " + plural(shown, "акция", "акции", "акций");
      try { history.replaceState(null, "", dir === "all" ? location.pathname : location.pathname + "?dir=" + dir); } catch (e) { /* file:// */ }
    }
    list.addEventListener("click", function (e) {
      var b = e.target.closest("[data-dir]");
      if (b) select(b.getAttribute("data-dir"), true);
    });
    var m = /[?&]dir=([\w-]+)/.exec(location.search), from = m && $('[data-dir="' + m[1] + '"]', list);
    if (from) {
      select(m[1], false);
      // на телефоне строка листается вбок — выбранное направление должно быть видно сразу
      list.scrollLeft += from.getBoundingClientRect().left - list.getBoundingClientRect().left - parseFloat(getComputedStyle(list).paddingLeft);
    }
  }

  /* ---------------------------------------------------------------- Подсказка у миниатюр товаров (13.10)
     «Мои заказы»: при наведении на миниатюру — название товара, на «+N поз.» — сколько ещё и где весь состав.
     Один элемент .lk-tip на страницу; только устройства с наведением. Список миниатюр скрыт от скринридера
     (у заказа есть «В заказе N позиций» и бланк), поэтому подсказка — только визуальная. */
  function initThumbTips() {
    if (!$(".lk-thumb[data-tip]") || !window.matchMedia("(hover: hover)").matches) return;
    var tip = document.createElement("div");
    tip.className = "lk-tip";
    tip.setAttribute("aria-hidden", "true");
    tip.hidden = true;
    document.body.appendChild(tip);
    var GAP = 8, EDGE = 8;
    function hide() { tip.hidden = true; }
    document.addEventListener("mouseover", function (e) {
      var th = e.target.closest(".lk-thumb[data-tip]");
      if (!th) { hide(); return; }
      tip.textContent = th.getAttribute("data-tip");
      tip.hidden = false;
      var r = th.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
      var left = Math.min(Math.max(EDGE, r.left + r.width / 2 - w / 2), window.innerWidth - w - EDGE);
      var top = r.top - h - GAP;
      if (top < EDGE) top = r.bottom + GAP; // у верхнего края окна — под миниатюрой
      tip.style.left = Math.round(left) + "px";
      tip.style.top = Math.round(top) + "px";
    });
    window.addEventListener("scroll", hide, { passive: true });
  }

  /* ---------------------------------------------------------------- «Оценить заказ» (13.10)
     Окно: звёзды 1–5 (обязательно), комментарий, «Отправить отзыв». Текст отзыва уходит письмом менеджерам;
     в ЛК остаётся только оценка: вместо кнопки «Оценить заказ» — «Ваша оценка» и звёзды (.lk-rated).
     Битрикс: оценка — свойство заказа (по нему сервер выводит звёзды вместо кнопки), плюс почтовое событие
     с номером заказа, оценкой и текстом. */
  function initReview() {
    var scrim = $("#reviewDialog");
    if (!scrim) return;
    var form = $("#reviewForm"), done = $("#reviewDone"), text = $("#rvText"), caption = $("#rvRateCaption"), err = $("#rvRate-error");
    var stars = $$(".lk-rate__star", form), inputs = $$(".lk-rate__input", form);
    var WORDS = ["Плохо", "Так себе", "Нормально", "Хорошо", "Отлично"];
    var opener = null, ratedEl = null;
    // та же разметка, что у заказов с оценкой в orders.html
    function rated(n) {
      var p = document.createElement("p"), stars = "";
      for (var i = 1; i <= 5; i++) stars += svgIcon("star-fill").replace('class="igro-icon"', 'class="igro-icon lk-rated__star' + (i <= n ? " is-on" : "") + '"');
      p.className = "lk-rated";
      p.tabIndex = -1;
      p.innerHTML = '<span class="lk-rated__label">Ваша оценка</span><span class="lk-rated__stars" aria-hidden="true">' + stars + '</span><span class="igro-sr-only">: ' + n + " из 5</span>";
      return p;
    }
    var value = function () { var c = inputs.filter(function (i) { return i.checked; })[0]; return c ? Number(c.value) : 0; };
    function paint(n) {
      stars.forEach(function (st, i) { st.classList.toggle("is-on", i < n); });
      caption.textContent = n ? WORDS[n - 1] : "";
    }
    function setError(msg) { err.textContent = msg; err.hidden = !msg; }
    function show(isDone) {
      form.hidden = isDone; done.hidden = !isDone;
      $("#reviewActions").hidden = isDone; $("#reviewDoneActions").hidden = !isDone;
    }
    stars.forEach(function (st, i) {
      st.addEventListener("mouseenter", function () { paint(i + 1); });
      st.addEventListener("mouseleave", function () { paint(value()); });
    });
    inputs.forEach(function (inp) { inp.addEventListener("change", function () { paint(value()); setError(""); }); });
    document.addEventListener("click", function (e) {
      var b = e.target.closest("[data-review]");
      if (!b) return;
      var card = b.closest("article"), time = card && $("time", card), num = b.getAttribute("data-review");
      form.reset();
      $("#rvOrder").value = num;
      $("#reviewSub").textContent = "Заказ №\u00a0" + num + (time ? " от " + time.textContent : "");
      text.dispatchEvent(new Event("input"));
      paint(0); setError(""); show(false);
      opener = b; ratedEl = null;
      openDialog(scrim, b);
    });
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!value()) { setError("Поставьте оценку от 1 до 5"); inputs[0].focus(); return; }
      show(true); // Битрикс: сохранить оценку в заказе и отправить письмо менеджерам
      if (opener && opener.parentNode) { ratedEl = rated(value()); opener.replaceWith(ratedEl); }
      $("#reviewClose").focus();
    });
    // кнопки «Оценить заказ» больше нет — фокус после закрытия окна переходит на поставленную оценку
    scrim.addEventListener("dialog:close", function () { if (ratedEl && document.body.contains(ratedEl)) ratedEl.focus(); ratedEl = null; });
  }

  /* ---------------------------------------------------------------- Profile: ladder meter, quick actions */
  function initLadder() {
    // Meters grow from zero once on load (server renders the final width inline).
    $$(".lk-progress__fill").forEach(function (fill) {
      var target = fill.style.width;
      if (!target) return;
      fill.style.width = "0%";
      void fill.offsetWidth;
      window.requestAnimationFrame(function () { fill.style.width = target; });
    });
    // Keep the «Вы здесь» marker inside its card near the ends of the scale.
    function clamp() {
      $$(".lk-progress__here").forEach(function (chip) {
        var arrow = $(".lk-progress__arrow", chip);
        chip.style.marginLeft = "";
        if (arrow) arrow.style.marginLeft = "";
        var box = chip.parentElement.getBoundingClientRect(), r = chip.getBoundingClientRect(), shift = 0;
        if (r.left < box.left) shift = box.left - r.left; else if (r.right > box.right) shift = box.right - r.right;
        if (shift) { chip.style.marginLeft = shift + "px"; if (arrow) arrow.style.marginLeft = -shift + "px"; }
      });
    }
    clamp();
    window.addEventListener("resize", clamp);
  }

  /* ---------------------------------------------------------------- Order form: print, copy, demo actions */
  function initDocument() {
    document.addEventListener("click", function (e) {
      var p = e.target.closest("[data-print]");
      if (p) { e.preventDefault(); window.print(); return; }
      var c = e.target.closest("[data-copy]");
      if (c) {
        var text = c.getAttribute("data-copy");
        var ok = function () { toast("Скопировано", text, "success"); };
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(ok, ok); else ok();
        return;
      }
      var t = e.target.closest("[data-toast]");
      if (t) {
        if (t.tagName === "A" && (t.getAttribute("href") || "").charAt(0) === "#") e.preventDefault();
        var parts = t.getAttribute("data-toast").split("|");
        toast(parts[0], parts[1] || "", "success");
      }
    });
  }

  /* ---------------------------------------------------------------- Carousels
     Keyboard focus on a half-visible card scrolls the whole card into the strip
     (scroll-snap alone keeps it cut off at the edge). */
  function initCarousels() {
    $$(".lk-reco__list").forEach(function (list) {
      list.addEventListener("focusin", function (e) {
        var li = e.target.closest("li");
        if (!li || li.parentElement !== list) return;
        var l = li.offsetLeft - list.offsetLeft, r = l + li.offsetWidth;
        // Scroll to the card's own snap point (its start), otherwise proximity snapping pulls the strip back.
        if (l < list.scrollLeft || r > list.scrollLeft + list.clientWidth) list.scrollLeft = l - parseFloat(getComputedStyle(list).scrollPaddingLeft || 0);
      });
    });
  }

  /* ---------------------------------------------------------------- Init */
  $$("[data-tabs]").forEach(initTabs);
  $$("[data-accordion]").forEach(initAccordion);
  $$("[data-dropdown]").forEach(initDropdown);
  $$("form[data-filter]").forEach(initFilter);
  initFields(document);
  initProfileForm();
  initNotifications();
  initFavorites();
  initCartSteppers();
  initReview();
  initThumbTips();
  initPromoDirs();
  initLadder();
  initCarousels();
  initDocument();
  // Прототип: системный список состояний «Моего профиля» в служебной полосе сверху — переход на выбранную страницу.
  $$("[data-proto-switch]").forEach(function (sel) { sel.addEventListener("change", function () { if (sel.value) location.href = sel.value; }); });

  window.IGRO_LK = {
    openDialog: openDialog, closeDialog: closeDialog, toast: toast, formatPhone: formatPhone,
    suggestAddress: suggestAddress, closeDropdowns: function () { closeAllDropdowns(false); }
  };
  initAddresses(); // after IGRO_LK: the address source can be swapped before the first suggestion
})();
