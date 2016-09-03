## Install

In settings.py


    INSTALLED_APPS = [
        ...
        'forest',
        'corsheaders'
        ...
    ]

    CORS_ORIGIN_ALLOW_ALL = False
    CORS_ORIGIN_WHITELIST = ('app.forestadmin.com')

    MIDDLEWARE_CLASSES = [
        ...
        'corsheaders.middleware.CorsMiddleware',
        ...
    ]

    FOREST_APP_NAME = <app_name>
    FOREST_SECRET_KEY = <forest_secret_key>
    FOREST_URL = 'https://forestadmin-server.herokuapp.com'

In your urls router (urls.py)

    url(r'^forest/', include('forest.urls')),


## Development

For local development, use:

`python setup.py develop`

## Build

`python setup.py sdist`

## Actions

Create the following structure in your app folder.
E.g. if your app is 'movies':

Create `./movies/forest/actions/__init__.py`

Then put single file action in the actions directory:

Create `./movies/forest/actions/ban_user.py` with the following content:

    ACTION = {
        'collection': 'Customers',
        'name': 'Ban User',
        'fields': [
            { 'field': 'duration', 'type': 'Number'}
        ]
    }

The variable name must be `ACTION`.

## Smart Collections

Create the following structure in your app folder.
E.g. if your app is 'movies':

Create `./movies/forest/smart_collections/__init__.py`

Then put single file smart_collection in the `smart_collections` directory:

Create `./movies/forest/smart_collections/brands.py` with the following content:

    SMART_COLLECTION = {
        'name': 'Brands',
        'fields': [
            { 'field': 'brand', 'type': 'String'},
            { 'field': 'count', 'type': 'Number'}
        ]
    }

The variable name must be `SMART_COLLECTION`.
