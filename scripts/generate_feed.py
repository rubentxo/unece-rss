import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import json
from datetime import datetime
import os

# URLs base para raspar
REGULATIONS_BASE = {
    "R53": "https://unece.org/transport/vehicle-regulations-wp29/standards/addenda-1958-agreement-regulations-41-60",
    "R148": "https://unece.org/transport/vehicle-regulations-wp29/standards/addenda-1958-agreement-regulations-141-160",
    "R149": "https://unece.org/transport/vehicle-regulations-wp29/standards/addenda-1958-agreement-regulations-141-160"
}

SEEN_FILE = "seen_links.json"

# Cargar PDFs ya vistos o inicializar vacío
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_links = json.load(f)
else:
    seen_links = []

fg = FeedGenerator()
fg.title("UNECE Regulations Updates")
fg.link(href="https://github.com/TU_USUARIO/unece-rss", rel="self")
fg.description("Actualizaciones de las normas UNECE R53, R148 y R149")
fg.language("en")

new_links = []

for reg, url in REGULATIONS_BASE.items():
    try:
        r = requests.get(url, headers={"User-Agent": "UNECE-RSS-Bot"}, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"Error al obtener {url}: {e}")
        continue

    soup = BeautifulSoup(r.text, "html.parser")

    # Buscar enlaces a PDFs o con el nombre de la norma
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.endswith(".pdf") or any(reg in href for reg in ["R53","R148","R149"]):
            if href.startswith("/"):
                href = "https://unece.org" + href
            if href in seen_links:
                continue
            title = a.get_text(strip=True) or f"{reg} update"
            fe = fg.add_entry()
            fe.title(title)
            fe.link(href=href)
            fe.pubDate(datetime.utcnow())
            new_links.append(href)

# Guardar links nuevos como vistos
seen_links.extend(new_links)
with open(SEEN_FILE, "w") as f:
    json.dump(seen_links, f)

# Guardar feed RSS
fg.rss_file("feed.xml")
print(f"Feed generado con {len(new_links)} nuevas entradas")
