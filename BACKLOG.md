# Backlog de millores

Idees per a la propera versió. Una idea per fila. Només passa a la versió nova el que està en **Incorporat** després de provar-ho a l'aigua.

**Estats:** Pendent → Provant → Incorporat / Descartat
**Prioritat:** Alta / Mitjana / Baixa

## Resum

| # | Data | Idea | Estat | Prioritat |
|---|------|------|-------|-----------|
| 1 | 25/10/2026 | Sèrie USRPT: crol a ritme de cursa 100 L | Pendent | Alta |
| 2 | 25/10/2026 | Definir patrons d'entrenament per enriquir el model | Pendent | Mitjana |
| 3 | 25/10/2026 | Seguretat quan l'app s'exposi a un endpoint | Pendent | Mitjana |
| 4 | 28/10/2026 | Replanificar a mitja temporada per canvi de dies o volum | Pendent | Mitjana |
| 5 | 29/10/2026 | Historial de millors marques | Pendent | Baixa |
| 6 | 29/10/2026 | Validació i verificació del correu (format, domini, bústia activa) | Pendent | Baixa |
| 7 | 29/10/2026 | Parcials i pacing de cursa | Pendent | Mitjana |
| 8 | 29/10/2026 | Conversió de marques 25 m ↔ 50 m | Pendent | Mitjana |
| 9 | 29/10/2026 | Marques mínimes amb caducitat | Pendent | Mitjana |
| 10 | 29/10/2026 | Categoria per edat (data de naixement) | Pendent | Baixa |
| 11 | 29/10/2026 | Tipus de cronometratge | Pendent | Baixa |
| 12 | 29/10/2026 | ADR de dades personals: supressió | Pendent | Mitjana |

## Notes

### 1. Sèrie USRPT: crol a ritme de cursa 100 L

- **Font:** mètode USRPT (Brent Rushall)
- **Objectiu:** millorar la velocitat de braçada i el ritme de 100 m lliures
- **On encaixa:** bloc específic de velocitat
- **Estat:** Pendent
- **Prioritat:** Alta
- **Detall:**
  - 20–30 × 25 m al ritme objectiu de 100 m lliures, amb 15–20 s de descans.
  - Regla del fallo: si no arribes al temps, et saltes la repetició següent. Amb 2–3 fallos s'acaba la sèrie.
  - Apuntar a Resultat: temps objectiu, repeticions aconseguides i on apareix el primer fallo.
- **Resultat:** —

### 2. Definir patrons d'entrenament per enriquir el model

- **Font:** idea pròpia
- **Objectiu:** tenir sessions tipus definides per objectiu, reutilitzables a la propera versió
- **On encaixa:** estructura del pla / model
- **Estat:** Pendent
- **Prioritat:** Mitjana
- **Detall:** primer patró a definir, una sessió per millorar la freqüència de braçada.
  Exemple proposat (per provar i ajustar):
  - Escalfament: 400 m variat + 4 × 50 m progressius
  - 8 × 25 m crol amb metrònom (tempo trainer), 2 a cada freqüència, accelerant el cicle pas a pas. Descans 20 s
  - 6 × 50 m a freqüència alta mantenint el nombre de braçades per llarg. Descans 30 s
  - 8 × 15 m sprint de freqüència màxima, sortida des de l'aigua. Descans 45 s
  - Tornada a la calma: 200 m suau

  Per a cada patró, registrar: objectiu, sèrie principal, variable de control (cicle/s, braçades per llarg) i criteri d'èxit.
- **Resultat:** —

### 3. Seguretat quan l'app s'exposi a un endpoint

- **Font:** idea pròpia, inspirada en l'autorització de GitHub des del mòbil
- **Objectiu:** protegir les dades de cada nedador quan l'app deixi de ser només una CLI local
- **On encaixa:** ADR propi i spec de l'endpoint, quan n'hi hagi
- **Estat:** Pendent
- **Prioritat:** Mitjana
- **Detall:**
  - **Autenticació delegada:** login amb un proveïdor extern (OIDC, p. ex. Google) o passkeys. El segon factor i l'aprovació al mòbil els aporta el proveïdor; l'app no guarda contrasenyes.
  - **Autorització per nedador a cada petició:** el coach veu els seus nedadors; cada nedador, només el seu espai. És la protecció real contra l'IDOR; l'UUID (ADR-0014) només n'és una capa addicional.
  - **Flux de dispositiu per a la CLI**, si ha de parlar amb el servidor: la CLI mostra un codi, s'aprova des del mòbil i rep un token que caduca.
  - **Model d'identitat en tres conceptes:**
    - *Nedador:* id intern UUID v4 (ADR-0014), sense cap dada personal, immutable.
    - *Compte d'usuari:* qui inicia sessió, enllaçat amb el proveïdor d'identitat per `iss` + `sub`, mai pel correu.
    - *Contacte:* correu i mòbil com a atributs del compte, només si hi ha un ús que ho requereixi (minimització, RGPD).
    - Relació compte → nedadors amb rol (coach / nedador), que és la base de l'autorització.
  - Descartat: id derivat d'un hash de l'UUID amb el correu o el mòbil (no afegeix unicitat, trenca la immutabilitat de l'id i hi introdueix una dada personal).
  - Fora d'abast: notificacions push pròpies, gestió de contrasenyes i 2FA propis.
- **Resultat:** —

### 4. Replanificar a mitja temporada per canvi de dies o volum

- **Font:** G1 r2 de la spec 001 (28/10/2026)
- **Objectiu:** que un canvi de `dies_entrenament` o `volum_setmanal` a mitja temporada torni a planificar amb la configuració nova
- **On encaixa:** spec 005 (CA-001-84)
- **Estat:** Pendent
- **Prioritat:** Mitjana
- **Detall:**
  - La 001 permet el canvi; la planificació passada es conserva com a registre.
  - Per decidir a la 005: des de quina setmana s'aplica la configuració nova.
  - Altres canvis del nedador (filtre de validació, camps immutables, operacions de modificació, arxivar i desarxivar) són de la 001.
- **Resultat:** —

### 5. Historial de millors marques

- **Font:** decisió B de la spec 001 (29/10/2026)
- **Objectiu:** poder veure l'evolució d'una marca, no només l'última
- **On encaixa:** spec futura de progressió (007); ara `millors_registres` desa un sol registre per prova i piscina (RN-007)
- **Estat:** Pendent
- **Prioritat:** Baixa
- **Detall:** els tests CSS ja es desen tots; els millors registres no.
- **Resultat:** —

### 6. Validació i verificació del correu (format, domini, bústia activa)

- **Font:** ADR-0017 (29/10/2026)
- **Objectiu:** assegurar que el correu del nedador existeix i arriba
- **On encaixa:** spec d'importació (002) o d'un futur flux de contacte
- **Estat:** Pendent
- **Prioritat:** Baixa
- **Detall:**
  - ADR-0017 només fixa un format simple (RN-032), sense llibreries externes.
  - Pendent: format complet, comprovació del domini i bústia activa.
- **Resultat:** —

### 7. Parcials i pacing de cursa

- **Font:** G1 de la spec 001
- **Objectiu:** registrar parcials de cursa i comparar-los amb el ritme previst
- **On encaixa:** spec 007
- **Estat:** Pendent
- **Prioritat:** Mitjana
- **Detall:** la 001 només desa els parcials informatius dels tests CSS (`detall_400`, `detall_200`).
- **Resultat:** —

### 8. Conversió de marques 25 m ↔ 50 m

- **Font:** idea pròpia
- **Objectiu:** comparar marques de piscines diferents
- **On encaixa:** spec 004 (zones i càrrega) o 003 (periodització)
- **Estat:** Pendent
- **Prioritat:** Mitjana
- **Detall:** cal definir el factor de conversió i qui el pot ajustar (principi V).
- **Resultat:** —

### 9. Marques mínimes amb caducitat

- **Font:** idea pròpia
- **Objectiu:** fixar marques mínimes per competició o categoria, amb data de caducitat
- **On encaixa:** spec 003
- **Estat:** Pendent
- **Prioritat:** Mitjana
- **Detall:** no es modela a la 001.
- **Resultat:** —

### 10. Categoria per edat (data de naixement)

- **Font:** idea pròpia
- **Objectiu:** derivar la categoria del nedador per l'edat
- **On encaixa:** spec futura; per això caldria la data de naixement, que és una dada personal
- **Estat:** Pendent
- **Prioritat:** Baixa
- **Detall:** la 001 no desa la data de naixement. Afecta l'ADR de supressió (nota 12).
- **Resultat:** —

### 11. Tipus de cronometratge

- **Font:** idea pròpia
- **Objectiu:** distingir marques manuals de marques electròniques
- **On encaixa:** `millors_registres` i tests CSS, en una spec futura
- **Estat:** Pendent
- **Prioritat:** Baixa
- **Detall:** la 001 no registra el tipus de cronometratge.
- **Resultat:** —

### 12. ADR de dades personals: supressió

- **Font:** G0 i G1 de la spec 001; `docs/estat.md`
- **Objectiu:** decidir com es compleix el dret de supressió (RGPD, art. 17) davant la regla d'arxivar sense esborrar (RN-004)
- **On encaixa:** ADR propi, quan un nedador ho demani
- **Estat:** Pendent
- **Prioritat:** Mitjana
- **Detall:**
  - Afecta `nedador.json` (correu i mòbil) i el registre d'avisos `data/avisos.jsonl`, que només creix.
  - Cap avís vigent no porta el correu ni el mòbil (RN-034 retirada).
- **Resultat:** —

## Plantilla per a una nota nova

```markdown
### N. <Idea>

- **Font:**
- **Objectiu:**
- **On encaixa:**
- **Estat:** Pendent
- **Prioritat:**
- **Detall:**
- **Resultat:** —
```
