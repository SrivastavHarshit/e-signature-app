"""
Run this directly on your machine:
  python test_email.py

It will tell you EXACTLY why emails are failing.
"""
import smtplib
import socket

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "srivastava63290@gmail.com"
SMTP_PASS = "hlglbpxyuqsdlqul"
TO_EMAIL  = "Harshit@itmcsystems.com"

print("=" * 50)
print("KAYAS EMAIL DIAGNOSTIC")
print("=" * 50)

# Step 1: DNS
print("\n[1] Checking DNS...")
try:
    ip = socket.gethostbyname(SMTP_HOST)
    print(f"    ✓ smtp.gmail.com resolved to {ip}")
except Exception as e:
    print(f"    ✗ DNS FAILED: {e}")
    print("    → Your internet/firewall is blocking DNS. Check your network.")
    exit(1)

# Step 2: TCP
print("\n[2] Checking TCP port 587...")
try:
    s = socket.create_connection((SMTP_HOST, SMTP_PORT), timeout=5)
    s.close()
    print("    ✓ Port 587 is reachable")
except Exception as e:
    print(f"    ✗ TCP FAILED: {e}")
    print("    → Port 587 is blocked. Try port 465 or check firewall/antivirus.")
    exit(1)

# Step 3: SMTP login
print("\n[3] Logging into Gmail SMTP...")
try:
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
    server.set_debuglevel(0)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(SMTP_USER, SMTP_PASS)
    print("    ✓ Login successful!")
except smtplib.SMTPAuthenticationError as e:
    print(f"    ✗ AUTH FAILED: {e}")
    print("\n    HOW TO FIX:")
    print("    1. Go to https://myaccount.google.com/apppasswords")
    print("    2. Delete the old App Password")
    print("    3. Create a NEW one (select 'Mail' + 'Other')")
    print("    4. Copy the 16-char code (no spaces) into SMTP_PASS")
    exit(1)
except Exception as e:
    print(f"    ✗ SMTP ERROR: {type(e).__name__}: {e}")
    exit(1)

# Step 4: Send test email
print(f"\n[4] Sending test email to {TO_EMAIL}...")
try:
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Kayas Email Test - If you see this, it works!"
    msg["From"]    = f"Kayas E-Sign <{SMTP_USER}>"
    msg["To"]      = TO_EMAIL

    html = f"""
    <html><body style="font-family:Arial;padding:20px">
      <h2 style="color:#c89b3c">✅ Kayas Email Test Passed!</h2>
      <p>Your email configuration is working correctly.</p>
      <p>Sent from: <strong>{SMTP_USER}</strong></p>
    </body></html>
    """
    msg.attach(MIMEText(html, "html"))

    server.sendmail(SMTP_USER, TO_EMAIL, msg.as_string())
    server.quit()
    print(f"    ✓ Email sent to {TO_EMAIL}!")
    print("\n✅ ALL CHECKS PASSED — check your inbox (and spam folder)")
except Exception as e:
    print(f"    ✗ SEND FAILED: {type(e).__name__}: {e}")
    exit(1)