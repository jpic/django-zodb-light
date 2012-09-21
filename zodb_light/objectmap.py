"""
Shamelessly stolen from SubstanceD.
"""

import uuid

from persistent import Persistent
import BTrees

from settings import ZODB_ROOT


def oid_of(obj):
    return obj.__objectid__


class ObjectMap(Persistent):
    family = BTrees.family64

    @classmethod
    def default(cls):
        if '_objectmap' not in ZODB_ROOT.keys():
            ZODB_ROOT['_objectmap'] = cls()

        return ZODB_ROOT['_objectmap']

    def __init__(self, family=None):
        if family is not None:
            self.family = family
        self.objectindex = self.family.OO.BTree()
        self.referencemap = ReferenceMap()

    def new_objectid(self):
        return uuid.uuid1()

    def object_for(self, objectid, context=None):
        """ Returns an object or ``None`` given an object id or a path tuple"""
        return self.objectindex.get(objectid)

    def add(self, obj):
        """ Add a new object to the object map at the location specified by
        ``path_tuple`` (must be the path of the object in the object graph as
        a tuple, as returned by Pyramid's ``resource_path_tuple`` function)."""
        if getattr(obj, '__objectid__', None):
            raise Exception()

        obj.__objectid__ = self.new_objectid()
        self.objectindex[obj.__objectid__] = obj

        return obj.__objectid__

    def remove(self, obj_objectid_or_path_tuple, references=True):
        """ Remove an object from the object map give an object, an object id
        or a path tuple.  If ``references`` is True, also remove any
        references added via ``connect``, otherwise leave them there
        (e.g. when moving an object)."""
        if references:
            self.referencemap.remove(obj_objectid_or_path_tuple)

    def _refids_for(self, source, target):
        sourceid, targetid = oid_of(source), oid_of(target)
        return sourceid, targetid

    def _refid_for(self, obj):
        oid = oid_of(obj)
        return oid

    def connect(self, source, target, reftype):
        """ Connect a source object or objectid to a target object or
        objectid using reference type ``reftype``"""
        sourceid, targetid = self._refids_for(source, target)
        self.referencemap.connect(sourceid, targetid, reftype)

    def disconnect(self, source, target, reftype):
        """ Disconnect a source object or objectid from a target object or
        objectid using reference type ``reftype``"""
        sourceid, targetid = self._refids_for(source, target)
        self.referencemap.disconnect(sourceid, targetid, reftype)

    # We make a copy of the set returned by ``targetids`` and ``sourceids``
    # because it's not atypical for callers to want to modify the
    # underlying bucket while iterating over the returned set.  For example:
    #
    # groups = objectmap.targetids(self, UserToGroup)
    # for group in groups:
    #    objectmap.disconnect(self, group, UserToGroup)
    #
    # if we don't make a copy, this kind of code will result in e.g.
    #
    #     for group in groups:
    # RuntimeError: the bucket being iterated changed size

    def sourceids(self, obj, reftype):
        """ Return a set of object identifiers of the objects connected to
        ``obj`` a a source using reference type ``reftype``"""
        oid = self._refid_for(obj)
        return self.family.OO.Set(self.referencemap.sourceids(oid, reftype))

    def targetids(self, obj, reftype):
        """ Return a set of object identifiers of the objects connected to
        ``obj`` a a target using reference type ``reftype``"""
        oid = self._refid_for(obj)
        return self.family.OO.Set(self.referencemap.targetids(oid, reftype))

    def sources(self, obj, reftype):
        """ Return a generator which will return the objects connected to
        ``obj`` as a source using reference type ``reftype``"""
        for oid in self.sourceids(obj, reftype):
            yield self.object_for(oid)

    def targets(self, obj, reftype):
        """ Return a generator which will return the objects connected to
        ``obj`` as a target using reference type ``reftype``"""
        for oid in self.targetids(obj, reftype):
            yield self.object_for(oid)


class ReferenceMap(Persistent):

    family = BTrees.family64

    def __init__(self, refmap=None):
        if refmap is None:
            refmap = self.family.OO.BTree()
        self.refmap = refmap

    def connect(self, source, target, reftype):
        refset = self.refmap.setdefault(reftype, ReferenceSet())
        refset.connect(source, target)

    def disconnect(self, source, target, reftype):
        refset = self.refmap.get(reftype)
        if refset is not None:
            refset.disconnect(source, target)

    def targetids(self, oid, reftype):
        refset = self.refmap.get(reftype)
        if refset is not None:
            return refset.targetids(oid)
        return self.family.OO.Set()

    def sourceids(self, oid, reftype):
        refset = self.refmap.get(reftype)
        if refset is not None:
            return refset.sourceids(oid)
        return self.family.OO.Set()

    def remove(self, oids):
        for refset in self.refmap.values():
            refset.remove(oids)


class ReferenceSet(Persistent):

    family = BTrees.family64

    def __init__(self):
        self.src2target = self.family.OO.BTree()
        self.target2src = self.family.OO.BTree()

    def connect(self, source, target):
        targets = self.src2target.setdefault(source, self.family.OO.TreeSet())
        targets.insert(target)
        sources = self.target2src.setdefault(target, self.family.OO.TreeSet())
        sources.insert(source)

    def disconnect(self, source, target):
        targets = self.src2target.get(source)
        if targets is not None:
            try:
                targets.remove(target)
            except KeyError:
                pass

        sources = self.target2src.get(target)
        if sources is not None:
            try:
                sources.remove(source)
            except KeyError:
                pass

    def targetids(self, oid):
        return self.src2target.get(oid, self.family.OO.Set())

    def sourceids(self, oid):
        return self.target2src.get(oid, self.family.OO.Set())

    def remove(self, oidset):
        # XXX is there a way to make this less expensive?
        removed = self.family.OO.Set()
        for oid in oidset:
            if oid in self.src2target:
                removed.insert(oid)
                targets = self.src2target.pop(oid)
                for target in targets:
                    oidset = self.target2src.get(target)
                    oidset.remove(oid)
                    if not oidset:
                        del self.target2src[target]
            if oid in self.target2src:
                removed.insert(oid)
                sources = self.target2src.pop(oid)
                for source in sources:
                    oidset = self.src2target.get(source)
                    oidset.remove(oid)
                    if not oidset:
                        del self.src2target[source]
        return removed
