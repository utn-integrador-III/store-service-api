import io
import os
import qrcode
import smtplib
from email.message import EmailMessage
from typing import Dict, Any, Optional, List

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas




def _env(name: str, default: Optional[str] = None) -> str:
    """Obtiene variables de entorno con default."""
    v = os.getenv(name)
    return v if v is not None else (default if default is not None else "")


SMTP_HOST = _env("SMTP_HOST") or _env("MAIL_SERVER") or "smtp.gmail.com"
SMTP_PORT = int(_env("SMTP_PORT") or _env("MAIL_PORT") or "587")
SMTP_USER = _env("SMTP_USER") or _env("MAIL_USERNAME") or ""
SMTP_PASSWORD = _env("SMTP_PASSWORD") or _env("MAIL_PASSWORD") or ""

FROM_EMAIL = _env("FROM_EMAIL") or _env("MAIL_DEFAULT_SENDER") or SMTP_USER or "no-reply@example.com"
FROM_NAME = _env("FROM_NAME") or _env("MAIL_FROM_NAME") or "ServiBook"

SMTP_USE_SSL = (_env("SMTP_USE_SSL") or "").lower() in ("1", "true", "yes") or (SMTP_PORT == 465)
SMTP_USE_TLS = (_env("SMTP_USE_TLS") or "").lower() in ("1", "true", "yes") or (SMTP_PORT == 587)


def _smtp_connect() -> smtplib.SMTP:
    """
    Crea y devuelve una sesión SMTP ya lista (con SSL/STARTTLS si aplica).
    Lanza excepción si faltan credenciales en un host que requiera autenticación.
    """
    if SMTP_USE_SSL:
        server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=20)
    else:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20)
        server.ehlo()
        if SMTP_USE_TLS:
            server.starttls()
            server.ehlo()

    must_login = bool(SMTP_USER and SMTP_PASSWORD) or ("gmail" in SMTP_HOST.lower())
    if must_login:
        if not SMTP_USER or not SMTP_PASSWORD:
            raise RuntimeError(
                "SMTP requiere autenticación pero faltan credenciales. "
                "Define SMTP_USER/SMTP_PASSWORD o MAIL_USERNAME/MAIL_PASSWORD."
            )
        server.login(SMTP_USER, SMTP_PASSWORD)

    return server


def _send_email(
    to: str,
    subject: str,
    body_text: str,
    attachments: Optional[List[dict]] = None
) -> bool:
    """
    Envía un correo simple con adjuntos opcionales.
    attachments: lista de dicts con:
      { "data": bytes, "maintype": "application", "subtype": "pdf", "filename": "archivo.pdf" }
    """
    try:
        msg = EmailMessage()
        real_from = FROM_EMAIL or SMTP_USER or "no-reply@example.com"
        msg["From"] = f"{FROM_NAME} <{real_from}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body_text)

        if attachments:
            for att in attachments:
                msg.add_attachment(
                    att["data"],
                    maintype=att.get("maintype", "application"),
                    subtype=att.get("subtype", "octet-stream"),
                    filename=att.get("filename", "attachment.bin"),
                )

        server = _smtp_connect()
        server.send_message(msg)
        server.quit()
        return True

    except Exception as e:
        print(f"[Email] Error enviando correo: {e}")
        print(
            f"[Email] DEBUG -> host={SMTP_HOST} port={SMTP_PORT} ssl={SMTP_USE_SSL} tls={SMTP_USE_TLS} "
            f"user_set={'YES' if SMTP_USER else 'NO'} from={FROM_EMAIL or '(empty)'}"
        )
        return False



def send_confirmation_email(*, user_email: str, details: Dict[str, Any], pdf_bytes: bytes) -> bool:
    """
    Envía correo de confirmación de cita con el PDF adjunto.
    details: { id, user_name, business_name, date, time, address, ... }
    """
    subject = f"Confirmación de cita - {details.get('business_name','')}"
    body = (
        f"Hola {details.get('user_name','')},\n\n"
        f"Tu cita ha sido confirmada.\n\n"
        f"Negocio: {details.get('business_name','')}\n"
        f"Fecha: {details.get('date','')}  Hora: {details.get('time','')}\n"
        f"Dirección: {details.get('address','')}\n"
        f"Cita ID: {details.get('id','')}\n\n"
        "Adjuntamos tu comprobante en PDF.\n\n"
        "Gracias por utilizar ServiBook."
    )
    return _send_email(
        to=user_email,
        subject=subject,
        body_text=body,
        attachments=[{
            "data": pdf_bytes,
            "maintype": "application",
            "subtype": "pdf",
            "filename": "Comprobante_Cita.pdf",
        }],
    )


def send_cancellation_email(*, user_email: str, details: Dict[str, Any], pdf_bytes: Optional[bytes] = None) -> bool:
    """
    Envía correo de cancelación de cita con PDF adjunto (opcional).
    details: { id, user_name, business_name, date, time, address, ... }
    """
    subject = f"Cita cancelada - {details.get('business_name','')}"
    body = (
        f"Hola {details.get('user_name','')},\n\n"
        f"Tu cita ha sido CANCELADA.\n\n"
        f"Negocio: {details.get('business_name','')}\n"
        f"Fecha: {details.get('date','')}  Hora: {details.get('time','')}\n"
        f"Dirección: {details.get('address','')}\n"
        f"Cita ID: {details.get('id','')}\n\n"
        "Adjuntamos el comprobante en PDF con el estado de cancelación.\n\n"
        "Equipo ServiBook."
    )
    attachments = []
    if pdf_bytes:
        attachments.append({
            "data": pdf_bytes,
            "maintype": "application",
            "subtype": "pdf",
            "filename": "Cita_Cancelada.pdf",
        })
    return _send_email(to=user_email, subject=subject, body_text=body, attachments=attachments)




def generate_qr_code_as_bytes(content: str) -> io.BytesIO:
    """
    Genera un PNG en memoria con un QR (retorna BytesIO posicionado al principio).
    En tu endpoint puedes pasar el appointment_id o una URL de verificación.
    """
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf




PRIMARY = colors.HexColor("#1976d2")
LIGHT_BG = colors.whitesmoke
TEXT_MUTED = colors.HexColor("#555555")

def generate_appointment_pdf_as_bytes(details: Dict[str, Any], cancelled: bool = False) -> bytes:
    """
    Renderiza un comprobante en PDF y lo devuelve como bytes.

    details admite: id, user_name, business_name, date, time, address, status, qr_png (bytes PNG)
    Si cancelled=True o details['status']=="cancelled", se coloca marca de agua CANCELADA.
    """
    buffer = io.BytesIO()
    w, h = A4
    c = canvas.Canvas(buffer, pagesize=A4)

    header_h = 28 * mm
    c.setFillColor(PRIMARY)
    c.rect(0, h - header_h, w, header_h, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(20 * mm, h - 16 * mm, "Comprobante de Cita")
    c.setFont("Helvetica", 11)
    c.drawRightString(w - 20 * mm, h - 12 * mm, f"ID: {details.get('id','')}")

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, h - header_h - 10 * mm, details.get("business_name", ""))

    top_box_y = h - header_h - 18 * mm
    box_h = 60 * mm
    c.setFillColor(LIGHT_BG)
    c.roundRect(15 * mm, top_box_y - box_h, w - 30 * mm, box_h, 6 * mm, stroke=0, fill=1)

    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 10)

    labels = [
        ("Cliente", details.get("user_name", "")),
        ("Fecha", details.get("date", "")),
        ("Hora", details.get("time", "")),
        ("Dirección", details.get("address", "")),
        ("Estado", "Cancelada" if cancelled or details.get("status") == "cancelled" else "Confirmada"),
    ]

    y = top_box_y - 12 * mm
    for label, value in labels:
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(colors.black)
        c.drawString(22 * mm, y, f"{label}:")
        c.setFont("Helvetica", 11)
        c.setFillColor(TEXT_MUTED)
        c.drawString(60 * mm, y, str(value))
        y -= 9 * mm

    qr_png = details.get("qr_png")
    if qr_png:
        try:
            img = ImageReader(io.BytesIO(qr_png))
            c.drawImage(img, w - 55 * mm, top_box_y - box_h + 10 * mm, 35 * mm, 35 * mm, preserveAspectRatio=True, mask='auto')
            c.setFont("Helvetica", 9)
            c.setFillColor(TEXT_MUTED)
            c.drawRightString(w - 20 * mm, top_box_y - box_h + 8 * mm, "Muestra este código en el negocio")
        except Exception:
            pass

    if cancelled or details.get("status") == "cancelled":
        c.saveState()
        c.setFillColor(colors.HexColor("#ff4d4d"))
        c.setFont("Helvetica-Bold", 70)
        c.translate(w / 2, h / 2)
        c.rotate(30)
        c.drawCentredString(0, 0, "CANCELADA")
        c.restoreState()

    c.setFont("Helvetica", 9)
    c.setFillColor(TEXT_MUTED)
    c.drawCentredString(w / 2, 10 * mm, "Gracias por reservar con ServiBook")

    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
