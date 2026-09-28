(function () {
  "use strict";
  var cfg = window.AGT_CONFIG || {};

  // Mobile nav
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Footer year
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();

  // Quote forms
  var today = new Date().toISOString().slice(0, 10);
  document.querySelectorAll("form.quote-form").forEach(function (form) {
    form.querySelectorAll('input[type="date"]').forEach(function (d) { d.min = today; });

    var trip = form.querySelector('[name="trip_type"]');
    var ret = form.querySelector('[name="return"]');
    if (trip && ret) {
      var sync = function () {
        var oneWay = trip.value === "One Way";
        ret.disabled = oneWay;
        if (oneWay) ret.value = "";
      };
      trip.addEventListener("change", sync);
      sync();
    }

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var status = form.querySelector(".form-status");
      var btn = form.querySelector('button[type="submit"]');
      var setStatus = function (msg, cls) {
        status.textContent = msg;
        status.className = "form-status " + (cls || "");
      };

      if (!form.checkValidity()) { form.reportValidity(); return; }
      var data = new FormData(form);
      if (data.get("company_website")) return; // honeypot: silently drop bots

      data.set("page", location.pathname);
      data.set("action", "submit");

      if (!cfg.leadsEndpoint) {
        window.location.href = buildMailto(data);
        setStatus("Opening your email app… If nothing happens, email " + cfg.email + " or call " + cfg.phone + ".", "ok");
        return;
      }

      btn.disabled = true;
      setStatus("Sending your request…");
      fetch(cfg.leadsEndpoint, { method: "POST", body: new URLSearchParams(data) })
        .then(function (r) { return r.json(); })
        .then(function (res) {
          if (!res.ok) throw new Error(res.error || "failed");
          form.reset();
          setStatus("Thank you! A group travel specialist will contact you shortly. For faster help call " + cfg.phone + ".", "ok");
          if (typeof window.gtag === "function") window.gtag("event", "generate_lead");
        })
        .catch(function () {
          setStatus("Sorry, we couldn't send that. Please call " + cfg.phone + " or email " + cfg.email + ".", "err");
        })
        .finally(function () { btn.disabled = false; });
    });
  });

  function buildMailto(data) {
    var fields = [
      ["Name", "name"], ["Email", "email"], ["Phone", "phone"], ["Trip type", "trip_type"],
      ["From", "from"], ["To", "to"], ["Departure", "depart"], ["Return", "return"],
      ["Passengers", "passengers"], ["Cabin", "cabin"], ["Message", "message"]
    ];
    var body = fields.map(function (f) { return f[0] + ": " + (data.get(f[1]) || "-"); }).join("\n");
    var subject = "Group quote request – " + (data.get("from") || "") + " to " + (data.get("to") || "") + " (" + (data.get("passengers") || "") + " pax)";
    return "mailto:" + cfg.email + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
  }
})();
