# Atlas project

Proof of concept of a system to store and query geopolitical entities with multiple domain ids. The idea is to have a database of entities we know about with a mapping to the id of these entities in different provider domains.

# Install

Create a Python 3 virtualenv and:
```
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Test with:
```
pytest
```

A script to load a [European database of train stations](https://public.opendatasoft.com/explore/dataset/european-train-stations/) is provided. Takes about 3 minutes to load in my laptop:
```
python manage.py load_european_train_stations
```

## Endpoints

- `/search/?name=something` : Search for entities whose name contains the given string.
- `/get/?id=some-uuid` : Get the entity with the given id or 404.
- `/get/?identifier=some-identifier&domain=some-domain` : Get the entity with the given identifier in the given domain or 404.

Example:
```
GET /get/?identifier=ESMCH&domain=sncf

{
  "type": "train_station",
  "name": "Madrid Chamartín",
  "children": [],
  "longitude": -3.68235,
  "domain_ids": {
    "sncf": "ESMCH",
    "benerail": "ESMCH",
    "euro": "6668",
    "renfe": "17000",
    "uic": "7117000",
    "db": "7100017"
  },
  "language_names": {
    "zh": "馬德里",
    "ko": "마드리드",
    "ja": "マドリード市",
    "ru": "Мадрид",
    "pl": "Madryt"
  },
  "latitude": 40.472151,
  "parents": [
    {
      "type": "city",
      "name": "Madrid",
      "longitude": -3.703733,
      "domain_ids": {
        "sncf": "ESMAD",
        "euro": "6663",
        "busbud": "ezjmgt"
      },
      "language_names": {
        "zh": "馬德里",
        "ko": "마드리드",
        "ja": "マドリード市",
        "ru": "Мадрид",
        "pl": "Madryt"
      },
      "latitude": 40.416824,
      "id": "60b159e3-4998-4e28-93d2-2620eb1b62bc"
    }
  ],
  "id": "65e3920c-c144-4565-ac66-bfc7f959de24"
}
```


## Design decisions
- Domains and languages are in separate tables to allow adding new domains and languages without rewriting the whole entities table. Additionally, this makes a more efficient use of space since most entities don't have ids in all domains (sparsity).

- Parents/children relationships are also in a separate table so an entity can have multiple parents of different types.