# forum/context_processors.py

from .models import Bildirim

def notifications_processor(request):
    if request.user.is_authenticated:
        okunmamis_bildirimler = Bildirim.objects.filter(kullanici=request.user, okundu=False)
        return {'okunmamis_bildirimler': okunmamis_bildirimler}
    return {}