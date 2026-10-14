import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from pypdf import PdfReader

import report_content as rc
from update_toc_pages import TOC_DATA, TABLES_LIST, FIGURES_LIST

OUT_PDF_PATH = "report_output/Autonomous_Agricultural_Robot_Report.pdf"
FIG_DIR = "report_output/figures"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        page_num = self._pageNumber
        
        # Title page (page 1) has no header/footer
        if page_num > 1:
            self.setFont("Times-Roman", 10)
            roman_map = {2: "ii", 3: "iii", 4: "iv", 5: "v", 6: "vi", 7: "vii", 8: "viii"}
            disp = roman_map.get(page_num, str(page_num))
            
            # Draw right-aligned page number in header
            self.drawRightString(612 - 66, 792 - 36, disp)
            
            # Subtle running header divider rule
            self.setStrokeColor(colors.HexColor("#d0d7d3"))
            self.setLineWidth(0.5)
            self.line(90, 792 - 42, 612 - 66, 792 - 42)

        self.restoreState()

def build_pdf():
    print("Initializing PDF document...")
    os.makedirs(os.path.dirname(OUT_PDF_PATH), exist_ok=True)
    
    doc = SimpleDocTemplate(
        OUT_PDF_PATH,
        pagesize=letter,
        leftMargin=90,
        rightMargin=66,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    style_normal = ParagraphStyle(
        "ReportNormal",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=11,
        leading=16.5,
        alignment=4,
        spaceAfter=6,
        textColor=colors.black
    )

    style_title_sch = ParagraphStyle(
        "TitleSch",
        fontName="Times-Bold",
        fontSize=13,
        leading=18,
        alignment=1,
        spaceAfter=24,
        textColor=colors.black
    )

    style_title_main = ParagraphStyle(
        "TitleMain",
        fontName="Times-Bold",
        fontSize=14,
        leading=20,
        alignment=1,
        spaceAfter=28,
        textColor=colors.black
    )

    style_title_sub = ParagraphStyle(
        "TitleSub",
        fontName="Times-Italic",
        fontSize=11.5,
        leading=16,
        alignment=1,
        spaceAfter=8,
        textColor=colors.black
    )

    style_title_author = ParagraphStyle(
        "TitleAuthor",
        fontName="Times-Bold",
        fontSize=12,
        leading=16,
        alignment=1,
        spaceAfter=2,
        textColor=colors.black
    )

    style_title_meta = ParagraphStyle(
        "TitleMeta",
        fontName="Times-Roman",
        fontSize=10.5,
        leading=15,
        alignment=1,
        spaceAfter=20,
        textColor=colors.black
    )

    style_ch_head = ParagraphStyle(
        "ChapterHead",
        fontName="Times-Bold",
        fontSize=13.5,
        leading=18,
        alignment=1,
        spaceBefore=10,
        spaceAfter=14,
        textColor=colors.black
    )

    style_sec_head = ParagraphStyle(
        "SectionHead",
        fontName="Times-Bold",
        fontSize=11.5,
        leading=16,
        alignment=0,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.black
    )

    style_caption = ParagraphStyle(
        "FigCaption",
        fontName="Times-BoldItalic",
        fontSize=9.5,
        leading=13,
        alignment=1,
        spaceBefore=4,
        spaceAfter=10,
        textColor=colors.HexColor("#222222")
    )

    style_tbl_title = ParagraphStyle(
        "TblTitle",
        fontName="Times-Bold",
        fontSize=10,
        leading=14,
        alignment=1,
        spaceBefore=10,
        spaceAfter=4,
        textColor=colors.black
    )

    style_cell = ParagraphStyle(
        "TblCell",
        fontName="Times-Roman",
        fontSize=8.5,
        leading=11.5,
        alignment=0,
        textColor=colors.black
    )

    style_cell_center = ParagraphStyle(
        "TblCellCenter",
        fontName="Times-Roman",
        fontSize=8.5,
        leading=11.5,
        alignment=1,
        textColor=colors.black
    )

    style_cell_hdr = ParagraphStyle(
        "TblCellHdr",
        fontName="Times-Bold",
        fontSize=8.5,
        leading=11.5,
        alignment=1,
        textColor=colors.black
    )

    style_ref = ParagraphStyle(
        "RefStyle",
        fontName="Times-Roman",
        fontSize=9.5,
        leading=13.5,
        alignment=4,
        spaceAfter=6,
        textColor=colors.black
    )

    story = []

    # TITLE PAGE
    logo_path = os.path.join(FIG_DIR, "university_logo.jpeg")
    if os.path.exists(logo_path):
        story.append(RLImage(logo_path, width=3.2*inch, height=0.75*inch))
        story.append(Spacer(1, 8))

    story.append(Paragraph("SCHOOL OF COMPUTING, AMARAVATI – 522503.", style_title_sch))
    story.append(Spacer(1, 15))
    story.append(Paragraph("SIMULATION OF AN AUTONOMOUS AGRICULTURAL ROBOT FOR AI-BASED PLANT DISEASE DETECTION AND PRECISION SPRAYING", style_title_main))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Submitted by", style_title_sub))
    story.append(Paragraph("AITY PRACHETHA [AV.SC.U4AIE24101]", style_title_author))
    story.append(Paragraph("Department of Computer Science and Artificial Intelligence", style_title_meta))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Under the guidance of", style_title_sub))
    story.append(Paragraph("RAVISHANKAR DESAI", style_title_author))
    story.append(Spacer(1, 15))
    story.append(Paragraph("accomplishment of the laboratory work for the subject", style_title_meta))
    story.append(Paragraph("22AIE441 Dynamics and Control of Robotics.", style_title_author))
    story.append(Spacer(1, 25))
    story.append(Paragraph("AMRITA VISHWA VIDYAPEETHAM<br/>October 2026", style_title_meta))
    story.append(PageBreak())

    # ABSTRACT
    story.append(Paragraph("ABSTRACT", style_ch_head))
    story.append(Paragraph(rc.ABSTRACT, style_normal))
    story.append(PageBreak())

    # TABLE OF CONTENTS
    story.append(Paragraph("CONTENTS", style_ch_head))
    t_rows = []
    for r_idx, row in enumerate(TOC_DATA):
        is_hdr = (r_idx == 0 or (row[0] != "" and "." not in row[0]))
        f_style = ParagraphStyle(
            f"TOC_{r_idx}",
            fontName="Times-Bold" if is_hdr else "Times-Roman",
            fontSize=9.5,
            leading=13
        )
        c0 = Paragraph(row[0], ParagraphStyle(f"c0_{r_idx}", parent=f_style, alignment=1))
        c1 = Paragraph(row[1], ParagraphStyle(f"c1_{r_idx}", parent=f_style, alignment=0))
        c2 = Paragraph(row[2], ParagraphStyle(f"c2_{r_idx}", parent=f_style, alignment=2))
        t_rows.append([c0, c1, c2])

    t_toc = Table(t_rows, colWidths=[65, 325, 65])
    t_toc.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1.0, colors.black),
        ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # LIST OF TABLES
    story.append(Paragraph("LIST OF TABLES", style_ch_head))
    t_lot_rows = []
    for tid, tname, tpg in TABLES_LIST:
        c0 = Paragraph(f"<b>{tid}</b>", ParagraphStyle("lot0", fontName="Times-Bold", fontSize=9.5, leading=13))
        c1 = Paragraph(tname, ParagraphStyle("lot1", fontName="Times-Roman", fontSize=9.5, leading=13))
        c2 = Paragraph(f"<b>{tpg}</b>", ParagraphStyle("lot2", fontName="Times-Bold", fontSize=9.5, leading=13, alignment=2))
        t_lot_rows.append([c0, c1, c2])

    t_lot = Table(t_lot_rows, colWidths=[70, 320, 65])
    t_lot.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e0e0e0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_lot)
    story.append(PageBreak())

    # LIST OF FIGURES
    story.append(Paragraph("LIST OF FIGURES", style_ch_head))
    t_lof_rows = []
    for fid, fname, fpg in FIGURES_LIST:
        c0 = Paragraph(f"<b>{fid}</b>", ParagraphStyle("lof0", fontName="Times-Bold", fontSize=9.5, leading=13))
        c1 = Paragraph(fname, ParagraphStyle("lof1", fontName="Times-Roman", fontSize=9.5, leading=13))
        c2 = Paragraph(f"<b>{fpg}</b>", ParagraphStyle("lof2", fontName="Times-Bold", fontSize=9.5, leading=13, alignment=2))
        t_lof_rows.append([c0, c1, c2])

    t_lof = Table(t_lof_rows, colWidths=[65, 325, 65])
    t_lof.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e0e0e0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_lof)
    story.append(PageBreak())

    # LIST OF ABBREVIATIONS
    story.append(Paragraph("LIST OF ABBREVIATIONS", style_ch_head))
    t_abbr_rows = []
    for s, full in rc.ABBREVIATIONS:
        c0 = Paragraph(f"<b>{s}</b>", ParagraphStyle("abb0", fontName="Times-Bold", fontSize=9, leading=12))
        c1 = Paragraph(full, ParagraphStyle("abb1", fontName="Times-Roman", fontSize=9, leading=12))
        t_abbr_rows.append([c0, c1])

    t_abbr = Table(t_abbr_rows, colWidths=[100, 355])
    t_abbr.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#e8e8e8")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_abbr)
    story.append(PageBreak())

    def make_rl_table(title, headers, rows, col_widths=None):
        flowables = [Paragraph(title, style_tbl_title)]
        table_data = []
        hdr_cells = [Paragraph(h, style_cell_hdr) for h in headers]
        table_data.append(hdr_cells)
        for r_idx, r in enumerate(rows):
            row_cells = []
            for c_idx, val in enumerate(r):
                s = style_cell if len(str(val)) > 25 else style_cell_center
                row_cells.append(Paragraph(str(val), s))
            table_data.append(row_cells)

        total_w = 455
        cw = [total_w / len(headers)] * len(headers) if col_widths is None else col_widths

        t = Table(table_data, colWidths=cw, repeatRows=1)
        t_style = [
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E8ECE9")),
            ('LINEABOVE', (0,0), (-1,0), 1.0, colors.HexColor("#333333")),
            ('LINEBELOW', (0,0), (-1,0), 1.0, colors.HexColor("#333333")),
            ('LINEBELOW', (0,-1), (-1,-1), 1.0, colors.HexColor("#333333")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 4),
            ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ]
        for r_idx in range(1, len(table_data)):
            if r_idx % 2 == 0:
                t_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), colors.HexColor("#F6F8F7")))
            t_style.append(('LINEBELOW', (0, r_idx), (-1, r_idx), 0.5, colors.HexColor("#DCE2DE")))

        t.setStyle(TableStyle(t_style))
        flowables.append(t)
        flowables.append(Spacer(1, 10))
        return flowables

    def make_rl_fig(img_path, caption, width=5.6*inch, height=None):
        flowables = []
        if os.path.exists(img_path):
            if height is None:
                from PIL import Image as PILImage
                im = PILImage.open(img_path)
                w_px, h_px = im.size
                calc_h = (h_px / w_px) * width
                if calc_h > 4.5 * inch:
                    calc_h = 4.5 * inch
                    width = (w_px / h_px) * calc_h
                height = calc_h
            flowables.append(RLImage(img_path, width=width, height=height))
            flowables.append(Paragraph(caption, style_caption))
            flowables.append(Spacer(1, 6))
        return flowables

    # CHAPTER 1
    story.append(Paragraph("CHAPTER 1<br/>INTRODUCTION", style_ch_head))
    for sec in rc.CHAPTER_1["sections"]:
        story.append(Paragraph(f"{sec['num']}  {sec['title']}", style_sec_head))
        for p_text in sec["paragraphs"]:
            story.append(Paragraph(p_text, style_normal))
    story.append(PageBreak())

    # CHAPTER 2
    story.append(Paragraph("CHAPTER 2<br/>RELATED WORK", style_ch_head))
    for sec in rc.CHAPTER_2["sections"]:
        story.append(Paragraph(f"{sec['num']}  {sec['title']}", style_sec_head))
        for p_text in sec["paragraphs"]:
            story.append(Paragraph(p_text, style_normal))
        if "table" in sec:
            t = sec["table"]
            story.extend(make_rl_table(f"{t['id']}<br/>{t['title']}", t["headers"], t["rows"],
                                       col_widths=[65, 65, 75, 65, 60, 65, 60]))
    story.append(PageBreak())

    # CHAPTER 3
    story.append(Paragraph("CHAPTER 3<br/>MATERIALS AND METHODS", style_ch_head))
    sec3_1 = rc.CHAPTER_3["sections"][0]
    story.append(Paragraph(f"{sec3_1['num']}  {sec3_1['title']}", style_sec_head))
    for p_text in sec3_1["paragraphs"][:12]:
        story.append(Paragraph(p_text, style_normal))

    story.extend(make_rl_fig(os.path.join(FIG_DIR, "fig_kinematics.png"),
                             "Fig. 1. Pioneer 3-DX differential kinematics and 3-DOF arm aiming geometry.", width=4.5*inch))

    for p_text in sec3_1["paragraphs"][12:]:
        story.append(Paragraph(p_text, style_normal))

    t2 = sec3_1["table_ii"]
    story.extend(make_rl_table(f"{t2['id']}<br/>{t2['title']}", t2["headers"], t2["rows"], col_widths=[125, 60, 60, 45, 165]))

    t3 = sec3_1["table_iii"]
    story.extend(make_rl_table(f"{t3['id']}<br/>{t3['title']}", t3["headers"], t3["rows"], col_widths=[110, 95, 55, 75, 120]))

    t4 = sec3_1["table_iv"]
    story.extend(make_rl_table(f"{t4['id']}<br/>{t4['title']}", t4["headers"], t4["rows"], col_widths=[45, 75, 50, 50, 50, 50, 35, 100]))

    for p_text in sec3_1["dataset_paragraphs"]:
        story.append(Paragraph(p_text, style_normal))

    sec3_2 = rc.CHAPTER_3["sections"][1]
    story.append(Paragraph(f"{sec3_2['num']}  {sec3_2['title']}", style_sec_head))
    for p_text in sec3_2["paragraphs"][:4]:
        story.append(Paragraph(p_text, style_normal))

    story.extend(make_rl_fig(os.path.join(FIG_DIR, "fig_model_architecture.png"),
                             "Fig. 2. EfficientNet-B0 deep neural network feature extractor architecture.", width=5.6*inch))

    for p_text in sec3_2["paragraphs"][4:]:
        story.append(Paragraph(p_text, style_normal))

    sec3_3 = rc.CHAPTER_3["sections"][2]
    story.append(Paragraph(f"{sec3_3['num']}  {sec3_3['title']}", style_sec_head))
    for p_text in sec3_3["paragraphs"]:
        story.append(Paragraph(p_text, style_normal))
    t5 = sec3_3["table_v"]
    story.extend(make_rl_table(f"{t5['id']}<br/>{t5['title']}", t5["headers"], t5["rows"], col_widths=[100, 55, 110, 190]))
    story.append(PageBreak())

    # CHAPTER 4
    story.append(Paragraph("CHAPTER 4<br/>METHODOLOGY", style_ch_head))
    sec4_1 = rc.CHAPTER_4["sections"][0]
    story.append(Paragraph(f"{sec4_1['num']}  {sec4_1['title']}", style_sec_head))
    for p_text in sec4_1["paragraphs"][:6]:
        story.append(Paragraph(p_text, style_normal))

    story.extend(make_rl_fig(os.path.join(FIG_DIR, "fig_control_loop.png"),
                             "Fig. 3. Closed-loop proportional aisle guidance & heading control system block diagram.", width=5.2*inch))

    for p_text in sec4_1["paragraphs"][6:]:
        story.append(Paragraph(p_text, style_normal))
    t6 = sec4_1["table_vi"]
    story.extend(make_rl_table(f"{t6['id']}<br/>{t6['title']}", t6["headers"], t6["rows"], col_widths=[130, 60, 60, 45, 160]))

    sec4_2 = rc.CHAPTER_4["sections"][1]
    story.append(Paragraph(f"{sec4_2['num']}  {sec4_2['title']}", style_sec_head))
    for p_text in sec4_2["paragraphs"]:
        story.append(Paragraph(p_text, style_normal))

    sec4_3 = rc.CHAPTER_4["sections"][2]
    story.append(Paragraph(f"{sec4_3['num']}  {sec4_3['title']}", style_sec_head))
    for p_text in sec4_3["paragraphs"]:
        story.append(Paragraph(p_text, style_normal))

    story.extend(make_rl_fig(os.path.join(FIG_DIR, "fig_system_architecture.png"),
                             "Fig. 4. Complete end-to-end autonomous agricultural robot system architecture.", width=5.6*inch))

    t7 = sec4_3["table_vii"]
    story.extend(make_rl_table(f"{t7['id']}<br/>{t7['title']}", t7["headers"], t7["rows"], col_widths=[110, 95, 80, 170]))

    sec4_4 = rc.CHAPTER_4["sections"][3]
    story.append(Paragraph(f"{sec4_4['num']}  {sec4_4['title']}", style_sec_head))
    for p_text in sec4_4["paragraphs"]:
        story.append(Paragraph(p_text, style_normal))

    sec4_5 = rc.CHAPTER_4["sections"][4]
    story.append(Paragraph(f"{sec4_5['num']}  {sec4_5['title']}", style_sec_head))
    for p_text in sec4_5["paragraphs"]:
        story.append(Paragraph(p_text, style_normal))

    story.extend(make_rl_fig(os.path.join(FIG_DIR, "fig_mission_flowchart.png"),
                             "Fig. 5. Complete autonomous agricultural robot operational mission flowchart.", width=4.8*inch))
    story.append(PageBreak())

    # CHAPTER 5
    story.append(Paragraph("CHAPTER 5<br/>RESULTS AND DISCUSSION", style_ch_head))
    sec5_1 = rc.CHAPTER_5["sections"][0]
    story.append(Paragraph(f"{sec5_1['num']}  {sec5_1['title']}", style_sec_head))
    for p_text in sec5_1["paragraphs"]:
        story.append(Paragraph(p_text, style_normal))
    t8 = sec5_1["table_viii"]
    story.extend(make_rl_table(f"{t8['id']}<br/>{t8['title']}", t8["headers"], t8["rows"], col_widths=[130, 70, 70, 45, 140]))

    sec5_2 = rc.CHAPTER_5["sections"][1]
    story.append(Paragraph(f"{sec5_2['num']}  {sec5_2['title']}", style_sec_head))
    for p_text in sec5_2["paragraphs"][:2]:
        story.append(Paragraph(p_text, style_normal))

    story.extend(make_rl_fig(os.path.join(FIG_DIR, "first_plant_inspection_frame.png"),
                             "Fig. 6. End-effector inspection camera capture of the first plant canopy in Webots.", width=2.5*inch, height=2.5*inch))

    for p_text in sec5_2["paragraphs"][2:4]:
        story.append(Paragraph(p_text, style_normal))

    story.extend(make_rl_fig(os.path.join(FIG_DIR, "fig_inspection_samples.png"),
                             "Fig. 7. Representative in-situ inspection frames annotated by EfficientNet-B0.", width=5.6*inch))

    for p_text in sec5_2["paragraphs"][4:]:
        story.append(Paragraph(p_text, style_normal))

    sec5_3 = rc.CHAPTER_5["sections"][2]
    story.append(Paragraph(f"{sec5_3['num']}  {sec5_3['title']}", style_sec_head))
    for p_text in sec5_3["paragraphs"]:
        story.append(Paragraph(p_text, style_normal))

    t9 = sec5_3["table_ix"]
    story.extend(make_rl_table(f"{t9['id']}<br/>{t9['title']}", t9["headers"], t9["rows"], col_widths=[140, 80, 80, 155]))

    t10 = sec5_3["table_x"]
    story.extend(make_rl_table(f"{t10['id']}<br/>{t10['title']}", t10["headers"], t10["rows"], col_widths=[105, 50, 50, 50, 50, 50, 50, 50]))

    story.extend(make_rl_fig(os.path.join(FIG_DIR, "fig_training_curves.png"),
                             "Fig. 8. EfficientNet-B0 model optimization curves over 25 epochs.", width=5.6*inch))

    t11 = sec5_3["table_xi"]
    story.extend(make_rl_table(f"{t11['id']}<br/>{t11['title']}", t11["headers"], t11["rows"], col_widths=[115, 45, 55, 55, 55, 45, 45, 40]))

    story.extend(make_rl_fig(os.path.join(FIG_DIR, "fig_confusion_matrix.png"),
                             "Fig. 9. Field inspection confusion matrix (66 leaves) and per-class performance metrics.", width=5.6*inch))

    story.extend(make_rl_fig(os.path.join(FIG_DIR, "confidence_graph.png"),
                             "Fig. 10. Leaf-by-leaf AI inspection confidence across all 66 crop panels.", width=5.6*inch))

    t12 = sec5_3["table_xii"]
    story.extend(make_rl_table(f"{t12['id']}<br/>{t12['title']}", t12["headers"], t12["rows"], col_widths=[125, 65, 65, 65, 55, 80]))

    story.extend(make_rl_fig(os.path.join(FIG_DIR, "fig_chemical_savings.png"),
                             "Fig. 11. Chemical volume and canopy treatment comparison (Targeted vs Broadcast).", width=4.8*inch))

    t13 = sec5_3["table_xiii"]
    story.extend(make_rl_table(f"{t13['id']}<br/>{t13['title']}", t13["headers"], t13["rows"], col_widths=[130, 85, 85, 75, 80]))

    t14 = sec5_3["table_xiv"]
    story.extend(make_rl_table(f"{t14['id']}<br/>{t14['title']}", t14["headers"], t14["rows"], col_widths=[95, 95, 95, 100, 70]))

    story.extend(make_rl_fig(os.path.join(FIG_DIR, "farm_dashboard.png"),
                             "Fig. 12. Comprehensive AI agricultural robot testing field report dashboard.", width=5.5*inch, height=4.2*inch))

    sec5_4 = rc.CHAPTER_5["sections"][3]
    story.append(Paragraph(f"{sec5_4['num']}  {sec5_4['title']}", style_sec_head))
    for p_text in sec5_4["paragraphs"]:
        story.append(Paragraph(p_text, style_normal))
    story.append(PageBreak())

    # CHAPTER 6
    story.append(Paragraph("CHAPTER 6<br/>CONCLUSION AND FUTURE DIRECTIONS", style_ch_head))
    for sec in rc.CHAPTER_6["sections"]:
        story.append(Paragraph(f"{sec['num']}  {sec['title']}", style_sec_head))
        for p_text in sec["paragraphs"]:
            story.append(Paragraph(p_text, style_normal))
    story.append(PageBreak())

    # CHAPTER 7
    story.append(Paragraph("CHAPTER 7<br/>REFERENCES", style_ch_head))
    for ref_str in rc.CHAPTER_7["references"]:
        story.append(Paragraph(ref_str, style_ref))

    print("Rendering PDF with ReportLab NumberedCanvas...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF build complete:", OUT_PDF_PATH)

    reader = PdfReader(OUT_PDF_PATH)
    page_count = len(reader.pages)
    print(f"Final PDF Page Count: {page_count} pages")
    return page_count

if __name__ == "__main__":
    build_pdf()
