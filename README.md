# AGT Codeberg — Airlines Group Travel promo site

A static, SEO-optimised promotion website for **Airlines Group Travel**, published on
**Codeberg Pages** at **https://airlinesgrouptravel.codeberg.page**.

| | |
|---|---|
| Brand | Airlines Group Travel (AGT) |
| Operated by | Airfare Services USA LLC, 8 The Green, Suite A, Dover, DE 19901, USA |
| Parent website | https://www.airlinesgrouptravel.com |
| Helpline (24/7) | **+1-888-609-1015** |
| Email | info@airlinesgrouptravel.com |
| Purpose | Promote group flight bookings (10+ travelers), capture quote leads, and build brand signals and backlinks for the parent site |

This GitHub repo (**AGT-Codeberg**) is the source of truth. Codeberg serves a copy of it
(see [Publishing](#publishing-to-codeberg-pages)).

---

## What's inside

```
.
├── index.html                 Home (hero + quote form, services, FAQ teaser)
├── group-flights/index.html   Service page (Service schema)
├── about/index.html           AboutPage
├── faq/index.html             FAQPage (10 Q&As, FAQPage schema)
├── contact/index.html         ContactPage + quote form
├── privacy-policy/ terms/     Legal pages
├── 404.html                   Custom not-found page (noindex)
├── admin/index.html           Private leads dashboard (noindex, blocked in robots.txt)
├── assets/css/style.css       All styles (no frameworks, no web fonts)
├── assets/js/config.js        ← set the leads endpoint here
├── assets/js/main.js          Mobile nav, quote form submit / mailto fallback
├── assets/js/admin.js         Leads dashboard (search, filter, status, notes, CSV export)
├── assets/img/                OG/Twitter card image, app icons, logo
├── favicon.ico / favicon.svg / apple-touch-icon.png / site.webmanifest
├── robots.txt  sitemap.xml  llms.txt  llms-full.txt  humans.txt
├── .well-known/security.txt
├── backend/Code.gs            Google Apps Script: lead storage + admin API
├── backend/README.md          Backend setup guide
├── build.py                   Generates all pages + SEO files (edit content here)
└── scripts/make_images.py     Regenerates favicon/icons/OG image (needs Pillow)
```

## SEO and ranking features checklist

| Area | Implementation |
|---|---|
| Titles and meta descriptions | Unique per page, keyword-led, within length limits |
| Canonical URLs | `<link rel="canonical">` on every indexable page |
| Structured data (JSON-LD `@graph`) | `TravelAgency` (organization, address, 24/7 hours, contactPoint, `sameAs` → parent site + socials), `WebSite`, `WebPage`/`AboutPage`/`ContactPage`/`FAQPage`, `BreadcrumbList`, `Service` |
| Breadcrumbs | Visible breadcrumb nav on every inner page plus `BreadcrumbList` schema |
| Sitemap | `sitemap.xml` with `lastmod`, `changefreq`, `priority` and an image entry |
| robots.txt | Allows all crawlers, explicitly welcomes AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended…), blocks `/admin/`, and points to the sitemap |
| AI / LLM discovery | `llms.txt` (summary + page index) and `llms-full.txt` (all page text); linked from `<head>` |
| Open Graph | Title, description, URL, 1200×630 image with alt text, locale |
| Twitter / X card | `summary_large_image`, `@airgrouptravel` as site and creator |
| Favicon set | `favicon.ico` (16/32/48), `favicon.svg`, `apple-touch-icon.png`, 192/512 and maskable PWA icons, `site.webmanifest`, `theme-color` |
| International / local | `lang="en-US"`, `hreflang` en-us + x-default, `geo.region` US-DE |
| Performance (Core Web Vitals) | No frameworks, no web fonts, one CSS file and small deferred JS; hashed `?v=` cache busting |
| Mobile | Responsive layout, mobile menu, sticky click-to-call button, no horizontal scroll |
| Accessibility | Skip link, semantic landmarks, labelled form fields, `aria-current`, focus styles, reduced-motion support |
| E-E-A-T and trust | Legal entity, physical address, phone, email, founding year, privacy and terms pages, airline non-affiliation disclaimer |
| Internal linking | Header, footer and in-content links between all pages |
| Brand entity links | `sameAs` and footer links to the parent site and all social profiles (`rel="me"`) |
| Verification | Add Google / Bing / Yandex tokens in `SITE` in `build.py` |
| Other | `humans.txt`, `security.txt`, custom 404, `format-detection` for phone links |

## Editing content

All copy, contact details and page settings live in **`build.py`** (`SITE`, `FAQS`,
`GROUP_TYPES`, `AIRLINES` and the `*_BODY` blocks). After editing, run:

```bash
python3 build.py
```

This rewrites every HTML page plus `sitemap.xml`, `robots.txt`, `llms.txt`,
`llms-full.txt`, `site.webmanifest`, `humans.txt` and `security.txt`.
It updates the `lastmod` dates and asset versions too. Always commit the generated files.

To change the logo or social image, edit `scripts/make_images.py` and run:

```bash
python3 -m pip install pillow && python3 scripts/make_images.py
```

Preview locally:

```bash
python3 -m http.server 8765
```

Then open http://localhost:8765.

## Lead capture and admin

- **Frontend:** the quote forms on Home, Group Flights and Contact send leads to the
  Google Apps Script endpoint set in `assets/js/config.js`. Until you set it, the form
  opens the visitor's email app addressed to **info@airlinesgrouptravel.com**, so no lead is lost.
- **Admin:** `https://airlinesgrouptravel.codeberg.page/admin/`. Sign in with your
  `ADMIN_KEY` to view, search and filter leads, change their status
  (New → Contacted → Quoted → Booked / Lost / Archived), add notes and export CSV.
- **Setup:** see [`backend/README.md`](backend/README.md).

## Publishing to Codeberg Pages

Codeberg serves `https://<user>.codeberg.page` from a repo named **`pages`**
owned by that user.

1. Create (or sign in to) the Codeberg account **`airlinesgrouptravel`**.
2. Create an empty public repo named **`pages`** under that account.
3. From this folder:
   ```bash
   git remote add codeberg https://codeberg.org/airlinesgrouptravel/pages.git
   git push codeberg main
   ```
4. Wait a minute or two, then open https://airlinesgrouptravel.codeberg.page.

**Keeping both in sync:** after each change, run `git push origin main && git push codeberg main`.
Alternatively, set up a *pull mirror* in Codeberg from this GitHub repo:
New Migration → GitHub → tick *This repository will be a mirror*.
Note that Codeberg Pages needs a normal repo, so pushing to both is the simplest option.

## After launch

1. **Google Search Console:** add the URL-prefix property `https://airlinesgrouptravel.codeberg.page/`,
   verify with the HTML-tag method (put the token in `build.py` → `google_site_verification`),
   then submit `sitemap.xml`.
2. **Bing Webmaster Tools:** import from GSC or verify with `bing_site_verification`, then submit the sitemap.
3. Validate the schema with the Rich Results Test (https://search.google.com/test/rich-results)
   and the Schema Markup Validator (https://validator.schema.org/).
4. Check the social cards with the LinkedIn Post Inspector and the Facebook Sharing Debugger.
5. Link to this site from the parent site and social profiles to strengthen the entity connection.

## Compliance notes

- Airlines Group Travel is an independent agency. The footer disclaimer states that it is
  not affiliated with any airline, and the site uses no airline logos.
- The site shows no reviews or ratings markup, because self-serving review schema breaks
  Google's guidelines. Add real, verifiable reviews on the parent site instead.
- Have the Privacy Policy and Terms reviewed by your legal adviser before launch.
