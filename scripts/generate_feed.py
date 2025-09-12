import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import email.utils as eut

# Normas que monitorizamos
REGULATIONS = {
    "R53": "https://unece.org/transport/standards/transport/vehicle-regulations-wp29/un-regulations/addenda-1958-agreement-r53",
    "R148": "https://unece.org/transport/standards/transport/vehicle-regulations-wp29/un-regulations/addenda-1958-agreement-r148",
    "R149": "https://unece.org/transport/standards/transport/vehicle-regulations-wp29/un-regulations/addenda-1958-agreement-r149",
}

OUTPUT_FILE = "feed.xml"

def iso_to_rfc2822(dt):
    return eut.format_datetime(dt)

def fetch_pdf_link(url):
    try:
        r = requests.get(url, headers={"User-Agent": "UNECE-RSS-Bot"}, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"Error al obtener {url}: {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all("a", href=True):
        if a["href"].lower().endswith(".pdf"):
            href = a["href"]
            if href.startswith("/"):
                href = "https://unece.org" + href
            return href
    return None

def build_feed():
    fg = FeedGenerator()
    fg.id("https://unece.org/un-regulations-addenda-1958-agreement")
    fg.title("UNECE Regulations RSS (R53, R148, R149)")
    fg.link(href="https://unece.org/un-regulations-addenda-1958-agreement", rel="alternate")
    fg.language("en")
    fg.description("Feed automático de actualizaciones UNECE para R53, R148 y R149")

    now = datetime.utcnow()
    pub_date = iso_to_rfc2822(now)

    for reg, url in REGULATIONS.items():
        pdf_link = fetch_pdf_link(url)
        fe = fg.add_entry()
        fe.id(url)
        fe.title(f"UN Regulation {reg}")
        fe.link(href=url)
        desc = f"Última versión disponible en UNECE: {url}"
        if pdf_link:
            desc += f" (PDF: {pdf_link})"
        fe.description(desc)
        fe.pubDate(pub_date)

    return fg

def main():
    fg = build_feed()
    fg.rss_file(OUTPUT_FILE)
    print(f"Feed actualizado: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
