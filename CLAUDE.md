@AGENTS.md

## Específic de Claude Code
- No llegeixis mai `.env` ni `~/.secrets`.
- Per a decisions de disseny, proposa primer i espera confirmació.
# BlondSwim v2.0

Planificador d'entrenaments de natació per a 4 nedadors màsters.
Pipeline en Python: funcions deterministes + crides a LLM només
en punts de judici.

## Regles de treball
- Spec-driven: cap codi sense especificació a docs/spec/.
- Si falta una definició o dues regles entren en conflicte:
  ATURA'T i pregunta. No inventis cap solució.
- La v1 (../ws_blondswim) és NOMÉS DE LECTURA. Mai la modifiquis.
  Cap codi de v1 entra a v2 sense passar per l'auditoria.

## Fase actual
0 — Inventari de regles i mòduls de v1 → docs/inventari/

## Documentació
- docs/inventari/  → inventari de v1
- docs/spec/       → especificació (fase 1)
- docs/decisions/  → decisions preses

