# ordered online locations service

This django based micro service manages all location (i.e., bars, restaurants, ...) related tasks.

## Technology Stack

- Python 3
- Django

## Quickstart

Make sure, that Python 3 and Django are installed. Run the server.

```
$ cd locations
$ python3 manage.py migrate
$ python3 manage.py runserver 127.0.0.1:8001
```

If you want to prepopulate your database with some examples, run:

```
$ python3 manage.py load_data
```

## Admin panel

The admin panel is accessible to a superuser via `/locations/admin/`
