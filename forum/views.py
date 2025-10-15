# forum/views.py (SON, TAM VE HATASIZ HALİ)

# --- Gerekli Django ve Python Kütüphaneleri ---
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, DeleteView, TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from allauth.account.views import PasswordChangeView
from django.utils import timezone
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.template.loader import render_to_string

# --- Kendi Projemizin Modelleri ve Formları ---
from .models import Kategori, Konu, Cevap, Profil, Bildirim
from blog.models import Makale
from .forms import (
    CevapForm, KonuForm, SignUpForm, 
    UserUpdateForm, ProfileUpdateForm
)


# ========================================
# === ANA SAYFA VE FORUM GÖRÜNÜMLERİ ===
# ========================================

def anasayfa(request):
    kategoriler = Kategori.objects.all()
    context = {'kategoriler_listesi': kategoriler}
    return render(request, 'forum/anasayfa.html', context)

def kategori_detay(request, kategori_id):
    kategori = get_object_or_404(Kategori, pk=kategori_id)
    sirala = request.GET.get('sirala', 'en-yeni')

    if sirala == 'en-populer':
        konu_listesi = Konu.objects.filter(kategori=kategori).annotate(cevap_sayisi=Count('cevap')).order_by('-cevap_sayisi', '-olusturma_tarihi')
    else:
        sirala = 'en-yeni'
        konu_listesi = Konu.objects.filter(kategori=kategori).order_by('-olusturma_tarihi')

    paginator = Paginator(konu_listesi, 10) 
    sayfa_numarasi = request.GET.get('page')
    sayfa_objeleri = paginator.get_page(sayfa_numarasi)

    context = {
        'kategori': kategori,
        'konular_listesi': sayfa_objeleri,
        'aktif_siralama': sirala, 
    }
    return render(request, 'forum/kategori_detay.html', context)

def konu_detay(request, konu_id):
    konu = get_object_or_404(Konu, pk=konu_id)
    
    session_key = f'viewed_topic_{konu.id}'
    if not request.session.get(session_key, False):
        konu.goruntulenme_sayisi += 1
        konu.save(update_fields=['goruntulenme_sayisi'])
        request.session[session_key] = True

    cevap_listesi = Cevap.objects.filter(konu=konu, parent__isnull=True).order_by('yazilma_tarihi')
    paginator = Paginator(cevap_listesi, 10)
    sayfa_numarasi = request.GET.get('page')
    sayfa_objeleri = paginator.get_page(sayfa_numarasi)

    if request.method == 'POST':
        cevap_formu = CevapForm(request.POST)
        if cevap_formu.is_valid():
            yeni_cevap = cevap_formu.save(commit=False)
            yeni_cevap.konu = konu
            yeni_cevap.yazan = request.user
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    yeni_cevap.parent = Cevap.objects.get(id=parent_id)
                except Cevap.DoesNotExist:
                    pass
            yeni_cevap.save()
            return redirect(yeni_cevap.konu.get_absolute_url() + f'#cevap-{yeni_cevap.id}')
    else:
        cevap_formu = CevapForm()

    context = {
        'konu': konu,
        'cevaplar_listesi': sayfa_objeleri,
        'cevap_formu': cevap_formu,
    }
    return render(request, 'forum/konu_detay.html', context)

@login_required
def yeni_konu(request):
    if request.method == 'POST':
        form = KonuForm(request.POST)
        if form.is_valid():
            konu = form.save(commit=False)
            konu.olusturan = request.user
            konu.save()
            return redirect('forum:konu_detay', konu_id=konu.id)
    else:
        form = KonuForm()
    return render(request, 'forum/yeni_konu.html', {'form': form})

# ===========================================
# === KULLANICI PROFİLİ VE AYARLAR ===
# ===========================================

def profil_view(request, username):
    profil_user = get_object_or_404(User, username=username)
    is_onayli_yazar = profil_user.groups.filter(name='Onaylı Yazarlar').exists()
    konular = Konu.objects.filter(olusturan=profil_user).order_by('-olusturma_tarihi')
    kullanicinin_cevaplari = Cevap.objects.filter(yazan=profil_user).select_related('konu').order_by('-yazilma_tarihi')
    makaleler = Makale.objects.filter(yazar=profil_user).order_by('-olusturma_tarihi')
    context = {
        'profil_user': profil_user, 'konular': konular,
        'kullanicinin_cevaplari': kullanicinin_cevaplari,
        'makaleler': makaleler, 'is_onayli_yazar': is_onayli_yazar,
    }
    return render(request, 'forum/profil.html', context)

@login_required
def profil_duzenle_view(request):
    try:
        profil = request.user.profil
    except Profil.DoesNotExist:
        profil = Profil.objects.create(user=request.user)
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profil)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profilin başarıyla güncellendi!')
            return redirect('forum:profil', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profil)
    context = {'u_form': u_form, 'p_form': p_form, 'profil': profil}
    return render(request, 'forum/profil_duzenle.html', context)

class AyarlarView(LoginRequiredMixin, TemplateView):
    template_name = 'account/ayarlar.html'

class HakkimizdaView(TemplateView):
    template_name = 'forum/hakkimizda.html'

# ========================================
# === ÜYELİK VE ŞİFRE İŞLEMLERİ ===
# ========================================

class KayitOlView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('forum:anasayfa')
    template_name = 'registration/kayit_ol.html'
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.info(self.request, 'hosgeldin_karti_goster')
        return response

class PusulaPasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('forum:password_reset_done')
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'

class PusulaPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

class PusulaPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('forum:password_reset_complete')

class PusulaPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'

class PusulaPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    def dispatch(self, request, *args, **kwargs):
        try:
            profil = request.user.profil
        except Profil.DoesNotExist:
            profil = Profil.objects.create(user=request.user)
        if profil.son_sifre_degistirme:
            izin_verilen_tarih = profil.son_sifre_degistirme + timedelta(days=90)
            if timezone.now() < izin_verilen_tarih:
                son_degistirme_str = profil.son_sifre_degistirme.strftime('%d.%m.%Y')
                messages.error(request, f"Şifrenizi en son {son_degistirme_str} tarihinde değiştirdiniz. 3 ay beklemeniz gerekmektedir.")
                return redirect('forum:ayarlar')
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        profil = self.request.user.profil
        profil.son_sifre_degistirme = timezone.now()
        profil.save(update_fields=['son_sifre_degistirme'])
        messages.success(self.request, 'Şifreniz başarıyla güncellendi!')
        return super().form_valid(form)

# ========================================
# === ETKİLEŞİM (AJAX) VE DİĞERLERİ ===
# ========================================

def arama_view(request):
    query = request.GET.get('q')
    sonuclar = []
    if query:
        sonuclar = Konu.objects.filter(Q(baslik__icontains=query) | Q(icerik__icontains=query)).order_by('-olusturma_tarihi')
    context = {'query': query, 'sonuclar': sonuclar}
    return render(request, 'forum/arama_sonuclari.html', context)

@login_required
def konu_begen_view(request, pk):
    konu = get_object_or_404(Konu, id=pk)
    begenildi = False
    if konu.begenenler.filter(id=request.user.id).exists():
        konu.begenenler.remove(request.user)
    else:
        konu.begenenler.add(request.user)
        begenildi = True
    return JsonResponse({"begenildi": begenildi, "begeni_sayisi": konu.begenenler.count()})

@login_required
def begen_view(request, pk):
    cevap = get_object_or_404(Cevap, id=pk)
    begenildi = False
    if cevap.begenenler.filter(id=request.user.id).exists():
        cevap.begenenler.remove(request.user)
    else:
        cevap.begenenler.add(request.user)
        begenildi = True
    return JsonResponse({"begenildi": begenildi, "begeni_sayisi": cevap.begenenler.count()})

@login_required
def begenenleri_getir_view(request):
    try:
        object_id = request.GET.get('object_id')
        object_type = request.GET.get('object_type')
        obj = None
        if object_type == 'konu': obj = Konu.objects.get(id=object_id)
        elif object_type == 'cevap': obj = Cevap.objects.get(id=object_id)
        elif object_type == 'makale': obj = Makale.objects.get(id=object_id)
        if obj:
            begenenler = obj.begenenler.all().select_related('profil')
            html = render_to_string('partials/begenenler_listesi.html', {'begenenler': begenenler}, request=request)
            return JsonResponse({'html': html})
    except Exception as e:
        print(f"HATA - begenenleri_getir_view: {e}")
    return JsonResponse({'html': '<li class="list-group-item">Bir hata oluştu.</li>'}, status=500)

@login_required
def bildirimleri_oku_view(request):
    if request.method == 'POST':
        Bildirim.objects.filter(kullanici=request.user, okundu=False).update(okundu=True)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

class TumBildirimlerView(LoginRequiredMixin, ListView):
    model = Bildirim
    template_name = 'forum/tum_bildirimler.html'
    context_object_name = 'bildirimler'
    paginate_by = 15
    def get_queryset(self):
        return Bildirim.objects.filter(kullanici=self.request.user).select_related('gonderen', 'gonderen__profil', 'ilgili_cevap', 'ilgili_cevap__konu')

@login_required
def konu_sil_ajax(request, pk):
    konu = get_object_or_404(Konu, pk=pk)
    if request.user == konu.olusturan and request.method == 'POST':
        konu.delete()
        return JsonResponse({'status': 'ok', 'message': f"'{konu.baslik}' başlıklı konu silindi."})
    return JsonResponse({'status': 'error', 'message': 'Bu işlemi yapma yetkiniz yok.'}, status=403)

@login_required
def cevap_sil_ajax(request, pk):
    cevap = get_object_or_404(Cevap, pk=pk)
    if request.user == cevap.yazan and request.method == 'POST':
        cevap.delete()
        return JsonResponse({'status': 'ok', 'message': 'Cevabınız silindi.'})
    return JsonResponse({'status': 'error', 'message': 'Bu işlemi yapma yetkiniz yok.'}, status=403)

def favicon_view(request):
    return HttpResponse(status=204)



from django.template.loader import render_to_string

@login_required
def begenenleri_getir_view(request):
    try:
        object_id = request.GET.get('object_id')
        object_type = request.GET.get('object_type')
        
        obj = None
        if object_type == 'konu':
            obj = Konu.objects.get(id=object_id)
        elif object_type == 'cevap':
            obj = Cevap.objects.get(id=object_id)
        elif object_type == 'makale':
            obj = Makale.objects.get(id=object_id)
        
        if obj:
            begenenler = obj.begenenler.all().select_related('profil')
            html = render_to_string(
                'partials/begenenler_listesi.html', 
                {'begenenler': begenenler},
                request=request
            )
            return JsonResponse({'html': html})
    except Exception as e:
        print(f"HATA - begenenleri_getir_view: {e}")

    return JsonResponse({'html': '<li class="list-group-item">İçerik yüklenirken bir hata oluştu.</li>'}, status=500)