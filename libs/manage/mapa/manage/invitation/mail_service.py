from email.mime.application import MIMEApplication
from typing import Any
from mapa.core.data.base_service import BaseService
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl
import re

register_tr = r"""<html>
   <head></head>
   <body>
     <div style="background-color:#eaebed;font-family:sans-serif;font-size:14px;line-height:1.4;margin:0;padding:0">
       <table role="presentation" border="0" cellpadding="0" cellspacing="0" style="border-collapse:separate;min-width:100%;background-color: #b9bec6;width:100%" width="100%" bgcolor="#eaebed">
         <tbody>
           <tr>
             <td style="font-family:sans-serif;font-size:14px;vertical-align:top;display:block;max-width:580px;padding:10px;width:580px;Margin:0 auto" width="580" valign="top">
               <div style="box-sizing:border-box;display:block;Margin:0 auto;max-width:580px;padding:10px">
                 <table role="presentation" style="border-collapse:separate;min-width:100%;background:#ffffff;border-radius:3px;width:100%" width="100%">
                   <tbody>
                     <tr>
                       <td style="font-family:sans-serif;font-size:14px;vertical-align:top;box-sizing:border-box;padding:20px" valign="top">
                         <table role="presentation" border="0" cellpadding="0" cellspacing="0" style="border-collapse:separate;min-width:100%;width:100%" width="100%">
                           <tbody>
                             <tr>
                               <td>
                                 <img width="48" style="display:block;margin:0 auto" align="center" align="center" data-emoji="👋" class="an1" alt="👋" aria-label="👋" src="https://fonts.gstatic.com/s/e/notoemoji/15.0/1f44b/72.png" loading="lazy">
                               </td>
                             </tr>
                             <tr>
                               <td height="10"></td>
                             </tr>
                             <tr>
                               <td class="m_6906578752728732323title" style="line-height:48px;text-align:center;color:#262626;font-size:42px;font-family:Inter,Roboto,Helvetica,Arial,sans-serif;font-weight:bold;letter-spacing:-0.022em" align="center">Mapa'ya Hoş Geldiniz!</td>
                             </tr>
                             <tr>
                               <td height="30"></td>
                             </tr>
                             <tr>
                               <td align="center" style="display:block;font-size:20px;color:#262626;font-family:Inter,Helvetica,Arial,sans-serif;letter-spacing:-0.017em;font-weight:bold;line-height:1.6">
                                 <strong style="max-width:390px;display:inline-block">Başladığınız için heyecanlıyız.</strong>
                               </td>
                             </tr>
                             <tr>
                               <td height="15"></td>
                             </tr>
                             <tr>
                               <td align="center" style="line-height:1.4;font-weight:normal;color:#262626;font-family:Inter,Helvetica,Arial,sans-serif;font-size:16px;letter-spacing:-0.011em;margin:0">Öncelikle hesabınızı kaydetmeniz gerekiyor, aşağıdaki adresi ziyaret edin:</td>
                             </tr>
                             <tr>
                               <td height="30"></td>
                             </tr>
                             <tr>
                               <td align="center">
                                 <a href="\2" style="margin:0 auto;color:#ffffff;background:#2f80ed;padding-top:13px;padding-bottom:13px;padding-left:20px;padding-right:20px;border-radius:6px;font-size:16px;text-decoration:none;font-family:Inter,Helvetica,Arial,sans-serif;font-weight:500;display:inline-block" bgcolor="#2F80ED" target="_blank">Hesabınızı kaydedin.</a>
                               </td>
                             </tr>
                           </tbody>
                         </table>
                       </td>
                     </tr>
                   </tbody>
                 </table>
               </div>
             </td>
           </tr>
         </tbody>
       </table>
     </div>
   </body>
 </html>"""
register_en = r"""
       <html>
   <head></head>
   <body>
     <div style="background-color:#eaebed;font-family:sans-serif;font-size:14px;line-height:1.4;margin:0;padding:0">
       <table role="presentation" border="0" cellpadding="0" cellspacing="0" style="border-collapse:separate;min-width:100%;background-color: #b9bec6;width:100%" width="100%" bgcolor="#eaebed">
         <tbody>
           <tr>
             <td style="font-family:sans-serif;font-size:14px;vertical-align:top;display:block;max-width:580px;padding:10px;width:580px;Margin:0 auto" width="580" valign="top">
               <div style="box-sizing:border-box;display:block;Margin:0 auto;max-width:580px;padding:10px">
                 <table role="presentation" style="border-collapse:separate;min-width:100%;background:#ffffff;border-radius:3px;width:100%" width="100%">
                   <tbody>
                     <tr>
                       <td style="font-family:sans-serif;font-size:14px;vertical-align:top;box-sizing:border-box;padding:20px" valign="top">
                         <table role="presentation" border="0" cellpadding="0" cellspacing="0" style="border-collapse:separate;min-width:100%;width:100%" width="100%">
                           <tbody>
                             <tr>
                               <td>
                                 <img width="48" style="display:block;margin:0 auto" align="center" align="center" data-emoji="👋" class="an1" alt="👋" aria-label="👋" src="https://fonts.gstatic.com/s/e/notoemoji/15.0/1f44b/72.png" loading="lazy">
                               </td>
                             </tr>
                             <tr>
                               <td height="10"></td>
                             </tr>
                             <tr>
                               <td class="m_6906578752728732323title" style="line-height:48px;text-align:center;color:#262626;font-size:42px;font-family:Inter,Roboto,Helvetica,Arial,sans-serif;font-weight:bold;letter-spacing:-0.022em" align="center">Welcome To Mapa!</td>
                             </tr>
                             <tr>
                               <td height="30"></td>
                             </tr>
                             <tr>
                               <td align="center" style="display:block;font-size:20px;color:#262626;font-family:Inter,Helvetica,Arial,sans-serif;letter-spacing:-0.017em;font-weight:bold;line-height:1.6">
                                 <strong style="max-width:390px;display:inline-block">We're excited to have you get started.</strong>
                               </td>
                             </tr>
                             <tr>
                               <td height="15"></td>
                             </tr>
                             <tr>
                               <td align="center" style="line-height:1.4;font-weight:normal;color:#262626;font-family:Inter,Helvetica,Arial,sans-serif;font-size:16px;letter-spacing:-0.011em;margin:0">First, you need to register your account, visit the following address:</td>
                             </tr>
                             <tr>
                               <td height="30"></td>
                             </tr>
                             <tr>
                               <td align="center">
                                 <a href="\2" style="margin:0 auto;color:#ffffff;background:#2f80ed;padding-top:13px;padding-bottom:13px;padding-left:20px;padding-right:20px;border-radius:6px;font-size:16px;text-decoration:none;font-family:Inter,Helvetica,Arial,sans-serif;font-weight:500;display:inline-block" bgcolor="#2F80ED" target="_blank">Register your account</a>
                               </td>
                             </tr>
                           </tbody>
                         </table>
                       </td>
                     </tr>
                   </tbody>
                 </table>
               </div>
             </td>
           </tr>
         </tbody>
       </table>
     </div>
   </body>
 </html>
    """


class MailService(BaseService):

    def __init__(
        self,
        smtp: Any,
        port: Any,
        user_name: Any,
        password: Any,
        method: Any,
        subject: Any,
        mail_header: Any,
        mail_header_en: Any
    ) -> None:
        self._smtp = smtp
        self._port = port
        self._user_name = user_name
        self._password = password
        self._method = method
        self._subject = subject
        self._mail_header = mail_header
        self._mail_header_en = mail_header_en
        super().__init__()

    async def send_register_email(self, to: str, link: str, lang: str):
        try:
            register_html = register_tr
            subject = r"""Mapa'ya Hoş Geldiniz!"""
            if lang == "en":
                register_html = register_en
                subject = "Welcome to Mapa!"

            if self._subject:
                subject = self._subject
                
            if self._mail_header:
              if lang == "en":
                register_html = register_en.replace("Welcome To Mapa!", self._mail_header_en)
              else:
                register_html = register_tr.replace("Mapa'ya Hoş Geldiniz!", self._mail_header)
                
            mail_msg = MailMessage(
                self._user_name, to, "", subject, register_html, True, link
            )
            
            if self._method == "SSL":
                mail = smtplib.SMTP_SSL(self._smtp, self._port, timeout=30)
            
            elif self._method == "STARTTLS":
                mail = smtplib.SMTP(self._smtp, self._port, timeout=30)
                mail.starttls()
            
            else:
                mail = smtplib.SMTP(self._smtp, self._port, timeout=30)
                
            if self._password is not None and str.upper(self._password) != "NONE":
                mail.login(self._user_name, self._password)
            mail.sendmail(self._user_name, to, mail_msg.get_message().as_string())
            mail.quit()
        except ValueError as val_err:
            raise val_err
        except Exception as err:
            raise err


class MailMessage(object):

    def __init__(
        self,
        from_email="",
        to_email="",
        cc_email="",
        subject="",
        body="",
        template_html=False,
        link="",
    ):
        self.from_email = from_email
        self.to_email = to_email
        self.cc_email = cc_email
        self.subject = subject
        self.template_html = template_html
        self.body = body
        self.link = link

    def get_message(self):
        try:
            if self.from_email == "":
                raise ValueError("Invalid From email address")

            if self.to_email == "":
                raise ValueError("Invalid To email address")

            if self.link == "":
                raise ValueError("Invalid link address")

            if self.link:
                pattern = re.compile(
                    r"(^|[\n ])(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)",
                    re.IGNORECASE | re.DOTALL,
                )
                self.body = pattern.sub(self.body, self.link)

            msg = MIMEMultipart("alternative")
            msg["To"] = self.to_email
            msg["Cc"] = self.cc_email
            msg["From"] = self.from_email
            msg["Subject"] = self.subject
            if self.template_html:
                msg.attach(MIMEText(self.body, "html"))
            else:
                msg.attach(MIMEText(self.body, "plain"))

            return msg

        except Exception as err:
            raise err
