import uuid

from django.http import JsonResponse
from django.views import View

from atlas.models import Entity, DomainId

class SearchEntityView(View):
    def get(self, request):
        entities = self._get_entities(request)
        results = serialize_entities(entities, include_related=True)
        data = {
            'results': results
        }
        return JsonResponse(data)

    def _get_entities(self, request):
        entities = Entity.objects.all().prefetch_related(
            'domain_ids', 'language_names', 'children')

        name = request.GET.get('name')
        if name:
            entities = entities.filter(name__icontains=name)

        return entities[:100]


class GetEntityView(View):
    def get(self, request):
        try:
            entity = self._get_entity(request)
        except Entity.DoesNotExist:
            return JsonResponse({}, status=404)

        data = serialize_entity(entity, include_related=True)
        return JsonResponse(data)

    def _get_entity(self, request):
        query_id = request.GET.get('id')

        query_identifier = request.GET.get('identifier')
        query_domain = request.GET.get('domain')

        if query_id:
            return self._get_by_uuid(query_id)
        elif query_identifier and query_domain:
            return self._get_by_domain_id(query_identifier, query_domain)
        else:
            raise Entity.DoesNotExist()

    def _get_by_uuid(self, query_id):
        if not is_valid_uuid(query_id):
            raise Entity.DoesNotExist()
        return Entity.objects.get(id=query_id)

    def _get_by_domain_id(self, identifier, domain):
        return Entity.get_by_domain_id(identifier, domain)


def is_valid_uuid(value):
    try:
        uuid.UUID(value)
    except ValueError:
        return False

    return True


def serialize_entities(entities, include_related=False):
    return [serialize_entity(entity, include_related=include_related)
            for entity in entities]


def serialize_entity(entity, include_related=False):
    domain_ids = entity.domain_ids.all()
    language_names = entity.language_names.all()
    data = {
        'id': str(entity.id),
        'type': entity.type,
        'name': entity.name,
        'latitude': entity.latitude,
        'longitude': entity.longitude,
        'domain_ids': {domain_id.domain: domain_id.identifier for domain_id in domain_ids},
        'language_names': {name.language: name.name for name in language_names},
    }

    if include_related:
        children = entity.children.all()
        parents = entity.parents.all()
        data['parents'] = serialize_entities(parents)
        data['children'] = serialize_entities(children)

    return data

