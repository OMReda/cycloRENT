from django.db import models
from django.utils import timezone
from decimal import Decimal


class Velo(models.Model):
    TYPE_CHOICES = [
        ('VTT', 'VTT'),
        ('Electrique', 'Électrique'),
        ('Ville', 'Ville'),
    ]

    numero_cadre = models.CharField(max_length=50, unique=True, verbose_name="Numéro de cadre")
    modele = models.CharField(max_length=100, verbose_name="Modèle")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type")
    prix_heure = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Prix/heure (€)")
    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Vélo"
        verbose_name_plural = "Vélos"
        ordering = ['modele']

    def __str__(self):
        return f"{self.modele} ({self.type}) - {self.numero_cadre}"

    def get_type_badge(self):
        badges = {
            'VTT': 'success',
            'Electrique': 'warning',
            'Ville': 'info',
        }
        return badges.get(self.type, 'secondary')

    def get_type_icon(self):
        icons = {
            'VTT': 'mountain',
            'Electrique': 'zap',
            'Ville': 'building',
        }
        return icons.get(self.type, 'bike')


class Client(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(unique=True, verbose_name="Email")
    date_inscription = models.DateField(auto_now_add=True, verbose_name="Date d'inscription")

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def get_nb_locations(self):
        return self.location_set.count()

    def get_total_depenses(self):
        total = self.location_set.exclude(statut='annulee').aggregate(total=models.Sum('prix_total'))['total']
        return total or Decimal('0.00')


class Location(models.Model):
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]

    DUREE_UNITE_CHOICES = [
        ('heures', 'Heures'),
        ('jours', 'Jours (8h)'),
    ]

    velo = models.ForeignKey(Velo, on_delete=models.PROTECT, verbose_name="Vélo")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="Client")
    duree = models.DecimalField(max_digits=6, decimal_places=1, verbose_name="Durée")
    duree_unite = models.CharField(
        max_length=10,
        choices=DUREE_UNITE_CHOICES,
        default='heures',
        verbose_name="Unité de durée"
    )
    prix_total = models.DecimalField(
        max_digits=8, decimal_places=2,
        verbose_name="Prix total (€)",
        blank=True, null=True
    )
    date_location = models.DateTimeField(default=timezone.now, verbose_name="Date de location")
    date_retour = models.DateTimeField(null=True, blank=True, verbose_name="Date de retour prévue")
    statut = models.CharField(
        max_length=15,
        choices=STATUT_CHOICES,
        default='en_cours',
        verbose_name="Statut"
    )
    notes = models.TextField(blank=True, verbose_name="Notes")

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ['-date_location']

    def __str__(self):
        return f"Location #{self.pk} - {self.client} / {self.velo.modele} ({self.date_location.strftime('%d/%m/%Y')})"

    def calculate_prix_total(self):
        if self.duree_unite == 'jours':
            heures = self.duree * 8  # 8h par jour
        else:
            heures = self.duree
        return round(Decimal(str(heures)) * self.velo.prix_heure, 2)

    def save(self, *args, **kwargs):
        # Auto-calculate prix_total if not set
        if not self.prix_total:
            self.prix_total = self.calculate_prix_total()

        # Update velo availability
        if self.statut == 'en_cours':
            self.velo.disponible = False
            self.velo.save()
        elif self.statut in ['terminee', 'annulee']:
            # Check no other active location for this velo
            other_active = Location.objects.filter(
                velo=self.velo, statut='en_cours'
            ).exclude(pk=self.pk).exists()
            if not other_active:
                self.velo.disponible = True
                self.velo.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        velo = self.velo
        super().delete(*args, **kwargs)
        # Check no other active location for this velo
        other_active = Location.objects.filter(
            velo=velo, statut='en_cours'
        ).exists()
        if not other_active:
            velo.disponible = True
            velo.save()

    def get_statut_badge(self):
        badges = {
            'en_cours': 'primary',
            'terminee': 'success',
            'annulee': 'danger',
        }
        return badges.get(self.statut, 'secondary')

    def get_statut_icon(self):
        icons = {
            'en_cours': 'clock',
            'terminee': 'check-circle',
            'annulee': 'x-circle',
        }
        return icons.get(self.statut, 'help-circle')

    def get_duree_display_full(self):
        unite = "heure(s)" if self.duree_unite == 'heures' else "jour(s)"
        return f"{self.duree} {unite}"
