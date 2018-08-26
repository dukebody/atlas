# -*- coding: utf8 -*-
import uuid

from django.db import models

ENTITY_TYPE_CHOICES = (
    ('city', 'City'),
    ('train_station', 'Train Station'),
)

class Entity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=100, choices=ENTITY_TYPE_CHOICES)
    name = models.CharField(max_length=512)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    children = models.ManyToManyField('atlas.Entity', related_name='parents', blank=True)

    def __str__(self):
        return '{self.name} ({self.type})'.format(self=self)

    @classmethod
    def get_by_domain_id(cls, identifier, domain):
        try:
            domain_id = DomainId.objects.select_related('entity').get(identifier=identifier, domain=domain)
        except DomainId.DoesNotExist:
            raise Entity.DoesNotExist()

        return domain_id.entity



class DomainId(models.Model):
    """
    Identifier of an entity in a certain domain.

    For example, in the Renfe domain the Atocha station has id 39032.
    """
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='domain_ids')
    domain = models.CharField(max_length=100)
    identifier = models.CharField(max_length=100)

    def __str__(self):
        return '({self.entity_id}) {self.domain} - {self.identifier}'.format(
            self=self)


class LanguageName(models.Model):
    """
    Name of an entity in a certain language.

    For example, the country Spain in Spanish is named España.
    """
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name='language_names')
    language = models.CharField(max_length=10)
    name = models.CharField(max_length=100)

    def __str__(self):
        return '({self.entity_id}) {self.language} - {self.name}'.format(
            self=self)