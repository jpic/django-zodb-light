import unittest

from ..models import Model
from ..objectmap import ReferenceMap, ObjectMap

class Book(Model):
    def __init__(self, name):
        super(Book, self).__init__()
        self.name = name


class Author(Model):
    def __init__(self, name):
        super(Author, self).__init__()
        self.name = name


class RelationRegistryTestCase(unittest.TestCase):
    def test_reference_map(self):
        book1 = 'Book 1 UUID'  # by Author 1 and Author 2
        book2 = 'Book 2 UUID'  # by Author 2 only

        author1 = 'Author 1 UUID'
        author2 = 'Author 2 UUID'  # has 2 books

        refname = 'authors_of_book'  # name of the relation

        themap = ReferenceMap()

        # add to book1: author1 and author2
        themap.connect(book1, author1, refname)
        themap.connect(book1, author2, refname)

        # add to author2: book2
        themap.connect(book2, author2, refname)

        # book1 should have author1 and author2
        self.assertEqual(list(themap.targetids(book1, refname)),
                [author1, author2])

        # author1 should have book1
        self.assertEqual(list(themap.sourceids(author1, refname)), [book1])

        # author2 should have book1 and book2
        self.assertEqual(list(themap.sourceids(author2, refname)),
            [book1, book2])

        # book2 should have author2
        self.assertEqual(list(themap.targetids(book2, refname)),
                [author2])


        # let's test disconnections
        themap.disconnect(book1, author2, refname)

        # book1 should have author1 only
        self.assertEqual(list(themap.targetids(book1, refname)),
                [author1])


class ObjectRegistryTestCase(unittest.TestCase):
    def test_object_registry(self):
        book1 = Book('Book 1 UUID')  # by Author 1 and Author 2
        book2 = Book('Book 2 UUID')  # by Author 2 only

        author1 = Author('Author 1 UUID')
        author2 = Author('Author 2 UUID')  # has 2 books

        refname = 'authors_of_book'  # name of the relation

        registry = ObjectMap.default()

        # add to book1: author1 and author2
        registry.connect(book1, author1, refname)
        registry.connect(book1, author2, refname)
        # add to book2: author2
        registry.connect(book2, author2, refname)

        # book1 should have author1 and author2
        self.assertEqual(list(registry.targetids(book1, refname)),
                [author1.__objectid__, author2.__objectid__])
        self.assertEqual(list(registry.targets(book1, refname)),
                [author1, author2])

        # author1 should have book1
        self.assertEqual(list(registry.sourceids(author1, refname)),
                [book1.__objectid__])
        self.assertEqual(list(registry.sources(author1, refname)),
                [book1])

        # author2 should have book1 and book2
        self.assertEqual(list(registry.sourceids(author2, refname)),
            [book1.__objectid__, book2.__objectid__])
        self.assertEqual(list(registry.sources(author2, refname)),
            [book1, book2])

        # book2 should have author2
        self.assertEqual(list(registry.targetids(book2, refname)),
                [author2.__objectid__])
        self.assertEqual(list(registry.targets(book2, refname)),
                [author2])

        # let's test disconnections
        registry.disconnect(book1, author2, refname)

        # book1 should have author1 only
        self.assertEqual(list(registry.targetids(book1, refname)),
                [author1.__objectid__])



