from django.urls import path

from .views import redirect_to_full_link

urlpatterns = [
    path(
        "<str:short_code>/",
        redirect_to_full_link,
        name="short-link-redirect"),
]
