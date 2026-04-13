from __future__ import annotations

from dataclasses import dataclass

from services.chemistry_service import ChemistryService
from utils.models import ADMERequest, ChemistrySummary


@dataclass(slots=True)
class ChemistryAgent:
    chemistry_service: ChemistryService

    def run(self, request: ADMERequest) -> ChemistrySummary:
        summary = self.chemistry_service.build_chemistry_summary(request.smiles)
        features = summary.structural_features or {}
        hotspot_summary = self.chemistry_service.build_hotspot_summary(
            features=features,
            chemistry_summary={
                "feature_flags": summary.feature_flags or [],
                "soft_spot_hints": summary.soft_spot_hints or [],
                "phase1_liabilities": summary.phase1_liabilities or [],
                "phase2_liabilities": summary.phase2_liabilities or [],
            },
        ) if features else []
        structure_to_assay_links = self.chemistry_service.map_hotspots_to_assays(
            hotspots=hotspot_summary,
            focus=request.focus,
            species=request.species,
        ) if hotspot_summary else []
        enriched = self.chemistry_service.build_species_chemistry_summary(
            features=features,
            species=request.species,
            focus=request.focus,
        ) if features else {
            "species_chemistry_interpretation": self.chemistry_service.infer_species_chemistry_interpretation({}, request.species),
            "assay_priorities": [],
            "disposition_assay_priorities": [],
            "pathway_priorities": [],
            "cyp_preference_hints": [],
            "transporter_hints": [],
            "permeability_hints": [],
            "clearance_route_hints": [],
            "disposition_summary": self.chemistry_service.build_disposition_summary({}, request.species, request.focus),
            "chemistry_driven_risk_notes": [],
        }
        if summary.smiles_valid or summary.rdkit_used:
            summary.species_chemistry_interpretation = enriched["species_chemistry_interpretation"]
            summary.assay_priorities = enriched["assay_priorities"]
            summary.disposition_assay_priorities = enriched["disposition_assay_priorities"]
            summary.pathway_priorities = enriched["pathway_priorities"]
            summary.cyp_preference_hints = enriched["cyp_preference_hints"] or summary.cyp_preference_hints
            summary.transporter_hints = enriched["transporter_hints"]
            summary.permeability_hints = enriched["permeability_hints"]
            summary.clearance_route_hints = enriched["clearance_route_hints"]
            summary.disposition_summary = enriched["disposition_summary"]
            summary.hotspot_summary = hotspot_summary
            summary.hotspot_priorities = []
            summary.structure_to_assay_links = structure_to_assay_links
            summary.chemistry_confidence_summary = {"summary": "Confidence calibration is applied downstream after literature linking."}
            summary.hotspot_confidence_summary = "Confidence calibration is applied downstream after literature linking."
            summary.recommendation_confidence_summary = {
                "high_confidence_priorities": [],
                "medium_confidence_priorities": [],
                "exploratory_priorities": [],
                "confidence_caveats": "Recommendation confidence is calibrated downstream after literature linking.",
            }
            summary.chemistry_driven_risk_notes = enriched["chemistry_driven_risk_notes"]
            return summary

        limitations = list(summary.limitations or [])
        if not request.smiles.strip():
            limitations.append("Chemistry agent continued in fallback mode because no SMILES was supplied.")
        return ChemistrySummary(
            smiles=summary.smiles,
            smiles_valid=summary.smiles_valid,
            rdkit_used=summary.rdkit_used,
            molecular_formula=summary.molecular_formula,
            molecular_weight=summary.molecular_weight,
            feature_flags=summary.feature_flags or [],
            structural_features=summary.structural_features or {},
            soft_spot_hints=summary.soft_spot_hints or [],
            phase1_liabilities=summary.phase1_liabilities or [],
            phase2_liabilities=summary.phase2_liabilities or [],
            reactive_metabolite_risks=summary.reactive_metabolite_risks or [],
            cyp_preference_hints=enriched["cyp_preference_hints"],
            transporter_hints=enriched["transporter_hints"],
            permeability_hints=enriched["permeability_hints"],
            clearance_route_hints=enriched["clearance_route_hints"],
            species_chemistry_interpretation=enriched["species_chemistry_interpretation"],
            assay_priorities=enriched["assay_priorities"],
            disposition_assay_priorities=enriched["disposition_assay_priorities"],
            pathway_priorities=enriched["pathway_priorities"],
            disposition_summary=enriched["disposition_summary"],
            hotspot_summary=hotspot_summary,
            hotspot_priorities=[],
            structure_to_assay_links=structure_to_assay_links,
            chemistry_confidence_summary={"summary": "Confidence calibration is limited in fallback mode."},
            hotspot_confidence_summary="Confidence calibration is limited in fallback mode.",
            recommendation_confidence_summary={
                "high_confidence_priorities": [],
                "medium_confidence_priorities": [],
                "exploratory_priorities": [],
                "confidence_caveats": "Recommendation confidence remains limited because chemistry linking is incomplete in fallback mode.",
            },
            chemistry_driven_risk_notes=enriched["chemistry_driven_risk_notes"],
            chemistry_summary_text=summary.chemistry_summary_text,
            limitations=limitations,
            protocol_implications=summary.protocol_implications or [],
        )
