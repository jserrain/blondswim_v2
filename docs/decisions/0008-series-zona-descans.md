# ADR-0008 — Sèries prescrites com a zona + descans

**Estat:** Acceptat

## Context
La planificació no depèn dels ritmes del nedador. Un nedador es pot planificar sense ritmes, i els ritmes canvien amb cada test CSS sense que calgui tocar el pla. Per això la sèrie es prescriu per zona.

## Decisió
Una sèrie es prescriu amb una zona del glossari (spec 000) i un descans. La sèrie no porta cap ritme ni cap temps. Cada nedador aplica el ritme que li correspon a la zona.

## Alternatives
- **Ritme absolut (temps objectiu per repetició):** descartat. Lliga la sèrie a ritmes concrets i obligaria a replanificar a cada test CSS.
- **Temps de sortida (cicle `c/`) com a prescripció:** descartat. El descans dependria de la velocitat del nedador: el més lent descansaria menys i l'estímul de la zona canviaria d'un nedador a un altre.

## Conseqüències
- Com s'obtenen els ritmes de cada zona ho decideix la spec 004.
- El pla emmagatzema sempre el descans (`d/`). A A0–A2, el render mostra el cicle (`c/` = ritme + descans), calculat amb els ritmes vigents. A A3, TOLA, MPLA i Vel mostra `d/`.
- A TOLA, MPLA i Vel, el descans es pot prescriure com a ràtio treball:descans (`d/×N`, glossari §3). La conversió a segons és de la spec 004.
- Si els cicles `c/` de les dades importades es converteixen i com es fa ho decideix la spec 002.
