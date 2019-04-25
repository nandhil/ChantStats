import os
import shutil

from .dendrogram2 import Dendrogram
from .logging import logger

__all__ = ["export_dendrogram_and_stacked_bar_chart"]


def export_dendrogram_and_stacked_bar_chart(
    *, output_root_dir, analysis_spec, modal_category, p_cutoff, sort_freqs_ascending=False, overwrite=False
):
    """
    Export dendrogram and stacked bar chart for this modal category.

    Parameters
    ----------
    output_root_dir : str
        The path under which to export results. Note that the actual directory
        where the plots are saved will be a sub-directory of this root directory,
        for example: `<output_root_dir>/authentic_modes/G_authentic`.
    analysis_spec : FullAnalysisSpec
    modal_cagetory : ModalCategory
    p_cutoff : float
    sort_freqs_ascending : bool, optional
    overwrite: book, optional
    """
    logger.info(f"Exporting results for anaysis_spec={analysis_spec}, modal_category={modal_category}")

    output_dir = analysis_spec.output_path(root_dir=output_root_dir, modal_category=modal_category)
    if os.path.exists(output_dir):
        if not overwrite:
            logger.warning(
                f"Output directory exists. Use `overwrite=True` to delete its contents before exporting results: '{output_dir}'"
            )
            return
        else:
            logger.warning(f"Deleting contents of existing output directory (because overwrite=True): '{output_dir}'")
            shutil.rmtree(output_dir)
    if not os.path.exists(output_dir):
        logger.debug(f"Creating output dir: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)

    df = modal_category.make_results_dataframe(analysis_func=analysis_spec.analysis_func)
    dendrogram = Dendrogram(df, p_threshold=p_cutoff)

    output_filename = os.path.join(output_dir, "dendrogram.png")
    title = f"Dendrogram: {analysis_spec.get_description(modal_category=modal_category)} (p_cutoff={p_cutoff})"
    fig = dendrogram.plot_dendrogram(title=title)
    fig.savefig(output_filename)
    logger.debug(f"Saved dendrogram plot: '{output_filename}'")

    output_filename = os.path.join(output_dir, "stacked_bar_chart.png")
    title = f"{analysis_spec.get_description(modal_category=modal_category)} (p_cutoff={p_cutoff})"
    fig = dendrogram.plot_stacked_bar_charts(title=title, sort_freqs_ascending=sort_freqs_ascending)
    fig.savefig(output_filename)
    logger.debug(f"Saved stacked bar chart: '{output_filename}'")