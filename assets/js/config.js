/*
 * Site configuration.
 * leadsEndpoint: the Google Apps Script "Web app" URL from backend/Code.gs
 * (see backend/README.md). While it is empty, the quote form falls back to
 * opening an email to the address below.
 * forgeApi / repo / branch: where the blog admin commits posts (Codeberg).
 */
window.AGT_CONFIG = {
  leadsEndpoint: "https://script.google.com/macros/s/AKfycbxFFUzm6765GPehOl5NEBzXdLhXCDbs76YWH0SwRx2rx_9cSRrjiRvC2Z5sP_GFYitUdA/exec",
  email: "info@airlinesgrouptravel.com",
  phone: "+1-888-609-1015",
  forgeApi: "https://codeberg.org/api/v1",
  repo: "airlinesgrouptravel/pages",
  branch: "pages"
};
