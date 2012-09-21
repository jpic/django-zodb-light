import os.path

from ZODB.FileStorage import FileStorage
from ZODB.DB import DB

from django.conf import settings


ZODB_FILENAME = getattr(settings, 'ZODB_FILENAME', os.path.normpath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')))

ZODB_STORAGE = FileStorage(settings.ZODB_FILENAME)

ZODB_DB = DB(ZODB_STORAGE)

ZODB_CONNECTION = ZODB_DB.open()

ZODB_ROOT = ZODB_CONNECTION.root()
