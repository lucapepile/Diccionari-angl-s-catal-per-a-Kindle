import os
import csv
from bs4 import BeautifulSoup, Tag
import lemminflect

from lemminflect import getAllInflections

# Elimina múltiples <br/> seguits arreu del document
def elimina_br_multiples(soup):
    br_tags = soup.find_all("br")
    i = 0
    while i < len(br_tags) - 1:
        current = br_tags[i]
        next_br = br_tags[i + 1]
        if next_br and current.find_next_sibling() == next_br:
            current.decompose()
            br_tags = soup.find_all("br")
            i = 0
        else:
            i += 1

# Elimina <h2> buits i <br/> finals innecessaris
def neteja_html(soup):
    for h2 in soup.find_all("h2"):
        if not h2.text.strip() and not h2.find():
            h2.decompose()
    for tag in soup.find_all(['div', 'li', 'ol']):
        while tag.contents and isinstance(tag.contents[-1], Tag) and tag.contents[-1].name == 'br':
            tag.contents[-1].decompose()
    elimina_br_multiples(soup)

# Obté totes les flexions de la paraula amb lemminflect
def obtenir_flexions(paraula):
    inflections = getAllInflections(paraula)
    formes = set()
    for formes_pos in inflections.values():
        formes.update(formes_pos)
    formes.discard(paraula)  # Elimina la paraula original
    return sorted(formes)

# Processa un fitxer HTML i el modifica amb formes flexionades automàtiques
def processa_html(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    neteja_html(soup)

    for idx_orth in soup.find_all("idx:orth"):
        paraula = idx_orth.text.strip()

        flexions = obtenir_flexions(paraula)
        if flexions:
            for infl in idx_orth.find_all("idx:infl"):
                infl.decompose()

            idx_infl = soup.new_tag("idx:infl")
            idx_orth.append(idx_infl)

            for flexio in flexions:
                idx_iform = soup.new_tag("idx:iform", value=flexio)
                idx_infl.append(idx_iform)

    with open(html_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(str(soup))

# Carpeta amb els fitxers HTML
html_folder = "parts_diccionari"

# Processa els fitxers HTML que comencen per "part_" i acaben en ".html"
for filename in sorted(os.listdir(html_folder)):
    if filename.startswith("part_") and filename.endswith(".html"):
        html_path = os.path.join(html_folder, filename)
        print(f"Processant: {html_path}")
        processa_html(html_path)

print("Processament complet!")

