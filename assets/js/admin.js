(function () {
  "use strict";
  var cfg = window.AGT_CONFIG || {};
  var KEY_STORE = "agt_admin_key";
  var state = { leads: [], statuses: [] };

  var $ = function (id) { return document.getElementById(id); };

  // Tabs (Leads / Blog)
  document.querySelectorAll(".tab").forEach(function (t) {
    t.addEventListener("click", function () {
      document.querySelectorAll(".tab").forEach(function (o) {
        var on = o === t;
        o.classList.toggle("active", on);
        o.setAttribute("aria-selected", on ? "true" : "false");
        $(o.dataset.tab).classList.toggle("hidden", !on);
      });
      try { sessionStorage.setItem("agt_admin_tab", t.dataset.tab); } catch (e) {}
    });
  });
  try {
    var lastTab = sessionStorage.getItem("agt_admin_tab");
    var btn = lastTab && document.querySelector('.tab[data-tab="' + lastTab + '"]');
    if (btn) btn.click();
  } catch (e) {}
  var loginBox = $("login"), panel = $("panel"), msg = $("admin-msg");

  function store(k, v) { try { v === null ? sessionStorage.removeItem(k) : sessionStorage.setItem(k, v); } catch (e) {} }
  function load(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function say(text, isErr) { msg.textContent = text || ""; msg.className = "form-status " + (isErr ? "err" : "ok"); }

  function api(params) {
    params.key = load(KEY_STORE) || "";
    return fetch(cfg.leadsEndpoint, { method: "POST", body: new URLSearchParams(params) })
      .then(function (r) { return r.json(); });
  }

  if (!cfg.leadsEndpoint) {
    say("Leads backend not connected yet. Set leadsEndpoint in assets/js/config.js (see backend/README.md).", true);
  }

  $("login-form").addEventListener("submit", function (e) {
    e.preventDefault();
    store(KEY_STORE, $("admin-key").value.trim());
    refresh();
  });
  $("logout").addEventListener("click", function () {
    store(KEY_STORE, null);
    state.leads = [];
    panel.classList.add("hidden");
    loginBox.classList.remove("hidden");
    say("Signed out.");
  });
  $("refresh").addEventListener("click", refresh);
  $("search").addEventListener("input", render);
  $("filter-status").addEventListener("change", render);
  $("export").addEventListener("click", exportCsv);

  function refresh() {
    if (!cfg.leadsEndpoint) return;
    say("Loading leads…");
    api({ action: "list" }).then(function (res) {
      if (!res.ok) {
        if (res.error === "unauthorized") store(KEY_STORE, null);
        loginBox.classList.remove("hidden");
        panel.classList.add("hidden");
        return say("Error: " + res.error, true);
      }
      state.leads = res.leads || [];
      state.statuses = res.statuses || [];
      var sel = $("filter-status");
      if (sel.options.length <= 1) {
        state.statuses.forEach(function (s) { sel.add(new Option(s, s)); });
      }
      loginBox.classList.add("hidden");
      panel.classList.remove("hidden");
      say("Loaded " + state.leads.length + " leads at " + new Date().toLocaleTimeString() + ".");
      render();
    }).catch(function () { say("Could not reach the leads backend.", true); });
  }

  function filtered() {
    var q = $("search").value.trim().toLowerCase();
    var st = $("filter-status").value;
    return state.leads.filter(function (l) {
      if (st && l.status !== st) return false;
      if (!q) return true;
      return ["name", "email", "phone", "from", "to", "message", "notes", "id"].some(function (f) {
        return String(l[f] || "").toLowerCase().indexOf(q) !== -1;
      });
    });
  }

  function render() {
    var rows = filtered();
    var counts = {};
    state.leads.forEach(function (l) { counts[l.status] = (counts[l.status] || 0) + 1; });
    $("stats").innerHTML = '<div class="stat"><b>' + state.leads.length + '</b>Total</div>' +
      state.statuses.map(function (s) { return '<div class="stat"><b>' + (counts[s] || 0) + '</b>' + esc(s) + '</div>'; }).join("");

    $("leads-body").innerHTML = rows.length ? rows.map(function (l) {
      var opts = state.statuses.map(function (s) {
        return '<option' + (s === l.status ? " selected" : "") + ">" + esc(s) + "</option>";
      }).join("");
      var when = l.timestamp ? new Date(l.timestamp).toLocaleString() : "";
      var dates = esc(l.depart) + (l["return"] ? " → " + esc(l["return"]) : "");
      return "<tr>" +
        "<td><span class='badge'>#" + esc(l.id) + "</span><br><small>" + esc(when) + "</small></td>" +
        "<td><strong>" + esc(l.name) + "</strong><br><a href='mailto:" + esc(l.email) + "'>" + esc(l.email) + "</a><br><a href='tel:" + esc(l.phone) + "'>" + esc(l.phone) + "</a></td>" +
        "<td>" + esc(l.from) + " → " + esc(l.to) + "<br><small>" + esc(l.trip_type) + " · " + dates + "</small></td>" +
        "<td>" + esc(l.passengers) + "<br><small>" + esc(l.cabin) + "</small></td>" +
        "<td style='max-width:260px'>" + esc(l.message) + "</td>" +
        "<td><select data-id='" + esc(l.id) + "' class='st'>" + opts + "</select></td>" +
        "<td><input data-id='" + esc(l.id) + "' class='nt' value='" + esc(l.notes) + "' placeholder='Add note, press Enter'></td>" +
        "</tr>";
    }).join("") : "<tr><td colspan='7'>No leads match.</td></tr>";

    document.querySelectorAll("#leads-body select.st").forEach(function (s) {
      s.addEventListener("change", function () { save(s.dataset.id, { status: s.value }); });
    });
    document.querySelectorAll("#leads-body input.nt").forEach(function (i) {
      i.addEventListener("keydown", function (e) { if (e.key === "Enter") save(i.dataset.id, { notes: i.value }); });
    });
  }

  function save(id, fields) {
    fields.action = "update";
    fields.id = id;
    say("Saving #" + id + "…");
    api(fields).then(function (res) {
      if (!res.ok) return say("Error: " + res.error, true);
      state.leads.forEach(function (l) {
        if (String(l.id) === String(id)) {
          if (fields.status) l.status = fields.status;
          if (fields.notes !== undefined) l.notes = fields.notes;
        }
      });
      say("Saved #" + id + ".");
      render();
    }).catch(function () { say("Save failed.", true); });
  }

  function exportCsv() {
    var rows = filtered();
    if (!rows.length) return;
    var cols = Object.keys(rows[0]);
    var csv = [cols.join(",")].concat(rows.map(function (r) {
      return cols.map(function (c) { return '"' + String(r[c] == null ? "" : r[c]).replace(/"/g, '""') + '"'; }).join(",");
    })).join("\n");
    var a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    a.download = "agt-leads-" + new Date().toISOString().slice(0, 10) + ".csv";
    a.click();
  }

  if (load(KEY_STORE)) refresh();
})();
