import ghasedakpack
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_otp_sms(phone_number, code):
    try:
        sms = ghasedakpack.Ghasedak(settings.GHASEDAK_API_KEY)
        response = sms.verification({
            'receptor': phone_number,
            'type': '1',  # مقدار 1 برای پیامک متنی و 2 برای تماس صوتی
            'template': settings.GHASEDAK_TEMPLATE,  # نام قالبی که در پنل قاصدک تایید کرده‌اید
            'param1': str(code)  # پارامتر اول قالب که همان کد تایید است
        })
        logger.info(f"SMS sent to {phone_number}, Response: {response}")
        return True
    except Exception as e:
        logger.error(f"Error in sending SMS via Ghasedak: {e}")
        return False
