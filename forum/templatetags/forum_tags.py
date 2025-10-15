from django import template
import hashlib

register = template.Library()

@register.simple_tag
def gravatar_url(email, size=40):
    if email: # E-posta boş değilse işlem yap
        email_hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{email_hash}?s={size}&d=mp"
    return "" # E-posta boşsa boş string döndür