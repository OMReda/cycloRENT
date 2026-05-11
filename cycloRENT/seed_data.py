# -*- coding: utf-8 -*-
"""
Script de peuplement CycloRent - donnees de demonstration.
Executer avec : python seed_data.py
"""
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cyclorent.settings')

import django
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from location.models import Velo, Client, Location

print("[*] Initialisation des donnees CycloRent...")

# ── SUPERUSER ──────────────────────────────────────────────────────────────────
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@cyclorent.fr', 'admin1234')
    print("[OK] Superuser cree : admin / admin1234")
else:
    print("[--] Superuser 'admin' existe deja")

if not User.objects.filter(username='employe').exists():
    User.objects.create_user(
        'employe', 'employe@cyclorent.fr', 'employe1234',
        first_name='Jean', last_name='Dupont'
    )
    print("[OK] Employe cree : employe / employe1234")
else:
    print("[--] Employe 'employe' existe deja")

# ── VELOS ──────────────────────────────────────────────────────────────────────
velos_data = [
    {'numero_cadre': 'VTT-001', 'modele': 'Trek Marlin 5',          'type': 'VTT',       'prix_heure': Decimal('4.50'), 'description': 'VTT tout-terrain, parfait pour les sentiers.'},
    {'numero_cadre': 'VTT-002', 'modele': 'Cube Analog',            'type': 'VTT',       'prix_heure': Decimal('5.00'), 'description': 'VTT robuste, cadre aluminium.'},
    {'numero_cadre': 'VTT-003', 'modele': 'Giant Talon 3',          'type': 'VTT',       'prix_heure': Decimal('4.00'), 'description': 'VTT entree de gamme fiable.'},
    {'numero_cadre': 'ELEC-001','modele': 'Specialized Turbo Vado', 'type': 'Electrique','prix_heure': Decimal('8.00'), 'description': 'VAE puissant, autonomie 80 km.'},
    {'numero_cadre': 'ELEC-002','modele': 'Decathlon E-STILUS',     'type': 'Electrique','prix_heure': Decimal('6.50'), 'description': 'VAE polyvalent, ideal ville et campagne.'},
    {'numero_cadre': 'ELEC-003','modele': 'Trek Allant+ 7',         'type': 'Electrique','prix_heure': Decimal('9.00'), 'description': 'VAE premium avec assistance puissante.'},
    {'numero_cadre': 'VILLE-001','modele': 'Peugeot LC01',          'type': 'Ville',     'prix_heure': Decimal('3.00'), 'description': 'Velo de ville classique, confortable.'},
    {'numero_cadre': 'VILLE-002','modele': 'Btwin Elops 520',       'type': 'Ville',     'prix_heure': Decimal('2.50'), 'description': 'Parfait pour les deplacements urbains.'},
    {'numero_cadre': 'VILLE-003','modele': 'Lapierre Urban 200',    'type': 'Ville',     'prix_heure': Decimal('3.50'), 'description': 'Velo urbain elegant avec porte-bagages.'},
]

velos = []
for data in velos_data:
    velo, created = Velo.objects.get_or_create(
        numero_cadre=data['numero_cadre'], defaults=data
    )
    velos.append(velo)
    status = "[+]" if created else "[-]"
    print(f"  {status} Velo : {velo.modele} ({velo.type})")

# ── CLIENTS ────────────────────────────────────────────────────────────────────
clients_data = [
    {'nom': 'Martin',  'prenom': 'Alice',   'telephone': '06 12 34 56 78', 'email': 'alice.martin@email.fr'},
    {'nom': 'Bernard', 'prenom': 'Thomas',  'telephone': '06 23 45 67 89', 'email': 'thomas.bernard@email.fr'},
    {'nom': 'Petit',   'prenom': 'Sophie',  'telephone': '07 34 56 78 90', 'email': 'sophie.petit@email.fr'},
    {'nom': 'Moreau',  'prenom': 'Lucas',   'telephone': '06 45 67 89 01', 'email': 'lucas.moreau@email.fr'},
    {'nom': 'Dubois',  'prenom': 'Camille', 'telephone': '07 56 78 90 12', 'email': 'camille.dubois@email.fr'},
    {'nom': 'Laurent', 'prenom': 'Hugo',    'telephone': '06 67 89 01 23', 'email': 'hugo.laurent@email.fr'},
    {'nom': 'Simon',   'prenom': 'Emma',    'telephone': '07 78 90 12 34', 'email': 'emma.simon@email.fr'},
    {'nom': 'Michel',  'prenom': 'Romain',  'telephone': '06 89 01 23 45', 'email': 'romain.michel@email.fr'},
]

clients = []
for data in clients_data:
    client, created = Client.objects.get_or_create(
        email=data['email'], defaults=data
    )
    clients.append(client)
    status = "[+]" if created else "[-]"
    print(f"  {status} Client : {client.prenom} {client.nom}")

# ── LOCATIONS ──────────────────────────────────────────────────────────────────
now = timezone.now()

locations_data = [
    # Locations terminees (historique)
    {'velo': velos[6], 'client': clients[0], 'duree': Decimal('3'), 'duree_unite': 'heures',
     'date_location': now - timedelta(days=20), 'statut': 'terminee'},
    {'velo': velos[3], 'client': clients[1], 'duree': Decimal('1'), 'duree_unite': 'jours',
     'date_location': now - timedelta(days=15), 'statut': 'terminee'},
    {'velo': velos[0], 'client': clients[2], 'duree': Decimal('4'), 'duree_unite': 'heures',
     'date_location': now - timedelta(days=12), 'statut': 'terminee'},
    {'velo': velos[7], 'client': clients[3], 'duree': Decimal('2'), 'duree_unite': 'heures',
     'date_location': now - timedelta(days=10), 'statut': 'terminee'},
    {'velo': velos[4], 'client': clients[4], 'duree': Decimal('2'), 'duree_unite': 'jours',
     'date_location': now - timedelta(days=8), 'statut': 'terminee'},
    {'velo': velos[1], 'client': clients[0], 'duree': Decimal('5'), 'duree_unite': 'heures',
     'date_location': now - timedelta(days=7), 'statut': 'terminee'},
    {'velo': velos[5], 'client': clients[5], 'duree': Decimal('1'), 'duree_unite': 'jours',
     'date_location': now - timedelta(days=5), 'statut': 'terminee'},
    {'velo': velos[2], 'client': clients[6], 'duree': Decimal('3'), 'duree_unite': 'heures',
     'date_location': now - timedelta(days=4), 'statut': 'terminee'},
    {'velo': velos[8], 'client': clients[7], 'duree': Decimal('2'), 'duree_unite': 'heures',
     'date_location': now - timedelta(days=3), 'statut': 'terminee'},
    {'velo': velos[3], 'client': clients[2], 'duree': Decimal('1'), 'duree_unite': 'jours',
     'date_location': now - timedelta(days=2), 'statut': 'terminee'},
    # Locations du jour (en cours)
    {'velo': velos[0], 'client': clients[1], 'duree': Decimal('3'), 'duree_unite': 'heures',
     'date_location': now - timedelta(hours=2), 'statut': 'en_cours'},
    {'velo': velos[4], 'client': clients[3], 'duree': Decimal('4'), 'duree_unite': 'heures',
     'date_location': now - timedelta(hours=1), 'statut': 'en_cours'},
]

for data in locations_data:
    exists = Location.objects.filter(
        velo=data['velo'],
        client=data['client'],
        statut=data['statut']
    ).exists()
    if not exists:
        loc = Location(
            velo=data['velo'],
            client=data['client'],
            duree=data['duree'],
            duree_unite=data['duree_unite'],
            date_location=data['date_location'],
            statut=data['statut'],
        )
        loc.prix_total = loc.calculate_prix_total()
        # Save directly to DB bypassing custom save() to avoid availability conflicts
        from django.db import connection
        loc.save_base(raw=True)
        print(f"  [+] Location : {loc.client} -> {loc.velo.modele} | {loc.prix_total} EUR | {loc.statut}")

# Fix velo availability based on active locations
for velo in velos:
    has_active = Location.objects.filter(velo=velo, statut='en_cours').exists()
    Velo.objects.filter(pk=velo.pk).update(disponible=not has_active)

print("")
print("[DONE] Base de donnees initialisee avec succes !")
print("=" * 45)
print(f"  Velos     : {Velo.objects.count()}")
print(f"  Clients   : {Client.objects.count()}")
print(f"  Locations : {Location.objects.count()}")
print("=" * 45)
print("  Admin    : admin / admin1234")
print("  Employe  : employe / employe1234")
print("  Serveur  : http://127.0.0.1:8000/")
