from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta, date
from decimal import Decimal
import json

from .models import Velo, Client, Location
from .forms import VeloForm, ClientForm, LocationForm, LocationFilterForm


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Stats générales
    total_velos = Velo.objects.count()
    velos_disponibles = Velo.objects.filter(disponible=True).count()
    total_clients = Client.objects.count()

    # Locations du jour
    locations_today = Location.objects.filter(
        date_location__date=today
    ).select_related('velo', 'client')

    locations_en_cours = Location.objects.filter(
        statut='en_cours'
    ).select_related('velo', 'client')

    # CA du jour
    ca_today = Location.objects.filter(
        date_location__date=today
    ).exclude(statut='annulee').aggregate(total=Sum('prix_total'))['total'] or Decimal('0.00')

    # CA du mois
    ca_month = Location.objects.filter(
        date_location__date__gte=month_start
    ).exclude(statut='annulee').aggregate(total=Sum('prix_total'))['total'] or Decimal('0.00')

    # CA total
    ca_total = Location.objects.exclude(statut='annulee').aggregate(total=Sum('prix_total'))['total'] or Decimal('0.00')

    # Dernières locations
    recent_locations = Location.objects.select_related('velo', 'client').order_by('-date_location')[:8]

    # Graphique CA 7 derniers jours
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        ca = Location.objects.filter(
            date_location__date=day
        ).exclude(statut='annulee').aggregate(total=Sum('prix_total'))['total'] or 0
        chart_labels.append(day.strftime('%d/%m'))
        chart_data.append(float(ca))

    # Répartition par type de vélo
    type_stats = Location.objects.exclude(statut='annulee').values('velo__type').annotate(
        total=Sum('prix_total'), count=Count('id')
    ).order_by('-total')

    context = {
        'total_velos': total_velos,
        'velos_disponibles': velos_disponibles,
        'velos_loues': total_velos - velos_disponibles,
        'total_clients': total_clients,
        'locations_today': locations_today,
        'locations_en_cours': locations_en_cours[:2],
        'nb_en_cours': locations_en_cours.count(),
        'ca_today': ca_today,
        'ca_month': ca_month,
        'ca_total': ca_total,
        'recent_locations': recent_locations,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'type_stats': type_stats,
        'today': today,
    }
    return render(request, 'location/dashboard.html', context)


# ─── VÉLOS ────────────────────────────────────────────────────────────────────

@login_required
def velo_list(request):
    velos = Velo.objects.all()
    type_filter = request.GET.get('type', '')
    dispo_filter = request.GET.get('disponible', '')
    q = request.GET.get('q', '')

    if type_filter:
        velos = velos.filter(type=type_filter)
    if dispo_filter == '1':
        velos = velos.filter(disponible=True)
    elif dispo_filter == '0':
        velos = velos.filter(disponible=False)
    if q:
        velos = velos.filter(Q(modele__icontains=q) | Q(numero_cadre__icontains=q))

    context = {
        'velos': velos,
        'type_filter': type_filter,
        'dispo_filter': dispo_filter,
        'q': q,
        'type_choices': Velo.TYPE_CHOICES,
    }
    return render(request, 'location/velo_list.html', context)


@login_required
def velo_create(request):
    if request.method == 'POST':
        form = VeloForm(request.POST)
        if form.is_valid():
            velo = form.save()
            messages.success(request, f'Vélo « {velo.modele} » ajouté avec succès !')
            return redirect('velo_list')
    else:
        form = VeloForm()
    return render(request, 'location/velo_form.html', {'form': form, 'action': 'Ajouter'})


@login_required
def velo_edit(request, pk):
    velo = get_object_or_404(Velo, pk=pk)
    if request.method == 'POST':
        form = VeloForm(request.POST, instance=velo)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vélo « {velo.modele} » mis à jour !')
            return redirect('velo_list')
    else:
        form = VeloForm(instance=velo)
    return render(request, 'location/velo_form.html', {'form': form, 'action': 'Modifier', 'velo': velo})


@login_required
def velo_delete(request, pk):
    velo = get_object_or_404(Velo, pk=pk)
    if request.method == 'POST':
        nom = str(velo)
        try:
            velo.delete()
            messages.warning(request, f'Vélo « {nom} » supprimé.')
        except ProtectedError:
            messages.error(request, f'Impossible de supprimer ce vélo : il est lié à des locations existantes.')
        return redirect('velo_list')
    return render(request, 'location/confirm_delete.html', {'object': velo, 'type': 'vélo'})


# ─── CLIENTS ──────────────────────────────────────────────────────────────────

@login_required
def client_list(request):
    clients = Client.objects.all()
    q = request.GET.get('q', '')
    if q:
        clients = clients.filter(
            Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(email__icontains=q)
        )
    clients = clients.annotate(nb_locations=Count('location'))
    context = {'clients': clients, 'q': q}
    return render(request, 'location/client_list.html', context)


@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Client « {client} » créé avec succès !')
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'location/client_form.html', {'form': form, 'action': 'Ajouter'})


@login_required
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f'Client « {client} » mis à jour !')
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)
    return render(request, 'location/client_form.html', {'form': form, 'action': 'Modifier', 'client': client})


@login_required
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        nom = str(client)
        try:
            client.delete()
            messages.warning(request, f'Client « {nom} » supprimé.')
        except ProtectedError:
            messages.error(request, f'Impossible de supprimer ce client : il a des locations enregistrées.')
        return redirect('client_list')
    return render(request, 'location/confirm_delete.html', {'object': client, 'type': 'client'})


@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    locations = client.location_set.select_related('velo').order_by('-date_location')
    context = {
        'client': client,
        'locations': locations,
        'total_depenses': client.get_total_depenses(),
    }
    return render(request, 'location/client_detail.html', context)


# ─── LOCATIONS ────────────────────────────────────────────────────────────────

@login_required
def location_list(request):
    locations = Location.objects.select_related('velo', 'client').all()
    form = LocationFilterForm(request.GET)

    if form.is_valid():
        q = form.cleaned_data.get('q')
        velo = form.cleaned_data.get('velo')
        date = form.cleaned_data.get('date')
        statut = form.cleaned_data.get('statut')

        if q:
            locations = locations.filter(
                Q(client__nom__icontains=q) | Q(client__prenom__icontains=q)
            )
        if velo:
            locations = locations.filter(velo=velo)
        if date:
            locations = locations.filter(date_location__date=date)
        if statut:
            locations = locations.filter(statut=statut)

    ca_total = locations.exclude(statut='annulee').aggregate(total=Sum('prix_total'))['total'] or Decimal('0.00')
    context = {
        'locations': locations,
        'filter_form': form,
        'ca_total': ca_total,
    }
    return render(request, 'location/location_list.html', context)


@login_required
def location_create(request):
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.prix_total = location.calculate_prix_total()
            location.save()
            messages.success(request, f'Location enregistrée ! Prix calculé : {location.prix_total} €')
            return redirect('location_list')
    else:
        form = LocationForm()
    return render(request, 'location/location_form.html', {'form': form, 'action': 'Ajouter location'})


@login_required
def location_edit(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance=location)
        if form.is_valid():
            loc = form.save(commit=False)
            loc.prix_total = loc.calculate_prix_total()
            loc.save()
            messages.success(request, f'Location #{pk} mise à jour !')
            return redirect('location_list')
    else:
        form = LocationForm(instance=location)
    return render(request, 'location/location_form.html', {
        'form': form, 'action': 'Modifier', 'location': location
    })


@login_required
def location_delete(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if request.method == 'POST':
        location.delete()
        messages.warning(request, f'Location #{pk} supprimée.')
        return redirect('location_list')
    return render(request, 'location/confirm_delete.html', {'object': location, 'type': 'location'})


@login_required
def location_terminer(request, pk):
    """Terminer rapidement une location en cours."""
    location = get_object_or_404(Location, pk=pk)
    if location.statut == 'en_cours':
        location.statut = 'terminee'
        location.date_retour = timezone.now()
        location.save()
        messages.success(request, f'Location #{pk} terminée. Vélo remis en disponibilité.')
    return redirect('location_list')


# ─── STATISTIQUES ─────────────────────────────────────────────────────────────

@login_required
def statistiques(request):
    today = timezone.now().date()

    # CA par mois (12 derniers mois) — precise month boundaries
    months_labels = []
    months_data = []
    current_month = today.replace(day=1)
    for i in range(11, -1, -1):
        # Calculate the correct month by rolling back month by month
        month_num = current_month.month - i
        year_offset = 0
        while month_num <= 0:
            month_num += 12
            year_offset -= 1
        month_start = date(current_month.year + year_offset, month_num, 1)
        if month_start.month == 12:
            month_end = date(month_start.year + 1, 1, 1)
        else:
            month_end = date(month_start.year, month_start.month + 1, 1)

        ca = Location.objects.filter(
            date_location__date__gte=month_start,
            date_location__date__lt=month_end,
        ).exclude(statut='annulee').aggregate(total=Sum('prix_total'))['total'] or 0

        months_labels.append(month_start.strftime('%b %Y'))
        months_data.append(float(ca))

    # Top 5 clients
    top_clients = Client.objects.annotate(
        total_depenses=Sum('location__prix_total', filter=~Q(location__statut='annulee')),
        nb_locations=Count('location', filter=~Q(location__statut='annulee'))
    ).filter(total_depenses__isnull=False).order_by('-total_depenses')[:5]

    # Stats par type de vélo
    type_stats = Location.objects.exclude(statut='annulee').values('velo__type').annotate(
        total=Sum('prix_total'),
        count=Count('id')
    ).order_by('-total')

    # Locations par statut
    statut_stats = list(Location.objects.values('statut').annotate(count=Count('id')))

    # CA mensuel actuel
    month_start_curr = today.replace(day=1)
    ca_month = Location.objects.filter(
        date_location__date__gte=month_start_curr
    ).exclude(statut='annulee').aggregate(total=Sum('prix_total'))['total'] or Decimal('0.00')

    # Locations terminées ce mois
    archived_month = Location.objects.filter(
        statut='terminee',
        date_location__date__gte=month_start_curr
    ).count()

    context = {
        'months_labels': months_labels,
        'months_data': months_data,
        'top_clients': top_clients,
        'type_stats': type_stats,
        'statut_stats': statut_stats,
        'ca_month': ca_month,
        'archived_month': archived_month,
        'today': today,
    }
    return render(request, 'location/statistiques.html', context)


# ─── API PRIX ─────────────────────────────────────────────────────────────────

@login_required
def api_calcul_prix(request):
    """AJAX: calculate price based on velo and duration."""
    velo_id = request.GET.get('velo_id')
    duree = request.GET.get('duree', 1)
    unite = request.GET.get('unite', 'heures')

    try:
        velo = Velo.objects.get(pk=velo_id)
        duree = float(duree)
        if unite == 'jours':
            heures = duree * 8
        else:
            heures = duree
        prix = round(heures * float(velo.prix_heure), 2)
        return JsonResponse({'prix': prix, 'prix_heure': float(velo.prix_heure)})
    except (Velo.DoesNotExist, ValueError):
        return JsonResponse({'prix': 0, 'prix_heure': 0})
