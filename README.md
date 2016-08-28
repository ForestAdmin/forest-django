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

In your urls router (urls.py)

    url(r'^forest/', include('forest.urls')),


## Development

For local development, use:

`export PYTHONPATH=$PYTHONPATH:/path/to/forest-django/`

## Build

`python setup.py sdist`
