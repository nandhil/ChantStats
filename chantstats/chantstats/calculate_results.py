from .analysis_spec import RepertoireAndGenreType, AnalysisType
from .dendrogram2 import Dendrogram
from .logging import logger
from .modal_category import ModalCategoryType, GroupingByModalCategory
from .plainchant_sequence_piece import load_pieces
from .unit import UnitType

__all__ = ["calculate_results"]


def get_path_stubs(repertoire_and_genre, analysis, unit, modal_category):
    rep_and_genre = RepertoireAndGenreType(repertoire_and_genre)
    analysis = AnalysisType(analysis)
    unit = UnitType(unit)
    return (
        rep_and_genre.output_path_stub_1,
        analysis.output_path_stub,
        rep_and_genre.output_path_stub_2,
        unit.output_path_stub,
        modal_category.output_path_stub_1,
        modal_category.output_path_stub_2,
    )


def calculate_pc_freqs(analysis_input, unit):
    if unit == "pcs":
        # freqs = PCFreqs(analysis_input.pc)
        freqs = analysis_input.pc_freqs.rel_freqs
    elif unit == "mode_degrees":
        # freqs = ModeDegreeFreqs(analysis_input.mode_degrees)
        freqs = analysis_input.mode_degree_freqs.rel_freqs
    else:
        raise NotImplementedError()

    return freqs


def get_analysis_function(analysis):
    if analysis == "pc_freqs":
        return calculate_pc_freqs
    else:
        raise NotImplementedError()


def calculate_dendrogram(modal_category, *, analysis_name, unit):
    unit = UnitType(unit)
    analysis_func = get_analysis_function(analysis_name)
    df = modal_category.make_results_dataframe(analysis_func=analysis_func, unit=unit)
    # df = df[[col for col in df.columns[(df != 0).any()]]]  # remove columns where all values are zero
    dendrogram = Dendrogram(df, analysis_name=analysis_name)
    return dendrogram


def calculate_results(repertoire_and_genre, analysis_name, cfg, min_length_monomodal_sections=3):
    results = {}

    pieces = load_pieces(repertoire_and_genre, cfg)

    for mode in list(ModalCategoryType):
        analysis_inputs = pieces.get_analysis_inputs(mode, min_length_monomodal_sections=min_length_monomodal_sections)
        grouping = GroupingByModalCategory(analysis_inputs, group_by=mode)
        for modal_category in grouping.groups.values():
            logger.info(f"Calculating results for {modal_category}")
            for unit in list(UnitType):
                dendrogram = calculate_dendrogram(modal_category, analysis_name=analysis_name, unit=unit)
                path_stubs = get_path_stubs(repertoire_and_genre, analysis_name, unit, modal_category)
                results[path_stubs] = {"dendrogram": dendrogram}

    return results