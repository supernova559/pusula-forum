# blog/views.py (TAM VE HATASIZ SON HALİ)

from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.db.models import Q

from .models import Makale
from .forms import MakaleForm

# --- Blog Sayfaları ---
class MakaleListView(ListView):
    model = Makale
    template_name = 'blog/makale_list.html'
    context_object_name = 'makaleler'
    paginate_by = 5
    def get_queryset(self):
        return Makale.objects.filter(durum=Makale.Durum.YAYINLANDI).select_related('yazar', 'kategori')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_onayli_yazar'] = self.request.user.groups.filter(name='Onaylı Yazarlar').exists()
        else: context['is_onayli_yazar'] = False
        return context

class MakaleDetailView(DetailView):
    model = Makale
    template_name = 'blog/makale_detay.html'
    context_object_name = 'makale'
    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        session_key = f'viewed_article_{obj.id}'
        if not self.request.session.get(session_key, False):
            obj.goruntulenme_sayisi += 1
            obj.save(update_fields=['goruntulenme_sayisi'])
            self.request.session[session_key] = True
        return obj
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_authenticated:
            return queryset.filter(durum=Makale.Durum.YAYINLANDI)
        return queryset.filter(Q(durum=Makale.Durum.YAYINLANDI) | (Q(yazar=self.request.user) & Q(durum=Makale.Durum.TASLAK)))

# --- Makale Oluşturma, Silme, Beğenme ---
class MakaleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Makale
    form_class = MakaleForm
    template_name = 'blog/makale_form.html'
    def test_func(self):
        return self.request.user.groups.filter(name='Onaylı Yazarlar').exists()
    def form_valid(self, form):
        form.instance.yazar = self.request.user
        messages.success(self.request, 'Makaleniz başarıyla gönderildi! İncelemenin ardından uygun bulunması durumunda yayınlanacaktır.')
        return super().form_valid(form)
    def get_success_url(self):
        return reverse_lazy('blog:blog_anasayfa')

class MakaleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Makale
    template_name = 'blog/makale_onayli_sil.html'
    success_url = reverse_lazy('blog:blog_anasayfa')
    def test_func(self):
        makale = self.get_object()
        return self.request.user == makale.yazar

@login_required
def makale_begen_view(request, pk):
    makale = get_object_or_404(Makale, id=pk)
    begenildi = False
    if makale.begenenler.filter(id=request.user.id).exists():
        makale.begenenler.remove(request.user)
        begenildi = False
    else:
        makale.begenenler.add(request.user)
        begenildi = True
    return JsonResponse({"begenildi": begenildi, "begeni_sayisi": makale.begenenler.count()})