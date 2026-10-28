"""Identificadores de módulo — sin dependencias para evitar ciclos de import."""

from enum import StrEnum


class ModuleKind(StrEnum):
    HABITAT = "habitat"
    SOLAR = "solar"
    RADAR = "radar"
    EXTRACTOR = "extractor"
    GREENHOUSE = "greenhouse"
    MINE = "mine"
    FABRICATOR = "fabricator"
    STORAGE = "storage"
    LAMP = "lamp"
    LABORATORY = "laboratory"
    ELECTROLYZER = "electrolyzer"
    CONDENSER = "condenser"
