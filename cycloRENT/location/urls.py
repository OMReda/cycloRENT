from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Vélos
    path('velos/', views.velo_list, name='velo_list'),
    path('velos/ajouter/', views.velo_create, name='velo_create'),
    path('velos/<int:pk>/modifier/', views.velo_edit, name='velo_edit'),
    path('velos/<int:pk>/supprimer/', views.velo_delete, name='velo_delete'),

    # Clients
    path('clients/', views.client_list, name='client_list'),
    path('clients/ajouter/', views.client_create, name='client_create'),
    path('clients/<int:pk>/', views.client_detail, name='client_detail'),
    path('clients/<int:pk>/modifier/', views.client_edit, name='client_edit'),
    path('clients/<int:pk>/supprimer/', views.client_delete, name='client_delete'),

    # Locations
    path('locations/', views.location_list, name='location_list'),
    path('locations/nouvelle/', views.location_create, name='location_create'),
    path('locations/<int:pk>/modifier/', views.location_edit, name='location_edit'),
    path('locations/<int:pk>/supprimer/', views.location_delete, name='location_delete'),
    path('locations/<int:pk>/terminer/', views.location_terminer, name='location_terminer'),

    # Statistiques
    path('statistiques/', views.statistiques, name='statistiques'),

    # API
    path('api/calcul-prix/', views.api_calcul_prix, name='api_calcul_prix'),
]
