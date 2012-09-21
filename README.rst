zodb-relations
==============

Status: alpha, API subject to changes, poorly documented.

This app intends to provide zodb-backed models to djangonauts.

Features
--------

- TransactionMiddleware that commits automatically, stolen from django-zodb,
- ObjectMap that maps UUIDs and persistent objects, stolen from SubstanceD
- Simple relations API with RelationDescriptor,
- Backward (reverse) relations support,

Information
-----------

This started as a reusable extraction of objectmap from SubstanceD framework.

Low level details:

http://blog.yourlabs.org/post/31829697648/handling-relations-between-zodb-persistent-objects

Currently under development, API is subject to changes:

- simplifications,
- name changes !
