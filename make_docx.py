import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

import report_content as rc
from update_toc_pages import TOC_DATA, TABLES_LIST, FIGURES_LIST

TEMPLATE_PATH = "/Users/aityprachetha/Desktop/Lab-Based_Project_Report_Template__1_.docx"
OUT_PATH = "report_output/Autonomous_Agricultural_Robot_Report.docx"
FIG_DIR = "report_output/figures"

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)

def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="333333"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="333333"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="CCCCCC"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def format_run(run, font_name="Times New Roman", size_pt=12, bold=False, italic=False, color_rgb=(0,0,0)):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)

def add_p(doc, text="", align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6, line_spacing=1.5, bold=False, italic=False, size_pt=12):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if text:
        run = p.add_run(text)
        format_run(run, size_pt=size_pt, bold=bold, italic=italic)
    return p

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    format_run(run, size_pt=14, bold=True)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    format_run(run, size_pt=12, bold=True)
    return p

def add_figure(doc, img_path, caption, width_in=5.8):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        p_img.add_run().add_picture(img_path, width=Inches(width_in))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        run = p_cap.add_run(caption)
        format_run(run, size_pt=10.5, bold=True, italic=True, color_rgb=(40,40,40))

def add_academic_table(doc, title, headers, rows, col_widths=None):
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(10)
    p_title.paragraph_format.space_after = Pt(4)
    run = p_title.add_run(title)
    format_run(run, size_pt=10.5, bold=True)

    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)

    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        set_cell_shading(hdr_cells[i], "E8ECE9")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=120, right=120)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if p.runs:
            format_run(p.runs[0], size_pt=9.5, bold=True)

    for r_idx, row_data in enumerate(rows):
        row_cells = table.rows[r_idx + 1].cells
        bg_col = "FDFDFD" if r_idx % 2 == 0 else "F4F6F5"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            set_cell_shading(row_cells[c_idx], bg_col)
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=100, right=100)
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if len(str(val)) > 25 else WD_ALIGN_PARAGRAPH.CENTER
            if p.runs:
                format_run(p.runs[0], size_pt=9.0)

    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def build_report():
    print("Loading template:", TEMPLATE_PATH)
    doc = docx.Document(TEMPLATE_PATH)
    
    for p in list(doc.paragraphs):
        p._element.getparent().remove(p._element)
    for t in list(doc.tables):
        t._element.getparent().remove(t._element)

    print("Building Title Page...")
    logo_path = os.path.join(FIG_DIR, "university_logo.jpeg")
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_after = Pt(4)
        p_logo.add_run().add_picture(logo_path, width=Inches(3.2))

    p_sch = doc.add_paragraph()
    p_sch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sch.paragraph_format.space_after = Pt(28)
    run = p_sch.add_run("SCHOOL OF COMPUTING, AMARAVATI – 522503.")
    format_run(run, size_pt=13, bold=True)

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit.paragraph_format.space_after = Pt(36)
    p_tit.paragraph_format.line_spacing = 1.3
    run = p_tit.add_run("SIMULATION OF AN AUTONOMOUS AGRICULTURAL ROBOT FOR AI-BASED PLANT DISEASE DETECTION AND PRECISION SPRAYING")
    format_run(run, size_pt=15, bold=True)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(10)
    run = p_sub.add_run("Submitted by")
    format_run(run, size_pt=12, italic=True)

    p_st1 = doc.add_paragraph()
    p_st1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_st1.paragraph_format.space_after = Pt(2)
    run = p_st1.add_run("AITY PRACHETHA [AV.SC.U4AIE24101]")
    format_run(run, size_pt=12, bold=True)

    p_st2 = doc.add_paragraph()
    p_st2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_st2.paragraph_format.space_after = Pt(24)
    run = p_st2.add_run("Department of Computer Science and Artificial Intelligence")
    format_run(run, size_pt=11)

    p_gui_lbl = doc.add_paragraph()
    p_gui_lbl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_gui_lbl.paragraph_format.space_after = Pt(6)
    run = p_gui_lbl.add_run("Under the guidance of")
    format_run(run, size_pt=12, italic=True)

    p_gui = doc.add_paragraph()
    p_gui.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_gui.paragraph_format.space_after = Pt(30)
    run = p_gui.add_run("RAVISHANKAR DESAI")
    format_run(run, size_pt=12, bold=True)

    p_req1 = doc.add_paragraph()
    p_req1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_req1.paragraph_format.space_after = Pt(4)
    run = p_req1.add_run("accomplishment of the laboratory work for the subject")
    format_run(run, size_pt=11)

    p_req2 = doc.add_paragraph()
    p_req2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_req2.paragraph_format.space_after = Pt(20)
    run = p_req2.add_run("22AIE441 Dynamics and Control of Robotics.")
    format_run(run, size_pt=12, bold=True)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_inst.add_run("AMRITA VISHWA VIDYAPEETHAM\nOctober 2026")
    format_run(run, size_pt=11, bold=True)

    doc.add_page_break()

    print("Building Abstract...")
    add_heading_1(doc, "ABSTRACT")
    add_p(doc, rc.ABSTRACT, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=12, line_spacing=1.5, size_pt=12)
    doc.add_page_break()

    print("Building Table of Contents...")
    add_heading_1(doc, "CONTENTS")
    t_toc = doc.add_table(rows=len(TOC_DATA), cols=3)
    t_toc.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_toc)
    for r_idx, row in enumerate(TOC_DATA):
        cells = t_toc.rows[r_idx].cells
        for c_idx, val in enumerate(row):
            cells[c_idx].text = val
            set_cell_margins(cells[c_idx], top=60, bottom=60, left=80, right=80)
            p = cells[c_idx].paragraphs[0]
            is_hdr = bool(r_idx == 0 or (cells[0].text and "." not in cells[0].text and len(cells[0].text.strip()) > 0))
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if c_idx == 2 else (WD_ALIGN_PARAGRAPH.CENTER if c_idx == 0 else WD_ALIGN_PARAGRAPH.LEFT)
            if p.runs:
                format_run(p.runs[0], size_pt=10.0, bold=is_hdr)
    t_toc.rows[0].cells[0].width = Inches(1.2)
    t_toc.rows[0].cells[1].width = Inches(4.3)
    t_toc.rows[0].cells[2].width = Inches(1.0)
    doc.add_page_break()

    print("Building List of Tables...")
    add_heading_1(doc, "LIST OF TABLES")
    for tid, tname, tpg in TABLES_LIST:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        r1 = p.add_run(f"{tid}.  {tname}")
        format_run(r1, size_pt=11)
        r2 = p.add_run(f"\t{tpg}")
        format_run(r2, size_pt=11, bold=True)
    doc.add_page_break()

    print("Building List of Figures...")
    add_heading_1(doc, "LIST OF FIGURES")
    for fid, fname, fpg in FIGURES_LIST:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        r1 = p.add_run(f"{fid}.  {fname}")
        format_run(r1, size_pt=11)
        r2 = p.add_run(f"\t{fpg}")
        format_run(r2, size_pt=11, bold=True)
    doc.add_page_break()

    print("Building List of Abbreviations...")
    add_heading_1(doc, "LIST OF ABBREVIATIONS")
    t_abbr = doc.add_table(rows=len(rc.ABBREVIATIONS), cols=2)
    t_abbr.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_abbr)
    for i, (short, full) in enumerate(rc.ABBREVIATIONS):
        c0, c1 = t_abbr.rows[i].cells
        c0.text = short
        c1.text = full
        set_cell_margins(c0, top=50, bottom=50, left=80, right=80)
        set_cell_margins(c1, top=50, bottom=50, left=80, right=80)
        p0 = c0.paragraphs[0]; format_run(p0.runs[0], size_pt=10.5, bold=True)
        p1 = c1.paragraphs[0]; format_run(p1.runs[0], size_pt=10.5)
    t_abbr.rows[0].cells[0].width = Inches(1.8)
    t_abbr.rows[0].cells[1].width = Inches(4.7)
    doc.add_page_break()

    print("Building Chapter 1...")
    add_heading_1(doc, "CHAPTER 1\nINTRODUCTION")
    for sec in rc.CHAPTER_1["sections"]:
        add_heading_2(doc, f"{sec['num']}  {sec['title']}")
        for p_text in sec["paragraphs"]:
            add_p(doc, p_text)
    doc.add_page_break()

    print("Building Chapter 2...")
    add_heading_1(doc, "CHAPTER 2\nRELATED WORK")
    for sec in rc.CHAPTER_2["sections"]:
        add_heading_2(doc, f"{sec['num']}  {sec['title']}")
        for p_text in sec["paragraphs"]:
            add_p(doc, p_text)
        if "table" in sec:
            t = sec["table"]
            add_academic_table(doc, f"{t['id']}\n{t['title']}", t["headers"], t["rows"])
    doc.add_page_break()

    print("Building Chapter 3...")
    add_heading_1(doc, "CHAPTER 3\nMATERIALS AND METHODS")
    sec3_1 = rc.CHAPTER_3["sections"][0]
    add_heading_2(doc, f"{sec3_1['num']}  {sec3_1['title']}")
    for p_text in sec3_1["paragraphs"][:12]:
        add_p(doc, p_text)
    
    add_figure(doc, os.path.join(FIG_DIR, "fig_kinematics.png"),
               "Fig. 1. Pioneer 3-DX differential kinematics and 3-DOF arm aiming geometry.", width_in=5.0)

    for p_text in sec3_1["paragraphs"][12:]:
        add_p(doc, p_text)

    t2 = sec3_1["table_ii"]
    add_academic_table(doc, f"{t2['id']}\n{t2['title']}", t2["headers"], t2["rows"])

    t3 = sec3_1["table_iii"]
    add_academic_table(doc, f"{t3['id']}\n{t3['title']}", t3["headers"], t3["rows"])

    t4 = sec3_1["table_iv"]
    add_academic_table(doc, f"{t4['id']}\n{t4['title']}", t4["headers"], t4["rows"])

    for p_text in sec3_1["dataset_paragraphs"]:
        add_p(doc, p_text)

    sec3_2 = rc.CHAPTER_3["sections"][1]
    add_heading_2(doc, f"{sec3_2['num']}  {sec3_2['title']}")
    for p_text in sec3_2["paragraphs"][:4]:
        add_p(doc, p_text)

    add_figure(doc, os.path.join(FIG_DIR, "fig_model_architecture.png"),
               "Fig. 2. EfficientNet-B0 deep neural network feature extractor architecture.", width_in=5.8)

    for p_text in sec3_2["paragraphs"][4:]:
        add_p(doc, p_text)

    sec3_3 = rc.CHAPTER_3["sections"][2]
    add_heading_2(doc, f"{sec3_3['num']}  {sec3_3['title']}")
    for p_text in sec3_3["paragraphs"]:
        add_p(doc, p_text)
    t5 = sec3_3["table_v"]
    add_academic_table(doc, f"{t5['id']}\n{t5['title']}", t5["headers"], t5["rows"])
    doc.add_page_break()

    print("Building Chapter 4...")
    add_heading_1(doc, "CHAPTER 4\nMETHODOLOGY")
    sec4_1 = rc.CHAPTER_4["sections"][0]
    add_heading_2(doc, f"{sec4_1['num']}  {sec4_1['title']}")
    for p_text in sec4_1["paragraphs"][:6]:
        add_p(doc, p_text)

    add_figure(doc, os.path.join(FIG_DIR, "fig_control_loop.png"),
               "Fig. 3. Closed-loop proportional aisle guidance & heading control system block diagram.", width_in=5.5)

    for p_text in sec4_1["paragraphs"][6:]:
        add_p(doc, p_text)
    t6 = sec4_1["table_vi"]
    add_academic_table(doc, f"{t6['id']}\n{t6['title']}", t6["headers"], t6["rows"])

    sec4_2 = rc.CHAPTER_4["sections"][1]
    add_heading_2(doc, f"{sec4_2['num']}  {sec4_2['title']}")
    for p_text in sec4_2["paragraphs"]:
        add_p(doc, p_text)

    sec4_3 = rc.CHAPTER_4["sections"][2]
    add_heading_2(doc, f"{sec4_3['num']}  {sec4_3['title']}")
    for p_text in sec4_3["paragraphs"]:
        add_p(doc, p_text)

    add_figure(doc, os.path.join(FIG_DIR, "fig_system_architecture.png"),
               "Fig. 4. Complete end-to-end autonomous agricultural robot system architecture.", width_in=5.8)

    t7 = sec4_3["table_vii"]
    add_academic_table(doc, f"{t7['id']}\n{t7['title']}", t7["headers"], t7["rows"])

    sec4_4 = rc.CHAPTER_4["sections"][3]
    add_heading_2(doc, f"{sec4_4['num']}  {sec4_4['title']}")
    for p_text in sec4_4["paragraphs"]:
        add_p(doc, p_text)

    sec4_5 = rc.CHAPTER_4["sections"][4]
    add_heading_2(doc, f"{sec4_5['num']}  {sec4_5['title']}")
    for p_text in sec4_5["paragraphs"]:
        add_p(doc, p_text)

    add_figure(doc, os.path.join(FIG_DIR, "fig_mission_flowchart.png"),
               "Fig. 5. Complete autonomous agricultural robot operational mission flowchart.", width_in=5.0)
    doc.add_page_break()

    print("Building Chapter 5...")
    add_heading_1(doc, "CHAPTER 5\nRESULTS AND DISCUSSION")
    sec5_1 = rc.CHAPTER_5["sections"][0]
    add_heading_2(doc, f"{sec5_1['num']}  {sec5_1['title']}")
    for p_text in sec5_1["paragraphs"]:
        add_p(doc, p_text)
    t8 = sec5_1["table_viii"]
    add_academic_table(doc, f"{t8['id']}\n{t8['title']}", t8["headers"], t8["rows"])

    sec5_2 = rc.CHAPTER_5["sections"][1]
    add_heading_2(doc, f"{sec5_2['num']}  {sec5_2['title']}")
    for p_text in sec5_2["paragraphs"][:2]:
        add_p(doc, p_text)

    add_figure(doc, os.path.join(FIG_DIR, "first_plant_inspection_frame.png"),
               "Fig. 6. End-effector inspection camera capture of the first plant canopy in Webots.", width_in=2.5)

    for p_text in sec5_2["paragraphs"][2:4]:
        add_p(doc, p_text)

    add_figure(doc, os.path.join(FIG_DIR, "fig_inspection_samples.png"),
               "Fig. 7. Representative in-situ inspection frames annotated by EfficientNet-B0.", width_in=5.8)

    for p_text in sec5_2["paragraphs"][4:]:
        add_p(doc, p_text)

    sec5_3 = rc.CHAPTER_5["sections"][2]
    add_heading_2(doc, f"{sec5_3['num']}  {sec5_3['title']}")
    for p_text in sec5_3["paragraphs"]:
        add_p(doc, p_text)

    t9 = sec5_3["table_ix"]
    add_academic_table(doc, f"{t9['id']}\n{t9['title']}", t9["headers"], t9["rows"])

    t10 = sec5_3["table_x"]
    add_academic_table(doc, f"{t10['id']}\n{t10['title']}", t10["headers"], t10["rows"])

    add_figure(doc, os.path.join(FIG_DIR, "fig_training_curves.png"),
               "Fig. 8. EfficientNet-B0 model optimization curves over 25 epochs.", width_in=5.8)

    t11 = sec5_3["table_xi"]
    add_academic_table(doc, f"{t11['id']}\n{t11['title']}", t11["headers"], t11["rows"])

    add_figure(doc, os.path.join(FIG_DIR, "fig_confusion_matrix.png"),
               "Fig. 9. Field inspection confusion matrix (66 leaves) and per-class performance metrics.", width_in=5.8)

    add_figure(doc, os.path.join(FIG_DIR, "confidence_graph.png"),
               "Fig. 10. Leaf-by-leaf AI inspection confidence across all 66 crop panels.", width_in=5.8)

    t12 = sec5_3["table_xii"]
    add_academic_table(doc, f"{t12['id']}\n{t12['title']}", t12["headers"], t12["rows"])

    add_figure(doc, os.path.join(FIG_DIR, "fig_chemical_savings.png"),
               "Fig. 11. Chemical volume and canopy treatment comparison (Targeted vs Broadcast).", width_in=5.0)

    t13 = sec5_3["table_xiii"]
    add_academic_table(doc, f"{t13['id']}\n{t13['title']}", t13["headers"], t13["rows"])

    t14 = sec5_3["table_xiv"]
    add_academic_table(doc, f"{t14['id']}\n{t14['title']}", t14["headers"], t14["rows"])

    add_figure(doc, os.path.join(FIG_DIR, "farm_dashboard.png"),
               "Fig. 12. Comprehensive AI agricultural robot testing field report dashboard.", width_in=5.8)

    sec5_4 = rc.CHAPTER_5["sections"][3]
    add_heading_2(doc, f"{sec5_4['num']}  {sec5_4['title']}")
    for p_text in sec5_4["paragraphs"]:
        add_p(doc, p_text)
    doc.add_page_break()

    print("Building Chapter 6...")
    add_heading_1(doc, "CHAPTER 6\nCONCLUSION AND FUTURE DIRECTIONS")
    for sec in rc.CHAPTER_6["sections"]:
        add_heading_2(doc, f"{sec['num']}  {sec['title']}")
        for p_text in sec["paragraphs"]:
            add_p(doc, p_text)
    doc.add_page_break()

    print("Building Chapter 7...")
    add_heading_1(doc, "CHAPTER 7\nREFERENCES")
    for ref_str in rc.CHAPTER_7["references"]:
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.space_after = Pt(6)
        p_ref.paragraph_format.line_spacing = 1.15
        run = p_ref.add_run(ref_str)
        format_run(run, size_pt=10.0)

    print("Saving document to:", OUT_PATH)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    doc.save(OUT_PATH)
    print("DOCX build complete and verified!")

if __name__ == "__main__":
    build_report()
