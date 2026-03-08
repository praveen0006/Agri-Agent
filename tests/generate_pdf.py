from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_pdf():
    doc = SimpleDocTemplate("data/papers/mock_cotton_research.pdf", pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom Styles
    title_style = styles["Title"]
    heading1 = styles["Heading1"]
    heading2 = styles["Heading2"]
    normal = styles["Normal"]

    formula_style = ParagraphStyle(
        "Formula", parent=styles["Normal"], fontName="Courier", fontSize=12, spaceAfter=10, leftIndent=20
    )

    story = []

    # Title
    story.append(Paragraph("Evapotranspiration and Yield Responses of Cotton to Irrigation", title_style))
    story.append(Spacer(1, 12))

    # Abstract
    story.append(Paragraph("Abstract", heading1))
    story.append(
        Paragraph(
            "This study evaluates the effects of varying irrigation schedules on cotton yield and water use efficiency in semi-arid loamy soils. We present updated crop coefficients and soil moisture thresholds.",
            normal,
        )
    )
    story.append(Spacer(1, 12))

    # Introduction
    story.append(Paragraph("1. Introduction", heading1))
    story.append(
        Paragraph(
            "Precision irrigation requires accurate evapotranspiration (ETc) modeling over different growth stages. Loamy soils, common in cotton-growing regions, have a volumetric field capacity extending to 25%.",
            normal,
        )
    )
    story.append(Spacer(1, 12))

    # Methodology & Formulas
    story.append(Paragraph("2. Evapotranspiration Calculation", heading1))
    story.append(Paragraph("We calculate ETc using the dual crop coefficient approach as follows:", normal))
    story.append(Spacer(1, 8))

    # Formula
    story.append(Paragraph("ETc = (Kcb + Ke) * ETo", formula_style))

    story.append(
        Paragraph(
            "Where ETo is the reference evapotranspiration, Kcb is the basal crop coefficient, and Ke is the soil evaporation coefficient.",
            normal,
        )
    )
    story.append(Spacer(1, 12))

    # Results Table
    story.append(Paragraph("3. Growth Stage Parameters", heading1))
    story.append(
        Paragraph("The optimal moisture limits and coefficients for each growth stage are detailed in Table 1.", normal)
    )
    story.append(Spacer(1, 8))

    # Table Data
    data = [
        ["Growth Stage", "Duration (Days)", "Kc Value", "Min Moisture (%)", "Max Moisture (%)"],
        ["Germination", "15", "0.40", "18", "25"],
        ["Vegetative", "45", "0.75", "16", "23"],
        ["Flowering", "30", "1.15", "15", "22"],
        ["Boll Formation", "40", "1.05", "14", "20"],
        ["Maturity", "20", "0.60", "12", "18"],
    ]

    table = Table(data)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 12))

    # Conclusion
    story.append(Paragraph("4. Conclusion", heading1))
    story.append(
        Paragraph(
            "Water stress during the flowering stage leads to a 30% reduction in boll retention. Maintaining soil moisture above 15% is critical during this period. The wilting point for cotton in these loamy soils is 12%.",
            normal,
        )
    )

    doc.build(story)


if __name__ == "__main__":
    generate_pdf()
