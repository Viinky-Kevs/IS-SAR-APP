from django.urls import path
from GEEMAP import views

urlpatterns = [
    path('', views.map.as_view(), name = 'map'),
    path('registeruser/', views.register_user, name = 'registration'),
    path('configurate/polygon', views.polygon, name='polygon'),
    path('configurate/polygon/manual', views.polygon2, name='polygon2'),
    path('configurate/point', views.save_polygon, name='point'),
    path('configurate/upload', views.upload, name='upload'),
    path('configurate/upload/KMZ-SHP', views.Config_up, name='configurate'),
]