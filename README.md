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

    FOREST_APP_MODELS = <app_name>
    FOREST_SECRET_KEY = <forest_secret_key>
    FOREST_URL = 'https://forestadmin-server.herokuapp.com'

In your urls router (urls.py)

    url(r'^forest/', include('forest.urls')),




## Development

For local development, use:

`python setup.py develop`

## Build

`python setup.py sdist`

