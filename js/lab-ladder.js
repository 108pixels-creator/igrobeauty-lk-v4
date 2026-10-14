/* Тестовая страница lab-ladder.html (13.10): переключатели служебной полосы.
   «Статус участника» показывает у всех вариантов состояние для выбранного статуса,
   «Показать» — вариант внутри блока профиля целиком или только сами уровни.
   Выбор сохраняется в адресе (#s=vip&c=only), чтобы ссылкой можно было поделиться. */
(function () {
  "use strict";
  var status = document.getElementById("labStatus");
  var ctx = document.getElementById("labCtx");
  if (!status || !ctx) return;

  function fromHash() {
    var m = /s=(\w+)/.exec(location.hash), c = /c=(\w+)/.exec(location.hash);
    if (m && status.querySelector('option[value="' + m[1] + '"]')) status.value = m[1];
    if (c && ctx.querySelector('option[value="' + c[1] + '"]')) ctx.value = c[1];
  }

  function apply(save) {
    var v = status.value;
    Array.prototype.forEach.call(document.querySelectorAll("[data-lab-state]"), function (el) {
      el.hidden = el.getAttribute("data-lab-state") !== v;
    });
    document.body.setAttribute("data-lab-ctx", ctx.value);
    if (save) history.replaceState(null, "", "#s=" + v + (ctx.value === "only" ? "&c=only" : ""));
    // lk.js держит метку «Вы здесь» внутри шкалы по resize — пересчитать для показанных состояний
    window.dispatchEvent(new Event("resize"));
  }

  status.addEventListener("change", function () { apply(true); });
  ctx.addEventListener("change", function () { apply(true); });
  if (/s=|c=/.test(location.hash)) { fromHash(); apply(false); }
})();
