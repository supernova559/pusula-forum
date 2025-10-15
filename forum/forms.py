# forum/forms.py (SON, TAM VE HATASIZ HALİ)

import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cevap, Konu, Profil
from .banned_words import BANNED_WORDS

# --- Yardımcı Fonksiyon ---
def contains_banned_words(text):
    clean_text_words = set(re.sub(r'[^\w\s]', '', text.lower()).split())
    clean_banned_words = set(word.lower().strip() for word in BANNED_WORDS if word.strip())
    return not clean_banned_words.isdisjoint(clean_text_words)

# --- Forum Formları ---
class CevapForm(forms.ModelForm):
    class Meta:
        model = Cevap
        fields = ['icerik']
        widgets = {'icerik': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Cevabınızı buraya yazın...'})}
        labels = { 'icerik': '' }
    def clean_icerik(self):
        icerik = self.cleaned_data.get('icerik')
        if contains_banned_words(icerik):
            raise forms.ValidationError("Cevabınız uygunsuz kelimeler içeremez.")
        return icerik

class KonuForm(forms.ModelForm):
    class Meta:
        model = Konu
        fields = ['kategori', 'baslik', 'icerik']
        widgets = {
            'kategori': forms.Select(attrs={'class': 'form-select'}),
            'baslik': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Konu başlığını buraya yazın...'}),
            'icerik': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Konu içeriğini buraya yazın...'}),
        }
        labels = { 'baslik': 'Başlık', 'icerik': 'İçerik', 'kategori': 'Kategori' }
    def clean_baslik(self):
        baslik = self.cleaned_data.get('baslik')
        if contains_banned_words(baslik):
            raise forms.ValidationError("Başlık uygunsuz kelimeler içeremez.")
        return baslik
    def clean_icerik(self):
        icerik = self.cleaned_data.get('icerik')
        if contains_banned_words(icerik):
            raise forms.ValidationError("İçerik uygunsuz kelimeler içeremez.")
        return icerik

# --- Üyelik Formları ---
class SignUpForm(UserCreationForm):
    gorunen_ad = forms.CharField(max_length=100, required=True, label="Görünen Adınız (örn: Vera)")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')
        help_texts = {
            'username': 'Kalıcıdır ve değiştirilemez. 3-25 karakter arasında olmalı, sadece küçük harf, rakam ve boşluk içerebilir.',
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not 3 <= len(username) <= 25: raise forms.ValidationError('Kullanıcı adı 3 ila 25 karakter arasında olmalıdır.')
        if not re.match(r'^[a-zA-Z0-9çğıöşüÇĞİÖŞÜ ]+$', username): raise forms.ValidationError('Kullanıcı adında sadece harf, rakam ve boşluk kullanabilirsiniz.')
        if "  " in username: raise forms.ValidationError('Kullanıcı adında art arda birden fazla boşluk olamaz.')
        if username.startswith(' ') or username.endswith(' '): raise forms.ValidationError('Kullanıcı adı boşluk ile başlayamaz veya bitemez.')
        if contains_banned_words(username): raise forms.ValidationError("Bu kullanıcı adı uygunsuz kelimeler içeremez.")
        return username

    def save(self, commit=True):
        user = super().save(commit=True)
        # Sinyal, kullanıcı oluşturulduğunda boş bir profil oluşturur.
        # Biz burada, o boş profili bulup 'gorunen_ad'ı güncelliyoruz.
        user.profil.gorunen_ad = self.cleaned_data.get('gorunen_ad')
        user.profil.save()
        return user

# --- Profil Güncelleme Formları ---
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        # Kullanıcı adı değiştirilemez, sadece e-posta yönetimi için ayrı sayfa var.
        # Bu formda 'gorunen_ad'ı güncelleyeceğiz.
        fields = [] # Bu formu doğrudan kullanmayacağız, bir sonraki daha iyi.

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ['gorunen_ad', 'foto']
        labels = {
            'gorunen_ad': 'Görünen Ad',
            'foto': 'Profil Fotoğrafı'
        }