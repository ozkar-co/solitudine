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
    RECYCLER = "recycler"
    FISH_TRAP = "fish_trap"
    BIODIESEL = "biodiesel"
    MONITOR = "monitor"
    COAL_EXTRACTOR = "coal_extractor"
    CRYSTAL_EXTRACTOR = "crystal_extractor"
    FUEL_GENERATOR = "fuel_generator"
