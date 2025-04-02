from flask import Blueprint, render_template, request, send_file
from flask_login import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os

from ..extensions import db
from ..models import Cargo

booking_bp = Blueprint('booking', __name__, url_prefix='/booking')

pdfmetrics.registerFont(
    TTFont("TimesNR", os.path.join("static", "fonts", "ofont.ru_Times New Roman.ttf"))
)

def inkscape_to_canvas(x_px, y_px):
    scale_x = 595 / 2480
    scale_y = 842 / 3505
    return x_px * scale_x, 842 - (y_px * scale_y)

def draw_multiline_text(c, x, y_start, lines, line_height=11):
    for i, line in enumerate(lines):
        txt = (line or '').strip()
        if txt:
            c.drawString(x, y_start - i * line_height, txt)

@booking_bp.route('/', methods=['GET'])
@login_required
def index():
    airport = request.args.get('airport', '', type=str)
    awb = request.args.get('awb', '', type=str)
    route = request.args.get('route', '', type=str)
    date_ = request.args.get('date_issued', '', type=str)
    cargo_type = request.args.get('cargo_type', '', type=str)
    recipient = request.args.get('recipient', '', type=str)
    search = request.args.get('search', '', type=str)

    query = Cargo.query

    if airport:
        query = query.filter(Cargo.airport_departure.ilike(f"%{airport}%"))
    if awb:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Cargo.airline_code.ilike(f"%{awb}%"),
                Cargo.awb_number.ilike(f"%{awb}%")
            )
        )
    if route:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Cargo.route1_to.ilike(f"%{route}%"),
                Cargo.route2_to.ilike(f"%{route}%"),
                Cargo.route3_to.ilike(f"%{route}%")
            )
        )
    if date_:
        query = query.filter(Cargo.date_issued.ilike(f"%{date_}%"))
    if cargo_type:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Cargo.cargo_description_line1.ilike(f"%{cargo_type}%"),
                Cargo.cargo_description_line2.ilike(f"%{cargo_type}%"),
                Cargo.cargo_description_line3.ilike(f"%{cargo_type}%")
            )
        )
    if recipient:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Cargo.recipient_line1.ilike(f"%{recipient}%"),
                Cargo.recipient_line2.ilike(f"%{recipient}%")
            )
        )
    if search:
        from sqlalchemy import or_
        query = query.filter(
            or_(
                Cargo.airport_departure.ilike(f"%{search}%"),
                Cargo.airline_code.ilike(f"%{search}%"),
                Cargo.awb_number.ilike(f"%{search}%"),
                Cargo.route1_to.ilike(f"%{search}%"),
                Cargo.route2_to.ilike(f"%{search}%"),
                Cargo.route3_to.ilike(f"%{search}%"),
                Cargo.date_issued.ilike(f"%{search}%"),
                Cargo.cargo_description_line1.ilike(f"%{search}%"),
                Cargo.cargo_description_line2.ilike(f"%{search}%"),
                Cargo.cargo_description_line3.ilike(f"%{search}%"),
                Cargo.recipient_line1.ilike(f"%{search}%"),
                Cargo.recipient_line2.ilike(f"%{search}%"),
            )
        )

    cargo_list = query.all()

    return render_template(
        'booking/index.html',
        cargo_list=cargo_list,
        filter_vals={
            'airport': airport,
            'awb': awb,
            'route': route,
            'date_issued': date_,
            'cargo_type': cargo_type,
            'recipient': recipient,
            'search': search
        }
    )

@booking_bp.route('/<int:cargo_id>/pdf')
@login_required
def generate_pdf(cargo_id):
    import datetime
    cargo = Cargo.query.get_or_404(cargo_id)

    def safe_str(value):
        if value is None or str(value).strip().lower() == "none":
            return ""
        if isinstance(value, datetime.date):
            return value.strftime("%d.%m.%Y")
        return str(value)

    data = {field: safe_str(getattr(cargo, field)) for field in [
        "airline_code", "awb_number",
        "shipper_line1", "shipper_line2", "shipper_line3", "shipper_line4",
        "recipient_line1", "recipient_line2", "recipient_line3", "recipient_line4",
        "cargo_description_line1", "cargo_description_line2", "cargo_description_line3",
        "places_count", "weight_brutto", "volume",
        "route1_to", "route1_by", "route2_to", "route2_by", "route3_to", "route3_by",
        "agent_line1", "agent_line2", "agent_line3",
        "agent_code", "airport_departure", "airport_arrival",
        "booking", "date_issued", "place_issued", "signature",
        "payment_line1", "payment_line2", "payment_line3",
        "special_customs_info"
    ]}

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("TimesNR", 9)

    bg_path = os.path.join("static", "background.png")
    c.drawImage(ImageReader(bg_path), 0, 0, width=595, height=842)

    c.setFont("TimesNR", 11)
    if data["airline_code"]:
        c.drawString(*inkscape_to_canvas(150, 150), data["airline_code"])
        c.drawString(*inkscape_to_canvas(1750, 150), data["airline_code"])
        c.drawString(*inkscape_to_canvas(1750, 3200), data["airline_code"])
    if data["awb_number"]:
        c.drawString(*inkscape_to_canvas(400, 150), data["awb_number"])
        c.drawString(*inkscape_to_canvas(1870, 150), data["awb_number"])
        c.drawString(*inkscape_to_canvas(1870, 3200), data["awb_number"])
    c.setFont("TimesNR", 9)

    shipper_lines = [line for line in [data[f"shipper_line{i}"] for i in range(1, 5)] if line]
    recipient_lines = [line for line in [data[f"recipient_line{i}"] for i in range(1, 5)] if line]
    cargo_lines = [line for line in [data[f"cargo_description_line{i}"] for i in range(1, 4)] if line]
    payment_lines = [line for line in [data[f"payment_line{i}"] for i in range(1, 4)] if line]
    agent_lines = [line for line in [data["agent_line1"], data["agent_line2"], data["agent_line3"]] if line]


    draw_multiline_text(c, *inkscape_to_canvas(155, 340), shipper_lines, line_height=9)
    draw_multiline_text(c, *inkscape_to_canvas(155, 620), recipient_lines, line_height=9)

    c.setFont("TimesNR", 8)
    draw_multiline_text(c, *inkscape_to_canvas(1660, 1700), cargo_lines, line_height=9)
    c.setFont("TimesNR", 9)
    draw_multiline_text(c, *inkscape_to_canvas(160, 880), agent_lines, line_height=8)

    if data["places_count"]:
        c.drawString(*inkscape_to_canvas(156, 1692), f"{data['places_count']} шт.")
        c.drawString(*inkscape_to_canvas(156, 2295), f"{data['places_count']} шт.")
    if data["weight_brutto"]:
        c.drawString(*inkscape_to_canvas(285, 1692), f"{data['weight_brutto']} кг")
        c.drawString(*inkscape_to_canvas(285, 2295), f"{data['weight_brutto']} кг")
    if data["volume"]:
        c.drawString(*inkscape_to_canvas(1850, 2300), f"{data['volume']} м³")

    routes = [
        ("route1_to", "route1_by", 150),
        ("route2_to", "route2_by", 810),
        ("route3_to", "route3_by", 1010)
    ]

    for to_field, by_field, x_base in routes:
        to_val = data.get(to_field)
        by_val = data.get(by_field)
        y = 1260
        if to_val:
            c.drawString(*inkscape_to_canvas(x_base, y), to_val)
        if by_val:
            c.drawString(*inkscape_to_canvas(x_base + 120, y), by_val)

    if data["agent_code"]:
        c.drawString(*inkscape_to_canvas(180, 1060), data["agent_code"])
    if data["airport_departure"]:
        c.drawString(*inkscape_to_canvas(155, 1160), data["airport_departure"])
    if data["airport_arrival"]:
        c.drawString(*inkscape_to_canvas(155, 1345), data["airport_arrival"])
    if data["booking"]:
        c.drawString(*inkscape_to_canvas(690, 1345), data["booking"])
    if data["date_issued"]:
        c.drawString(*inkscape_to_canvas(1000, 3020), data["date_issued"])
    if data["place_issued"]:
        c.drawString(*inkscape_to_canvas(1510, 3020), data["place_issued"])
    if data["signature"]:
        c.drawString(*inkscape_to_canvas(1850, 3020), data["signature"])

    if data["special_customs_info"]:
        draw_multiline_text(c, *inkscape_to_canvas(170, 1420), [data["special_customs_info"]])
    draw_multiline_text(c, *inkscape_to_canvas(1210, 860), payment_lines)

    c.save()
    buffer.seek(0)

    filename = f"airwaybill_{cargo.id}.pdf"
    return send_file(buffer, mimetype="application/pdf", as_attachment=False,
                     download_name=filename)
