# blog/forms.py

from django import forms
from .models import Makale
from ckeditor.widgets import CKEditorWidget

class MakaleForm(forms.ModelForm):
    # CKEditor'ı bu formda da aktif hale getiriyoruz
    icerik = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Makale
        # Yazardan sadece bu alanları istiyoruz
        fields = ['baslik', 'kategori', 'one_cikan_gorsel', 'icerik']
        labels = {
            'baslik': 'Makale Başlığı',
            'kategori': 'Kategori',
            'one_cikan_gorsel': 'Öne Çıkan Görsel (Kapak Fotoğrafı)',
            'icerik': 'Makale İçeriği'
        }
        widgets = {
            'baslik': forms.TextInput(attrs={'class': 'form-control'}),
            'kategori': forms.Select(attrs={'class': 'form-select'}),
            'one_cikan_gorsel': forms.FileInput(attrs={'class': 'form-control'}),
        }