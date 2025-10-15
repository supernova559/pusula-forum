# blog/urls.py (DÜZELTİLMİŞ VE TAM HALİ)

from django.urls import path
from .views import (
    MakaleListView, 
    MakaleDetailView, 
    MakaleDeleteView, 
    makale_begen_view,
    MakaleCreateView # Yeni view'ımızı import ediyoruz
)

app_name = 'blog'

urlpatterns = [
    # /blog/ -> Tüm makalelerin listesi
    path('', MakaleListView.as_view(), name='blog_anasayfa'),
    
    # /blog/yeni-makale/ -> Yeni makale oluşturma sayfası
    path('yeni-makale/', MakaleCreateView.as_view(), name='makale_yeni'),
    
    # /blog/123/ -> ID'si 123 olan makalenin detayı
    path('<int:pk>/', MakaleDetailView.as_view(), name='makale_detay'),
    
    # /blog/123/sil/ -> Makale silme
    path('<int:pk>/sil/', MakaleDeleteView.as_view(), name='makale_sil'),
    
    # /blog/123/begen/ -> Makale beğenme
    path('<int:pk>/begen/', makale_begen_view, name='makale_begen'),
]