from django.urls import path
from GEEMAP import views

urlpatterns = [
    path('', views.map.as_view(), name = 'map'),
    path('registeruser/', views.register_user, name = 'registration'),
    path('configurate/polygon', views.polygon, name='polygon'),
    path('configurate/point', views.point, name='point'),
]