from django.contrib import admin
from .models import Velo, Client, Location


@admin.register(Velo)
class VeloAdmin(admin.ModelAdmin):
    list_display = ['modele', 'numero_cadre', 'type', 'prix_heure', 'disponible']
    list_filter = ['type', 'disponible']
    search_fields = ['modele', 'numero_cadre']
    list_editable = ['prix_heure', 'disponible']
    ordering = ['modele']
    fieldsets = (
        ('Informations générales', {
            'fields': ('numero_cadre', 'modele', 'type', 'description')
        }),
        ('Tarification & Disponibilité', {
            'fields': ('prix_heure', 'disponible')
        }),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'email', 'telephone', 'date_inscription', 'get_nb_locations']
    search_fields = ['nom', 'prenom', 'email', 'telephone']
    ordering = ['nom', 'prenom']
    readonly_fields = ['date_inscription']

    def get_nb_locations(self, obj):
        return obj.get_nb_locations()
    get_nb_locations.short_description = 'Nb locations'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'velo', 'duree', 'duree_unite', 'prix_total', 'date_location', 'statut']
    list_filter = ['statut', 'duree_unite', 'velo__type', 'date_location']
    search_fields = ['client__nom', 'client__prenom', 'velo__modele', 'velo__numero_cadre']
    list_editable = ['statut']
    ordering = ['-date_location']
    date_hierarchy = 'date_location'
    readonly_fields = ['prix_total']
    autocomplete_fields = ['client', 'velo']

    fieldsets = (
        ('Location', {
            'fields': ('velo', 'client', 'statut')
        }),
        ('Durée & Prix', {
            'fields': ('duree', 'duree_unite', 'prix_total')
        }),
        ('Dates', {
            'fields': ('date_location', 'date_retour')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('velo', 'client')


# Customize admin site
admin.site.site_header = '🚲 CycloRent Administration'
admin.site.site_title = 'CycloRent Admin'
admin.site.index_title = 'Tableau de bord administrateur'
