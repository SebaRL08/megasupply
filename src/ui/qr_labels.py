"""Etiquetas QR imprimibles: el QR contiene solo el código; debajo se imprimen código y nombre."""
import os
import re

import qrcode
from PIL import Image, ImageDraw, ImageFont

QR_DIR = "qr_generados"


def next_code(codes, prefix: str = "PROD-", width: int = 3) -> str:
    """Devuelve el siguiente código libre: si existen PROD-001..PROD-003, devuelve PROD-004."""
    nums = [int(m.group(1)) for c in codes if (m := re.fullmatch(rf"{re.escape(prefix)}(\d+)", c))]
    return f"{prefix}{(max(nums) + 1 if nums else 1):0{width}d}"


def _font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # versiones antiguas de Pillow
        return ImageFont.load_default()


def _center(draw, text: str, font, width: int, y: int) -> None:
    box = draw.textbbox((0, 0), text, font=font)
    draw.text(((width - (box[2] - box[0])) / 2, y), text, fill="black", font=font)


def make_label(code: str, name: str = "") -> Image.Image:
    qr = qrcode.make(code).get_image().convert("RGB")
    w, h = qr.size
    canvas = Image.new("RGB", (w, h + 90), "white")
    canvas.paste(qr, (0, 0))
    draw = ImageDraw.Draw(canvas)
    _center(draw, code, _font(30), w, h + 4)
    if name:
        _center(draw, name[:30], _font(22), w, h + 48)
    return canvas


def save_label(code: str, name: str = "") -> str:
    """Guarda la etiqueta en qr_generados/ y devuelve la ruta completa."""
    os.makedirs(QR_DIR, exist_ok=True)
    path = os.path.join(QR_DIR, re.sub(r"[^\w\-]", "_", code) + ".png")
    make_label(code, name).save(path)
    return os.path.abspath(path)
