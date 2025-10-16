from django.urls import re_path, path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    re_path(
        r"^(?P<tricount_id>t[a-zA-Z]{15,17})$",
        views.tricount_details,
        name="tricount_details",
    ),
]
