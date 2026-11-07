from django import template

from apps.users.identity import (
    decrypt_display_name,
    get_user_full_name,
    get_user_login,
)

register = template.Library()


@register.filter
def user_login(user):
    return get_user_login(user)


@register.filter
def user_full_name(user):
    return get_user_full_name(user)


@register.filter
def plain_name(value):
    return decrypt_display_name(value or "")
