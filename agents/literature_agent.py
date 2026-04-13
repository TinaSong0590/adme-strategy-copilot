from __future__ import annotations

from dataclasses import dataclass

from services.literature_service import LiteratureService
from utils.models import ADMERequest, LiteratureSearchResult, MetabolismPrediction


@dataclass(slots=True)
class LiteratureAgent:
    literature_service: LiteratureService

    def run(
        self,
        request: ADMERequest,
        metabolism: MetabolismPrediction,
    ) -> LiteratureSearchResult:
        _ = metabolism
        return self.literature_service.search_compound(
            drug_name=request.drug_name,
            smiles=request.smiles,
            focus=request.focus,
            species=request.species,
            max_results=self.literature_service.default_max_results,
        )

    def build_query(
        self,
        request: ADMERequest,
        metabolism: MetabolismPrediction,
    ) -> list[str]:
        _ = metabolism
        return self.literature_service.build_queries(
            drug_name=request.drug_name,
            smiles=request.smiles,
            focus=request.focus,
        )
