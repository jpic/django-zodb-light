from persistent import Persistent
from BTrees.OOBTree import OOBTree

from settings import ZODB_ROOT
from objectmap import ObjectMap

class ClassProperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class Model(Persistent):
    @ClassProperty
    @classmethod
    def db(cls):
        try:
            return ZODB_ROOT[cls.__name__]
        except KeyError:
            ZODB_ROOT[cls.__name__] = OOBTree()
        return cls.db

    def __init__(self):
        ObjectMap.default().add(self)


class RelationDescriptor(object):
    def __init__(self, source, target, name):
        self.source = source
        self.target = target
        self.name = name

    def __get__(self, obj, objtype=None):
        return Relation(obj, self)

    def __set__(self, obj, related_list):
        Relation(obj, self).set(related_list)


class Relation(object):
    def __init__(self, obj, relation):
        self.obj = obj
        self.relation = relation

    def set(self, related_list):
        self._clear()

        for related in related_list:
            self.append(related)

    def _clear(self):
        if isinstance(self.obj, self.relation.source):
            ids = ObjectMap.default().targets(self.obj, self.relation.name)
        elif isinstance(self.obj, self.relation.target):
            ids = ObjectMap.default().sources(self.obj, self.relation.name)

        for objid in list(ids):
            ObjectMap.default().disconnect(self.obj, objid,
                    self.relation.name)

    def __iter__(self):
        if isinstance(self.obj, self.relation.source):
            return ObjectMap.default().targets(self.obj, self.relation.name)
        elif isinstance(self.obj, self.relation.target):
            return ObjectMap.default().sources(self.obj, self.relation.name)

    def append(self, related):
        if isinstance(self.obj, self.relation.source):
            args = [self.obj, related, self.relation.name]
        elif isinstance(self.obj, self.relation.target):
            args = [related, self.obj, self.relation.name]

        ObjectMap.default().connect(*args)
