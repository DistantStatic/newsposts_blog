from django.conf import settings

def captcha_key(request):
  return {'CAPTCHA_SITE_KEY': settings.CAPTCHA_SITE_KEY}