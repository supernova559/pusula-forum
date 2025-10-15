# blog/models.py (SADELEŞTİRİLMİŞ HALİ)

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from forum.models import Kategori # <-- Forum'un Kategori modelini import ediyoruz

class Makale(models.Model):
    class Durum(models.TextChoices):
        TASLAK = 'TSL', 'Taslak'
        YAYINLANDI = 'YAY', 'Yayınlandı'

    baslik = models.CharField(max_length=200)
    icerik = models.TextField()
    yazar = models.ForeignKey(User, on_delete=models.CASCADE)
    # DİKKAT: Artık 'forum.Kategori' modelini kullanıyoruz
    kategori = models.ForeignKey(Kategori, on_delete=models.SET_NULL, null=True, blank=True)
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    guncelleme_tarihi = models.DateTimeField(auto_now=True)
    one_cikan_gorsel = models.ImageField(upload_to='blog_gorselleri/', null=True, blank=True, help_text="Makalenin en üstünde görünecek fotoğraf.")
    durum = models.CharField(max_length=3, choices=Durum.choices, default=Durum.TASLAK)
    goruntulenme_sayisi = models.IntegerField(default=0)
    begenenler = models.ManyToManyField(User, related_name='begenilen_makaleler', blank=True)

    class Meta:
        ordering = ['-olusturma_tarihi']

    def __str__(self):
        return self.baslik

    def get_absolute_url(self):
        return reverse('blog:makale_detay', kwargs={'pk': self.pk})

# BlogKategori modeli buradan silindi.