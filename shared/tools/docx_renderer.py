from __future__ import annotations

from typing import Any

from shared.schemas.template import TemplateFormattingProfile


def apply_cjk_formatting(document: Any, formatting: TemplateFormattingProfile) -> None:
    """Apply Chinese-friendly font settings to a python-docx document."""
    for style_name in ("Normal", "Heading 1", "Heading 2", "Heading 3", "List Bullet"):
        if style_name in document.styles:
            _set_style_font(document.styles[style_name], formatting)

    for paragraph in document.paragraphs:
        if paragraph.style is not None:
            _set_style_font(paragraph.style, formatting)
        paragraph.paragraph_format.line_spacing = formatting.line_spacing
        for run in paragraph.runs:
            set_run_cjk_font(run, formatting.font_family, formatting.font_size_pt)

    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                apply_cjk_formatting(cell, formatting)


def set_run_cjk_font(run: Any, font_family: str, font_size_pt: float | None = None) -> None:
    from docx.oxml.ns import qn
    from docx.shared import Pt

    run.font.name = font_family
    if font_size_pt is not None:
        run.font.size = Pt(font_size_pt)

    r_pr = run._element.get_or_add_rPr()
    r_fonts = r_pr.rFonts
    if r_fonts is None:
        from docx.oxml import OxmlElement

        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)

    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        r_fonts.set(qn(attr), font_family)


def _set_style_font(style: Any, formatting: TemplateFormattingProfile) -> None:
    from docx.oxml.ns import qn
    from docx.shared import Pt

    style.font.name = formatting.font_family
    style.font.size = Pt(formatting.font_size_pt)

    r_pr = style.element.get_or_add_rPr()
    r_fonts = r_pr.rFonts
    if r_fonts is None:
        from docx.oxml import OxmlElement

        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)

    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        r_fonts.set(qn(attr), formatting.font_family)
