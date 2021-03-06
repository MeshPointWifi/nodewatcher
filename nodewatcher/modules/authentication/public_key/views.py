from django.core import urlresolvers
from django.views import generic

from nodewatcher.core.frontend import views
from nodewatcher.extra.accounts import mixins

from . import models


class AddPublicKey(mixins.AuthenticatedRequiredMixin, views.CancelableFormMixin, generic.CreateView):
    template_name = 'public_key/new.html'
    model = models.UserAuthenticationKey
    fields = ['name', 'public_key']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(AddPublicKey, self).form_valid(form)

    def get_cancel_url(self):
        return urlresolvers.reverse('PublicKeyComponent:list')

    def get_success_url(self):
        return urlresolvers.reverse('PublicKeyComponent:list')


class RemovePublicKey(mixins.AuthenticatedRequiredMixin, views.CancelableFormMixin, generic.DeleteView):
    template_name = 'public_key/remove.html'
    model = models.UserAuthenticationKey

    def get_queryset(self):
        return super(RemovePublicKey, self).get_queryset().filter(user=self.request.user)

    def get_cancel_url(self):
        return urlresolvers.reverse('PublicKeyComponent:list')

    def get_success_url(self):
        return urlresolvers.reverse('PublicKeyComponent:list')


class ListPublicKeys(mixins.AuthenticatedRequiredMixin, generic.TemplateView):
    template_name = 'public_key/list_public_keys.html'
