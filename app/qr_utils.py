"""
QR Code Generation Utilities
For generating QR codes for quick activity join
"""

import qrcode
from io import BytesIO
import base64
from flask import url_for, request


def generate_qr_code(data, size=10, border=2):
    """
    Generate QR code image
    
    Args:
        data: Data to encode (usually URL)
        size: QR code size (box_size)
        border: Border size
    
    Returns:
        base64 encoded image string, can be directly used in HTML img src
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def generate_activity_qr_code(activity, _external=True):
    """
    Generate QR code for activity
    
    Args:
        activity: Activity model instance
        _external: Whether to generate full external URL
    
    Returns:
        base64 encoded QR code image
    """
    if not activity.join_token:
        activity.generate_join_token()
    
    # Generate join URL
    join_url = url_for(
        'activities.quick_join',
        token=activity.join_token,
        _external=_external
    )
    
    return generate_qr_code(join_url)


def get_activity_join_url(activity, _external=True):
    """
    Get quick join URL for activity
    
    Args:
        activity: Activity model instance
        _external: Whether to generate full external URL
    
    Returns:
        Join URL string
    """
    if not activity.join_token:
        return None
    
    return url_for(
        'activities.quick_join',
        token=activity.join_token,
        _external=_external
    )
