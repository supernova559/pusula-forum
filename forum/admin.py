# forum/admin.py (GÜNCELLENMİŞ VE DOĞRU HALİ)

from django.contrib import admin
# Profil modelini de import ediyoruz
from .models import Kategori, Konu, Cevap, Profil, Bildirim 

# Kategori, Konu ve Cevap için olan admin sınıfları aynı kalıyor...

@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ('ad', 'konu_sayisi')
    search_fields = ('ad',)

@admin.register(Konu)
class KonuAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'kategori', 'olusturan', 'olusturma_tarihi')
    list_filter = ('kategori', 'olusturma_tarihi')
    search_fields = ('baslik', 'icerik')

@admin.register(Cevap)
class CevapAdmin(admin.ModelAdmin):
    list_display = ('icerik_ozeti', 'konu', 'yazan', 'yazilma_tarihi')
    list_filter = ('yazan', 'yazilma_tarihi')
    search_fields = ('icerik',)

    def icerik_ozeti(self, obj):
        return obj.icerik[:50]

# YENİ EKLENEN BÖLÜM
@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    # Profil listesinde ve formunda görünecek alanlar
    list_display = ('user', 'foto_tag')
    
    def foto_tag(self, obj):
        from django.utils.html import format_html
        if obj.foto:
            return format_html('<img src="{}" style="width: 45px; height: 45px; border-radius: 50%;" />'.format(obj.foto.url))
        return "Fotoğraf Yok"
    foto_tag.short_description = 'Fotoğraf'

@admin.register(Bildirim)
class BildirimAdmin(admin.ModelAdmin):
    list_display = ('kullanici', 'mesaj', 'okundu', 'tarih')
    list_filter = ('okundu', 'tarih')