# forum/urls.py (SON, TAM VE HATASIZ HALİ)

from django.urls import path, include
from . import views

app_name = 'forum'

urlpatterns = [
    # Ana Sayfa ve Statik Sayfalar
    path('', views.anasayfa, name='anasayfa'),
    path('hakkimizda/', views.HakkimizdaView.as_view(), name='hakkimizda'),

    # Üyelik İşlemleri
    path('kayit-ol/', views.KayitOlView.as_view(), name='kayit_ol'),
    path('giris/', views.auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('cikis/', views.auth_views.LogoutView.as_view(), name='logout'),
    
    # Şifre Sıfırlama
    path('sifre-sifirlama/', views.PusulaPasswordResetView.as_view(), name='password_reset'),
    path('sifre-sifirlama/gonderildi/', views.PusulaPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('sifre-sifirlama-onay/<uidb64>/<token>/', views.PusulaPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('sifre-sifirlama/tamamlandi/', views.PusulaPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Ayarlar ve Profil
    path('ayarlar/', views.AyarlarView.as_view(), name='ayarlar'),
    path('ayarlar/sifre-degistir/', views.PusulaPasswordChangeView.as_view(), name='account_change_password'),
    path('profil/duzenle/', views.profil_duzenle_view, name='profil_duzenle'),
    path('profil/<str:username>/', views.profil_view, name='profil'),
    
    # Forum İşlemleri
    path('kategori/<int:kategori_id>/', views.kategori_detay, name='kategori_detay'),
    path('konu/<int:konu_id>/', views.konu_detay, name='konu_detay'),
    path('yeni-konu/', views.yeni_konu, name='yeni_konu'),
    path('arama/', views.arama_view, name='arama'),

    # Etkileşim ve Bildirimler (AJAX)
    path('konu/<int:pk>/begen/', views.konu_begen_view, name='konu_begen'),
    path('cevap/<int:pk>/begen/', views.begen_view, name='begen_cevap'),
    path('yanit/<int:pk>/begen/', views.begen_view, name='begen_yanit'),
    path('ajax/begenenleri-getir/', views.begenenleri_getir_view, name='ajax_begenenleri_getir'),
    path('bildirimleri-oku/', views.bildirimleri_oku_view, name='bildirimleri_oku'),
    path('bildirimler/', views.TumBildirimlerView.as_view(), name='tum_bildirimler'),

    # Silme İşlemleri (AJAX)
    path('konu/<int:pk>/sil/', views.konu_sil_ajax, name='konu_sil_ajax'),
    path('cevap/<int:pk>/sil/', views.cevap_sil_ajax, name='cevap_sil_ajax'),
]