# -*- coding: utf-8 -*-
import csv
import os
from collections import defaultdict

import six
from django.core.management.base import BaseCommand

from atlas import models


DEFAULT_CSV = os.path.join(os.path.dirname(__file__), '..', '..',
                           'data', 'european-train-stations.csv')


# column - domain
DOMAINS = {
    'id': 'euro',
    'uic': 'uic',
    'sncf_id': 'sncf',
    'db_id': 'db',
    'busbud_id': 'busbud',
    'trenitalia_id': 'trenitalia',
    'ntv_id': 'ntv',
    'hkx_id': 'hkx',
    'renfe_id': 'renfe',
    'atoc_id': 'atoc',
    'benerail_id': 'benerail'
}


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--csv_file',
            action='store',
            dest='csv_file',
            default=DEFAULT_CSV,
            help='CSV file: path to file containing records'
        )

    def handle(self, *args, **options):
        hierarchy = defaultdict(list)
        with open(options['csv_file'], 'r') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=';')
            fieldnames = reader.fieldnames

            language_fields = [f for f in fieldnames if 'info:' in f]

            for row in reader:
                latitude, longitude = self._unpack_latlong(row['latlong'])
                entity = models.Entity.objects.create(
                    name=row['name'],
                    type=self._get_type(row['is_city']),
                    latitude=latitude,
                    longitude=longitude
                )
                domain_ids = []
                for domain_column, domain in DOMAINS.items():
                    if row[domain_column]:
                        domain_id = models.DomainId(
                                identifier=row[domain_column],
                                domain=domain,
                                entity=entity)

                        domain_ids.append(domain_id)

                models.DomainId.objects.bulk_create(domain_ids)

                language_names = []
                for language_field in language_fields:
                    if row[language_field]:
                        language = language_field[-2:]
                        language_name = models.LanguageName(
                            language=language,
                            name=row[language_field],
                            entity=entity)
                        language_names.append(language_name)

                models.LanguageName.objects.bulk_create(language_names)

                if row['parent_station_id']:
                    parent_euro_id = row['parent_station_id']
                    hierarchy[parent_euro_id].append(entity)

        self._bind_parents_children(hierarchy)

    def _get_type(self, is_city):
        if is_city == 't':
            return 'city'

        return 'train_station'

    def _unpack_latlong(self, latlong):
        if latlong:
            lat, lon = latlong.split(',')
            return float(lat.strip()), float(lon.strip())
        return None, None

    def _bind_parents_children(self, hierarchy):
        for parent_euro_id, children in hierarchy.items():
            try:
                parent = models.Entity.get_by_domain_id(
                    identifier=parent_euro_id,
                    domain='euro')
            except models.Entity.DoesNotExist:
                continue

            parent.children.set(children)
