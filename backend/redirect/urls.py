from .views import redirect_to_full_link
from django.urls import path

urlpatterns = [
    path(
        "<str:short_code>",
        redirect_to_full_link,
        name="short-link-redirect"),
]
