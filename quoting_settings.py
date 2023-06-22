DEBUG = True
ALLOWED_HOSTS = ['localhost', 'sql7.freemysqlhosting.net', '127.0.0.1', '0.0.0.0']
SECRET_KEY = '124'
ROOT_URLCONF = 'quotingservice.urls'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'sql7627262',
#         'USER': 'sql7627262',
#         'PASSWORD': 'nYTUTNVGmR',
#         'HOST': 'sql7.freemysqlhosting.net',
#         'PORT': '3306',
#         'charset': 'utf8',
#         'OPTIONS': {
#             'charset': 'utf8',
#         },
#     }
# }

INSTALLED_APPS = [
    # 'quotingservice',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes'
]
