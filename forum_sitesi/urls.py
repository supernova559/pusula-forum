# forum_sitesi/urls.py (SON VE EN DOĞRU HALİ)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# favicon için view'ı buraya taşıdık, daha mantıklı
from forum.views import favicon_view 

urlpatterns = [
    path('yonetim/', admin.site.urls),
    path('favicon.ico', favicon_view),

    # /blog/ ile başlayan tüm istekleri 'blog.urls'e gönder
    path('blog/', include('blog.urls', namespace='blog')),
    
    # YENİ YAPI:
    # /uyelik/ ile başlayan (sosyal medya, e-posta vb.) tüm standart istekleri 'allauth'a gönder
    path('uyelik/', include('allauth.urls')),
    
    # Diğer tüm istekleri (ana sayfa, forum, BİZİM ÖZEL ÜYELİK SAYFALARIMIZ) 'forum.urls'e gönder
    path('', include('forum.urls', namespace='forum')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)