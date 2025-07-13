from email.mime.application import MIMEApplication
from typing import Any
from mapa.core.data.base_service import BaseService
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import ssl
import re

forgot_password_tr = r""" <html>
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
                                 <table cellpadding="0" cellspacing="0" width="100%" align="center">
                                   <tbody>
                                     <tr>
                                       <td>
                                         <img src="https://ci6.googleusercontent.com/proxy/GBQkpDhoWEbDyVGFHplOhMxfl2Wwj8GiBjEfMc-ZTsqi28JergHqrFZCsG6F_vWdCjzgjkkgPcdhktSE8ouYayUrOaWoar6JJPGk3_GDXdyQ9E5_GrqJ6sgRn60yY-88SYVhgAEN7vlcj14QvQBvdrdMqatkG9aOyhnR131A8MKqsH-KioqMblKcNTkcUtyovPNWYHchig_NVeHfUsG0VeRd_PVYRnn-2pLWZ1_RBui41vSdP5y6ZPRmkVkj2EyBtXbNjxyn0569DQN1KIjAuQ3xUBuS8aJoq6ZbiZrUWRioduC4o7D3UUs7Hr97BxeK4bAqDuGM4fSef4n0bvpajmbQ71AAEDdL8RqfNHyJonIXcUuBCs86JLWG3IuEqi4tGRAZnjqydP3DWbdvth7amJAipU4l8r-3MRGdsMCTpAGACfqrlq2rWUGoqzfvirHjjteKHVLObAFKcG8uDeTOb5dGNI8GJDxvLulfHUAq4S2eG9IEEu5G1-JRhBCZ45FiBMJf3p4y1g5pU6TCMVGLnFUToFs1BlnApoJDDhLzTJNWOG7iiOeXD89AzW-P=s0-d-e1-ft#https://img.e.designmodo.com/im/2474129/39d744e8646ec293ed71cd1a527ff185e456f5f44cf5aa2405af6e9c24d64e4e.png?e=nu3iXhg6tso_6go6MTleU5bYYcZTWBdfuGbYZWirZboO2D0CQ-tu0gXdp4kshmeb-84h1Nc4pTk8rPKXOjhMERU3YtUE0hhD-WkMApqjJyXaOQR_PzZyjpweiy6eSppRFn5DZzIYp0TwxTlWVQNqFHyoOtdcL4zCi518JffJSgF2rsbrI5fcAXqU4ZoQVRd29TcGvTqaum9xgwk7geO5lIY7yjwiIEiXM15CX21Ls8fZz5w4UoFEAQe-mF4vQU_6YSZW3tnIvSL5B56otd_pl73Tbju3aVgJMO-27FV8zA" width="48" style="display:block;margin:0 auto" align="center" class="CToWUd" data-bit="iit">
                                       </td>
                                     </tr>
                                     <tr>
                                       <td height="15"></td>
                                     </tr>
                                     <tr>
                                       <td class="m_6906578752728732323title" style="line-height:48px;text-align:center;color:#262626;font-size:42px;font-family:Inter,Roboto,Helvetica,Arial,sans-serif;font-weight:bold;letter-spacing:-0.022em" align="center">Parolanızı Sıfırlayın</td>
                                     </tr>
                                   </tbody>
                                 </table>
                               </td>
                             </tr>
                             <tr>
                               <td height="30"></td>
                             </tr>
                             <tr>
                               <td align="center" style="display:block;font-size:20px;color:#262626;font-family:Inter,Helvetica,Arial,sans-serif;letter-spacing:-0.017em;font-weight:bold;line-height:1.6">
                                 <strong style="max-width:390px;display:inline-block">Birisi, aşağıdaki hesap için parolanın sıfırlanmasını istedi:</strong>
                               </td>
                             </tr>
                             <tr>
                               <td height="30"></td>
                             </tr>
                             <tr>
                               <td align="center" style="line-height:1.4;font-weight:normal;color:#262626;font-family:Inter,Helvetica,Arial,sans-serif;font-size:16px;letter-spacing:-0.011em;margin:0">Parolanızı sıfırlamak için aşağıdaki adresi ziyaret edin:</td>
                             </tr>
                             <tr>
                               <td height="30"></td>
                             </tr>
                             <tr>
                               <td align="center">
                                 <a href="\2" style="margin:0 auto;color:#ffffff;background:#2f80ed;padding-top:13px;padding-bottom:13px;padding-left:20px;padding-right:20px;border-radius:6px;font-size:16px;text-decoration:none;font-family:Inter,Helvetica,Arial,sans-serif;font-weight:500;display:inline-block" bgcolor="#2F80ED" target="_blank">Şifrenizi sıfırlamak için buraya tıklayın.</a>
                               </td>
                             </tr>
                             <tr>
                               <td height="15"></td>
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
forgot_password_en = r"""
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
                                 <table cellpadding="0" cellspacing="0" width="100%" align="center">
                                   <tbody>
                                     <tr>
                                       <td>
                                         <img src="https://ci6.googleusercontent.com/proxy/GBQkpDhoWEbDyVGFHplOhMxfl2Wwj8GiBjEfMc-ZTsqi28JergHqrFZCsG6F_vWdCjzgjkkgPcdhktSE8ouYayUrOaWoar6JJPGk3_GDXdyQ9E5_GrqJ6sgRn60yY-88SYVhgAEN7vlcj14QvQBvdrdMqatkG9aOyhnR131A8MKqsH-KioqMblKcNTkcUtyovPNWYHchig_NVeHfUsG0VeRd_PVYRnn-2pLWZ1_RBui41vSdP5y6ZPRmkVkj2EyBtXbNjxyn0569DQN1KIjAuQ3xUBuS8aJoq6ZbiZrUWRioduC4o7D3UUs7Hr97BxeK4bAqDuGM4fSef4n0bvpajmbQ71AAEDdL8RqfNHyJonIXcUuBCs86JLWG3IuEqi4tGRAZnjqydP3DWbdvth7amJAipU4l8r-3MRGdsMCTpAGACfqrlq2rWUGoqzfvirHjjteKHVLObAFKcG8uDeTOb5dGNI8GJDxvLulfHUAq4S2eG9IEEu5G1-JRhBCZ45FiBMJf3p4y1g5pU6TCMVGLnFUToFs1BlnApoJDDhLzTJNWOG7iiOeXD89AzW-P=s0-d-e1-ft#https://img.e.designmodo.com/im/2474129/39d744e8646ec293ed71cd1a527ff185e456f5f44cf5aa2405af6e9c24d64e4e.png?e=nu3iXhg6tso_6go6MTleU5bYYcZTWBdfuGbYZWirZboO2D0CQ-tu0gXdp4kshmeb-84h1Nc4pTk8rPKXOjhMERU3YtUE0hhD-WkMApqjJyXaOQR_PzZyjpweiy6eSppRFn5DZzIYp0TwxTlWVQNqFHyoOtdcL4zCi518JffJSgF2rsbrI5fcAXqU4ZoQVRd29TcGvTqaum9xgwk7geO5lIY7yjwiIEiXM15CX21Ls8fZz5w4UoFEAQe-mF4vQU_6YSZW3tnIvSL5B56otd_pl73Tbju3aVgJMO-27FV8zA" width="48" style="display:block;margin:0 auto" align="center" class="CToWUd" data-bit="iit">
                                       </td>
                                     </tr>
                                     <tr>
                                       <td height="15"></td>
                                     </tr>
                                     <tr>
                                       <td class="m_6906578752728732323title" style="line-height:48px;text-align:center;color:#262626;font-size:42px;font-family:Inter,Roboto,Helvetica,Arial,sans-serif;font-weight:bold;letter-spacing:-0.022em" align="center">Reset Your Password</td>
                                     </tr>
                                   </tbody>
                                 </table>
                               </td>
                             </tr>
                             <tr>
                               <td height="30"></td>
                             </tr>
                             <tr>
                               <td align="center" style="display:block;font-size:20px;color:#262626;font-family:Inter,Helvetica,Arial,sans-serif;letter-spacing:-0.017em;font-weight:bold;line-height:1.6">
                                 <strong style="max-width:390px;display:inline-block">Someone requested that the password be reset for the following account:</strong>
                               </td>
                             </tr>
                             <tr>
                               <td height="30"></td>
                             </tr>
                             <tr>
                               <td align="center" style="line-height:1.4;font-weight:normal;color:#262626;font-family:Inter,Helvetica,Arial,sans-serif;font-size:16px;letter-spacing:-0.011em;margin:0">To reset your password, visit the following address:</td>
                             </tr>
                             <tr>
                               <td height="30"></td>
                             </tr>
                             <tr>
                               <td align="center">
                                 <a href="\2" style="margin:0 auto;color:#ffffff;background:#2f80ed;padding-top:13px;padding-bottom:13px;padding-left:20px;padding-right:20px;border-radius:6px;font-size:16px;text-decoration:none;font-family:Inter,Helvetica,Arial,sans-serif;font-weight:500;display:inline-block" bgcolor="#2F80ED" target="_blank">Click here to reset your password</a>
                               </td>
                             </tr>
                             <tr>
                               <td height="15"></td>
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
        self, smtp: Any, port: Any, user_name: Any, password: Any, method: Any
    ) -> None:
        self._smtp = smtp
        self._port = port
        self._user_name = user_name
        self._password = password
        self._method = method
        super().__init__()

    async def send_verify_email(self, to: str, lang: str): ...

    async def send_forgot_password(self, to: str, link: str, lang: str):
        try:

            forgot_password_html = forgot_password_tr
            subject = r"""Parolanızı mı unuttunuz!"""
            if lang == "en":
                forgot_password_html = forgot_password_en
                subject = "Forgot Your Password!"

            mail_msg = MailMessage(
                self._user_name, to, "", subject, forgot_password_html, True, link
            )
            mail = smtplib.SMTP(self._smtp, self._port, timeout=30)
            if self._method is not None:
                mail.starttls()
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
