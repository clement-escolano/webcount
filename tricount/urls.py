from django.urls import path, include

urlpatterns = [
    path("", include("tricount_proxy.urls")),
]
