import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether, CondPageBreak, NextPageTemplate)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

out = sys.argv[1]
FD = "/System/Library/Fonts/Supplemental/"
for n, f in [("Body", "Arial.ttf"), ("Body-B", "Arial Bold.ttf"), ("Body-I", "Arial Italic.ttf"),
             ("Body-BI", "Arial Bold Italic.ttf")]:
    pdfmetrics.registerFont(TTFont(n, FD + f))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-B", italic="Body-I", boldItalic="Body-BI")

NAVY = colors.HexColor("#12304A"); TEAL = colors.HexColor("#0F8B8D"); AMBER = colors.HexColor("#E8A33D")
LIGHT = colors.HexColor("#EEF4F7"); GRID = colors.HexColor("#C9D6DE"); INK = colors.HexColor("#1F2933")
GREY = colors.HexColor("#6B7B88"); PALEAMBER = colors.HexColor("#FDF3E1")
W, H = A4; LM = RM = 18 * mm; CW = W - LM - RM

S = lambda n, **k: ParagraphStyle(n, fontName=k.pop("fontName", "Body"), textColor=k.pop("textColor", INK), **k)
body = S("body", fontSize=9.5, leading=14, spaceAfter=5)
bul = S("bul", fontSize=9.5, leading=13.5, leftIndent=12, bulletIndent=2, spaceAfter=2.5)
h1 = S("h1", fontName="Body-B", fontSize=19, leading=23, textColor=colors.white)
h2 = S("h2", fontName="Body-B", fontSize=12.5, leading=16, textColor=NAVY, spaceBefore=11, spaceAfter=5)
h3 = S("h3", fontName="Body-B", fontSize=10, leading=13, textColor=TEAL, spaceBefore=6, spaceAfter=3)
cell = S("cell", fontSize=8.6, leading=11.5)
cellb = S("cellb", fontName="Body-B", fontSize=8.6, leading=11.5)
cellh = S("cellh", fontName="Body-B", fontSize=8.6, leading=11.5, textColor=colors.white)
cellc = S("cellc", fontSize=9, leading=12, alignment=TA_CENTER)
cellcb = S("cellcb", fontName="Body-B", fontSize=9, leading=12, alignment=TA_CENTER)
small = S("small", fontSize=8, leading=11, textColor=GREY)

P = lambda t, s=body: Paragraph(t, s)
def bullets(items): return [Paragraph(t, bul, bulletText="•") for t in items]
def numbered(items): return [Paragraph(t, bul, bulletText=f"{i}.") for i, t in enumerate(items, 1)]

def table(rows, widths, bold_first_col=False, zebra=True):
    data = []
    for r, row in enumerate(rows):
        if r == 0:
            data.append([Paragraph(c, cellh) for c in row])
        else:
            data.append([Paragraph(c, cellb if (bold_first_col and i == 0) else cell) for i, c in enumerate(row)])
    t = Table(data, colWidths=[w * CW for w in widths], repeatRows=1)
    st = [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LINEBELOW", (0, 0), (-1, -1), 0.4, GRID), ("BOX", (0, 0), (-1, -1), 0.6, GRID),
          ("TOPPADDING", (0, 0), (-1, -1), 4.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
          ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]
    if zebra:
        for r in range(2, len(rows), 2): st.append(("BACKGROUND", (0, r), (-1, r), LIGHT))
    t.setStyle(TableStyle(st)); return [t, Spacer(1, 6)]

def callout(title, text, bg=PALEAMBER, bar=AMBER):
    t = Table([[Paragraph(f"<b>{title}</b><br/>{text}", S("co", fontSize=9, leading=13))]], colWidths=[CW])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("LINEBEFORE", (0, 0), (0, -1), 3, bar),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return [t, Spacer(1, 7)]

def banner(num, title, subtitle=""):
    inner = [Paragraph(num, S("bn", fontName="Body-B", fontSize=9, textColor=AMBER, leading=12)), Paragraph(title, h1)]
    if subtitle: inner.append(Paragraph(subtitle, S("bs", fontSize=9.5, leading=13, textColor=colors.HexColor("#CFE3EA"))))
    t = Table([[inner]], colWidths=[CW])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY), ("LEFTPADDING", (0, 0), (-1, -1), 14),
                           ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                           ("LINEBELOW", (0, 0), (-1, -1), 3, TEAL)]))
    return [t, Spacer(1, 8)]

def sec(title): return [CondPageBreak(60 * mm), Paragraph(title, h2)]

# ---------------- page decorations ----------------
def cover(c, d):
    c.saveState()
    c.setFillColor(NAVY); c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(TEAL); c.rect(0, H * 0.36, W, 5, stroke=0, fill=1)
    c.setFillColor(AMBER); c.rect(LM, H * 0.36 - 40, 60, 5, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Body-B", 11); c.setFillColor(AMBER); c.drawString(LM, H - 70 * mm, "STRATEGIC FEASIBILITY REPORT")
    c.setFillColor(colors.white); c.setFont("Body-B", 31)
    for i, line in enumerate(["Logistics Business", "Models for the", "Amaravati Capital", "Region"]):
        c.drawString(LM, H - 90 * mm - i * 38, line)
    c.setFont("Body", 12); c.setFillColor(colors.HexColor("#CFE3EA"))
    c.drawString(LM, H * 0.36 - 70, "Vijayawada – Guntur – Mangalagiri Corridor")
    c.setFont("Body", 10)
    for i, t in enumerate(["1  Medical Distribution & Pharmaceutical Logistics",
                           "2  Printing, Paper Stock & Industrial Supply Logistics",
                           "3  General Lorry Transport & Bulk Cargo (Asset-Light Brokerage)"]):
        c.drawString(LM, H * 0.36 - 105 - i * 16, t)
    c.setFont("Body", 8.5); c.setFillColor(colors.HexColor("#8FB0BF"))
    c.drawString(LM, 22 * mm, "Figures are indicative estimates (mid-2026). Verify rates, GST rules and project status before committing capital.")
    c.restoreState()

def page(c, d):
    c.saveState()
    c.setStrokeColor(GRID); c.setLineWidth(0.5); c.line(LM, H - 14 * mm, W - RM, H - 14 * mm)
    c.setFont("Body", 8); c.setFillColor(GREY)
    c.drawString(LM, H - 11 * mm, "Strategic Feasibility Report – Amaravati Logistics Models")
    c.drawRightString(W - RM, 12 * mm, f"Page {d.page}")
    c.setFillColor(TEAL); c.rect(LM, 12 * mm - 2, 18, 2, stroke=0, fill=1)
    c.restoreState()

doc = BaseDocTemplate(out, pagesize=A4, leftMargin=LM, rightMargin=RM, topMargin=22 * mm, bottomMargin=20 * mm,
                      title="Strategic Feasibility Report: Logistics Models in the Amaravati Capital Region",
                      author="", subject="Logistics market-entry feasibility")
fr = Frame(LM, 20 * mm, CW, H - 42 * mm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate("cover", frames=[Frame(0, 0, W, H)], onPage=cover),
                      PageTemplate("main", frames=[fr], onPage=page)])

st = [NextPageTemplate("main"), PageBreak()]

# ---------------- executive summary ----------------
st += banner("OVERVIEW", "Executive Summary", "What this report evaluates and the bottom line")
st += [P("This report compares three logistics business models for the Amaravati capital region and the Vijayawada–Guntur–Mangalagiri corridor. "
         "Each is assessed on market dynamics, operations, financial structure, regulation and GST, and risk. The final chapter ranks them and recommends an entry sequence.")]
st += table([["Model", "Core idea", "Verdict"],
             ["1. Pharma logistics", "Temperature-controlled and compliant delivery for manufacturers, stockists and hospitals", "Best margins, highest compliance burden. Enter last."],
             ["2. Printing and paper logistics", "Reels, reams and finished print moved for printers, publishers and packaging plants", "Balanced, but strongly seasonal. Enter second."],
             ["3. General and bulk brokerage", "Matching construction and commercial loads with independent lorry owners", "Fastest cash flow, lowest capital. Recommended entry point."]],
            [0.24, 0.46, 0.30], bold_first_col=True)
st += callout("Bottom line", "Start with <b>asset-light bulk and general freight brokerage</b>, targeting material dealers and suppliers rather than main contractors. "
              "Use the vehicle network and billing discipline it builds to add paper logistics within 9–18 months, and carrier-only pharma logistics after that.")
st += callout("Basis of figures", "All rates, margins, credit periods and tax rules are indicative estimates as of mid-2026. Before committing capital: collect 10–15 live freight quotes per lane, "
              "confirm current GST rates with a practising GST consultant, and check the latest CRDA and APMSIDC tender status.", bg=LIGHT, bar=TEAL)

# ---------------- regional baseline ----------------
st += sec("Regional Baseline (applies to all three models)")
st += [Paragraph("Project pipeline", h3)]
st += [P("Amaravati works resumed in 2024–25, funded by World Bank, ADB, HUDCO and central support. The pipeline includes:")]
st += bullets(["The Secretariat/HOD towers, the Legislature and the High Court complex.",
               "Housing for ministers, officers and staff, plus trunk roads and utilities.",
               "The Outer Ring Road and the Errupalem–Amaravati–Nambur rail link.",
               "Announced institutional projects such as a health-city cluster and the Quantum Valley initiative."])
st += [P("Treat the timelines as policy-dependent and track the tender status.")]
st += [Paragraph("Corridor strengths", h3)]
st += bullets(["<b>Vijayawada:</b> the logistics node, with the Autonagar lorry hub, rail junction and airport.",
               "<b>Guntur:</b> the agri-trade and warehousing node.",
               "<b>Mangalagiri:</b> AIIMS and institutional campuses."])
st += [Paragraph("Anchor lanes", h3)]
st += table([["Lane", "Approx. distance", "Typical cargo"],
             ["Hyderabad ↔ Vijayawada (NH-65)", "~270–275 km", "Pharma, paper, general freight"],
             ["Chennai ↔ Vijayawada", "~450 km", "Industrial, FMCG"],
             ["Visakhapatnam ↔ Vijayawada", "~350 km", "Steel, industrial"],
             ["Palnadu cement belt → Amaravati", "~80–120 km", "Cement"],
             ["Krishna river / quarry belt → Amaravati", "Short haul", "Sand, aggregates"]], [0.46, 0.22, 0.32])
st += [Paragraph("Indicative market freight rates (open trucks, long haul)", h3)]
st += table([["Truck type", "Rate"], ["6-wheeler (9–10 t)", "Rs. 25–30 per km"], ["10-wheeler (16–18 t)", "Rs. 32–40 per km"],
             ["14-wheeler (25–28 t)", "Rs. 40–50 per km"]], [0.5, 0.5])
st += [P("Short-haul tipper work is priced per trip or per tonne. Refrigerated rates run roughly 40–80% above dry-van rates.")]
st += callout("Eluru district coal-gasification proposal (Chintalapudi–Recherla)",
              "Press reports describe a large Underground Coal Gasification proposal in Eluru district, with an exploration and pilot phase from late 2026 and local farmer opposition. "
              "Because the coal stays underground and the output moves by pipeline, there would be <b>no coal haulage</b>. At most it adds construction-material and equipment demand later in the decade. "
              "Treat it as upside, not as part of the base case, and verify its status independently.", bg=LIGHT, bar=TEAL)

# ================= STRATEGY 1 =================
st += [PageBreak()] + banner("STRATEGY 1", "Medical Distribution & Pharmaceutical Logistics", "Highest margin and stickiness, highest compliance burden")
st += [Paragraph("1. Market Dynamics &amp; Amaravati Context", h2), Paragraph("Demand drivers", h3)]
st += bullets(["AIIMS Mangalagiri, the Guntur and Vijayawada government hospitals, and the large private tertiary chains create steady institutional demand.",
               "A planned or announced health-city cluster in Amaravati would add hospitals, diagnostic chains and medical colleges, each needing recurring supply of drugs, consumables and implants.",
               "Government relocation raises resident population, which raises retail pharmacy and clinic density.",
               "APMSIDC, the state procurement agency, moves bulk drugs through central drug stores. Last-mile and inter-store transfers are partly outsourced.",
               "Vijayawada is a regional wholesale drug hub for coastal Andhra. Most branded stock arrives from Hyderabad (Genome Valley) and Chennai, with some from Visakhapatnam."])
st += [Paragraph("Target B2B personas", h3)]
st += table([["Persona", "Expectation", "Core pain point"],
             ["Pharma manufacturers and C&amp;F agents", "GDP-compliant, damage-free movement, tracking", "Temperature excursions, pilferage, delayed replenishment"],
             ["Wholesale stockists", "Same-day or next-day city and district delivery", "Many small drops, invoice and acknowledgment handling"],
             ["Hospital chains", "Urgent (stat) deliveries, expiry-safe stock", "Stock-outs, emergency requests, cold-chain reagents"],
             ["Diagnostic labs", "Sample and reagent movement at 2–8°C", "Reliable pickup windows"],
             ["Retail pharmacy chains", "Scheduled replenishment", "Returns and near-expiry reverse logistics"]], [0.26, 0.37, 0.37], bold_first_col=True)
st += [Paragraph("Seasonality", h3)]
st += bullets(["The most stable of the three models, with no real off-season.",
               "Monsoon and post-monsoon months (July–October) lift volumes of antibiotics, antipyretics, anti-diabetics and vector-borne disease medicines.",
               "Summer heat (March–June) raises cold-chain failure risk and cost.",
               "Government procurement is lumpy and often bunches near fiscal year-end (Q4)."])
st += [Paragraph("2. Operational Mechanics &amp; Workflow", h2)]
st += callout("Critical decision: carrier or distributor",
              "A pure <b>transport/3PL carrier</b> moves goods it does not own and needs no drug licence for the transport itself. A <b>distributor/stockist</b> buys and sells drugs and needs a wholesale drug licence and a registered pharmacist. "
              "Storing drugs for others usually raises a licensing question with the AP Drugs Control Administration, so confirm in writing before leasing any warehouse. The lowest-risk entry is the asset-light carrier/3PL role.")
st += [Paragraph("Transaction lifecycle", h3)]
st += numbered(["Secure a contract or rate card with a manufacturer, C&amp;F agent or stockist.",
                "Receive the dispatch request: invoice, e-way bill Part A, and the temperature requirement (ambient, 15–25°C, or 2–8°C).",
                "Allocate a vehicle: a vetted, rate-contracted fleet (LCV, closed-body, insulated or reefer) or a spot-sourced vehicle. Check fitness, closed body, working reefer unit and a calibrated data logger.",
                "Pre-dispatch check: pre-cool the vehicle, verify seals, record the logger start, and check driver KYC.",
                "Update Part B of the e-way bill with the vehicle number, and issue the consignment note (LR).",
                "Track in transit, with temperature and route-deviation alerts.",
                "Deliver and collect a signed, stamped acknowledgment on the invoice copy, plus the temperature log printout for cold-chain loads.",
                "Handle exceptions (short receipt, damage, rejection) and reverse logistics.",
                "Bill with the POD and temperature report attached."])
st += [Paragraph("Technology stack", h3)]
st += bullets(["A TMS or lightweight dispatch tool, with GPS and mobile-app driver check-in.",
               "IoT temperature loggers with real-time alerts (SMS or WhatsApp).",
               "e-way bill integration and digital POD capture (photo plus OTP or signature).",
               "A WhatsApp Business broadcast group per client."])
st += [Paragraph("Day-to-day risk management", h3)]
st += bullets(["<b>Breakdown:</b> keep a standby reefer or insulated LCV in Vijayawada, with a transfer protocol that preserves logger continuity and a 2-hour escalation rule.",
               "<b>Reefer unit failure:</b> carry gel packs and insulated shippers as backup, and maintain a temperature-excursion SOP.",
               "<b>Driver no-show:</b> keep 2–3 pre-vetted drivers per client lane.",
               "<b>Route diversion:</b> configure alternative routes and note city heavy-vehicle entry timings."])
st += [Paragraph("3. Financial Architecture &amp; Revenue Model", h2), Paragraph("Cash flow cycle", h3)]
st += table([["Counterparty", "Typical term"],
             ["Pharma manufacturers and C&amp;F agents", "30–60 days"], ["Wholesalers", "15–45 days"], ["Private hospitals", "45–90 days"],
             ["Government hospitals and agencies (APMSIDC-linked)", "90–180+ days (high delay risk)"],
             ["Vehicle operators and drivers", "Advance at loading, balance within 0–7 days"]], [0.55, 0.45], bold_first_col=True)
st += [Paragraph("Margins", h3)]
st += bullets(["Pure freight brokerage on pharma: roughly 8–15% on specialised or temperature-controlled loads, against 3–8% on general loads.",
               "A 3PL with contracted fleet and handling: 12–20% gross.",
               "Distributor trade margins are typically about 8–10% for the stockist on non-scheduled drugs, but this is capital-intensive (inventory plus receivables)."])
st += [Paragraph("Working-capital strategy", h3)]
st += bullets(["Stay a carrier/3PL initially and avoid holding inventory.",
               "Pay vehicle owners 50–70% at loading and the balance after the POD.",
               "Require a 20–30% advance or deposit from new or small clients, and use invoice discounting for larger ones.",
               "Exclude government and APMSIDC-linked clients until a credit buffer exists."])
st += [Paragraph("4. Regulatory, Legal &amp; GST Compliance", h2), Paragraph("Registrations", h3)]
st += bullets(["GST registration, PAN, Udyam, Shop &amp; Establishment, and a current account.",
               "<b>Carrier only:</b> no drug licence for pure transport. Vehicles need valid fitness, insurance, PUC and permit or authorisation as applicable. Goods carriages are largely permit-exempt for intra-state operation since the 2018 MoRTH notification, but verify.",
               "<b>Distributor:</b> a wholesale drug licence (Forms 20B/21B for restricted categories, plus 20/21 as applicable) under the Drugs &amp; Cosmetics Act 1940 and Rules 1945, with a registered pharmacist or competent person and suitable premises with cold storage.",
               "<b>Controlled categories:</b> narcotics and psychotropic substances (NDPS Rules) and Schedule H1/X need strict record-keeping and are best excluded at entry.",
               "Follow WHO-GDP and an SOP-based quality system. Track-and-trace QR coding applies to the top brands."])
st += [Paragraph("GST", h3)]
st += bullets(["Medicines are mostly taxed at 5% after the 2025 rate rationalisation, with some life-saving drugs at nil. Confirm the HSN-specific rate.",
               "<b>E-way bill</b> is required where consignment value exceeds Rs. 50,000. Part A is by the consignor and Part B (vehicle number) by the transporter. Validity is 1 day per 200 km. Medicines are <i>not</i> exempt.",
               "E-invoicing applies above the Rs. 5 crore turnover threshold.",
               "Transport-service GST and RCM rules are set out under Strategy 3 (Section 4).",
               "Under section 43B(h), micro and small suppliers (Udyam-registered) must be paid within 45 days for the buyer to claim the deduction. This helps collections from corporates."])
st += [Paragraph("5. Risk-Benefit Matrix &amp; Mitigation", h2)]
st += table([["Risk", "Impact", "Mitigation"],
             ["Temperature excursion claim", "High: a whole consignment can be rejected", "Calibrated loggers, pre-cooling SOP, carrier liability insurance, contractual liability limits"],
             ["Regulatory misstep (storing drugs without a licence)", "Severe", "Stay carrier-only at first; get written clarity from the AP DCA"],
             ["Government payment delays", "High", "Exclude, or demand advance; use invoice discounting"],
             ["Undercutting by unorganised LCV operators", "Medium", "Differentiate on logs, POD and reliability; target contract clients"],
             ["Theft or pilferage", "Medium", "Sealed vehicles, GPS geo-fencing, transit insurance"],
             ["Small-lot density (many small drops)", "Medium", "Route consolidation, milk-run schedules"]], [0.30, 0.22, 0.48], bold_first_col=True)
st += callout("Hidden vulnerability", "The whole value proposition rests on documented compliance. One failed audit, or a single temperature failure with no logs, can end a client relationship. "
              "Capex for reefers and loggers also arrives before revenue does.")

# ================= STRATEGY 2 =================
st += [PageBreak()] + banner("STRATEGY 2", "Printing, Paper Stock & Industrial Supply Logistics", "Balanced economics, strongly seasonal demand")
st += [Paragraph("1. Market Dynamics &amp; Amaravati Context", h2), Paragraph("Demand drivers", h3)]
st += bullets(["Government relocation generates large volumes of forms, stationery, registers, files, notices and publications. State departments are major buyers.",
               "The textbook and exam-material cycle for the school education system is large and tender-based. Guntur, Vijayawada and nearby districts have a dense printer base.",
               "Packaging and corrugated demand follows regional manufacturing and agri-processing (chilli, rice, aqua exports).",
               "Universities, colleges and new institutional campuses add steady stationery volume.",
               "Paper mills are mostly outside the region (Andhra Paper at Rajahmundry, ITC Bhadrachalam in Telangana, plus south and west India mills and traders). Inbound trucks therefore terminate at Vijayawada and Guntur, and printed output flows back out."])
st += [Paragraph("Target B2B personas", h3)]
st += table([["Persona", "Expectation", "Pain point"],
             ["Commercial printers and press owners", "Damage-free reels and sheets, on-time delivery", "Moisture damage, rework, tender-deadline delays"],
             ["Paper traders and stockists", "Cost-efficient bulk movement", "Handling losses, unloading delays"],
             ["Packaging and corrugated plants", "Reliable inbound roll supply", "Line stoppages"],
             ["Publishers and textbook contractors", "Time-bound multi-district distribution", "Dispatch compression just before school reopening"],
             ["Government departments", "Compliant, documented deliveries", "Long payment cycles, paperwork"]], [0.28, 0.36, 0.36], bold_first_col=True)
st += [Paragraph("Seasonality", h3)]
st += table([["Period", "Driver"], ["March–June", "Textbook and notebook peak ahead of school reopening"], ["January–March", "Exam stationery"],
             ["October–December", "Calendar, diary and festive print work"], ["July–September", "Trough; monsoon moisture raises damage risk"]], [0.3, 0.7], bold_first_col=True)
st += [Paragraph("2. Operational Mechanics &amp; Workflow", h2), Paragraph("Transaction lifecycle", h3)]
st += numbered(["Win a repeat supply relationship with a printer, trader or publisher.",
                "Receive load details: weight, dimensions, packaging (reels, reams, cartons, pallets) and handling needs such as a reel clamp or forklift.",
                "Source an appropriate vehicle: a covered body, or a tarpaulin-covered open truck with a waterproof layer. Check the floor condition.",
                "Issue the LR and e-way bill, and record loading condition with photos.",
                "Track the vehicle and update the client.",
                "Deliver with a signed POD and an unloading and damage remark.",
                "Handle claims if there is damage, then invoice."])
st += [Paragraph("Technology and risk management", h3)]
st += bullets(["A TMS or simple dispatch sheet integrated with e-way bill tools; GPS tracking and WhatsApp client updates; photo-based loading and unloading evidence.",
               "<b>Rain or moisture:</b> require tarpaulin plus plastic wrap, and avoid dispatch in heavy rain.",
               "<b>Breakdown:</b> any transshipment must be done under cover.",
               "<b>Driver cancellation:</b> keep a bench of at least 2–3 operators per major lane.",
               "<b>Deadline-driven jobs:</b> build buffer time into textbook dispatches."])
st += [Paragraph("3. Financial Architecture &amp; Revenue Model", h2)]
st += table([["Counterparty", "Typical term"], ["Printers and traders (private, MSME)", "15–45 days"], ["Larger publishers and corporates", "45–60 days"],
             ["Government textbook or department work", "60–120+ days"], ["Vehicle operators", "Advance plus balance on POD within 3–7 days"]], [0.55, 0.45], bold_first_col=True)
st += [Paragraph("Margins and working capital", h3)]
st += bullets(["Brokerage or freight margin of about 5–10% on contracted lanes, roughly Rs. 1,000–2,500 per full-truckload trip.",
               "Specialised handling (reel clamps, careful unloading) can command a premium, as can value-added warehousing and delivery coordination.",
               "Many printers run on thin margins, so freight is price-sensitive.",
               "Seek monthly contracts with a 15–30 day term or a part-advance, and pay the vehicle owner 60–70% at loading and the rest against POD.",
               "Ask publishers to fund the March–June peak partially through pre-season advances.",
               "Avoid inventory ownership. If you supply paper, restrict it to back-to-back orders confirmed before you buy."])
st += [Paragraph("4. Regulatory, Legal &amp; GST Compliance", h2)]
st += bullets(["GST, PAN, Udyam, Shop &amp; Establishment. No industry-specific transport licence beyond vehicle compliance. If trading paper, add GST registration for goods and a trade licence.",
               "<b>Overload compliance is vital.</b> Paper reels are dense, and overloading penalties under the Motor Vehicles Act (2019 amendment) are heavy. Verify axle limits.",
               "Paper and paperboard attract varied GST rates by HSN. Several education items, such as exercise books, moved to nil or lower rates in 2025. Confirm the rate per item.",
               "E-way bill is mandatory above Rs. 50,000, which reel consignments will usually exceed.",
               "GTA and broker rules are as described under Strategy 3: 5% RCM if the GTA issues a consignment note, and 18% on commission if you act as a broker.",
               "If you trade paper, supplies carry normal GST and require e-invoicing above the turnover threshold."])
st += [Paragraph("5. Risk-Benefit Matrix &amp; Mitigation", h2)]
st += table([["Risk", "Impact", "Mitigation"],
             ["Seasonality and peak overload", "High", "Contract bench of operators, pre-booked capacity, off-season lanes (packaging, agri-processing)"],
             ["Moisture or handling damage claims", "Medium–High", "Tarpaulin and wrap SOP, photo evidence, cargo insurance, liability-limit clause"],
             ["Slow-paying government or textbook clients", "High", "Advances, shorter credit, no concentration above 25% of revenue"],
             ["Unorganised undercutters", "Medium", "Reliability SLAs and claims handling"],
             ["Paper price volatility if trading", "Medium–High", "Trade only back-to-back, never speculatively"]], [0.30, 0.18, 0.52], bold_first_col=True)
st += callout("Hidden vulnerability", "Concentration. A handful of printers or publishers may generate most of your volume, and the textbook cycle makes revenue lumpy. "
              "Fixed overhead then has to be carried through the July–September trough.")

# ================= STRATEGY 3 =================
st += [PageBreak()] + banner("STRATEGY 3", "General Lorry Transport & Bulk Material Cargo", "Asset-light brokerage: fastest cash flow, lowest capital")
st += [Paragraph("1. Market Dynamics &amp; Amaravati Context", h2), Paragraph("Demand drivers", h3)]
st += bullets(["<b>Construction-materials surge:</b> capital-city building consumes cement, steel, sand, aggregates, bricks, ready-mix inputs and pipes. This is the largest and most immediate demand pool in the region.",
               "<b>Sand and aggregates:</b> the state's free-sand policy from 2024 shifted cost mostly to transport and loading. Short-haul tipper trips from river reaches and quarries (Mangalagiri, Kondapalli, Guntur belt) repeat daily.",
               "<b>Cement:</b> the Palnadu and Guntur cement cluster supplies Amaravati over a short haul.",
               "<b>Steel and industrial inputs</b> come from Visakhapatnam, Chennai and Hyderabad.",
               "<b>Agri-commodities:</b> Guntur chilli, cotton, rice and pulses give the corridor a strong counter-seasonal backhaul base.",
               "<b>Infrastructure projects:</b> NH widening, the ORR and the rail link create sustained heavy-haul demand."])
st += [Paragraph("Target B2B personas", h3)]
st += table([["Persona", "Expectation", "Pain point"],
             ["Material dealers (cement, steel, tiles)", "Quick vehicle availability, reliable delivery", "Vehicle shortage in peak weeks, rate swings"],
             ["Construction contractors and RMC plants", "Timely tipper supply", "Idle-site cost, poor trip tracking"],
             ["Aggregate and sand suppliers", "Daily dispatch scale", "Weighbridge disputes, shortages"],
             ["Manufacturers and traders", "Dependable FTL for long haul", "Return-load pricing, detention"],
             ["Agri traders and mills", "Seasonal bulk loads", "Peak-season shortage"]], [0.32, 0.34, 0.34], bold_first_col=True)
st += [Paragraph("Seasonality", h3)]
st += bullets(["Monsoon (June–September) and flood periods slow construction and restrict sand extraction, so demand dips.",
               "October–December can bring cyclone-related disruption on the east coast.",
               "Peak construction runs roughly November to May.",
               "Agri-cargo peaks February to May, which fills the backhaul gap when construction slows."])
st += [Paragraph("2. Operational Mechanics &amp; Workflow", h2), Paragraph("Transaction lifecycle", h3)]
st += numbered(["<b>Secure the load.</b> Take an order from a dealer, contractor or manufacturer with load type, weight, origin, destination and loading time. Quote on a margin-plus basis.",
                "<b>Source the vehicle</b> from a verified owner network (Autonagar, the Guntur lorry yard, Mangalagiri) and open-market load boards. Check RC, insurance, fitness, driver licence, PAN and past performance.",
                "<b>Confirm the rate</b> and advance terms with the owner, and issue a vehicle booking slip.",
                "<b>Documentation:</b> issue the LR and confirm the e-way bill (Part A from the consignor, Part B with the vehicle number).",
                "<b>Dispatch and tracking</b> using driver calls, a GPS link or app, and milestone updates.",
                "<b>Delivery:</b> obtain the POD with the weighbridge slip, stamp and signature.",
                "<b>Settlement:</b> pay the owner's balance against the original POD, then invoice the client."])
st += [Paragraph("Technology and risk management", h3)]
st += bullets(["A basic TMS, or a structured spreadsheet and WhatsApp workflow at first; GPS and FASTag-based location data; digital LR and POD capture; a vehicle-owner database with ratings; per-trip payment tracking.",
               "<b>Breakdown:</b> replace the vehicle from the standby network within a set number of hours. The booking terms should make the owner bear the cost where at fault.",
               "<b>Cancellations:</b> keep a 15–20% over-supply bench and a penalty or ratings system.",
               "<b>Route diversions:</b> monitor NH-16 and NH-65 works and city entry timings.",
               "<b>Overloading and fines:</b> ban overloading in the booking contract and allocate e-challan responsibility.",
               "<b>Fraud and non-delivery:</b> use GPS, check owner identity, and do not send high-value cargo with unknown operators."])
st += [Paragraph("3. Financial Architecture &amp; Revenue Model", h2)]
st += table([["Counterparty", "Typical term"], ["Material dealers", "Cash or 7–15 days (best payers)"], ["RMC plants and mid-sized contractors", "30–60 days"],
             ["Large contractors on government work", "60–120+ days, with retention"], ["Vehicle owners", "70–80% advance at loading, balance on POD within 3–7 days"]], [0.5, 0.5], bold_first_col=True)
st += [P("<b>The structural gap:</b> owners want cash in days, and clients pay in weeks. The broker funds the difference.")]
st += [Paragraph("Illustrative working-capital sizing", h3),
       P("Assumptions: 40 trips a month at an average freight of Rs. 18,000, so Rs. 7.2 lakh billed monthly. Float scales linearly with volume.")]
st += table([["Client credit period", "Approx. peak float needed"], ["15 days", "~Rs. 3.5 lakh"], ["30 days", "~Rs. 7 lakh"], ["45 days", "~Rs. 10.5 lakh"]], [0.5, 0.5], bold_first_col=True)
st += [Paragraph("Margins", h3)]
st += bullets(["General brokerage: 3–8% of freight, about Rs. 500–1,500 per trip.",
               "Bulk and short-haul: roughly Rs. 15–60 per tonne, depending on the lane.",
               "At roughly Rs. 1,000 per trip, about 150–250 trips a month are needed to clear meaningful net income after overhead. Revenue is volume-driven, and thin until scale."])
st += [Paragraph("Self-funding structure", h3)]
st += bullets(["Ask for a <b>20–30% client advance</b> on new or unproven accounts.",
               "Prefer <b>dealers and suppliers</b> (fast payers) over main contractors.",
               "<b>Owner advance equals what the client has already advanced, or at most 70%.</b> Settle diesel through fuel cards or pump settlements, not cash to the driver.",
               "Pay the <b>balance only against the original POD</b> and weighbridge slip.",
               "Set <b>lane and customer credit limits</b>. Cap any single client's exposure at about 2 weeks of billing.",
               "Use <b>invoice discounting</b>, and <b>Udyam registration</b> to invoke the 45-day rule (s.43B(h)) against corporate buyers.",
               "Keep a <b>rolling reserve</b> from margin (for example 20% of monthly margin) to absorb a default."])
st += [Paragraph("4. Regulatory, Legal &amp; GST Compliance", h2), Paragraph("Registrations", h3)]
st += bullets(["GST (take it from day one, as brokers are intermediaries), PAN, Udyam, Shop &amp; Establishment, a current account and a trade licence.",
               "No specific licence is mandated for brokerage. If you also operate as a common carrier, check registration obligations under the Carriage by Road Act 2007. Carrier liability there is limited if value is not declared, and your contract terms should reflect this.",
               "Vehicles must be compliant: registration, fitness, insurance, PUC, valid driving licence, and permit or authorisation where applicable. Overloading brings heavy penalties.",
               "Goods-in-transit insurance is advisable for higher-value cargo."])
st += [Paragraph("GST and RCM (verify against current notifications)", h3)]
st += table([["Situation", "Rule"],
             ["GTA (issues consignment note) to a registered recipient", "RCM at 5%; the recipient pays"],
             ["GTA forward-charge option", "5% without ITC, or 18% with ITC"],
             ["Broker or agent commission", "18% GST (forward charge)"],
             ["Transport of goods by road by a non-GTA", "Generally exempt"],
             ["Unregistered recipient (individual)", "Typically no GTA tax on that supply"]], [0.55, 0.45], bold_first_col=True)
st += bullets(["<b>Structuring point:</b> whether you issue the LR (acting as GTA, with full freight as your value) or act as an agent (commission only) changes your tax base, invoice and liability. Settle this with a GST professional before the first trade.",
               "<b>E-way bill:</b> needed above Rs. 50,000 consignment value. Validity is 1 day per 200 km, and 1 day per 20 km for over-dimensional cargo. Part B must be updated for a vehicle change. Check state-specific thresholds for movements within AP.",
               "<b>TDS (s.194C):</b> the client deducts 1% (individual or HUF) or 2% (others) on your bill. Payments to owners with a PAN and a declaration of ten or fewer vehicles are exempt, so collect declarations.",
               "<b>GTA annual option:</b> the declaration is due each financial year, before the March deadline."])
st += [Paragraph("5. Risk-Benefit Matrix &amp; Mitigation", h2)]
st += table([["Risk", "Impact", "Mitigation"],
             ["Client credit default (contractors)", "High", "Dealer-first client mix, advances, per-client credit caps"],
             ["Owner non-delivery or cargo fraud", "High", "KYC, GPS, rating system, no full advance to unknown operators"],
             ["Thin margin and rate volatility", "Medium–High", "Fixed monthly lane rates, cost-plus quote formula, diesel escalation clauses"],
             ["Undercutting by yard-level agents", "High", "Service SLAs, digital POD, reliability, consolidated billing"],
             ["Dependence on the monsoon cycle", "Medium", "Agri and general backhaul loads, counter-seasonal contracts"],
             ["Local association or union friction", "Medium", "Work within the lorry-yard turn system and maintain relationships"]], [0.30, 0.18, 0.52], bold_first_col=True)
st += callout("Hidden vulnerability", "The broker can be disintermediated. Clients and owners eventually meet directly and cut you out, so the moat is <b>payment reliability, a vetted supply base and documentation</b>, not information.")

# ================= COMPARISON =================
st += [PageBreak()] + banner("COMPARISON", "Comparative Evaluation & Recommendation", "Scale 1–5, where 5 is most favourable to a new entrant")
st += [P("For Operational Complexity, 5 means simplest. For Barrier to Entry, 5 means the lowest barrier.")]
scores = [("Capital Efficiency", 2, 3, 5), ("Operational Complexity", 1, 3, 4), ("Margin Potential", 4, 3, 2),
          ("Scalability Speed", 2, 3, 5), ("Barrier to Entry", 1, 4, 5)]
def best(vals, i): return vals[i] == max(vals)
rows = [[Paragraph(x, cellh) for x in ["Dimension", "1. Pharma Logistics", "2. Printing / Paper", "3. General / Bulk Brokerage"]]]
for n, a, b, c in scores:
    v = (a, b, c)
    rows.append([Paragraph(n, cellb)] + [Paragraph(str(x), cellcb if best(v, i) else cellc) for i, x in enumerate(v)])
tot = [sum(s[i] for s in scores) for i in (1, 2, 3)]
rows.append([Paragraph("Total (of 25)", cellb)] + [Paragraph(str(t), cellcb) for t in tot])
t = Table(rows, colWidths=[0.34 * CW, 0.20 * CW, 0.20 * CW, 0.26 * CW])
ts = [("BACKGROUND", (0, 0), (-1, 0), NAVY), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("BOX", (0, 0), (-1, -1), 0.6, GRID),
      ("LINEBELOW", (0, 0), (-1, -1), 0.4, GRID), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
      ("BACKGROUND", (0, -1), (-1, -1), LIGHT), ("BACKGROUND", (3, 1), (3, -1), colors.HexColor("#E3F3F3"))]
t.setStyle(TableStyle(ts)); st += [t, Spacer(1, 12)]

d = Drawing(CW, 80); mx = 25
for i, (lab, val, col) in enumerate([("Pharma Logistics", tot[0], GREY), ("Printing / Paper", tot[1], NAVY), ("General / Bulk Brokerage", tot[2], TEAL)]):
    y = 52 - i * 26
    d.add(String(0, y + 5, lab, fontName="Body", fontSize=9, fillColor=INK))
    d.add(Rect(130, y, (CW - 170) * val / mx, 16, fillColor=col, strokeColor=None))
    d.add(String(130 + (CW - 170) * val / mx + 5, y + 4, f"{val}/25", fontName="Body-B", fontSize=9, fillColor=INK))
st += [d, Spacer(1, 6)]
st += bullets(["Pharma has the best margins and the stickiest contracts, but needs the most capital, compliance and operating discipline.",
               "Paper offers a balanced middle: better margins than bulk, with moderate complexity and a seasonal peak.",
               "Bulk brokerage is the easiest and fastest to launch, though it has thin margins and the weakest moat."])

st += sec("Final Recommendation")
st += callout("Enter through Strategy 3: General Lorry Transport and Bulk Material Cargo, as an asset-light brokerage.",
              "It offers the fastest cash conversion, the lowest capital and licensing burden, and builds the vehicle network, dispatch process and documentation discipline that the other two models depend on.",
              bg=colors.HexColor("#E3F3F3"), bar=TEAL)
st += [Paragraph("Why this is the optimal first step", h3)]
st += numbered(["<b>Fastest cash conversion.</b> Construction materials in the Amaravati corridor move daily, demand is deep, and trips can start within weeks of registration.",
                "<b>Lowest capital and licensing burden.</b> No fleet, no drug licence and no specialised assets are required, so the business can be self-funded through client advances and disciplined payouts.",
                "<b>It builds the base the other two need.</b> A vetted owner network, dispatch process, documentation discipline and client book transfer directly to paper and pharma logistics.",
                "<b>Best scalability</b> of the three."])
st += [Paragraph("Conditions that make it work", h3)]
st += bullets(["Target dealers and suppliers first, not main contractors.",
               "Take client advances on new accounts, and cap per-client exposure.",
               "Settle the GTA versus agent GST structure before the first invoice.",
               "Treat the margin as volume-driven: plan for roughly 150–250 trips a month before the business is comfortably profitable.",
               "Retain a rolling reserve against defaults."])
st += [Paragraph("Expansion sequence", h3)]
st += table([["Phase", "Focus", "Objective"],
             ["Months 0–9", "Bulk and general brokerage", "Establish cash flow, a reliable vehicle network and credit discipline"],
             ["Months 9–18", "Printing and paper logistics", "Reuse the fleet and billing process on Hyderabad, Chennai and Vijayawada lanes; contract ahead of the March–June textbook peak"],
             ["Month 18 onward", "Pharma logistics, carrier-only first", "Add a small temperature-controlled capability with calibrated loggers and a documented SOP; pursue distribution and a wholesale licence only after compliance and capital are proven"]],
            [0.17, 0.28, 0.55], bold_first_col=True)
st += callout("Caveat", "The recommendation rests on Amaravati construction continuing on schedule. If funding or tender flow slows, shift weight toward general freight and agri backhaul, "
              "since the Guntur and Vijayawada trade base does not depend on the capital project alone.", bg=LIGHT, bar=TEAL)

doc.build(st)
print("built", out)
