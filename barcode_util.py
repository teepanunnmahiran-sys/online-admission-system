"""
Utility for generating QR Codes and Vector SVG Barcodes (Code 128)
"""
import io
import base64
import qrcode

def generate_qr_code_base64(text: str) -> str:
    """Generate high-contrast QR code as base64 PNG data URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=5,
        border=1,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{b64}"

def generate_code128_svg(code_str: str, height: int = 50, bar_width: int = 2) -> str:
    """
    Generate clean, vector SVG Code 128 barcode directly.
    Guarantees crisp printing without blur on any printer or PDF export.
    """
    # Code 128 patterns (Subset B)
    # 0 = space, 1 = bar
    # Standard 11-module patterns for code 128
    PATTERNS = [
        "11011001100", "11001101100", "11001100110", "10010011000", "10010001100",
        "10001001100", "10011001000", "10011000100", "10001100100", "11001001000",
        "11001000100", "11000100100", "10110011100", "10011011100", "10011001110",
        "10111001100", "10011101100", "10011100110", "11001110010", "11001011100",
        "11001001110", "11011100100", "11001110100", "11101101110", "11101001100",
        "11100101100", "11100100110", "11101100100", "11100110100", "11100110010",
        "11011011000", "11011000110", "11000110110", "10100011000", "10001011000",
        "10001000110", "10110001000", "10001101000", "10001100010", "11010001000",
        "11000101000", "11000100010", "10110111000", "10110001110", "10001101110",
        "10111011000", "10111000110", "10001110110", "11101110110", "11010001110",
        "11000101110", "11011101000", "11011100010", "11011101110", "11101011000",
        "11101000110", "11100010110", "11101101000", "11101100010", "11100011010",
        "11101111010", "11001000010", "11110001010", "10100110000", "10100001100",
        "10010110000", "10010000110", "10000101100", "10000100110", "10110010000",
        "10110000100", "10011010000", "10011000010", "10000110100", "10000110010",
        "11000010010", "11001010000", "11110111010", "11000010100", "10001111010",
        "10100111100", "10010111100", "10010011110", "10111100100", "10011110100",
        "10011110010", "11110100100", "11110010100", "11110010010", "11011011110",
        "11011110110", "11110110110", "10101111000", "10100011110", "10001011110",
        "10111101000", "10111100010", "11110101000", "11110100010", "10111011110",
        "10111101110", "11101011110", "11110101110", "11010000100", "11010010000",
        "11010011100", "1100011101011"
    ]
    START_B = 104
    STOP = 106

    clean_str = "".join([c for c in code_str if 32 <= ord(c) <= 126])
    if not clean_str:
        clean_str = "00000000"

    indices = [START_B]
    checksum = START_B
    for idx, char in enumerate(clean_str, 1):
        val = ord(char) - 32
        indices.append(val)
        checksum += val * idx

    check_val = checksum % 103
    indices.append(check_val)
    indices.append(STOP)

    modules = ""
    for idx in indices:
        if idx < len(PATTERNS):
            modules += PATTERNS[idx]

    total_width = len(modules) * bar_width + 20
    rects = []
    x = 10
    for char in modules:
        if char == "1":
            rects.append(f'<rect x="{x}" y="5" width="{bar_width}" height="{height}" fill="#0F172A" />')
        x += bar_width

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_width} {height + 25}" width="{total_width}" height="{height + 25}">
        <rect width="100%" height="100%" fill="#FFFFFF" />
        {''.join(rects)}
        <text x="{total_width / 2}" y="{height + 18}" font-family="monospace" font-size="12" text-anchor="middle" fill="#334155">{clean_str}</text>
    </svg>"""
    return svg_content
