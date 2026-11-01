import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, PageBreak, NextPageTemplate
from reportlab.graphics.shapes import Drawing, Rect, Circle, String, Polygon
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

out = sys.argv[1]
FD = "/System/Library/Fonts/Supplemental/"
for n, f in [("Body", "Arial.ttf"), ("Body-B", "Arial Bold.ttf"), ("Body-I", "Arial Italic.ttf"), ("Body-BI", "Arial Bold Italic.ttf")]:
    pdfmetrics.registerFont(TTFont(n, FD + f))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-B", italic="Body-I", boldItalic="Body-BI")

NAVY = colors.HexColor("#12304A"); TEAL = colors.HexColor("#0F8B8D"); AMBER = colors.HexColor("#E8A33D")
LIGHT = colors.HexColor("#EEF4F7"); GRID = colors.HexColor("#C9D6DE"); INK = colors.HexColor("#1F2933")
GREY = colors.HexColor("#6B7B88"); MINT = colors.HexColor("#E3F3F3"); SLATE = colors.HexColor("#8A99A6")
W, H = A4; LM = RM = 18 * mm; CW = W - LM - RM

def S(n, **k): return ParagraphStyle(n, fontName=k.pop("fontName", "Body"), textColor=k.pop("textColor", INK), **k)
body = S("body", fontSize=10, leading=14.5, spaceAfter=4)
h2 = S("h2", fontName="Body-B", fontSize=13, leading=17, textColor=NAVY, spaceBefore=10, spaceAfter=6)
cell = S("cell", fontSize=9.5, leading=13)
cellb = S("cellb", fontName="Body-B", fontSize=9.5, leading=13)
cellh = S("cellh", fontName="Body-B", fontSize=9.5, leading=13, textColor=colors.white)
P = Paragraph

def banner(tag, title, sub):
    t = Table([[[P(tag, S("t", fontName="Body-B", fontSize=9, textColor=AMBER, leading=12)),
                 P(title, S("tt", fontName="Body-B", fontSize=21, leading=26, textColor=colors.white)),
                 P(sub, S("ts", fontSize=10, leading=14, textColor=colors.HexColor("#CFE3EA")))]]], colWidths=[CW])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY), ("LEFTPADDING", (0, 0), (-1, -1), 16),
                           ("TOPPADDING", (0, 0), (-1, -1), 14), ("BOTTOMPADDING", (0, 0), (-1, -1), 14), ("LINEBELOW", (0, 0), (-1, -1), 3, TEAL)]))
    return [t, Spacer(1, 12)]

def verdict():
    inner = [P("OUR VISION", S("v1", fontName="Body-B", fontSize=9, textColor=AMBER, leading=12)),
             P("Start with General &amp; Bulk Freight Brokerage", S("v2", fontName="Body-B", fontSize=17, leading=22, textColor=colors.white)),
             Spacer(1, 3),
             P("It is the only one of the three that can earn cash in weeks, with no vehicles, no special licence and little capital. "
               "Then grow into paper logistics, and finally pharma logistics.", S("v3", fontSize=10.5, leading=15, textColor=colors.HexColor("#E6F2F5")))]
    t = Table([[inner]], colWidths=[CW])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TEAL), ("LEFTPADDING", (0, 0), (-1, -1), 16), ("RIGHTPADDING", (0, 0), (-1, -1), 16),
                           ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 13)]))
    return [t, Spacer(1, 12)]

def dots(n, col):
    d = Drawing(70, 12)
    for i in range(5):
        d.add(Circle(6 + i * 13, 6, 4.5, fillColor=col if i < n else colors.white, strokeColor=col if i < n else GRID, strokeWidth=0.8))
    return d

def scorecard():
    dims = [("Capital needed to start", 2, 3, 5), ("Ease of running day to day", 1, 3, 4), ("Profit per trip", 4, 3, 2),
            ("Speed of growth", 2, 3, 5), ("Ease of entry (licences)", 1, 4, 5)]
    rows = [[P("", cellh), P("Pharma", cellh), P("Paper &amp; Print", cellh), P("Bulk Brokerage", cellh)]]
    for n, a, b, c in dims:
        rows.append([P(n, cellb), dots(a, SLATE), dots(b, NAVY), dots(c, TEAL)])
    rows.append([P("Total score", cellb), P("<b>10 / 25</b>", cell), P("<b>16 / 25</b>", cell), P("<b>21 / 25</b>", S("w", fontName="Body-B", fontSize=9.5, leading=13, textColor=TEAL))])
    t = Table(rows, colWidths=[0.34 * CW, 0.2 * CW, 0.22 * CW, 0.24 * CW])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("BOX", (0, 0), (-1, -1), 0.6, GRID),
                           ("LINEBELOW", (0, 0), (-1, -1), 0.4, GRID), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("BACKGROUND", (3, 1), (3, -1), MINT), ("BACKGROUND", (0, -1), (2, -1), LIGHT)]))
    return [t, P("More filled circles = better for a new business (so 5 on “Ease” means easiest).", S("n", fontSize=8, leading=11, textColor=GREY)), Spacer(1, 4)]

def cards():
    def card(rank, name, col, lines, tag):
        inner = [P(rank, S("c1", fontName="Body-B", fontSize=8.5, textColor=col, leading=11)),
                 P(name, S("c2", fontName="Body-B", fontSize=11, leading=14, textColor=NAVY)), Spacer(1, 4)]
        inner += [P(l, S("c3", fontSize=9, leading=12.5, spaceAfter=3)) for l in lines]
        inner += [Spacer(1, 3), P(tag, S("c4", fontName="Body-B", fontSize=9, leading=12, textColor=col))]
        return inner
    cs = [card("ENTER THIRD", "Pharma Logistics", SLATE,
               ["<b>Money:</b> best margin (8–15%)", "<b>Set-up:</b> temperature-controlled vehicles, strict compliance", "<b>Start:</b> after 18 months"], "Great later, risky first"),
          card("ENTER SECOND", "Printing &amp; Paper", NAVY,
               ["<b>Money:</b> moderate margin (5–10%)", "<b>Set-up:</b> covered trucks, careful handling", "<b>Start:</b> months 9–18"], "Strong, but seasonal"),
          card("ENTER FIRST", "Bulk &amp; General Freight", TEAL,
               ["<b>Money:</b> thin margin (3–8%), high volume", "<b>Set-up:</b> phone, WhatsApp, lorry-owner list", "<b>Start:</b> now"], "Fastest cash flow")]
    t = Table([cs], colWidths=[CW / 3] * 3)
    t.setStyle(TableStyle([("BOX", (0, 0), (0, 0), 0.6, GRID), ("BOX", (1, 0), (1, 0), 0.6, GRID), ("BOX", (2, 0), (2, 0), 1.6, TEAL),
                           ("LINEABOVE", (0, 0), (0, 0), 3, SLATE), ("LINEABOVE", (1, 0), (1, 0), 3, NAVY), ("LINEABOVE", (2, 0), (2, 0), 3, TEAL),
                           ("BACKGROUND", (2, 0), (2, 0), MINT), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9)]))
    return [t, Spacer(1, 6)]

def roadmap():
    d = Drawing(CW, 44)
    steps = [("MONTHS 0–9", "Bulk &amp; general", "brokerage", TEAL, "Build cash flow, a lorry-owner network, credit discipline"),
             ("MONTHS 9–18", "Printing &amp; paper", "logistics", NAVY, "Reuse the network; lock in contracts before the Mar–Jun peak"),
             ("MONTH 18+", "Pharma logistics", "(carrier only)", SLATE, "Add temperature control and compliance, then consider distribution")]
    w = CW / 3
    for i, (when, a, b, col, note) in enumerate(steps):
        x = i * w
        pts = [x, 44, x + w - 12, 44, x + w, 22, x + w - 12, 0, x, 0] if i == 0 else [x, 44, x + w - 12, 44, x + w, 22, x + w - 12, 0, x, 0, x + 12, 22]
        if i == 2: pts = [x, 44, x + w, 44, x + w, 0, x, 0, x + 12, 22]
        d.add(Polygon(pts, fillColor=col, strokeColor=colors.white, strokeWidth=2))
        d.add(String(x + 18, 30, when, fontName="Body-B", fontSize=8, fillColor=colors.HexColor("#FFE2A8")))
        d.add(String(x + 18, 16, a.replace("&amp;", "&"), fontName="Body-B", fontSize=10, fillColor=colors.white))
        d.add(String(x + 18, 5, b, fontName="Body", fontSize=9, fillColor=colors.white))
    return [d]

def notes():
    w = CW / 3
    ts = [P(n, S("rn", fontSize=8.8, leading=12, textColor=GREY)) for n in
          ["Build cash flow, a lorry-owner network and credit discipline.", "Reuse the network; lock in contracts before the March–June peak.", "Add temperature control and compliance; consider distribution only later."]]
    t = Table([ts], colWidths=[w] * 3); t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 6)]))
    return [t, Spacer(1, 8)]

def rules():
    items = [("1", "Never fund diesel from your own pocket", "Take a 20–30% advance from the client and pass it to the owner."),
             ("2", "Pay the balance only against the original delivery proof", "Signed POD plus weighbridge slip, every time."),
             ("3", "Choose dealers and suppliers first", "They pay in 7–15 days. Large contractors can take 60–120+ days."),
             ("4", "Cap any one client at about 2 weeks of billing", "One default must never stop the business."),
             ("5", "Register for GST from day one", "Decide “GTA vs agent” billing with a GST professional before the first invoice.")]
    rows = [[P(f"<b>{n}</b>", S("rb", fontName="Body-B", fontSize=12, textColor=colors.white, alignment=TA_CENTER, leading=15)),
             [P(f"<b>{a}</b>", S("ra", fontSize=9.8, leading=13)), P(b, S("rb2", fontSize=9, leading=12.5, textColor=GREY))]] for n, a, b in items]
    t = Table(rows, colWidths=[9 * mm, CW - 9 * mm])
    st = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (1, 0), (1, -2), 0.4, GRID), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
          ("LEFTPADDING", (1, 0), (1, -1), 10)]
    for i in range(len(items)): st.append(("BACKGROUND", (0, i), (0, i), TEAL))
    t.setStyle(TableStyle(st)); return [t, Spacer(1, 6)]

def numbers():
    items = [("3–8%", "typical brokerage margin on freight"), ("150–250", "trips a month needed for a comfortable profit"),
             ("7–15 days", "payment from material dealers (best payers)"), ("Rs. 7 lakh", "working capital for ~40 trips/month at 30-day credit")]
    cells = [[P(a, S("k1", fontName="Body-B", fontSize=15, leading=19, textColor=TEAL)), P(b, S("k2", fontSize=8.5, leading=11.5, textColor=GREY))] for a, b in items]
    t = Table([cells], colWidths=[CW / 4] * 4)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9), ("LINEAFTER", (0, 0), (-2, -1), 0.6, colors.white)]))
    return [t, Spacer(1, 6)]

def risks():
    rows = [[P("Risk", cellh), P("What to do", cellh)],
            [P("Clients pay late or default", cellb), P("Advances, dealer-first client mix, per-client limit, small reserve from every month's margin", cell)],
            [P("Lorry owner fails to deliver", cellb), P("Verify documents, use GPS, keep a standby list, no full advance to unknown owners", cell)],
            [P("Clients and owners go direct", cellb), P("Win on reliability: on-time trucks, clean paperwork, fast payment to owners", cell)],
            [P("Monsoon slowdown (Jun–Sep)", cellb), P("Take agri and general loads (Guntur chilli, cotton, rice) to fill the gap", cell)]]
    t = Table(rows, colWidths=[0.32 * CW, 0.68 * CW])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BOX", (0, 0), (-1, -1), 0.6, GRID),
                           ("LINEBELOW", (0, 0), (-1, -1), 0.4, GRID), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("BACKGROUND", (0, 2), (-1, 2), LIGHT), ("BACKGROUND", (0, 4), (-1, 4), LIGHT)]))
    return [t, Spacer(1, 6)]

def page(c, d):
    c.saveState(); c.setStrokeColor(GRID); c.setLineWidth(0.5); c.line(LM, H - 13 * mm, W - RM, H - 13 * mm)
    c.setFont("Body", 8); c.setFillColor(GREY)
    c.drawString(LM, H - 10 * mm, "Amaravati Logistics: Which Business to Start")
    c.drawRightString(W - RM, 11 * mm, f"Page {d.page} of 2")
    c.drawString(LM, 11 * mm, "Figures are indicative estimates (mid-2026). Verify rates and GST rules before committing capital.")
    c.restoreState()

doc = BaseDocTemplate(out, pagesize=A4, leftMargin=LM, rightMargin=RM, topMargin=20 * mm, bottomMargin=18 * mm,
                      title="Amaravati Logistics: Which Business to Start", author="")
doc.addPageTemplates([PageTemplate("m", frames=[Frame(LM, 18 * mm, CW, H - 38 * mm, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)], onPage=page)])

st = banner("AMARAVATI CAPITAL REGION  |  VIJAYAWADA – GUNTUR – MANGALAGIRI",
            "Which Logistics Business Should We Start?", "Three options compared simply, with a clear starting point")
st += verdict()
st += [P("The three options at a glance", h2)] + cards()
st += [P("Scorecard", h2)] + scorecard()
st += [P("Why bulk and general freight brokerage comes first", h2)]
st += [P("• <b>Cash in weeks.</b> Construction in the capital region moves cement, sand, steel and aggregates every day. Loads are available now.", body),
       P("• <b>Almost no capital.</b> You match loads with independent lorry owners and earn a commission. No vehicle loans, no staff, no special licence.", body),
       P("• <b>It builds what the other two need.</b> The lorry-owner network, dispatch routine and billing discipline carry straight over to paper and pharma.", body)]
st += [P("The growth path", h2)] + roadmap() + notes()
st += [P("The numbers to remember", h2)] + numbers()
st += [P("Five rules that protect the business", h2)] + rules()
st += [P("Main risks and the answer to each", h2)] + risks()

doc.build(st); print("built", out)
