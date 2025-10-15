# forum/models.py (SON, TAM VE HATASIZ HALİ)

import re
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# === TEMEL FORUM MODELLERİ ===

class Kategori(models.Model):
    ad = models.CharField(max_length=100)
    aciklama = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Kategoriler" # Yönetim panelinde daha güzel görünmesi için

    def __str__(self):
        return self.ad

    def konu_sayisi(self):
        return self.konu_set.count()

    def cevap_sayisi(self):
        # Bu kategorideki konulara ait tüm cevapları say
        return Cevap.objects.filter(konu__kategori=self).count()

class Konu(models.Model):
    baslik = models.CharField(max_length=255)
    icerik = models.TextField()
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE)
    olusturan = models.ForeignKey(User, on_delete=models.CASCADE)
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    goruntulenme_sayisi = models.IntegerField(default=0)
    begenenler = models.ManyToManyField(User, related_name='begenilen_konular', blank=True)

    def __str__(self):
        return self.baslik

    def get_absolute_url(self):
        return reverse('forum:konu_detay', kwargs={'konu_id': self.pk})

class Cevap(models.Model):
    konu = models.ForeignKey(Konu, on_delete=models.CASCADE)
    icerik = models.TextField()
    yazan = models.ForeignKey(User, on_delete=models.CASCADE)
    yazilma_tarihi = models.DateTimeField(auto_now_add=True)
    begenenler = models.ManyToManyField(User, related_name='begenilen_cevaplar', blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='yanitlar')
    
    class Meta:
        ordering = ['yazilma_tarihi'] # Cevapları en eskiden yeniye doğru sırala

    def __str__(self):
        return self.icerik[:50]

    @property
    def icerik_html(self):
        # Profil linkini doğru namespace ile oluşturuyoruz
        return re.sub(r'@(\w+)', r'<a class="profil-linki" href="/profil/\1/">@\1</a>', self.icerik)

# === KULLANICI İLE İLGİLİ MODELLER ===

class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gorunen_ad = models.CharField(max_length=100, blank=True, verbose_name="Görünen Ad")
    foto = models.ImageField(upload_to='profil_fotolari/', null=True, blank=True)
    son_sifre_degistirme = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.username} Profili'

class Bildirim(models.Model):
    class BildirimTipi(models.TextChoices):
        BEGENI = 'BEGENI', 'Beğeni'
        YANIT = 'YANIT', 'Yanıt'
        CEVAP = 'CEVAP', 'Cevap'
        
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bildirimler')
    gonderen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gonderdigi_bildirimler')
    bildirim_tipi = models.CharField(max_length=10, choices=BildirimTipi.choices, default=BildirimTipi.BEGENI)
    ilgili_cevap = models.ForeignKey(Cevap, on_delete=models.CASCADE, null=True, blank=True)
    mesaj = models.CharField(max_length=255)
    okundu = models.BooleanField(default=False)
    tarih = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-tarih']

    def __str__(self):
        return self.mesaj

    def get_absolute_url(self):
        if self.ilgili_cevap:
            return self.ilgili_cevap.konu.get_absolute_url() + f'#cevap-{self.ilgili_cevap.id}'
        return '#'