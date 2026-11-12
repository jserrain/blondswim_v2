# Contracte: casos d'ús i ports de la importació

**Spec**: [../spec.md](../spec.md) § Contracte del cas d'ús · **Model**: [../data-model.md](../data-model.md)

## Casos d'ús (`application/importacio`)

```text
importar_calendari(peticio: PeticioCalendari, repositoris, rellotge, registre) -> ResultatImportacio
importar_inscripcions(peticio: PeticioInscripcions, repositoris, rellotge, registre) -> ResultatImportacio
importar_fitxa(peticio: PeticioFitxa, repositoris, generador_id, rellotge, registre) -> ResultatImportacio
```

- No fan I/O: reben els repositoris i els ports per injecció.
- Retornen sempre un `ResultatImportacio`; mai llancen excepcions per errors de dades.
- Un error bloquejant no desa res, ni amb `confirma`.
- Els avisos que requereixen confirmació es registren només en desar amb `confirma`, amb `decisio: confirmat`.

## Servei (`application/importacio/serveis.py`)

```text
ServeisImportacio.fitxa(cami: str, alta: bool, confirma: bool) -> ResultatImportacio
ServeisImportacio.calendari(temporada: str, confirma: bool) -> ResultatImportacio
ServeisImportacio.inscripcions(temporada: str, alias: str, confirma: bool) -> ResultatImportacio
```

- Deriva la ruta d'entrada (`<arrel>/<temporada>/calendari.csv`, `<arrel>/<temporada>/inscripcions_<alias>.csv`) i crida el port `LectorCsv`.
- Converteix `ErrorLectura` en una incidència `fitxer` (CA-002-02, 03, 55, 59).
- Un nom de temporada que no segueix RN-031 és una incidència `fitxer` i no es llegeix res.
- Només retorna `ResultatImportacio` (tipus primitius): és l'única API que veu la CLI.

## Ports nous (`application/ports.py`)

```text
class LectorCsv(Protocol):
    def taula(self, ruta: str, capcalera: tuple[str, ...]) -> ContingutTaula: ...
    def parells(self, ruta: str) -> ContingutParells: ...
```

Les dues operacions llancen `ErrorLectura`. Implementació: `infrastructure/csv/lector.py` (R1). Només obre el fitxer, comprova codificació, capçalera i que hi hagi files, i retorna text; no conté regles ni importa `domain`.

## Ports existents que es reutilitzen
`RepositoriNedadors`, `RepositoriCataleg`, `GeneradorId`, `RegistreAvisos`, `Rellotge`. `RegistreAvisos.afegeix` documenta `decisio` com `confirmat` o `None` (ja no `rebutjat`).

## Nivells i codis
- `nivell`: `bloquejant` o `avís`. ERROR i AVÍS de la spec hi mapegen 1:1.
- `codi`: una RN (`RN-008`, `RN-036`…), `FORMAT-<camp>`, `FORMAT-fila` (nombre de camps incorrecte) o `FORMAT-fitxer`.
- Els nivells i els codis viuen als casos d'ús (constitució IX), no a la vista.
