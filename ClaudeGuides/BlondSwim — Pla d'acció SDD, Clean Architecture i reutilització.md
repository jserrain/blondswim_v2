# BlondSwim — Pla d'acció: SDD, Clean Architecture i reutilització

Oct 14, 2026 · @Jep

## Resum

Els tres eixos encaixen i es reforcen, però l'ordre del pla anterior canvia. Amb spec-driven development (SDD), l'especificació governa tota la resta: l'arquitectura se'n deriva, i la reutilització es jutja comparant el codi actual amb l'especificació.

Ordre: especificació → auditoria → arquitectura → implementació.

## 1. Spec-driven development

L'especificació passa de ser una peça aïllada (`regles.yaml`) a una jerarquia de tres nivells:

- **Constitució** (`docs/constitucio.md`): principis no negociables. Per exemple: les regles dures es comproven amb codi; el LLM no inventa, declara conflictes; el domini no fa IO.
- **Especificació del domini**: glossari, model de periodització, regles.
- **Especificacions per funcionalitat**: calendari, mesocicles, sessió, verificador, exportació. Cadascuna amb criteris d'acceptació comprovables.

Cicle per a cada funcionalitat: especificació → pla tècnic → tasques → implementació → tests que verifiquen els criteris. Una eina d'SDD (per exemple, GitHub Spec Kit amb Claude CLI) ja estructura aquest cicle; sense eina també funciona amb fitxers markdown i disciplina.

| Risc | Prevenció |
| --- | --- |
| Especificació massa gran abans de començar | Començar només amb constitució, glossari i una funcionalitat (mesocicles) |
| Criteris vagues ("la sessió ha de ser equilibrada") | Format verificable: QUAN la fase és X, LLAVORS el volum d'intensitat ≤ Y% |
| L'especificació i el codi divergeixen | Tot canvi comença per l'especificació; cap canvi de codi afegeix regles sense canvi d'especificació |
| Tornar a apilar regles reactivament | Un resultat dolent obre una revisió de l'especificació, no un pegat |

## 2. Clean Architecture dimensionada

Tres capes, no quatre:

| Capa | Contingut |
| --- | --- |
| domain | Entitats i regles pures: periodització, estructura de sessió, validador |
| application | Etapes del pipeline com a casos d'ús, i els `Protocol` (ports) |
| infrastructure | JSON, Excel, llama.cpp, LLM al núvol, CLI |

Es deixa fora conscientment: capa separada d'interface adapters, DTOs per capa, injecció de dependències amb framework. S'afegirà a la fase de clubs si cal.

Afegit clau: un test d'arquitectura (per exemple, `import-linter`) que falli si `domain` importa d'`infrastructure`. Sense això, la regla de dependències es degrada a mesura que l'agent genera codi.

## 3. Avaluació de reutilització

Es fa després de l'especificació: el criteri és "compleix l'especificació?", no "funciona?".

Criteris per classificar cada mòdul:

1. Barreja lògica i IO? → cal separar-lo.
2. Depèn de regles de la cadena antiga? → reescriure.
3. Té tests o es pot caracteritzar amb tests? → candidat a reutilitzar.
4. Coincideix amb el glossari i el model nous? → reutilitzar.

Previsió orientativa, pendent de confirmar amb el codi:

| Peça | Decisió prevista |
| --- | --- |
| Dades: JSON per nedador, catàleg de competicions, ritmes, tests CSS | Reutilitzar |
| Càlculs purs: ritmes, zones, temps | Reutilitzar |
| Lectura del registre d'entrenaments 2025-26 | Reutilitzar |
| Client de llama.cpp | Adaptar: darrere un `LLMClient` |
| Exportació a Excel | Adaptar: separar format i dades |
| Verificador | Adaptar: comprovacions al domini |
| Cadena de regles | Reescriure |
| Prompts amb regles incrustades | Reescriure |
| Orquestració del generador de sessions | Reescriure |

Estratègia: nucli nou, perifèria aprofitada. Domini i regles es fan de nou a partir de l'especificació; adaptadors i dades es migren. Patró strangler: l'estructura nova conviu amb la vella, es migra un mòdul cada cop amb tests de caracterització, i el codi vell s'esborra quan ja no el fa servir ningú.

## Pla revisat

- [ ] Congelar i inventariar: regles i mòduls existents, en dues llistes
- [ ] Constitució + especificació del domini: glossari, model, regles classificades, conflictes resolts
- [ ] Auditoria de reutilització contra l'especificació: reutilitzar / adaptar / reescriure / descartar
- [ ] Esquelet Clean amb test d'arquitectura i casos golden buits
- [ ] Cicle SDD per funcionalitat: calendari → mesocicles → sessió → verificador → exportació, migrant les peces reutilitzables
- [ ] Retirar el codi vell

El pas crític és el segon: amb una especificació del domini ben feta, la resta són passos mecànics que un agent fa bé.
