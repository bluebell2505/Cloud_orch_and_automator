import psycopg2
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import sys

DB_URL = "postgresql://cicd_user:cicd_pass@127.0.0.1:5432/cicd_db"

NAVY       = colors.HexColor("#0C447C")
BLUE       = colors.HexColor("#185FA5")
BLUE_MID   = colors.HexColor("#378ADD")
LIGHT_BLUE = colors.HexColor("#E6F1FB")
GREEN      = colors.HexColor("#1D9E75")
AMBER      = colors.HexColor("#EF9F27")
PURPLE     = colors.HexColor("#7F77DD")
RED        = colors.HexColor("#E24B4A")
DARK       = colors.HexColor("#2C2C2A")
GRAY       = colors.HexColor("#888780")
WHITE      = colors.white


def get_data():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM pipeline_events;")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM pipeline_events WHERE fix_successful = true;")
    fixed = cur.fetchone()[0]
    cur.execute("SELECT ROUND(AVG(time_to_fix)) FROM pipeline_events WHERE fix_successful = true;")
    mttr = cur.fetchone()[0] or 0
    cur.execute("SELECT ROUND(AVG(confidence)::numeric, 2) FROM pipeline_events;")
    avg_conf = float(cur.fetchone()[0] or 0)
    cur.execute("SELECT ROUND(COUNT(*) FILTER (WHERE fix_successful = true) * 100.0 / NULLIF(COUNT(*),0), 1) FROM pipeline_events;")
    success_rate = cur.fetchone()[0] or 0
    cur.execute("SELECT failure_type, COUNT(*) as count FROM pipeline_events GROUP BY failure_type ORDER BY count DESC;")
    failure_dist = cur.fetchall()
    cur.execute("SELECT action_taken, COUNT(*) FROM pipeline_events GROUP BY action_taken ORDER BY count DESC;")
    actions = cur.fetchall()
    cur.execute("SELECT id, repo, failure_type, fix_type, confidence, fix_successful, action_taken, created_at FROM pipeline_events ORDER BY created_at DESC LIMIT 10;")
    recent = cur.fetchall()
    cur.close()
    conn.close()
    return total, fixed, mttr, avg_conf, success_rate, failure_dist, actions, recent


def draw_header_footer(canvas, doc):
    canvas.saveState()
    w, h = letter

    # Navy header bar
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 60, w, 60, fill=1, stroke=0)

    # Blue accent line below header
    canvas.setFillColor(BLUE_MID)
    canvas.rect(0, h - 64, w, 4, fill=1, stroke=0)

    # Header text
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 15)
    canvas.drawString(0.75*inch, h - 36, "CI/CD Pipeline Intelligence Report")
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(w - 0.75*inch, h - 36, datetime.now().strftime("%B %d, %Y  |  %H:%M"))

    # Footer bar
    canvas.setFillColor(colors.HexColor("#F1EFE8"))
    canvas.rect(0, 0, w, 40, fill=1, stroke=0)
    canvas.setFillColor(BLUE_MID)
    canvas.rect(0, 40, w, 1, fill=1, stroke=0)
    canvas.setFillColor(GRAY)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(0.75*inch, 15, "AI-Powered CI/CD Pipeline Orchestration")
    canvas.drawRightString(w - 0.75*inch, 15, f"Page {doc.page}")

    canvas.restoreState()


def generate_report():
    try:
        total, fixed, mttr, avg_conf, success_rate, failure_dist, actions, recent = get_data()
    except Exception as e:
        print(f"Error connecting to database: {e}")
        print("Make sure Docker is running and the database is up.")
        sys.exit(1)

    filename = f"cicd_pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    # topMargin must be large enough to clear the header bar (64px + padding)
    doc = SimpleDocTemplate(
        filename, pagesize=letter,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=1.2*inch, bottomMargin=0.8*inch
    )

    section_style = ParagraphStyle("Section", fontName="Helvetica-Bold", fontSize=13,
                                    textColor=NAVY, spaceBefore=18, spaceAfter=8)
    body_style    = ParagraphStyle("Body", fontName="Helvetica", fontSize=10,
                                    textColor=DARK, spaceAfter=6, leading=16)
    label_style   = ParagraphStyle("Label", fontName="Helvetica", fontSize=9,
                                    textColor=GRAY, spaceAfter=16)

    story = []

    # Date label just below header
    story.append(Paragraph(f"Report generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", label_style))

    # KPI row 1
    story.append(Paragraph("Executive Summary", section_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE_MID, spaceAfter=12))

    metrics = [
        ["Total Failures", "Auto-Fixed", "Success Rate", "Avg MTTR"],
        [str(total), str(fixed), f"{success_rate}%", f"{mttr}s"]
    ]
    metric_table = Table(metrics, colWidths=[1.6*inch, 1.6*inch, 1.6*inch, 1.6*inch])
    metric_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), BLUE),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0), 11),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND",    (0,1), (-1,1), LIGHT_BLUE),
        ("TEXTCOLOR",     (0,1), (-1,1), NAVY),
        ("FONTNAME",      (0,1), (-1,1), "Helvetica-Bold"),
        ("FONTSIZE",      (0,1), (-1,1), 18),
        ("GRID",          (0,0), (-1,-1), 0.5, WHITE),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(metric_table)
    story.append(Spacer(1, 10))

    # AI confidence line
    conf_label = "High confidence" if avg_conf >= 0.75 else "Medium confidence" if avg_conf >= 0.5 else "Low confidence"
    conf_hex = "#1D9E75" if avg_conf >= 0.75 else "#EF9F27" if avg_conf >= 0.5 else "#E24B4A"
    story.append(Paragraph(
        f"<font color='{conf_hex}'><b>Avg AI Confidence Score: {avg_conf} — {conf_label}</b></font>",
        body_style))

    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_BLUE, spaceBefore=6, spaceAfter=6))

    # Failure distribution
    story.append(Paragraph("Failure Type Distribution", section_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE_MID, spaceAfter=10))
    if failure_dist:
        fd_data = [["Failure Type", "Count", "% of Total"]]
        for ftype, count in failure_dist:
            pct = round(count * 100 / total, 1) if total > 0 else 0
            fd_data.append([ftype or "unknown", str(count), f"{pct}%"])
        fd_table = Table(fd_data, colWidths=[3.5*inch, 1.5*inch, 1.5*inch])
        fd_table.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), NAVY),
            ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 10),
            ("ALIGN",         (1,0), (-1,-1), "CENTER"),
            ("ALIGN",         (0,0), (0,-1), "LEFT"),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_BLUE]),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#B5D4F4")),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING",   (0,0), (-1,-1), 12),
        ]))
        story.append(fd_table)

    # Actions taken
    story.append(Paragraph("Remediation Actions", section_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE_MID, spaceAfter=10))
    if actions:
        act_data = [["Action Taken", "Count"]]
        for action, count in actions:
            act_data.append([action or "unknown", str(count)])
        act_table = Table(act_data, colWidths=[4.5*inch, 2*inch])
        act_table.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), PURPLE),
            ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 10),
            ("ALIGN",         (1,0), (-1,-1), "CENTER"),
            ("ALIGN",         (0,0), (0,-1), "LEFT"),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, colors.HexColor("#EEEDFE")]),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#AFA9EC")),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING",   (0,0), (-1,-1), 12),
        ]))
        story.append(act_table)

    # Recent events
    story.append(Paragraph("Recent Pipeline Events (Last 10)", section_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BLUE_MID, spaceAfter=10))
    if recent:
        rec_data = [["ID", "Failure Type", "Fix Type", "Conf.", "Fixed?", "Action"]]
        for row in recent:
            id_, repo, ftype, fix_type, conf, fix_ok, action, created = row
            rec_data.append([
                str(id_),
                ftype or "-",
                fix_type or "-",
                str(conf) if conf else "-",
                "Yes" if fix_ok else "No",
                action or "-"
            ])
        rec_table = Table(rec_data, colWidths=[0.5*inch, 1.4*inch, 1.2*inch, 0.6*inch, 0.7*inch, 1.3*inch])
        rec_table.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), DARK),
            ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,-1), 9),
            ("ALIGN",         (0,0), (-1,-1), "CENTER"),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, colors.HexColor("#F1EFE8")]),
            ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#D3D1C7")),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(rec_table)

    doc.build(story, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    print(f"\nReport generated: {filename}")
    print("Double-click it to open!")


if __name__ == "__main__":
    generate_report()