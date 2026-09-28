/**
 * Airlines Group Travel — lead capture + admin API (Google Apps Script)
 *
 * Stores quote requests from airlinesgrouptravel.codeberg.page in a Google
 * Sheet, emails a notification, and serves the /admin/ leads dashboard.
 *
 * Script properties (Project Settings → Script properties):
 *   ADMIN_KEY     long random passphrase used to sign in to /admin/   (required)
 *   NOTIFY_EMAIL  where new-lead alerts go (default info@airlinesgrouptravel.com)
 *
 * Deploy: Deploy → New deployment → Web app → Execute as: Me,
 *         Who has access: Anyone. Paste the /exec URL into assets/js/config.js.
 */

var SHEET_NAME = "Leads";
var HEADERS = ["id", "timestamp", "status", "name", "email", "phone", "trip_type", "from", "to",
               "depart", "return", "passengers", "cabin", "message", "page", "notes", "updated"];
var STATUSES = ["New", "Contacted", "Quoted", "Booked", "Lost", "Archived"];
var LEAD_FIELDS = ["name", "email", "phone", "trip_type", "from", "to", "depart", "return",
                   "passengers", "cabin", "message", "page"];

function doPost(e) {
  var p = (e && e.parameter) || {};
  try {
    switch (p.action || "submit") {
      case "submit": return json_(submit_(p));
      case "list":   return json_(authed_(p, list_));
      case "update": return json_(authed_(p, update_));
      default:       return json_({ ok: false, error: "unknown action" });
    }
  } catch (err) {
    return json_({ ok: false, error: String(err && err.message || err) });
  }
}

function doGet() {
  return json_({ ok: true, service: "AGT leads API" });
}

// ---- actions ---------------------------------------------------------------

function submit_(p) {
  if (p.company_website) return { ok: true }; // honeypot
  if (!p.name || !p.email || !p.phone) return { ok: false, error: "missing required fields" };
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(p.email)) return { ok: false, error: "invalid email" };

  // simple rate limit: 1 submission per email per 60 seconds
  var cache = CacheService.getScriptCache();
  var rlKey = "rl_" + String(p.email).toLowerCase().slice(0, 200);
  if (cache.get(rlKey)) return { ok: false, error: "please wait a minute before submitting again" };
  cache.put(rlKey, "1", 60);

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var sheet = sheet_();
    var id = Utilities.getUuid().slice(0, 8);
    var now = new Date().toISOString();
    var row = HEADERS.map(function (h) {
      if (h === "id") return id;
      if (h === "timestamp" || h === "updated") return now;
      if (h === "status") return "New";
      if (h === "notes") return "";
      return clean_(p[h]);
    });
    sheet.appendRow(row);
    notify_(p, id);
    return { ok: true, id: id };
  } finally {
    lock.releaseLock();
  }
}

function list_() {
  var sheet = sheet_();
  var values = sheet.getDataRange().getValues();
  var head = values.shift();
  var leads = values.map(function (r) {
    var o = {};
    head.forEach(function (h, i) { o[h] = r[i] instanceof Date ? r[i].toISOString() : r[i]; });
    return o;
  }).reverse(); // newest first
  return { ok: true, leads: leads, statuses: STATUSES };
}

function update_(p) {
  if (!p.id) return { ok: false, error: "missing id" };
  if (p.status && STATUSES.indexOf(p.status) === -1) return { ok: false, error: "bad status" };
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var sheet = sheet_();
    var ids = sheet.getRange(2, 1, Math.max(sheet.getLastRow() - 1, 1), 1).getValues();
    for (var i = 0; i < ids.length; i++) {
      if (String(ids[i][0]) === String(p.id)) {
        var rowNum = i + 2;
        if (p.status) sheet.getRange(rowNum, HEADERS.indexOf("status") + 1).setValue(p.status);
        if (p.notes !== undefined) sheet.getRange(rowNum, HEADERS.indexOf("notes") + 1).setValue(clean_(p.notes));
        sheet.getRange(rowNum, HEADERS.indexOf("updated") + 1).setValue(new Date().toISOString());
        return { ok: true };
      }
    }
    return { ok: false, error: "lead not found" };
  } finally {
    lock.releaseLock();
  }
}

// ---- helpers ---------------------------------------------------------------

function authed_(p, fn) {
  var key = PropertiesService.getScriptProperties().getProperty("ADMIN_KEY");
  if (!key || key.length < 12) return { ok: false, error: "ADMIN_KEY not configured" };
  if (!p.key || p.key !== key) {
    Utilities.sleep(800); // slow down guessing
    return { ok: false, error: "unauthorized" };
  }
  return fn(p);
}

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

// Trim, cap length, and neutralise spreadsheet formula injection.
function clean_(v) {
  var s = String(v === undefined || v === null ? "" : v).trim().slice(0, 2000);
  if (/^[=+\-@\t\r]/.test(s)) s = "'" + s;
  return s;
}

function notify_(p, id) {
  var to = PropertiesService.getScriptProperties().getProperty("NOTIFY_EMAIL") || "info@airlinesgrouptravel.com";
  var body = LEAD_FIELDS.map(function (f) { return f + ": " + (p[f] || "-"); }).join("\n");
  try {
    MailApp.sendEmail({
      to: to,
      replyTo: p.email,
      subject: "New group quote #" + id + " – " + (p.from || "") + " → " + (p.to || "") + " (" + (p.passengers || "?") + " pax)",
      body: body
    });
  } catch (err) {
    console.warn("notify failed: " + err);
  }
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
