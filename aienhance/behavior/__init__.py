"""
行为层模块
"""

from .adaptive_output import (
    AdaptedContent,
    ConceptGranularity,
    InformationDensity,
    IntegratedAdaptiveOutput,
    OutputStructure,
)

__all__ = [
    "IntegratedAdaptiveOutput",
    "AdaptedContent",
    "InformationDensity",
    "OutputStructure",
    "ConceptGranularity",
]
