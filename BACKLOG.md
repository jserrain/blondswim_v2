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
