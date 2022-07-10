import ghasedak
from django.core.mail import EmailMessage

class SendOTP:
    def send_email(self, email, otp):
        subject = 'Semicolon World'
        message = 'Your verification code is: ' + otp
        email_from = 'metiii.py@gmail.com'
        email_to = email
        email = EmailMessage(subject, message, email_from, [email_to])
        email.send()
        print("email sent")
    
    def send_sms(self, phone, otp):
        template_name = 'semicolonworld'
        param1=otp
        receptor = phone
        type_sms = '1'
        sms = ghasedak.Ghasedak("258c7017a4e17d76e801dbf0ba574c71d5c31df7f0fb50cc0aebdd12e6aa0b77")
        
        try:
            send = sms.verification(
                {
                    'receptor': phone,
                    'type': type_sms,
                    'template': template_name,
                    'param1': param1,
                }
            )
            if send:
                print("sms sended.")
            else:
                print("sms not sended.")
        except:
            print("sms not send")

send_otp = SendOTP()