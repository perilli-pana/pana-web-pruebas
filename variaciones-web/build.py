# Arma las variaciones a partir de src.html:
#   index.html            -> para abrir local (usa fonts/ e img/ de esta carpeta)
#   pana-variaciones.html -> todo embebido (fuentes e imágenes), para la presentación online
# Correr: python3 build.py
import base64, os, re

here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "src.html"), encoding="utf-8").read()
paths = open(os.path.join(here, "_paths.txt"), encoding="utf-8").read().split("\n")
for key, d in zip(["P", "A1", "N", "A2"], paths):
    src = src.replace("{{%s}}" % key, d)

head = '<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
title, rest = src.split("</title>", 1)
local = head + title + "</title>\n" + rest.replace("<style>", "<style>", 1)
local = local.replace("</style>", "</style>\n</head>\n<body>", 1) + "\n</body>\n</html>\n"
open(os.path.join(here, "index.html"), "w", encoding="utf-8").write(local)

MIME = {".woff2": "font/woff2", ".jpg": "image/jpeg"}
def inline(m):
    rel = m.group(0)
    data = open(os.path.join(here, rel), "rb").read()
    return "data:%s;base64,%s" % (MIME[os.path.splitext(rel)[1]], base64.b64encode(data).decode())
embedded = re.sub(r"(?:fonts|img)/[\w.-]+\.(?:woff2|jpg)", inline, src)
open(os.path.join(here, "pana-variaciones.html"), "w", encoding="utf-8").write(embedded)
print("ok", len(local), len(embedded))
