"""
Test email sending functionality
测试邮件发送功能
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from app import create_app
from app.email_utils import send_temp_password_email

def test_email():
    """Test sending a temporary password email"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🧪 Testing Email Sending Functionality")
        print("=" * 60)
        
        # Test email details
        test_email = input("\nEnter your test email address: ").strip()
        test_name = input("Enter test user name (default: Test User): ").strip() or "Test User"
        test_password = "Test1234"
        
        print(f"\n📧 Sending test email to: {test_email}")
        print(f"👤 User name: {test_name}")
        print(f"🔑 Test password: {test_password}")
        print("\nSending email...")
        
        try:
            success = send_temp_password_email(test_email, test_name, test_password)
            
            if success:
                print("\n✅ SUCCESS! Email sent successfully!")
                print(f"\n📬 Please check your inbox at {test_email}")
                print("💡 Tips:")
                print("   - Check your spam/junk folder if you don't see it")
                print("   - It may take a few minutes to arrive")
                print("   - Make sure you entered the correct email address")
            else:
                print("\n❌ FAILED! Email sending failed.")
                print("💡 Possible reasons:")
                print("   - Email server credentials are incorrect")
                print("   - Network connection issue")
                print("   - Email server is blocking connections")
                print("   - Check the error logs above for details")
                
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            print("\n💡 Troubleshooting:")
            print("   1. Check your .env file has correct MAIL_* settings")
            print("   2. Verify your email password/auth code")
            print("   3. Make sure less secure apps or SMTP is enabled")
            print("   4. For QQ mail, use authorization code not login password")
            print("   5. For Gmail, use App Password not account password")
        
        print("\n" + "=" * 60)

if __name__ == '__main__':
    test_email()
