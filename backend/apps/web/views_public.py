from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "web/public/home.html"


class AboutView(TemplateView):
    template_name = "web/public/about.html"


class ContactView(TemplateView):
    template_name = "web/public/contact.html"


def page_not_found(request, exception=None):
    return render(request, "web/public/404.html", status=404)
