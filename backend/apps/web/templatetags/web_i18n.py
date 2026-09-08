from django import template

from apps.web.i18n import translate

register = template.Library()


@register.simple_tag(takes_context=True)
def t(context, key, default="", **kwargs):
    messages = context.get("i18n") or {}
    return translate(messages, key, default=default, **kwargs)
