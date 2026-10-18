# ADR-0005 — Biblioteca d'exercicis de tècnica, confeccionada pel coach

**Estat:** Acceptat

## Context
El contingut tècnic és diferent per a cada nedador i depèn dels seus estils preferents i de les seves proves objectiu.

## Decisió
- El coach confecciona una biblioteca comuna d'exercicis de tècnica, ordenats per estil.
- El nedador fa exercicis de tècnica orientats als seus estils preferents i a les seves proves objectiu.
- El sistema indica:
  - el bloc de tècnica;
  - el total de metres de la tècnica.
- La durada surt de cada exercici i d'altres variables; no la planifica el sistema.
- La tècnica és una sola part de la sessió, en la posició que fixa l'ADR-0004. No es desdobla.
- El coach revisa i ajusta els exercicis.

## Alternatives
- Tècnica generada per l'LLM: descartat, perquè seria contingut sense control del coach.

## Conseqüències
- La spec 002b passa a ser «Biblioteca d'exercicis de tècnica».
- Abans de planificar un nedador, cal que la biblioteca cobreixi els estils que necessita.
