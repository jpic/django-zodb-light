import uuid
import importlib

from persistent import Persistent
from BTrees.OOBTree import OOBTree

from settings import ZODB_ROOT
from objectmap import ObjectMap


class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class Model(Persistent):
    @classmethod
    def uuid_key(self, uuid_str):
        return uuid.UUID(uuid_str)

    @property
    def uuid(self):
        return self.__class__.uuid_key(self.__objectid__)

    @classmethod
    def exists(self, uuid_str):
        return self.uuid_key(uuid_str) in self.db.keys()

    @classmethod
    def get(self, uuid_str, default=None):
        return self.db.get(self.uuid_key(uuid_str), default)

    @classmethod
    def get_by_name(self, name):
        for obj in self.db.values():
            if obj.name == name:
                return obj

    @ClassProperty
    @classmethod
    def db(cls):
        try:
            return ZODB_ROOT[cls.__name__]
        except KeyError:
            ZODB_ROOT[cls.__name__] = OOBTree()
        return cls.db

    def __init__(self, name):
        self.name = name
        ObjectMap.default().add(self)
        self.db[self.__objectid__] = self

    def __unicode__(self):
        return self.name

def get_model(name):
    bits = name.split('.')
    mod = importlib.import_module('.'.join(bits[:-1]))
    return getattr(mod, bits[-1])


class RelationDescriptor(object):
    def __init__(self, source, target, name, one=False):
        self._source = source
        self._target = target
        self.name = name
        self.one = one

    @property
    def target(self):
        if self._target != 'self' and isinstance(self._target, str):
            self._target = get_model(self._target)
        return self._target

    @property
    def source(self):
        if self._source != 'self' and isinstance(self._source, str):
            self._source = get_model(self._source)
        return self._source

    def __get__(self, obj, objtype=None):
        if self.one:
            for relation in Relation(obj, self):
                return relation
        else:
            return Relation(obj, self)

    def __set__(self, obj, related):
        if self.one:
            related = [related]

        Relation(obj, self).set(related)


class Relation(object):
    def __init__(self, obj, relation):
        self.obj = obj
        self.relation = relation

    def set(self, related_list):
        self._clear()

        for related in related_list:
            self.append(related)

    def is_source(self):
        if self.relation.source == 'self':
            return True
        elif self.relation.target == 'self':
            return False

        return isinstance(self.obj, self.relation.source)

    def _clear(self):
        if self.is_source():
            ids = ObjectMap.default().targets(self.obj, self.relation.name)
        else:
            ids = ObjectMap.default().sources(self.obj, self.relation.name)

        for objid in list(ids):
            ObjectMap.default().disconnect(self.obj, objid,
                    self.relation.name)

    def __iter__(self):
        if self.is_source():
            return ObjectMap.default().targets(self.obj, self.relation.name)
        else:
            return ObjectMap.default().sources(self.obj, self.relation.name)

    def append(self, related):
        if self.is_source():
            args = [self.obj, related, self.relation.name]
        else:
            args = [related, self.obj, self.relation.name]

        ObjectMap.default().connect(*args)
