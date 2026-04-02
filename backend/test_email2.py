"""
Run this directly on your machine:
  python test_email2.py

Tests sending to multiple email addresses and shows exact error for each.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "srivastava63290@gmail.com"
SMTP_PASS = "hlglbpxyuqsdlqul"

# ✅ ADD ALL EMAILS YOU WANT TO TEST HERE
TEST_EMAILS = [
    "Harshit@itmcsystems.com",      # your office mail - works
    "rahul@itmcsystems.com",          # add more here
    "admin@itmcsystems.com",
    "Priyanshu@itmcsystems.com"
]

print("=" * 55)
print("KAYAS MULTI-RECIPIENT EMAIL TEST")
print("=" * 55)

# Login once
try:
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(SMTP_USER, SMTP_PASS)
    print(f"✓ Logged in as {SMTP_USER}\n")
except Exception as e:
    print(f"✗ Login failed: {e}")
    exit(1)

# Send to each address individually
for to_email in TEST_EMAILS:
    print(f"Sending to: {to_email}")
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"]    = "Kayas E-Sign — Test Email"
        msg["From"]       = f"Kayas E-Sign <{SMTP_USER}>"
        msg["To"]         = to_email
        msg["Date"]       = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain="gmail.com")

        plain = f"This is a test email from Kayas E-Sign sent to {to_email}."
        html  = f"<html><body><p>This is a test email from <strong>Kayas E-Sign</strong> sent to <strong>{to_email}</strong>.</p></body></html>"
        msg.attach(MIMEText(plain, "plain"))
        msg.attach(MIMEText(html,  "html"))

        # ✅ Send individually — not bulk
        result = server.sendmail(SMTP_USER, to_email, msg.as_string())
        if result:
            print(f"  ✗ Partial failure: {result}")
        else:
            print(f"  ✓ Accepted by Gmail SMTP")

    except smtplib.SMTPRecipientsRefused as e:
        print(f"  ✗ RECIPIENT REFUSED: {e}")
        print(f"     → Gmail rejected this address. It may be invalid or blocked.")
    except smtplib.SMTPDataError as e:
        print(f"  ✗ DATA ERROR: {e}")
        print(f"     → Gmail refused the message content.")
    except Exception as e:
        print(f"  ✗ ERROR: {type(e).__name__}: {e}")

server.quit()
print("\nDone. Check inbox AND spam folder for each address.")
print("If Gmail says 'Accepted' but mail never arrives → it's a spam/delivery issue on recipient's end.")