from django import forms
from django.utils import timezone
from .models import Velo, Client, Location


class VeloForm(forms.ModelForm):
    class Meta:
        model = Velo
        fields = ['numero_cadre', 'modele', 'type', 'prix_heure', 'disponible', 'description']
        widgets = {
            'numero_cadre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: VTT-001'}),
            'modele': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Trek Marlin 5'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'prix_heure': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.50', 'min': '0'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'numero_cadre': 'Numéro de cadre',
            'modele': 'Modèle',
            'type': 'Type de vélo',
            'prix_heure': 'Prix par heure (€)',
            'disponible': 'Disponible à la location',
            'description': 'Description',
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'telephone', 'email']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de famille'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '06 XX XX XX XX'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
        }
        labels = {
            'nom': 'Nom',
            'prenom': 'Prénom',
            'telephone': 'Téléphone',
            'email': 'Email',
        }

    def clean_telephone(self):
        telephone = self.cleaned_data.get('telephone', '')
        # Remove common separators for validation
        cleaned_tel = telephone.replace(' ', '').replace('-', '').replace('.', '')
        
        import re
        if not re.match(r'^\+?[0-9]{8,15}$', cleaned_tel):
            raise forms.ValidationError("Veuillez entrer un numéro de téléphone valide avec ou sans indicatif (ex: +33612345678 ou 0612345678).")
        
        return telephone


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['velo', 'client', 'duree', 'duree_unite', 'date_location', 'date_retour', 'statut', 'notes']
        widgets = {
            'velo': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'duree': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '1.0'}),
            'duree_unite': forms.Select(attrs={'class': 'form-select'}),
            'date_location': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'date_retour': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'velo': 'Vélo',
            'client': 'Client',
            'duree': 'Durée',
            'duree_unite': 'Unité',
            'date_location': 'Date de location',
            'date_retour': 'Date de retour prévue',
            'statut': 'Statut',
            'notes': 'Notes',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_location'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['date_retour'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['date_retour'].required = False
        self.fields['notes'].required = False
        # Only show available bikes for new locations
        if not self.instance.pk:
            self.fields['velo'].queryset = Velo.objects.filter(disponible=True)


class LocationFilterForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Recherche client',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom ou prénom du client...'
        })
    )
    velo = forms.ModelChoiceField(
        queryset=Velo.objects.all(),
        required=False,
        label='Vélo',
        empty_label='Tous les vélos',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date = forms.DateField(
        required=False,
        label='Date',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    statut = forms.ChoiceField(
        required=False,
        label='Statut',
        choices=[('', 'Tous les statuts')] + Location.STATUT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
