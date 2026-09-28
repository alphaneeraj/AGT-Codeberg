#!/usr/bin/env python3
"""
Static site generator for airlinesgrouptravel.codeberg.page

Edit SITE / PAGES below, then run:  python3 build.py
It (re)writes every page's index.html plus sitemap.xml, robots.txt,
llms.txt, llms-full.txt, site.webmanifest, humans.txt and security.txt.
No dependencies beyond the Python 3 standard library.
"""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TODAY = date.today().isoformat()


def asset_version():
    import hashlib
    h = hashlib.md5()
    for f in ["assets/css/style.css", "assets/js/main.js", "assets/js/config.js", "assets/js/admin.js"]:
        h.update((ROOT / f).read_bytes())
    return h.hexdigest()[:8]


V = asset_version()

SITE = {
    "name": "Airlines Group Travel",
    "short": "AGT",
    "url": "https://airlinesgrouptravel.codeberg.page",
    "parent_url": "https://www.airlinesgrouptravel.com",
    "legal_name": "Airfare Services USA LLC",
    "phone": "+1-888-609-1015",
    "phone_tel": "+18886091015",
    "email": "info@airlinesgrouptravel.com",
    "street": "8 The Green, Suite A",
    "city": "Dover",
    "region": "DE",
    "postal": "19901",
    "country": "US",
    "founded": "2022",
    "twitter": "@airgrouptravel",
    "locale": "en_US",
    "theme": "#0b3d91",
    "tagline": "Group flight bookings for 10+ travelers",
    "description": ("Airlines Group Travel books discounted group flights for 10 or more passengers "
                    "on domestic and international routes, with 24/7 support from group travel specialists. "
                    "Call +1-888-609-1015 for a free group quote."),
    "social": [
        ("Facebook", "https://www.facebook.com/airgrouptravel"),
        ("X (Twitter)", "https://x.com/airgrouptravel"),
        ("Instagram", "https://www.instagram.com/airgrouptravel/"),
        ("LinkedIn", "https://www.linkedin.com/company/airlines-group-travel"),
        ("YouTube", "https://www.youtube.com/@airlinesgrouptravel"),
        ("Pinterest", "https://www.pinterest.com/airlinesgrouptravel/"),
    ],
    # Paste verification tokens here once you have them (leave "" to omit the tag).
    "google_site_verification": "",
    "bing_site_verification": "",
    "yandex_verification": "",
}

DISCLAIMER = ("Airlines Group Travel is an independent travel agency operated by Airfare Services USA LLC. "
              "We are not an airline and are not affiliated with, endorsed by, or sponsored by any airline "
              "mentioned on this site. Airline names are used only to describe the carriers we can book. "
              "Fares, availability and group policies are set by each airline and can change until tickets are issued.")

AIRLINES = ["American Airlines", "Delta Air Lines", "United Airlines", "Southwest Airlines", "Alaska Airlines",
            "JetBlue", "Lufthansa", "British Airways", "Air France", "KLM", "Emirates", "Qatar Airways",
            "Turkish Airlines", "Air Canada", "Singapore Airlines", "Etihad Airways"]

GROUP_TYPES = [
    ("⚽", "Sports teams", "Tournament and league travel for teams, coaches and supporters, with dates matched to your fixtures."),
    ("💍", "Weddings & family events", "Destination weddings, reunions and milestone celebrations, keeping the whole family on one itinerary."),
    ("💼", "Corporate & conferences", "Meetings, incentives, trade shows and offsites, with name-change flexibility for busy teams."),
    ("🎓", "Schools & students", "Class trips, study abroad, choirs and bands, with chaperone-friendly seating and deposit plans."),
    ("⛪", "Religious & mission trips", "Pilgrimages, church groups and mission teams travelling to one destination together."),
    ("🧳", "Tours & leisure groups", "Tour operators, clubs and friends travelling together on domestic or international holidays."),
]

FAQS = [
    ("How many passengers count as a group booking?",
     "Most airlines treat 10 or more passengers travelling together on the same itinerary as a group. "
     "If your party is smaller, call us anyway — we can often still find fares that keep everyone together."),
    ("How do I get a group flight quote?",
     "Call +1-888-609-1015 (24/7) or send the quote form with your route, dates, number of travelers and cabin class. "
     "A group travel specialist compares options across airlines and gets back to you with a quote."),
    ("Is a group fare cheaper than booking individual tickets?",
     "Often, yes. Group fares can be lower than the public fares for the same seats, and they usually come with added "
     "flexibility such as a small deposit, later name submission and a single locked-in fare for the whole group. "
     "Savings depend on the airline, route and travel dates."),
    ("Do I need all passenger names when I book?",
     "Usually not. Many airline group contracts let you hold seats with a deposit and submit final passenger names "
     "closer to departure. Name deadlines vary by airline and are confirmed in your quote."),
    ("Can I book now and pay later?",
     "Many group contracts need only a deposit to hold the seats, with the balance due before ticketing. "
     "Your specialist explains the deposit and payment schedule for your group before you commit."),
    ("Which airlines can you book for groups?",
     "We can book group travel on most major US and international airlines, including American, Delta, United, "
     "Southwest, Alaska, JetBlue, Lufthansa, British Airways, Emirates and Qatar Airways. We are an independent "
     "agency and not affiliated with any airline."),
    ("Can you book business class or first class for groups?",
     "Yes. We quote economy, premium economy, business and first class for groups, and can mix cabins within one group when needed."),
    ("How far in advance should we book group flights?",
     "As early as possible — ideally 3 to 11 months before departure. Group seat inventory is limited per flight, "
     "and booking early gives you the best choice of fares and schedules."),
    ("Can passengers travel from different cities?",
     "Yes. We can coordinate groups flying from several departure cities so that everyone arrives at the destination together."),
    ("Is Airlines Group Travel an airline?",
     "No. Airlines Group Travel is an independent travel agency run by Airfare Services USA LLC in Dover, Delaware. "
     "Our main website is www.airlinesgrouptravel.com."),
]

# ---------------------------------------------------------------------------
# Page content (HTML fragments). `path` is the URL path; "" is the home page.
# ---------------------------------------------------------------------------

def quote_form(heading="Get a free group quote", sub="Tell us about your trip. A specialist will reply quickly."):
    return f"""
<div class="quote-card" id="quote">
  <h2>{heading}</h2>
  <p class="sub">{sub}</p>
  <form class="quote-form" novalidate>
    <div class="form-grid">
      <div class="full"><label for="q-trip">Trip type</label>
        <select id="q-trip" name="trip_type"><option>Round Trip</option><option>One Way</option><option>Multi City</option></select></div>
      <div><label for="q-from">Flying from *</label><input id="q-from" name="from" required placeholder="City or airport" autocomplete="off"></div>
      <div><label for="q-to">Flying to *</label><input id="q-to" name="to" required placeholder="City or airport" autocomplete="off"></div>
      <div><label for="q-depart">Departure *</label><input id="q-depart" name="depart" type="date" required></div>
      <div><label for="q-return">Return</label><input id="q-return" name="return" type="date"></div>
      <div><label for="q-pax">Travelers *</label><input id="q-pax" name="passengers" type="number" min="2" max="999" value="10" required></div>
      <div><label for="q-cabin">Cabin</label>
        <select id="q-cabin" name="cabin"><option>Economy</option><option>Premium Economy</option><option>Business</option><option>First Class</option></select></div>
      <div class="full"><label for="q-name">Full name *</label><input id="q-name" name="name" required autocomplete="name"></div>
      <div><label for="q-email">Email *</label><input id="q-email" name="email" type="email" required autocomplete="email"></div>
      <div><label for="q-phone">Phone *</label><input id="q-phone" name="phone" type="tel" required autocomplete="tel"></div>
      <div class="full"><label for="q-msg">Group details (optional)</label><textarea id="q-msg" name="message" placeholder="Event, flexibility on dates, departure cities, special requests…"></textarea></div>
      <div class="hp" aria-hidden="true"><label for="q-web">Leave this empty</label><input id="q-web" name="company_website" tabindex="-1" autocomplete="off"></div>
      <div class="full"><label class="check"><input type="checkbox" name="consent" value="yes" required> I agree to be contacted about my quote by phone or email, as described in the <a href="/privacy-policy/">Privacy Policy</a>.</label></div>
    </div>
    <button type="submit" class="btn btn-primary">Request my free quote</button>
    <p class="form-status" role="status" aria-live="polite"></p>
  </form>
</div>"""


def cta_band():
    return f"""
<section class="cta-band">
  <div class="wrap">
    <div><h2>Planning a trip for 10+ people?</h2><p>Talk to a group travel specialist now. We answer 24/7.</p></div>
    <a class="btn btn-navy" href="tel:{SITE['phone_tel']}">📞 Call {SITE['phone']}</a>
  </div>
</section>"""


def faq_html(items):
    return '<div class="faq">' + "".join(
        f"<details><summary>{html.escape(q)}</summary><div><p>{html.escape(a)}</p></div></details>" for q, a in items
    ) + "</div>"


HOME_BODY = f"""
<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <h1>Group flights for 10+ travelers, sorted in one call</h1>
      <p class="lead">Airlines Group Travel finds discounted group airfare on major airlines for sports teams, weddings, companies, schools and tours. You get one specialist, one itinerary and one quote for the whole group.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="tel:{SITE['phone_tel']}">📞 Call {SITE['phone']}</a>
        <a class="btn btn-outline" href="#quote">Get a free quote</a>
      </div>
      <ul class="hero-points">
        <li>Group fares on major US and international airlines</li>
        <li>Hold seats with a deposit and add names later (varies by airline)</li>
        <li>Economy, premium economy, business and first class</li>
        <li>Group specialists available 24/7</li>
      </ul>
    </div>
    {quote_form()}
  </div>
</section>

<section class="block">
  <div class="wrap">
    <h2>Why book group flights with Airlines Group Travel?</h2>
    <p class="section-intro">Booking ten or more seats is different from booking one. Airlines release limited group inventory with its own rules. We handle that for you.</p>
    <div class="grid grid-3">
      <div class="card"><span class="icon" aria-hidden="true">💲</span><h3>Group discounts</h3><p>We compare group contracts and public fares across airlines to find the best overall price for your party.</p></div>
      <div class="card"><span class="icon" aria-hidden="true">📝</span><h3>Flexible names</h3><p>Hold your seats now and send passenger names closer to departure, within each airline's deadline.</p></div>
      <div class="card"><span class="icon" aria-hidden="true">💳</span><h3>Deposit-based holds</h3><p>Many group bookings need only a deposit up front, so you can collect payments from your group before ticketing.</p></div>
      <div class="card"><span class="icon" aria-hidden="true">🕑</span><h3>24/7 support</h3><p>One point of contact for schedule changes, seating, special requests and day-of-travel questions.</p></div>
      <div class="card"><span class="icon" aria-hidden="true">🌍</span><h3>Domestic &amp; international</h3><p>US domestic groups and international itineraries to Europe, the Middle East, Asia and beyond.</p></div>
      <div class="card"><span class="icon" aria-hidden="true">✈️</span><h3>Any cabin class</h3><p>From budget-friendly economy for student groups to business class for executive teams.</p></div>
    </div>
  </div>
</section>

<section class="block alt">
  <div class="wrap">
    <h2>Who we book group travel for</h2>
    <div class="grid grid-3">
      {"".join(f'<div class="card"><span class="icon" aria-hidden="true">{i}</span><h3>{t}</h3><p>{d}</p></div>' for i, t, d in GROUP_TYPES)}
    </div>
    <p style="margin-top:24px"><a class="btn btn-navy" href="/group-flights/">Explore group flight services</a></p>
  </div>
</section>

<section class="block">
  <div class="wrap">
    <h2>How group booking works</h2>
    <ol class="steps">
      <li><h3>Share your trip</h3><p>Call us or send the form with your route, dates, group size and cabin.</p></li>
      <li><h3>Compare quotes</h3><p>Your specialist checks group fares across airlines and explains the deposit, name and payment rules.</p></li>
      <li><h3>Hold your seats</h3><p>Confirm the option you like and secure the seats, usually with a deposit.</p></li>
      <li><h3>Finalize &amp; fly</h3><p>Submit names, complete payment before ticketing, and travel together.</p></li>
    </ol>
  </div>
</section>

<section class="block alt">
  <div class="wrap">
    <h2>Airlines we can book for groups</h2>
    <p class="section-intro">We can quote group travel on most major carriers, including:</p>
    <ul class="pill-list">{"".join(f"<li>{a}</li>" for a in AIRLINES)}</ul>
    <p class="note">Airlines Group Travel is independent and not affiliated with any airline listed.</p>
  </div>
</section>

<section class="block">
  <div class="wrap prose">
    <h2>Group flight FAQs</h2>
    {faq_html(FAQS[:5])}
    <p><a href="/faq/">See all frequently asked questions →</a></p>
  </div>
</section>
{cta_band()}
"""

ABOUT_BODY = f"""
<section class="block">
  <div class="wrap grid grid-2">
    <div class="prose">
      <h2>Group travel is all we do</h2>
      <p>Airlines Group Travel started in {SITE['founded']} to make group air travel simpler. Coordinating flights for a team, a wedding party or a company is complicated: limited seats, name deadlines, deposits and many travelers to keep informed. Our group travel specialists handle those details so organizers can focus on the trip itself.</p>
      <p>We are a US travel agency operated by <strong>{SITE['legal_name']}</strong> and based in Dover, Delaware. We book group airfare on most major domestic and international airlines, in every cabin class.</p>
      <h2>What we stand for</h2>
      <ul>
        <li><strong>Clear quotes.</strong> We explain fares, deposits, name deadlines and change rules before you commit.</li>
        <li><strong>One point of contact.</strong> Your group gets a dedicated specialist from quote to travel day.</li>
        <li><strong>Always reachable.</strong> Our team is available 24/7 at <a href="tel:{SITE['phone_tel']}">{SITE['phone']}</a>.</li>
      </ul>
      <h2>Our main website</h2>
      <p>This page gives a short overview of our group flight service. For deals, destinations, routes and our blog, visit <a href="{SITE['parent_url']}/" rel="noopener">www.airlinesgrouptravel.com</a>.</p>
    </div>
    <div>
      <div class="card">
        <h3>Company details</h3>
        <ul class="contact-list">
          <li><strong>Brand</strong>{SITE['name']}</li>
          <li><strong>Operated by</strong>{SITE['legal_name']}</li>
          <li><strong>Founded</strong>{SITE['founded']}</li>
          <li><strong>Address</strong>{SITE['street']}, {SITE['city']}, Delaware {SITE['postal']}, USA</li>
          <li><strong>Phone (24/7)</strong><a href="tel:{SITE['phone_tel']}">{SITE['phone']}</a></li>
          <li><strong>Email</strong><a href="mailto:{SITE['email']}">{SITE['email']}</a></li>
        </ul>
      </div>
    </div>
  </div>
</section>
{cta_band()}
"""

SERVICES_BODY = f"""
<section class="block">
  <div class="wrap prose">
    <h2>What is a group flight booking?</h2>
    <p>A group booking reserves seats for 10 or more passengers travelling together on the same flights. Airlines price and manage these bookings separately from individual tickets. Group bookings usually include a negotiated fare, a deposit to hold the seats, and a later deadline for passenger names and final payment.</p>
    <h2>What's included when you book with us</h2>
    <ul>
      <li>Group fare comparisons across multiple airlines and routings</li>
      <li>Economy, premium economy, business and first-class quotes</li>
      <li>Round-trip, one-way and multi-city itineraries</li>
      <li>Groups departing from several cities and meeting at one destination</li>
      <li>Help with deposit schedules, name lists and ticketing deadlines</li>
      <li>Seating requests, special assistance and schedule-change support</li>
    </ul>
  </div>
</section>

<section class="block alt">
  <div class="wrap">
    <h2>Group types we specialize in</h2>
    <div class="grid grid-3">
      {"".join(f'<div class="card"><span class="icon" aria-hidden="true">{i}</span><h3>{t}</h3><p>{d}</p></div>' for i, t, d in GROUP_TYPES)}
    </div>
  </div>
</section>

<section class="block">
  <div class="wrap grid grid-2">
    <div class="prose">
      <h2>Tips for a smooth group booking</h2>
      <ul>
        <li><strong>Book early.</strong> Airlines limit how many group seats they sell on each flight. Aim for 3 to 11 months ahead.</li>
        <li><strong>Be flexible where you can.</strong> Moving your dates by a day, or choosing a nearby airport, can lower the group fare a lot.</li>
        <li><strong>Know your headcount range.</strong> Give us a minimum and maximum. Many contracts allow some attrition before a deadline.</li>
        <li><strong>Collect names early.</strong> Names must match government ID exactly, so start collecting them early.</li>
      </ul>
      <h2>Airlines we can book</h2>
      <ul class="pill-list">{"".join(f"<li>{a}</li>" for a in AIRLINES)}</ul>
      <p class="note">Group policies differ by airline. We are an independent agency and not affiliated with any airline.</p>
    </div>
    <div>{quote_form("Request a group quote", "Group of 10 or more? Get options across airlines.")}</div>
  </div>
</section>
{cta_band()}
"""

CONTACT_BODY = f"""
<section class="block">
  <div class="wrap grid grid-2">
    <div>
      <h2>Talk to a group travel specialist</h2>
      <p>The fastest way to get a group quote is to call us. We answer 24 hours a day, 7 days a week.</p>
      <ul class="contact-list card">
        <li><strong>📞 Phone (24/7)</strong><a href="tel:{SITE['phone_tel']}">{SITE['phone']}</a></li>
        <li><strong>✉️ Email</strong><a href="mailto:{SITE['email']}">{SITE['email']}</a></li>
        <li><strong>🏢 Mailing address</strong>{SITE['legal_name']}<br>{SITE['street']}<br>{SITE['city']}, Delaware {SITE['postal']}, USA</li>
        <li><strong>🌐 Main website</strong><a href="{SITE['parent_url']}/" rel="noopener">www.airlinesgrouptravel.com</a></li>
      </ul>
      <h3 style="margin-top:24px">Follow us</h3>
      <p>{" · ".join(f'<a href="{u}" rel="noopener me">{n}</a>' for n, u in SITE['social'])}</p>
    </div>
    <div>{quote_form()}</div>
  </div>
</section>
"""

FAQ_BODY = f"""
<section class="block">
  <div class="wrap prose">
    {faq_html(FAQS)}
    <p>Still have a question? Call <a href="tel:{SITE['phone_tel']}">{SITE['phone']}</a> or email <a href="mailto:{SITE['email']}">{SITE['email']}</a>.</p>
  </div>
</section>
{cta_band()}
"""

PRIVACY_BODY = f"""
<section class="block">
  <div class="wrap prose">
    <p><em>Last updated: {TODAY}</em></p>
    <p>This Privacy Policy explains how {SITE['legal_name']} ("Airlines Group Travel", "we", "us") collects and uses information on {SITE['url'].replace('https://', '')}.</p>
    <h2>Information we collect</h2>
    <ul>
      <li><strong>Quote requests:</strong> your name, email, phone number, travel details and any message you send through our forms.</li>
      <li><strong>Communications:</strong> records of calls and emails with our specialists.</li>
      <li><strong>Technical data:</strong> the page you submitted a form from. This site uses no advertising cookies.</li>
    </ul>
    <h2>How we use it</h2>
    <ul>
      <li>To prepare and send group travel quotes and to contact you about your request.</li>
      <li>To make bookings you ask for, which means sharing passenger details with airlines and travel suppliers.</li>
      <li>To meet legal, accounting and fraud-prevention obligations.</li>
    </ul>
    <h2>Sharing</h2>
    <p>We do not sell your personal information. We share it only with airlines and suppliers needed for your booking, with service providers who store data for us (for example, Google Workspace), or when the law requires it.</p>
    <h2>Retention</h2>
    <p>We keep quote requests for as long as we need them to serve you and meet legal obligations, then delete them.</p>
    <h2>Your choices</h2>
    <p>You can ask to see, correct or delete your information, or opt out of follow-up contact, by emailing <a href="mailto:{SITE['email']}">{SITE['email']}</a>. California residents may have extra rights under the CCPA/CPRA.</p>
    <h2>Hosting</h2>
    <p>This website is hosted on Codeberg Pages. Codeberg may process server logs such as IP addresses to operate the service.</p>
    <h2>Contact</h2>
    <p>{SITE['legal_name']}, {SITE['street']}, {SITE['city']}, DE {SITE['postal']}, USA · <a href="tel:{SITE['phone_tel']}">{SITE['phone']}</a></p>
  </div>
</section>
"""

TERMS_BODY = f"""
<section class="block">
  <div class="wrap prose">
    <p><em>Last updated: {TODAY}</em></p>
    <p>These terms govern your use of {SITE['url'].replace('https://', '')}, operated by {SITE['legal_name']} ("Airlines Group Travel").</p>
    <h2>Our role</h2>
    <p>Airlines Group Travel is an independent travel agency. We are not an airline. Air transportation is provided by the airline shown on your ticket, under that airline's conditions of carriage.</p>
    <h2>Quotes and fares</h2>
    <p>Quotes are estimates based on availability at the time they are given. Fares, taxes and seat availability are not guaranteed until the airline confirms the booking and tickets are issued.</p>
    <h2>Deposits, names and payments</h2>
    <p>Group bookings follow the deposit, name-submission, payment and cancellation rules of the airline's group contract. We tell you these rules in writing before you confirm. Missing a deadline can mean losing seats or deposits.</p>
    <h2>Changes and cancellations</h2>
    <p>Changes and cancellations follow airline rules and may cost extra fees. Our service fees, if any, are disclosed before booking. See the refund policy on <a href="{SITE['parent_url']}/" rel="noopener">our main website</a> for details.</p>
    <h2>Travel documents</h2>
    <p>Each traveler is responsible for valid passports, visas and health documents, and for making sure names match government ID.</p>
    <h2>Website content</h2>
    <p>Information on this site is general and may change. Airline names and trademarks belong to their owners and are used only for identification.</p>
    <h2>Limitation of liability</h2>
    <p>To the extent the law allows, we are not liable for airline schedule changes, cancellations, delays or other acts of suppliers outside our control.</p>
    <h2>Contact</h2>
    <p>Questions? Call <a href="tel:{SITE['phone_tel']}">{SITE['phone']}</a> or email <a href="mailto:{SITE['email']}">{SITE['email']}</a>.</p>
  </div>
</section>
"""

PAGES = [
    {"path": "", "nav": "Home", "title": "Group Flights for 10+ Travelers | Airlines Group Travel",
     "h1": None, "type": "WebPage",
     "desc": "Book discounted group flights for 10+ travelers on major airlines. Sports teams, weddings, corporate & school groups. Free quote 24/7: +1-888-609-1015.",
     "body": HOME_BODY, "priority": "1.0", "faq": FAQS[:5]},
    {"path": "group-flights/", "nav": "Group Flights", "title": "Group Flight Booking Services | Airlines Group Travel",
     "h1": "Group flight booking services",
     "lead": "Discounted airfare and flexible group contracts for 10+ travelers on domestic and international routes.",
     "type": "WebPage", "desc": "Group flight booking for teams, weddings, corporate, school and religious groups. Group fares, deposit holds, flexible names. Call +1-888-609-1015.",
     "body": SERVICES_BODY, "priority": "0.9", "service": True},
    {"path": "about/", "nav": "About", "title": "About Us | Airlines Group Travel",
     "h1": "About Airlines Group Travel",
     "lead": f"A US group travel agency operated by {SITE['legal_name']}, helping groups fly together since {SITE['founded']}.",
     "type": "AboutPage", "desc": "Airlines Group Travel is a US group travel agency run by Airfare Services USA LLC in Dover, Delaware, booking group flights since 2022.",
     "body": ABOUT_BODY, "priority": "0.7"},
    {"path": "faq/", "nav": "FAQ", "title": "Group Flight Booking FAQ | Airlines Group Travel",
     "h1": "Group flight booking FAQ",
     "lead": "Answers to common questions about group fares, deposits, name changes and booking group flights.",
     "type": "FAQPage", "desc": "How many people make a group booking? Can I pay later or add names later? Answers to common group flight questions from Airlines Group Travel.",
     "body": FAQ_BODY, "priority": "0.8", "faq": FAQS},
    {"path": "contact/", "nav": "Contact", "title": "Contact Us – Group Flight Quotes 24/7 | Airlines Group Travel",
     "h1": "Contact Airlines Group Travel",
     "lead": "Call us 24/7 or send your group's trip details for a free quote.",
     "type": "ContactPage", "desc": "Contact Airlines Group Travel for group flight quotes 24/7. Call +1-888-609-1015 or email info@airlinesgrouptravel.com.",
     "body": CONTACT_BODY, "priority": "0.8"},
    {"path": "privacy-policy/", "nav": None, "title": "Privacy Policy | Airlines Group Travel",
     "h1": "Privacy Policy", "lead": "How we collect, use and protect your information.",
     "type": "WebPage", "desc": "Privacy Policy for Airlines Group Travel (Airfare Services USA LLC): what we collect through quote requests and how we use it.",
     "body": PRIVACY_BODY, "priority": "0.3"},
    {"path": "terms/", "nav": None, "title": "Terms & Conditions | Airlines Group Travel",
     "h1": "Terms & Conditions", "lead": "The terms that apply to this website and our group travel services.",
     "type": "WebPage", "desc": "Terms and conditions for using the Airlines Group Travel website and booking group flights through us.",
     "body": TERMS_BODY, "priority": "0.3"},
]

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

LOGO_SVG = ('<svg viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="14" fill="#0b3d91"/>'
            '<path fill="#fff" transform="rotate(45 32 32)" d="M32 6l3 5v15l23 14v5l-23-7v14l7 6v4l-10-3-10 3v-4l7-6V38L6 45v-5l23-14V11z"/>'
            '<circle cx="50" cy="50" r="5" fill="#ffb400"/></svg>')

ORG_ID = SITE["url"] + "/#organization"
WEBSITE_ID = SITE["url"] + "/#website"


def abs_url(path):
    return f"{SITE['url']}/{path}"


def org_node():
    return {
        "@type": "TravelAgency",
        "@id": ORG_ID,
        "name": SITE["name"],
        "alternateName": SITE["short"],
        "legalName": SITE["legal_name"],
        "url": SITE["url"] + "/",
        "logo": {"@type": "ImageObject", "url": abs_url("assets/img/logo-512.png"), "width": 512, "height": 512},
        "image": abs_url("assets/img/og-image.png"),
        "description": SITE["description"],
        "foundingDate": SITE["founded"],
        "telephone": SITE["phone"],
        "email": SITE["email"],
        "priceRange": "$$",
        "address": {"@type": "PostalAddress", "streetAddress": SITE["street"], "addressLocality": SITE["city"],
                    "addressRegion": SITE["region"], "postalCode": SITE["postal"], "addressCountry": SITE["country"]},
        "areaServed": [{"@type": "Country", "name": "United States"}, {"@type": "Place", "name": "Worldwide"}],
        "openingHoursSpecification": {"@type": "OpeningHoursSpecification",
                                      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                      "opens": "00:00", "closes": "23:59"},
        "contactPoint": [{"@type": "ContactPoint", "telephone": SITE["phone"], "email": SITE["email"],
                          "contactType": "reservations", "areaServed": ["US", "CA"], "availableLanguage": ["English"],
                          "hoursAvailable": {"@type": "OpeningHoursSpecification",
                                             "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                             "opens": "00:00", "closes": "23:59"}}],
        "sameAs": [SITE["parent_url"] + "/"] + [u for _, u in SITE["social"]],
        "knowsAbout": ["Group flight booking", "Group airfare", "Corporate travel", "Sports team travel",
                       "Destination wedding travel", "Student group travel", "Business class flights"],
    }


def breadcrumb_items(page):
    items = [("Home", SITE["url"] + "/")]
    if page["path"]:
        items.append((page["h1"], abs_url(page["path"])))
    return items


def schema_graph(page):
    url = abs_url(page["path"])
    graph = [
        org_node(),
        {"@type": "WebSite", "@id": WEBSITE_ID, "url": SITE["url"] + "/", "name": SITE["name"],
         "description": SITE["tagline"], "publisher": {"@id": ORG_ID}, "inLanguage": "en-US"},
        {"@type": page["type"], "@id": url + "#webpage", "url": url, "name": page["title"],
         "description": page["desc"], "isPartOf": {"@id": WEBSITE_ID}, "about": {"@id": ORG_ID},
         "breadcrumb": {"@id": url + "#breadcrumb"}, "inLanguage": "en-US", "dateModified": TODAY,
         "primaryImageOfPage": {"@type": "ImageObject", "url": abs_url("assets/img/og-image.png")},
         **({"mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                             for q, a in page["faq"]]} if page["type"] == "FAQPage" else {})},
        {"@type": "BreadcrumbList", "@id": url + "#breadcrumb",
         "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u}
                             for i, (n, u) in enumerate(breadcrumb_items(page))]},
    ]
    if page.get("service") or page["path"] == "":
        graph.append({
            "@type": "Service", "@id": SITE["url"] + "/group-flights/#service",
            "name": "Group Flight Booking", "serviceType": "Group airfare booking",
            "description": "Group flight reservations for 10 or more passengers on domestic and international airlines, in all cabin classes.",
            "provider": {"@id": ORG_ID}, "areaServed": {"@type": "Place", "name": "Worldwide"},
            "audience": [{"@type": "Audience", "audienceType": t} for _, t, _ in GROUP_TYPES],
            "availableChannel": {"@type": "ServiceChannel", "servicePhone": {"@type": "ContactPoint", "telephone": SITE["phone"]},
                                 "serviceUrl": SITE["url"] + "/contact/"},
        })
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)


def header(active_path):
    current = ' aria-current="page"'
    links = "".join(
        f'<li><a href="/{p["path"]}"{current if p["path"] == active_path else ""}>{p["nav"]}</a></li>'
        for p in PAGES if p["nav"])
    return f"""<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap"><span class="tagline">✈️ Group bookings for 10+ travelers · 24/7</span><a href="tel:{SITE['phone_tel']}">📞 {SITE['phone']}</a></div></div>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/" aria-label="{SITE['name']} home">{LOGO_SVG}<span>{SITE['name']}</span></a>
    <button class="nav-toggle" aria-controls="site-nav" aria-expanded="false" aria-label="Menu"><span></span><span></span><span></span></button>
    <nav class="nav" id="site-nav" aria-label="Main"><ul>{links}</ul></nav>
    <a class="btn btn-primary header-cta" href="tel:{SITE['phone_tel']}">Call now</a>
  </div>
</header>"""


def breadcrumbs(page):
    if not page["path"]:
        return ""
    items = breadcrumb_items(page)
    lis = "".join(
        f'<li><a href="{u}">{html.escape(n)}</a></li>' if i < len(items) - 1
        else f'<li aria-current="page">{html.escape(n)}</li>'
        for i, (n, u) in enumerate(items))
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><div class="wrap"><ol>{lis}</ol></div></nav>'


def footer():
    social = "".join(f'<a href="{u}" rel="noopener me">{n}</a>' for n, u in SITE["social"])
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <h2>{SITE['name']}</h2>
        <p>Group flights for 10+ travelers on major airlines, with 24/7 support. Established {SITE['founded']}.</p>
        <p><a href="{SITE['parent_url']}/" rel="noopener">Visit www.airlinesgrouptravel.com →</a></p>
      </div>
      <div>
        <h2>Company</h2>
        <ul><li><a href="/">Home</a></li><li><a href="/group-flights/">Group Flights</a></li><li><a href="/about/">About Us</a></li><li><a href="/contact/">Contact</a></li></ul>
      </div>
      <div>
        <h2>Help</h2>
        <ul><li><a href="/faq/">FAQ</a></li><li><a href="/privacy-policy/">Privacy Policy</a></li><li><a href="/terms/">Terms &amp; Conditions</a></li><li><a href="/sitemap.xml">Sitemap</a></li></ul>
      </div>
      <div>
        <h2>Contact</h2>
        <address style="font-style:normal">
          {SITE['legal_name']}<br>{SITE['street']}<br>{SITE['city']}, DE {SITE['postal']}, USA<br>
          <a href="tel:{SITE['phone_tel']}">{SITE['phone']}</a><br>
          <a href="mailto:{SITE['email']}">{SITE['email']}</a>
        </address>
        <div class="social">{social}</div>
      </div>
    </div>
    <p class="disclaimer">{DISCLAIMER}<br>© <span id="year">{date.today().year}</span> {SITE['name']} · {SITE['legal_name']}. All rights reserved.</p>
  </div>
</footer>
<a class="btn btn-primary float-call" href="tel:{SITE['phone_tel']}">📞 Call {SITE['phone']} (24/7)</a>"""


def head(page, robots="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1", schema=True, canonical=True):
    url = abs_url(page["path"])
    img = abs_url("assets/img/og-image.png")
    verify = "".join(
        f'\n<meta name="{n}" content="{SITE[k]}">' for n, k in
        [("google-site-verification", "google_site_verification"), ("msvalidate.01", "bing_site_verification"),
         ("yandex-verification", "yandex_verification")] if SITE[k])
    t, d = html.escape(page["title"]), html.escape(page["desc"])
    return f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<meta name="robots" content="{robots}">
{f'<link rel="canonical" href="{url}">' if canonical else ''}
<link rel="alternate" hreflang="en-us" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<meta name="author" content="{SITE['name']}">
<meta name="publisher" content="{SITE['legal_name']}">
<meta name="theme-color" content="{SITE['theme']}">
<meta name="format-detection" content="telephone=yes">
<meta name="geo.region" content="US-DE">
<meta name="geo.placename" content="Dover">{verify}
<!-- Open Graph -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE['name']}">
<meta property="og:locale" content="{SITE['locale']}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{SITE['name']} – group flights for 10+ travelers, call {SITE['phone']}">
<!-- Twitter / X card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="{SITE['twitter']}">
<meta name="twitter:creator" content="{SITE['twitter']}">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{img}">
<meta name="twitter:image:alt" content="{SITE['name']} – group flights for 10+ travelers">
<!-- Icons -->
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<!-- AI / discovery -->
<link rel="alternate" type="text/plain" href="/llms.txt" title="LLM summary">
<link rel="sitemap" type="application/xml" href="/sitemap.xml">
<link rel="author" href="/humans.txt">
<link rel="stylesheet" href="/assets/css/style.css?v={V}">
{f'<script type="application/ld+json">{schema_graph(page)}</script>' if schema else ''}
</head>"""


def render(page):
    hero = "" if not page.get("h1") else (
        f'<section class="page-hero"><div class="wrap"><h1>{html.escape(page["h1"])}</h1>'
        f'<p>{html.escape(page.get("lead", ""))}</p></div></section>')
    return f"""{head(page)}
<body>
{header(page['path'])}
{breadcrumbs(page)}
<main id="main">
{hero}
{page['body']}
</main>
{footer()}
<script src="/assets/js/config.js?v={V}" defer></script>
<script src="/assets/js/main.js?v={V}" defer></script>
</body>
</html>
"""


def render_404():
    page = {"path": "404.html", "title": "Page not found | Airlines Group Travel", "desc": "This page could not be found."}
    return f"""{head(page, robots="noindex, follow", schema=False, canonical=False)}
<body>
{header(None)}
<main id="main">
<section class="page-hero"><div class="wrap"><h1>Page not found</h1><p>The page you are looking for doesn't exist or has moved.</p></div></section>
<section class="block"><div class="wrap prose">
<p>Try one of these instead:</p>
<ul><li><a href="/">Home</a></li><li><a href="/group-flights/">Group flight services</a></li><li><a href="/faq/">FAQ</a></li><li><a href="/contact/">Contact us</a></li></ul>
<p>Or call us 24/7 at <a href="tel:{SITE['phone_tel']}">{SITE['phone']}</a>.</p>
</div></section>
</main>
{footer()}
<script src="/assets/js/main.js?v={V}" defer></script>
</body>
</html>
"""


def render_admin():
    page = {"path": "admin/", "title": "Leads Admin | Airlines Group Travel", "desc": "Private admin area."}
    return f"""{head(page, robots="noindex, nofollow, noarchive", schema=False, canonical=False)}
<body>
<main id="main" class="wrap" style="padding-top:28px;padding-bottom:40px">
  <a class="brand" href="/">{LOGO_SVG}<span>{SITE['name']} · Leads admin</span></a>
  <p class="form-status" id="admin-msg" role="status" aria-live="polite"></p>

  <section id="login" class="card" style="max-width:420px;margin-top:16px">
    <h1 style="font-size:1.4rem">Sign in</h1>
    <form id="login-form">
      <label for="admin-key">Admin key</label>
      <input id="admin-key" type="password" autocomplete="current-password" required>
      <button class="btn btn-navy" style="margin-top:12px" type="submit">View leads</button>
    </form>
    <p class="note" style="margin-top:12px">The key is checked by the Google Apps Script backend (script property <code>ADMIN_KEY</code>). It is kept only in this browser tab.</p>
  </section>

  <section id="panel" class="hidden">
    <div class="stats" id="stats"></div>
    <div class="admin-bar">
      <div><label for="search">Search</label><input id="search" type="search" placeholder="Name, email, route, note…"></div>
      <div><label for="filter-status">Status</label><select id="filter-status"><option value="">All</option></select></div>
      <button class="btn btn-navy" id="refresh" type="button">Refresh</button>
      <button class="btn btn-primary" id="export" type="button">Export CSV</button>
      <button class="btn" id="logout" type="button" style="border-color:var(--line)">Sign out</button>
    </div>
    <div class="table-wrap">
      <table class="leads">
        <thead><tr><th>Lead</th><th>Contact</th><th>Trip</th><th>Pax / Cabin</th><th>Message</th><th>Status</th><th>Notes</th></tr></thead>
        <tbody id="leads-body"></tbody>
      </table>
    </div>
  </section>
</main>
<script src="/assets/js/config.js?v={V}"></script>
<script src="/assets/js/admin.js?v={V}" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Machine-readable files
# ---------------------------------------------------------------------------

def sitemap():
    urls = "".join(f"""
  <url>
    <loc>{abs_url(p['path'])}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{'weekly' if p['priority'] >= '0.8' else 'monthly'}</changefreq>
    <priority>{p['priority']}</priority>{f'''
    <image:image><image:loc>{abs_url("assets/img/og-image.png")}</image:loc><image:title>{SITE["name"]}</image:title></image:image>''' if p['path'] == '' else ''}
  </url>""" for p in PAGES)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">{urls}
</urlset>
"""


def robots():
    ai_bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
               "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot-Extended", "Bingbot", "CCBot"]
    ai = "\n".join(f"User-agent: {b}" for b in ai_bots)
    return f"""# robots.txt for {SITE['url']}
# All public pages may be crawled by search engines and AI assistants.

User-agent: *
Allow: /
Disallow: /admin/
Disallow: /backend/

# AI crawlers are welcome, so our group travel info can be cited accurately
{ai}
Allow: /
Disallow: /admin/
Disallow: /backend/

Sitemap: {SITE['url']}/sitemap.xml
"""


def text_of(fragment):
    s = re.sub(r"<(script|style)[\s\S]*?</\1>", "", fragment)
    s = re.sub(r'<div class="hp"[\s\S]*?</div>', "", s)
    s = re.sub(r'<span class="icon"[^>]*>[^<]*</span>', "", s)
    s = re.sub(r'<a class="btn[^>]*>[^<]*</a>', "", s)
    s = re.sub(r"<form[\s\S]*?</form>", "[Quote request form]", s)
    s = re.sub(r"<h[1-3][^>]*>", "\n\n### ", s)
    s = re.sub(r"<li[^>]*>", "\n- ", s)
    s = re.sub(r"<summary[^>]*>", "\n\n**Q: ", s)
    s = re.sub(r"</summary>", "**\n", s)
    s = re.sub(r"<(p|br|tr)[^>]*>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n\s*\n+", "\n\n", s)
    s = re.sub(r"\n\s*\n(\s*- )", r"\n\1", s)
    return "\n".join(line.strip() for line in s.strip().splitlines())


def llms_txt():
    pages = "\n".join(f"- [{p['h1'] or 'Home'}]({abs_url(p['path'])}): {p['desc']}" for p in PAGES)
    return f"""# {SITE['name']}

> {SITE['description']}

{SITE['name']} ({SITE['short']}) is an independent US travel agency operated by {SITE['legal_name']}, {SITE['street']}, {SITE['city']}, DE {SITE['postal']}, USA, established in {SITE['founded']}. It specializes in group air travel (10+ passengers) for sports teams, weddings, corporate events, schools, religious groups and tours, in all cabin classes. It is not an airline and is not affiliated with any airline.

Key facts:
- Phone (24/7 group reservations): {SITE['phone']}
- Email: {SITE['email']}
- Main website: {SITE['parent_url']}/
- This site: {SITE['url']}/
- Services: group flight quotes, group fare comparison across airlines, deposit-based seat holds, name-list management, multi-city and multi-origin groups, business and first-class groups.

## Pages

{pages}

## Optional

- [Full site content for LLMs]({SITE['url']}/llms-full.txt): all page text in one file
- [Main website]({SITE['parent_url']}/): deals, destinations, routes and travel blog
- [Sitemap]({SITE['url']}/sitemap.xml)
"""


def llms_full_txt():
    parts = [f"# {SITE['name']} — full site content\n\n> {SITE['description']}\n\nSource: {SITE['url']}/  ·  Generated: {TODAY}\n"]
    for p in PAGES:
        parts.append(f"\n---\n\n## {p['h1'] or 'Home'}\n\nURL: {abs_url(p['path'])}\n\n{text_of(p['body'])}\n")
    parts.append(f"\n---\n\n## Contact & company\n\n- Legal name: {SITE['legal_name']}\n- Address: {SITE['street']}, {SITE['city']}, DE {SITE['postal']}, USA\n"
                 f"- Phone (24/7): {SITE['phone']}\n- Email: {SITE['email']}\n- Main website: {SITE['parent_url']}/\n"
                 + "".join(f"- {n}: {u}\n" for n, u in SITE['social'])
                 + f"\n## Disclaimer\n\n{DISCLAIMER}\n")
    return "".join(parts)


def manifest():
    return json.dumps({
        "name": SITE["name"], "short_name": SITE["short"], "description": SITE["tagline"],
        "start_url": "/", "scope": "/", "display": "standalone", "lang": "en-US",
        "background_color": "#ffffff", "theme_color": SITE["theme"],
        "icons": [
            {"src": "/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "/assets/img/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
            {"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"},
        ],
    }, indent=2) + "\n"


def humans():
    return f"""/* TEAM */
Company: {SITE['legal_name']}
Brand: {SITE['name']}
Contact: {SITE['email']}
Phone: {SITE['phone']}
From: {SITE['city']}, Delaware, USA

/* SITE */
Last update: {TODAY}
Language: English (en-US)
Standards: HTML5, CSS3, schema.org JSON-LD
Hosting: Codeberg Pages
"""


def security():
    return f"""Contact: mailto:{SITE['email']}
Expires: {date.today().year + 1}-12-31T23:59:59.000Z
Preferred-Languages: en
Canonical: {SITE['url']}/.well-known/security.txt
"""


def write(rel, content):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print("wrote", rel)


def main():
    for p in PAGES:
        write((p["path"] or "") + "index.html", render(p))
    write("404.html", render_404())
    write("admin/index.html", render_admin())
    write("sitemap.xml", sitemap())
    write("robots.txt", robots())
    write("llms.txt", llms_txt())
    write("llms-full.txt", llms_full_txt())
    write("site.webmanifest", manifest())
    write("humans.txt", humans())
    write(".well-known/security.txt", security())


if __name__ == "__main__":
    main()
