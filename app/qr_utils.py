"""
QR Code Generation Utilities
用于生成活动快速加入的二维码
"""

import qrcode
from io import BytesIO
import base64
from flask import url_for, request


def generate_qr_code(data, size=10, border=2):
    """
    生成二维码图片
    
    Args:
        data: 要编码的数据（通常是 URL）
        size: 二维码大小（box_size）
        border: 边框大小
    
    Returns:
        base64 编码的图片字符串，可直接用于 HTML img src
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
    
    # 转换为 base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"


def generate_activity_qr_code(activity, _external=True):
    """
    为活动生成二维码
    
    Args:
        activity: Activity 模型实例
        _external: 是否生成完整的外部 URL
    
    Returns:
        base64 编码的二维码图片
    """
    if not activity.join_token:
        activity.generate_join_token()
    
    # 生成加入链接
    join_url = url_for(
        'activities.quick_join',
        token=activity.join_token,
        _external=_external
    )
    
    return generate_qr_code(join_url)


def get_activity_join_url(activity, _external=True):
    """
    获取活动的快速加入 URL
    
    Args:
        activity: Activity 模型实例
        _external: 是否生成完整的外部 URL
    
    Returns:
        加入 URL 字符串
    """
    if not activity.join_token:
        return None
    
    return url_for(
        'activities.quick_join',
        token=activity.join_token,
        _external=_external
    )
