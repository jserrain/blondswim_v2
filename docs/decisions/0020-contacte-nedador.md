# ADR-0020 — Contacte del nedador

**Estat:** Acceptat. Substitueix l'ADR-0019 i l'ADR-0018. Esmena RN-032 i RN-035; RN-033 i RN-034 continuen retirades (spec 001).

## Context
El sistema fa servir el correu només per a notificacions; no identifica el nedador (l'id és l'UUID, ADR-0014). Normalitzar-lo o validar-lo amb una expressió regular estricta (ADR-0019) i verificar-ne l'existència (ADR-0018) afegeix complexitat i tampoc no garanteix que sigui rebible.
- RFC 5321: la part local d'una adreça pot distingir majúscules; passar-la a minúscules pot canviar l'adreça.
- OWASP: no s'han de fer transformacions pròpies de cada proveïdor (punts, etiquetes després de «+»).

## Decisió
> **El correu electrònic és un camp de contacte opcional. El sistema no corregeix, normalitza ni verifica que el correu sigui rebible. Si s'introdueix un correu incorrecte, les notificacions no es podran lliurar; la responsabilitat és de qui l'ha introduït, que l'haurà de modificar. El sistema només comprova que el correu contingui el símbol @ i que el domini tingui un punt.**

- `correu`: opcional (absent o `null` = sense correu). Si hi és, es desa exactament tal com s'ha entrat (majúscules i espais als extrems inclosos).
- Format (ERROR si no es compleix), avaluat sense tenir en compte els espais en blanc dels extrems: conté una `@`, la part d'abans no és buida, el domini (després de la darrera `@`) no és buit, conté un punt i no té espais en blanc; cap espai en blanc al mig. Sense expressió regular estricta i sense consultes de xarxa.
- Unicitat: si hi ha correu, és únic entre tots els nedadors (arxivats inclosos). La comparació és en minúscules i sense espais en blanc als extrems; el valor desat no canvia.
- El correu no identifica el nedador: la clau és l'id (ADR-0014). S'usa només per a notificacions.
- No hi ha verificació: ni correu de confirmació, ni MX, ni SMTP. Desapareix `correu_verificat`.
- `mobil`: obligatori (no buit després de treure'n els espais en blanc als extrems: espais, tabuladors i salts de línia). No intervé en cap regla de planificació, no és únic i no té format.
- `canal_preferent` (`correu` o `mobil`): absent o `null` genera un avís (RN-035); un valor fora de `correu` i `mobil` és un error de format; `correu` sense correu genera un avís (RN-035).
- La unicitat només s'aplica a correu i alias. Cap identificador del sistema no deriva del correu ni del mòbil.

## Alternatives
- **Normalització i expressió regular completa (ADR-0019):** descartada; transforma l'adreça introduïda, rebutja adreces vàlides i no garanteix que sigui rebible.
- **Verificació amb un codi per correu (ADR-0018):** descartada; afegeix un canal d'enviament i un flux de confirmació, i el camp `correu_verificat`, a canvi d'una dada que no bloqueja res.
- **Llibreria de validació de correus:** descartada; afegiria una dependència per a una comprovació que és només de caràcters.

## Conseqüències
- RN-032 porta el format mínim, la unicitat sense distingir majúscules i el valor original; RN-035 afegeix el cas `canal_preferent` = `correu` sense correu. RN-033 i RN-034 continuen retirades i `data/avisos.jsonl` no porta mòbils.
- Un correu amb errors tipogràfics s'accepta i es desa tal qual; el coach el pot modificar. El sistema no detecta que no es pugui lliurar.
- `correu_verificat` deixa d'existir al model i als fitxers; la spec de verificació del mapa queda retirada.
- La comprovació del format és només per caràcters, sense xarxa.
- Quines dades de contacte poden arribar a un LLM ho fixa l'ADR pendent de dades cap a l'LLM.
- La supressió de dades personals (correu i mòbil) és al pendent «ADR de dades personals: supressió» (`docs/estat.md`).
