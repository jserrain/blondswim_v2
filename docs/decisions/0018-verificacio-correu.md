# ADR-0018 — Verificació del correu

**Estat:** Acceptat. Complementa l'ADR-0019.

## Context
L'ADR-0019 fixa el format del correu (RN-032) però no comprova que l'adreça existeixi ni que estigui activa. Una adreça amb el format correcte pot no arribar a ningú.

## Decisió
- Verificar que l'adreça existeix i és activa (s'envia un codi per correu i el nedador el confirma) és una spec pròpia futura (`docs/mapa_specs.md`).
- Des de la spec 001, el nedador té `correu_verificat`: booleà, obligatori, `false` en crear-lo.
- Modificar el correu torna `correu_verificat` a `false` només si el correu normalitzat canvia; un canvi només de majúscules o d'espais el conserva.
- Cap operació de la spec 001 el posa a `true`: només ho farà la spec de verificació.

## Alternatives
- **Esperar la spec de verificació per afegir el camp:** descartat; el camp és obligatori i, si s'afegís després, caldria migrar tots els fitxers de nedador.
- **Verificar dins de la spec 001:** descartat; afegiria un canal d'enviament i un flux de confirmació a una spec que és només model de domini.

## Conseqüències
- El fitxer `nedador.json` porta `correu_verificat` (spec 001, data model i contracte).
- La verificació no bloqueja res: un correu no verificat no impedeix planificar.
- Les variants d'una mateixa bústia (p. ex. les de Gmail) queden al `BACKLOG.md`.
