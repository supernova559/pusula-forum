# forum/signals.py (SADELEŞTİRİLMİŞ SON HALİ)

from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Cevap, Bildirim, Konu, Profil

# --- BİLDİRİM SİNYALLERİ ---

@receiver(m2m_changed, sender=Cevap.begenenler.through)
def cevap_begenildi_bildirimi(sender, instance, action, pk_set, **kwargs):
    cevap = instance
    
    # Beğeniyi yapan/geri çeken kullanıcının ID'sini al
    if not pk_set:
        return
    kullanici_id = list(pk_set)[0]
    begenen_kullanici = User.objects.get(id=kullanici_id)

    # 1. Beğeni EKLENDİĞİNDE
    if action == "post_add":
        if cevap.yazan != begenen_kullanici:
            # Daha önce aynı bildirimden var mı diye kontrol edip tekrar oluşturulmasını engelleyebiliriz.
            # Şimdilik basitçe oluşturalım.
            Bildirim.objects.create(
                kullanici=cevap.yazan,
                gonderen=begenen_kullanici,
                bildirim_tipi=Bildirim.BildirimTipi.BEGENI,
                ilgili_cevap=cevap,
                mesaj="bir cevabınızı beğendi."
            )
    
    # 2. Beğeni GERİ ÇEKİLDİĞİNDE
    elif action == "post_remove":
        # Bu kullanıcıdan, bu cevap için daha önce oluşturulmuş "beğendi" bildirimini bul
        Bildirim.objects.filter(
            kullanici=cevap.yazan,
            gonderen=begenen_kullanici,
            bildirim_tipi=Bildirim.BildirimTipi.BEGENI,
            ilgili_cevap=cevap
        ).delete() # Ve o bildirimi SİL

@receiver(post_save, sender=Cevap)
def yeni_cevap_bildirimi(sender, instance, created, **kwargs):
    if created:
        cevap = instance
        mesaj, tip, hedef_kullanici = "", None, None
        if cevap.parent:
            hedef_kullanici = cevap.parent.yazan
            mesaj = "bir cevabınıza yanıt verdi."
            tip = Bildirim.BildirimTipi.YANIT
        else:
            hedef_kullanici = cevap.konu.olusturan
            mesaj = f"'{cevap.konu.baslik}' konunuza bir cevap yazdı."
            tip = Bildirim.BildirimTipi.CEVAP
        if hedef_kullanici != cevap.yazan:
            Bildirim.objects.create(
                kullanici=hedef_kullanici,
                gonderen=cevap.yazan,
                bildirim_tipi=tip,
                ilgili_cevap=cevap,
                mesaj=mesaj
            )

# --- OTOMATİK PROFİL OLUŞTURMA SİNYALİ ---

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Yeni bir kullanıcı oluşturulduğunda, ona otomatik olarak bir Profil de oluşturur.
    """
    if created:
        if not Profil.objects.filter(user=instance).exists():
            Profil.objects.create(user=instance)