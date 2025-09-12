import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

URL = "https://unece.org/un-regulations-addenda-1958-agreement#"

response = requests.get(URL)
soup = BeautifulSoup(response.text, "lxml")

fg = FeedGenerator()
fg.id("https://unece.org/")
fg.title("UNECE Regulations (R53, R148, R149)")
fg.link(href=URL, rel="alternate")
fg.language("en")

# Buscar enlaces en la página
for link in soup.find_all("a", href=True):
    text = link.get_text(strip=True)
    if any(reg in text for reg in ["R53", "R148", "R149"]):
        fe = fg.add_entry()
        fe.id(link["href"])
        fe.title(text)
        fe.link(href=link["href"])

# Guardar el feed.xml en la raíz del repo
fg.rss_file("feed.xml")
