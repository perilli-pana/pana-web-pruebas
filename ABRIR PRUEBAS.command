#!/bin/bash
cd "$(dirname "$0")"
lsof -ti:4417 | xargs kill 2>/dev/null
python3 -m http.server 4417 >/dev/null 2>&1 &
sleep 1
open -a "Google Chrome" "http://localhost:4417/?fx=moire#1"
echo "Pruebas abiertas en Chrome. Cerrá esta ventana cuando termines."
wait
