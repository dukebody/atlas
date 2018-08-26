from atlas.views import SearchEntityView, GetEntityView

from django.urls import path

urlpatterns = [
    path('search/', SearchEntityView.as_view(), name='search'),
    path('get/', GetEntityView.as_view(), name='get')
]
