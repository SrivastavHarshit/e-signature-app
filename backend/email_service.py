import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SMTP_HOST  = "smtp.gmail.com"
SMTP_PORT  = 587
SMTP_USER  = "123@gmail.com"
SMTP_PASS  = "asdfghjklklwercefetdc"
FROM_NAME  = "Kayas E-Sign"
APP_URL    = "http://127.0.0.1:8000"


def send_signing_email(to_name: str, to_email: str, doc_name: str,
                       message: str, sender_name: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"]    = f"Action Required: Please sign '{doc_name}'"
        msg["From"]       = f"{FROM_NAME} <{SMTP_USER}>"
        msg["To"]         = f"{to_name} <{to_email}>"
        msg["Reply-To"]   = SMTP_USER
        msg["Date"]       = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain="gmail.com")

        plain_body = f"""Hello {to_name},

{sender_name} has sent you a document that requires your signature.

Document: {doc_name}
{f'Message: {message}' if message.strip() else ''}

Click the link below to review and sign:
{APP_URL}

---
This email was sent by Kayas E-Sign on behalf of {sender_name}.
If you were not expecting this, you can safely ignore this email.
"""

        html_body = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:0;background:#f7f5f0;font-family:'DM Sans',Arial,sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr><td align="center" style="padding:40px 20px">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.08)">

        <tr><td style="background:#0d0d12;padding:24px 32px">
          <h1 style="margin:0;font-size:26px;color:#fff;font-family:Georgia,serif;letter-spacing:-0.5px">
            Kaya<span style="color:#c89b3c">s</span>
          </h1>
          <p style="margin:6px 0 0;font-size:12px;color:rgba(255,255,255,.4);letter-spacing:.08em;text-transform:uppercase">
            E-Signature Platform
          </p>
        </td></tr>

        <tr><td style="padding:40px 32px">
          <h2 style="margin:0 0 12px;font-size:22px;color:#1a1a24">Hello {to_name},</h2>
          <p style="margin:0 0 20px;font-size:15px;color:#5a5a72;line-height:1.7">
            <strong style="color:#1a1a24">{sender_name}</strong> has sent you a document
            that requires your signature.
          </p>

          <div style="background:#f7f5f0;border-radius:10px;padding:20px 24px;margin:0 0 24px;">
            <p style="margin:0;font-size:16px;font-weight:600;color:#1a1a24">📄 {doc_name}</p>
            <p style="margin:4px 0 0;font-size:12px;color:#9898b0">Awaiting your signature</p>
          </div>

          {f'<div style="border-left:3px solid #c89b3c;padding:12px 16px;margin:0 0 24px;background:#fffbf0;border-radius:0 8px 8px 0"><p style="margin:0;font-size:14px;color:#5a5a72;font-style:italic">&ldquo;{message}&rdquo;</p></div>' if message.strip() else ''}

          <table cellpadding="0" cellspacing="0" style="margin:0 0 28px">
            <tr><td style="background:#c89b3c;border-radius:10px">
              <a href="{APP_URL}" style="display:inline-block;padding:14px 36px;
                 font-size:15px;font-weight:600;color:#fff;text-decoration:none;letter-spacing:.02em">
                Review &amp; Sign Document &rarr;
              </a>
            </td></tr>
          </table>

          <p style="margin:0;font-size:13px;color:#9898b0;line-height:1.6">
            If the button above doesn't work, copy and paste this link into your browser:<br/>
            <a href="{APP_URL}" style="color:#c89b3c">{APP_URL}</a>
          </p>
        </td></tr>

        <tr><td style="background:#f7f5f0;padding:20px 32px;border-top:1px solid #e0dbd0">
          <p style="margin:0;font-size:12px;color:#9898b0;line-height:1.6">
            This email was sent by <strong>Kayas E-Sign</strong> on behalf of {sender_name}.<br/>
            If you were not expecting this request, you can safely ignore this email.
          </p>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

        msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        print(f"[EMAIL SENT] ✓ To: {to_email}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"[EMAIL ERROR] Auth failed: {e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"[EMAIL ERROR] Recipient refused: {e}")
        return False
    except Exception as e:
        print(f"[EMAIL ERROR] {type(e).__name__}: {e}")
        return False
