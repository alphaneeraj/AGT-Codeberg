# Leads backend (Google Apps Script + Google Sheets)

Codeberg Pages only hosts static files, so quote-form leads are stored in a
Google Sheet through a small Google Apps Script web app. The same script
powers the private dashboard at `/admin/`.

```
Visitor ──form POST──▶ Apps Script (Code.gs) ──▶ Google Sheet "Leads"
                                  │                        ▲
                                  └── email alert          │
Admin (/admin/) ──POST list/update + ADMIN_KEY ────────────┘
```

## One-time setup (about 10 minutes)

1. Sign in to Google with the account that should own the leads, then create a
   new Google Sheet named **AGT Leads**.
2. In the sheet, open **Extensions → Apps Script**. Delete the sample code,
   paste in all of [`Code.gs`](Code.gs), and save.
3. Open **Project Settings (⚙) → Script properties** and add:
   | Property | Value |
   |---|---|
   | `ADMIN_KEY` | a long random passphrase (20+ characters). This is your admin sign-in key. |
   | `NOTIFY_EMAIL` | `info@airlinesgrouptravel.com` (or wherever new-lead alerts should go) |
4. Click **Deploy → New deployment → Select type: Web app**.
   - Execute as: **Me**
   - Who has access: **Anyone**
   - Click **Deploy** and authorize the permissions it asks for (Sheets + send email).
5. Copy the **Web app URL**, which ends in `/exec`, and paste it into
   `assets/js/config.js`:
   ```js
   leadsEndpoint: "https://script.google.com/macros/s/XXXXXXXX/exec",
   ```
6. Run `python3 build.py` (this refreshes the cache-busting version), then commit and push.
7. Open `https://airlinesgrouptravel.codeberg.page/admin/` and sign in with your `ADMIN_KEY`.

## Updating the script later
If you edit `Code.gs`, use **Deploy → Manage deployments → Edit (✏️) → Version: New version**.
That keeps the same `/exec` URL. Creating a *new deployment* instead gives you a new URL.

## Security notes
- The admin key is never stored in the website code. The script checks it
  server-side, and the browser keeps it only for the current tab (sessionStorage).
- `/admin/` is marked `noindex` and blocked in `robots.txt`.
- Spam protection: a hidden honeypot field, a one-per-minute limit per email,
  and length caps. The script also neutralises spreadsheet formula injection.
- Leads are never deleted from the dashboard. Set their status to **Archived** instead.
  Delete rows directly in the Google Sheet if you need to.
- Anyone with edit access to the Google Sheet can see all leads, so share it carefully.
