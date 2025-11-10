"""
诊断邮件发送问题
Diagnose Email Sending Issues
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app import create_app, mail
from flask_mail import Message

def diagnose_email_config():
    """诊断邮件配置"""
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("📧 邮件配置诊断工具")
        print("=" * 70)
        
        # 1. 检查邮件配置
        print("\n1️⃣  检查邮件配置:")
        print(f"   MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
        print(f"   MAIL_PORT: {app.config.get('MAIL_PORT')}")
        print(f"   MAIL_USE_SSL: {app.config.get('MAIL_USE_SSL')}")
        print(f"   MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
        print(f"   MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
        print(f"   MAIL_PASSWORD: {'*' * len(str(app.config.get('MAIL_PASSWORD', '')))}")
        print(f"   MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")
        
        # 2. 测试SMTP连接
        print("\n2️⃣  测试SMTP连接:")
        try:
            import socket
            import ssl
            
            server = app.config.get('MAIL_SERVER')
            port = app.config.get('MAIL_PORT')
            
            print(f"   尝试连接 {server}:{port} ...")
            
            # 测试基本连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((server, port))
            
            if result == 0:
                print(f"   ✅ 连接成功!")
                sock.close()
                
                # 测试SSL连接
                if app.config.get('MAIL_USE_SSL'):
                    print(f"   测试SSL连接...")
                    context = ssl.create_default_context()
                    with socket.create_connection((server, port), timeout=5) as sock:
                        with context.wrap_socket(sock, server_hostname=server) as ssock:
                            print(f"   ✅ SSL连接成功!")
            else:
                print(f"   ❌ 连接失败! 错误代码: {result}")
                print(f"   可能原因:")
                print(f"      - 网络不通")
                print(f"      - 端口被防火墙阻止")
                print(f"      - MAIL_SERVER 地址错误")
                
        except socket.timeout:
            print(f"   ❌ 连接超时!")
            print(f"   可能原因:")
            print(f"      - 网络慢")
            print(f"      - 防火墙阻止")
        except Exception as e:
            print(f"   ❌ 连接错误: {str(e)}")
        
        # 3. 测试发送邮件
        print("\n3️⃣  测试发送邮件:")
        test_email = input("   输入测试邮箱地址: ").strip()
        
        if test_email:
            try:
                print(f"   正在发送测试邮件到 {test_email} ...")
                
                msg = Message(
                    subject="测试邮件 - Test Email",
                    recipients=[test_email],
                    body="这是一封测试邮件。如果你收到了这封邮件,说明邮件配置正确。\n\nThis is a test email. If you receive this, your email configuration is correct."
                )
                
                import time
                start_time = time.time()
                
                mail.send(msg)
                
                elapsed = time.time() - start_time
                print(f"   ✅ 邮件发送成功! 耗时: {elapsed:.2f}秒")
                print(f"   💡 请检查 {test_email} 的收件箱(包括垃圾邮件)")
                
            except Exception as e:
                print(f"   ❌ 邮件发送失败!")
                print(f"   错误信息: {str(e)}")
                print(f"\n   可能的原因:")
                print(f"   1. MAIL_USERNAME 或 MAIL_PASSWORD 错误")
                print(f"   2. QQ邮箱需要使用授权码,不是登录密码")
                print(f"   3. 邮箱未开启SMTP服务")
                print(f"   4. 邮件服务器拒绝连接")
                
                # 详细错误信息
                import traceback
                print(f"\n   详细错误:")
                traceback.print_exc()
        else:
            print("   跳过邮件发送测试")
        
        # 4. 检查环境变量
        print("\n4️⃣  检查环境变量:")
        env_vars = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USERNAME', 'MAIL_PASSWORD']
        for var in env_vars:
            value = os.getenv(var)
            if value:
                if 'PASSWORD' in var:
                    print(f"   ✅ {var}: {'*' * len(value)}")
                else:
                    print(f"   ✅ {var}: {value}")
            else:
                print(f"   ⚠️  {var}: 未设置(使用默认值)")
        
        # 5. 建议
        print("\n5️⃣  建议:")
        print("   ✅ 如果邮件发送慢或卡住:")
        print("      - 检查网络连接")
        print("      - 尝试切换邮件服务商(QQ → 163)")
        print("      - 使用异步发送邮件")
        
        print("\n   ✅ 如果邮件发送失败:")
        print("      - 确认QQ邮箱使用授权码,不是登录密码")
        print("      - 检查SMTP服务是否开启")
        print("      - 尝试使用其他邮箱(163, Gmail)")
        
        print("\n   ✅ 获取QQ邮箱授权码:")
        print("      1. 登录QQ邮箱网页版")
        print("      2. 设置 → 账户 → POP3/SMTP服务")
        print("      3. 开启服务并生成授权码")
        
        print("\n" + "=" * 70)

if __name__ == '__main__':
    diagnose_email_config()
