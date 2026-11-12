# Contracte: CLI d'importació

**Spec**: [../spec.md](../spec.md) § Ordres, § Flux, § Informe · **Casos d'ús**: [casos-d-us.md](casos-d-us.md)

## Ordres

```text
blondswim importar fitxa <camí> [--alta] [--confirma]
blondswim importar calendari --temporada <AAAA-AA> [--confirma]
blondswim importar inscripcions --temporada <AAAA-AA> --alias <alias> [--confirma]
```

Implementació: `argparse` a `interfaces/cli.py`. Un argument incorrecte és un error d'ús d'`argparse` (codi 2 de la biblioteca, abans de cap importació) i no genera `ResultatImportacio`.

## Codi de sortida

| Codi | Quan |
|---|---|
| `0` | `desat` |
| `1` | alguna incidència `bloquejant` |
| `2` | `pendent_confirmacio` |

La CLI només tradueix `ok/desat/pendent_confirmacio`; no avalua cap regla (CA-002-50).

## Informe

Per fitxer, per la sortida estàndard:

```text
<ruta> — <files llegides> files
<fila>:<columna|clau>  <bloquejant|avís>  <codi>  <valor>  <missatge>  → <acció>
...
<n> bloquejants, <m> avisos — <desat | pendent de confirmar | no desat>
```

- Les incidències van ordenades per fila (o per clau). Les d'origen `fitxer` van al principi, amb `-` en lloc de `fila:columna`.
- El valor només es mostra a la incidència que l'afecta (spec 002, § Dades sensibles).
- L'estat final és `desat` (codi 0), `pendent de confirmar` (codi 2) o `no desat` (codi 1).
