# -*- coding: utf-8 -*-
import os
import json
from uuid import uuid4

from django.test import TestCase
from django.core.management import call_command

from atlas.models import Entity, DomainId, LanguageName
from atlas.views import serialize_entity


class SearchEntityTests(TestCase):
    def test_no_query_shows_all(self):
        Entity.objects.create(type='city', name='Madrid')
        Entity.objects.create(type='train_station',
                              name='Madrid Puerta de Atocha')
        response = self.client.get('/search/')
        data = load_json(response)

        assert len(data['results']) == 2

    def test_query_by_name_contains(self):
        Entity.objects.create(type='city', name='Madrid')

        response = self.client.get('/search/?name=a')
        data = load_json(response)
        assert len(data['results']) == 1

        response = self.client.get('/search/?name=j')
        data = load_json(response)
        assert len(data['results']) == 0


class GetEntityTests(TestCase):
    def test_get_by_id_found(self):
        entity = Entity.objects.create(type='city', name='Madrid')

        response = self.client.get('/get/?id={}'.format(entity.id))

        assert response.status_code == 200

        data = load_json(response)
        assert data['id'] == str(entity.id)

    def test_get_by_id_not_found(self):
        uuid = uuid4()
        response = self.client.get('/get/?id={}'.format(uuid))

        assert response.status_code == 404

    def test_get_by_id_malformed(self):
        response = self.client.get('/get/?id=not-an-uuid')

        assert response.status_code == 404

    def test_get_by_identifier_domain(self):
        entity = Entity.objects.create(type='city', name='Madrid')
        DomainId.objects.create(entity=entity, domain='iata',
                                            identifier='MAD')

        response = self.client.get('/get/?identifier=MAD&domain=iata')

        assert response.status_code == 200

        data = load_json(response)
        assert data['id'] == str(entity.id)

    def test_get_by_identifier_domain_notfound(self):
        response = self.client.get('/get/?identifier=MAD&domain=iata')

        assert response.status_code == 404


def load_json(response):
    return json.loads(response.content.decode('utf-8'))


class TestEntitySerializer(TestCase):
    def test_domain_ids_included(self):
        entity = Entity.objects.create(type='city', name='Madrid')
        DomainId.objects.create(entity=entity, domain='iata',
                                            identifier='MAD')
        DomainId.objects.create(entity=entity, domain='mydomain',
                                            identifier='4211')
        data = serialize_entity(entity)

        assert data['domain_ids'] == {
            'iata': 'MAD',
            'mydomain': '4211'
        }

    def test_language_names_included(self):
        entity = Entity.objects.create(type='city', name='London')
        LanguageName.objects.create(entity=entity, language='es',
                                            name='Londres')
        LanguageName.objects.create(entity=entity, language='it',
                                            name='Londra')
        data = serialize_entity(entity)

        assert data['language_names'] == {
            'es': 'Londres',
            'it': 'Londra'
        }

    def test_children_included(self):
        city = Entity.objects.create(type='city', name='London')
        station = Entity.objects.create(type='train_station', name='London St Pancras')
        city.children.set([station])

        data = serialize_entity(city, include_related=True)

        assert len(data['children']) == 1
        assert data['children'][0]['id'] == str(station.id)

    def test_parents_included(self):
        city = Entity.objects.create(type='city', name='London')
        station = Entity.objects.create(type='train_station', name='London St Pancras')
        city.children.set([station])

        data = serialize_entity(station, include_related=True)

        assert len(data['parents']) == 1
        assert data['parents'][0]['id'] == str(city.id)


test_csv_stations = os.path.join(os.path.dirname(__file__), 'data', 'european-train-stations-test.csv')

class LoadEuropeanTrainStationsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        call_command('load_european_train_stations', csv_file=test_csv_stations)
        super().setUpClass()

    def test_load_count(self):
        assert Entity.objects.count() == 1961

    def test_latitude_longitude(self):
        atocha = Entity.objects.get(name='Madrid Atocha')

        assert atocha.latitude == 40.405963
        assert atocha.longitude == -3.689757

    def test_type(self):
        atocha = Entity.objects.get(name='Madrid Atocha')
        assert atocha.type == 'train_station'

        madrid = Entity.objects.get(name='Madrid')
        assert madrid.type == 'city'

    def test_domain_ids(self):
        atocha = Entity.objects.get(name='Madrid Atocha')
        assert DomainId.objects.filter(
            identifier='7160000', domain='uic', entity=atocha).exists()
        assert DomainId.objects.filter(
            identifier='60000', domain='renfe', entity=atocha).exists()
        assert DomainId.objects.filter(
            identifier='ESMAT', domain='sncf', entity=atocha).exists()
        assert DomainId.objects.filter(
            identifier='7100049', domain='db', entity=atocha).exists()
        assert DomainId.objects.filter(
            identifier='6667', domain='euro', entity=atocha).exists()

    def test_language_names(self):
        atocha = Entity.objects.get(name='Madrid Atocha')
        assert LanguageName.objects.filter(
            name='マドリード市', language='ja', entity=atocha).exists()
        assert LanguageName.objects.filter(
            name='마드리드', language='ko', entity=atocha).exists()
        assert LanguageName.objects.filter(
            name='Madryt', language='pl', entity=atocha).exists()
        assert LanguageName.objects.filter(
            name='Мадрид', language='ru', entity=atocha).exists()
        assert LanguageName.objects.filter(
            name='馬德里', language='zh', entity=atocha).exists()

    def test_children(self):
        atocha = Entity.objects.get(name='Madrid Atocha')
        madrid = Entity.objects.get(name='Madrid')

        assert atocha in madrid.children.all()
