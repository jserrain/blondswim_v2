"""Resultat de la validació (research R5) i validador únic."""

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass

from blondswim.domain.cataleg import Cataleg
from blondswim.domain.definicions import Temporada, es_prova_oficial
from blondswim.domain.derivats import test_vigent
from blondswim.domain.inscripcions import Inscripcions
from blondswim.domain.nedador import MillorRegistre, Nedador
from blondswim.domain.valors import (
    BLANCS,
    Canal,
    Classe,
    CodiTemporada,
    Correu,
    IdNedador,
    Piscina,
    Prioritat,
)


@dataclass(frozen=True)
class ErrorValidacio:
    """`nedador`: l'alias, o l'UUID si no n'hi ha o el fitxer no es pot llegir.

    `implicats`: en una col·lisió d'unicitat, tots els nedadors que la formen.
    """

    rn: str
    fitxer: str
    camp: str
    valor: object
    missatge: str
    accio: str = ""
    nedador: str = ""
    implicats: tuple[IdNedador, ...] = ()


@dataclass(frozen=True)
class Avis:
    rn: str
    fitxer: str
    camp: str
    valor: object
    missatge: str
    accio: str = ""
    nedador: str = ""


@dataclass(frozen=True)
class Resultat:
    errors: tuple[ErrorValidacio, ...] = ()
    avisos: tuple[Avis, ...] = ()

    @property
    def es_valid(self) -> bool:
        return not self.errors


class ErrorCarrega(Exception):
    """La càrrega ha trobat un o més errors; els acumula tots."""

    def __init__(self, errors: tuple[ErrorValidacio, ...]) -> None:
        super().__init__("; ".join(f"{e.fitxer}: {e.camp}: {e.missatge}" for e in errors))
        self.errors = errors


class CatalegAbsent(ErrorCarrega):
    """No hi ha catàleg per a la temporada. La càrrega del sistema només el demana si hi ha
    inscripcions d'aquella temporada, i aleshores exclou els nedadors afectats."""

    def __init__(self, temporada: CodiTemporada) -> None:
        self.temporada = temporada
        super().__init__(
            (
                ErrorValidacio(
                    "format",
                    fitxer_cataleg(temporada),
                    "",
                    None,
                    f"falta el catàleg de la temporada {temporada}",
                    "Importa el calendari d'aquella temporada",
                ),
            )
        )


@dataclass(frozen=True)
class Identitat:
    """Els dos camps que compten per a la unicitat (D1), llegits com a text cru.

    Un camp `None` (absent, `null` o il·legible) no participa a la unicitat d'aquell camp.
    """

    correu: str | None
    alias: str | None

    @property
    def clau_correu(self) -> str | None:
        """Clau de comparació del correu (RN-032); el valor no canvia."""
        return None if self.correu is None else Correu(self.correu).clau

    @classmethod
    def de(cls, nedador: Nedador) -> "Identitat":
        return cls(
            correu=None if nedador.correu is None else nedador.correu.valor,
            alias=None if nedador.alias is None else str(nedador.alias),
        )


def fitxer_nedador(id_nedador: IdNedador) -> str:
    return f"nedadors/{id_nedador}/nedador.json"


def fitxer_cataleg(temporada: CodiTemporada) -> str:
    return f"competicions/{temporada}.json"


def carpeta_temporada(id_nedador: IdNedador, temporada: str) -> str:
    return f"nedadors/{id_nedador}/temporades/{temporada}"


def fitxer_inscripcions(id_nedador: IdNedador, temporada: CodiTemporada) -> str:
    return f"{carpeta_temporada(id_nedador, str(temporada))}/inscripcions.json"


def valida_inscripcions(
    id_nedador: IdNedador,
    qui: str,
    temporada: CodiTemporada,
    inscripcions: Inscripcions,
    cataleg: Cataleg,
) -> Resultat:
    """Validació creuada amb el catàleg i la temporada: RN-011, RN-013, RN-015 i RN-030.

    RN-012, RN-014 i RN-016 els garanteix la construcció de les `Inscripcions`.
    """
    fitxer = fitxer_inscripcions(id_nedador, temporada)
    periode = Temporada.de_codi(str(temporada))
    accio = "Corregeix el fitxer d'inscripcions"
    errors: list[ErrorValidacio] = []

    def error(rn: str, camp: str, valor: object, missatge: str) -> None:
        errors.append(ErrorValidacio(rn, fitxer, camp, valor, missatge, accio, qui))

    for i, participacio in enumerate(inscripcions.participacions):
        camp = f"participacions.{i}"
        competicio = cataleg.competicio(participacio.id_competicio)
        if competicio is None:
            error(
                "RN-011",
                f"{camp}.id_competicio",
                participacio.id_competicio,
                f"la competició {participacio.id_competicio!r} no és al catàleg de {temporada}",
            )
            continue
        for dia in competicio.dates:
            if not periode.inici <= dia <= periode.fi:
                error(
                    "RN-013",
                    f"{camp}.id_competicio",
                    dia,
                    f"la competició {competicio.id!r} té la data {dia.isoformat()} "
                    f"fora de la temporada {temporada}",
                )
        for j, inscripcio in enumerate(participacio.proves):
            prova = f"{inscripcio.prova.distancia} {inscripcio.prova.estil.value}"
            if inscripcio.dia not in competicio.dates:
                error(
                    "RN-015",
                    f"{camp}.proves.{j}.dia",
                    inscripcio.dia,
                    f"el dia {inscripcio.dia.isoformat()} de la prova {prova} no és "
                    f"una data de {competicio.id!r}",
                )
            if not es_prova_oficial(inscripcio.prova, competicio.piscina):
                error(
                    "RN-030",
                    f"{camp}.proves.{j}.prova",
                    prova,
                    f"la prova {prova} no és oficial en piscina de {int(competicio.piscina)} m",
                )
    return Resultat(errors=tuple(errors))


def valida_cataleg(temporada: CodiTemporada, cataleg: Cataleg) -> Resultat:
    """Avís RN-009 (seu desconeguda). RN-008 i els invariants de format els garanteix la
    construcció del `Cataleg`."""
    fitxer = fitxer_cataleg(temporada)
    avisos = tuple(
        Avis(
            "RN-009",
            fitxer,
            f"competicions.{i}.seu",
            None,
            f"la seu de la competició {competicio.id!r} és desconeguda",
            "Indica la seu de la competició",
        )
        for i, competicio in enumerate(cataleg.competicions)
        if competicio.seu is None
    )
    return Resultat(avisos=avisos)


def _marca(mal: str, registre: MillorRegistre) -> str:
    return f"{mal}: {registre.descripcio}"


def _valida_registres(
    registres: tuple[MillorRegistre, ...], fitxer: str, nedador: str
) -> list[ErrorValidacio]:
    errors: list[ErrorValidacio] = []
    anterior: dict[tuple[object, int, object], MillorRegistre] = {}
    for i, registre in enumerate(registres):
        camp = f"millors_registres.{i}"
        if not es_prova_oficial(registre.prova, registre.piscina):
            errors.append(
                ErrorValidacio(
                    "RN-030",
                    fitxer,
                    camp,
                    registre.descripcio,
                    _marca("prova no oficial", registre),
                    "Corregeix la prova o la piscina del registre",
                    nedador,
                )
            )
        if not registre.competicio:
            errors.append(
                ErrorValidacio(
                    "RN-007",
                    fitxer,
                    f"{camp}.competicio",
                    registre.competicio,
                    _marca("competició absent o buida", registre),
                    "Indica el nom de la competició",
                    nedador,
                )
            )
        clau = (registre.estil, registre.distancia, registre.piscina)
        previ = anterior.get(clau)
        if previ is not None:
            if registre.temps >= previ.temps:
                mal = f"el temps ({registre.temps}) no millora l'anterior ({previ.temps})"
            elif registre.data <= previ.data:
                mal = f"la data ({registre.data}) no és posterior a l'anterior ({previ.data})"
            else:
                mal = ""
            if mal:
                errors.append(
                    ErrorValidacio(
                        "RN-007",
                        fitxer,
                        camp,
                        registre.descripcio,
                        _marca(mal, registre),
                        "Ordena les marques de la prova i la piscina, cada una millor i "
                        "posterior a l'anterior",
                        nedador,
                    )
                )
        anterior[clau] = registre
    return errors


def valida_nedador(id_nedador: IdNedador, nedador: Nedador) -> Resultat:
    """Errors (RN-003, RN-007, RN-030, RN-032 i format) i avisos (RN-035) d'un nedador.

    Els invariants de RN-005 i RN-006 els garanteix la construcció de l'entitat.
    """
    fitxer = fitxer_nedador(id_nedador)
    qui = str(id_nedador) if nedador.alias is None else str(nedador.alias)
    errors: list[ErrorValidacio] = []
    avisos: list[Avis] = []

    if nedador.alias is None:
        errors.append(
            ErrorValidacio(
                "RN-003",
                fitxer,
                "alias",
                None,
                "l'alias és obligatori",
                "Afegeix l'alias `<part>_<sufix>` del nedador",
                qui,
            )
        )
    elif not nedador.alias.coincideix_amb(id_nedador):
        errors.append(
            ErrorValidacio(
                "RN-003",
                fitxer,
                "alias",
                str(nedador.alias),
                "el sufix de l'alias no coincideix amb els 7 primers caràcters de l'id",
                "Corregeix l'alias perquè el sufix sigui el de l'id",
                qui,
            )
        )

    if nedador.correu is not None and not nedador.correu.format_valid:
        errors.append(
            ErrorValidacio(
                "RN-032",
                fitxer,
                "correu",
                nedador.correu.valor,
                "el correu no té el format mínim (`@`, part local, domini amb punt, "
                "sense espais en blanc al mig)",
                "Corregeix el correu o treu-lo",
                qui,
            )
        )

    if not nedador.mobil.strip(BLANCS):
        errors.append(
            ErrorValidacio(
                "format",
                fitxer,
                "mobil",
                nedador.mobil,
                "el mòbil és obligatori i no pot ser buit",
                "Indica el mòbil del nedador",
                qui,
            )
        )

    errors.extend(_valida_registres(nedador.millors_registres, fitxer, qui))

    if nedador.canal_preferent is None:
        avisos.append(
            Avis(
                "RN-035",
                fitxer,
                "canal_preferent",
                None,
                "el canal preferent és absent",
                "Indica si el canal preferent és `correu` o `mobil`",
                qui,
            )
        )
    elif nedador.canal_preferent is Canal.CORREU and nedador.correu is None:
        avisos.append(
            Avis(
                "RN-035",
                fitxer,
                "canal_preferent",
                nedador.canal_preferent.value,
                "el canal preferent és `correu` però el nedador no té correu",
                "Afegeix un correu o tria el canal `mobil`",
                qui,
            )
        )
    return Resultat(errors=tuple(errors), avisos=tuple(avisos))


def valida_unicitat(identitats: Mapping[IdNedador, Identitat]) -> tuple[ErrorValidacio, ...]:
    """RN-003 (alias únic) i RN-032 (correu únic, arxivats inclosos).

    Compta tots els fitxers llegibles, valguin o no. El correu es compara per la seva
    `clau`; un camp `None` no hi participa.
    """
    errors: list[ErrorValidacio] = []
    ordenats = sorted(identitats.items(), key=lambda element: element[0].valor)
    for rn, camp in (("RN-003", "alias"), ("RN-032", "correu")):
        grups: defaultdict[str, list[IdNedador]] = defaultdict(list)
        for id_nedador, identitat in ordenats:
            clau = identitat.alias if camp == "alias" else identitat.clau_correu
            if clau is not None:
                grups[clau].append(id_nedador)
        for clau, ids in grups.items():
            if len(ids) > 1:
                llista = ", ".join(str(i) for i in ids)
                errors.append(
                    ErrorValidacio(
                        rn,
                        fitxer_nedador(ids[0]),
                        camp,
                        clau,
                        f"{camp} repetit als nedadors {llista}",
                        f"Canvia el {camp} d'un dels nedadors implicats",
                        str(ids[0]),
                        tuple(ids),
                    )
                )
    return tuple(errors)


def valida_aptitud(
    id_nedador: IdNedador,
    qui: str,
    nedador: Nedador,
    inscripcions: Inscripcions | None,
    temporada: CodiTemporada | None = None,
) -> Resultat:
    """Aptitud per planificar (data-model § Validació, nivell 3).

    Bloquegen RN-017 («arxivat») i RN-018 («falta competició A»); RN-019 i RN-020 són avisos.
    `inscripcions`: les de la temporada que es planifica (`None` si no n'hi ha).
    """
    fitxer = fitxer_nedador(id_nedador)
    fitxer_ins = fitxer if temporada is None else fitxer_inscripcions(id_nedador, temporada)
    errors: list[ErrorValidacio] = []
    avisos: list[Avis] = []
    if nedador.arxivat:
        errors.append(
            ErrorValidacio(
                "RN-017", fitxer, "arxivat", True, "arxivat", "Desarxiva el nedador", qui
            )
        )
    participacions = () if inscripcions is None else inscripcions.participacions
    if not any(p.classe is Classe.A for p in participacions):
        errors.append(
            ErrorValidacio(
                "RN-018",
                fitxer_ins,
                "participacions",
                None,
                "falta competició A",
                "Inscriu el nedador a una competició de classe A",
                qui,
            )
        )
    for i, participacio in enumerate(participacions):
        if participacio.classe is Classe.A and not any(
            x.prioritat is Prioritat.PRINCIPAL for x in participacio.proves
        ):
            avisos.append(
                Avis(
                    "RN-019",
                    fitxer_ins,
                    f"participacions.{i}",
                    participacio.id_competicio,
                    f"la participació A a {participacio.id_competicio!r} no té cap prova principal",
                    "Marca una prova com a principal",
                    qui,
                )
            )
    if all(test_vigent(nedador, piscina) is None for piscina in Piscina):
        avisos.append(
            Avis(
                "RN-020",
                fitxer,
                "tests_css",
                None,
                "sense ritmes",
                "Registra i accepta un test CSS o introdueix els ritmes (spec 004)",
                qui,
            )
        )
    return Resultat(errors=tuple(errors), avisos=tuple(avisos))
