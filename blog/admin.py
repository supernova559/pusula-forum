# blog/admin.py (TEMİZLENMİŞ HALİ)

from django.contrib import admin
from .models import Makale

@admin.register(Makale)
class MakaleAdmin(admin.ModelAdmin):
    list_display = ('baslik', 'yazar', 'kategori', 'durum', 'olusturma_tarihi')
    list_filter = ('durum', 'kategori', 'yazar', 'olusturma_tarihi')
    search_fields = ('baslik', 'icerik')
    actions = ['make_published']

    def make_published(self, request, queryset):
        queryset.update(durum=Makale.Durum.YAYINLANDI)
    make_published.short_description = "Seçili makaleleri yayınla"
