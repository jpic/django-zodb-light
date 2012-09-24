import unittest

from ..models import Model, RelationDescriptor


class Book(Model):
    pass


class Author(Model):
    pass


class ModelsTestCase(unittest.TestCase):
    def test_named_model(self):
        desc = RelationDescriptor('zodb_light.tests.models.Author',
            'zodb_light.tests.models.Book', 'tree')
        self.assertEqual(desc.source, Author)
        self.assertEqual(desc.target, Book)

    def test_self_relation(self):
        Author.parent = RelationDescriptor(Author, 'self', 'tree', True)
        Author.children = RelationDescriptor('self', Author, 'tree')

        author1 = Author('1')
        author2 = Author('2')
        author3 = Author('3')

        author2.parent = author1
        self.assertEqual(author1.parent, None)
        self.assertEqual(author2.parent, author1)
        self.assertEqual(author3.parent, None)
        self.assertEqual(list(author1.children), [author2])
        self.assertEqual(list(author2.children), [])
        self.assertEqual(list(author3.children), [])

        author1.children.append(author3)
        self.assertEqual(author1.parent, None)
        self.assertEqual(author2.parent, author1)
        self.assertEqual(author3.parent, author1)
        self.assertEqual(list(author1.children), [author2, author3])
        self.assertEqual(list(author2.children), [])
        self.assertEqual(list(author3.children), [])

        # circular hierarchy should work as a side effect
        author1.parent = author3
        self.assertEqual(author1.parent, author3)
        self.assertEqual(author2.parent, author1)
        self.assertEqual(author3.parent, author1)
        self.assertEqual(list(author1.children), [author2, author3])
        self.assertEqual(list(author2.children), [])
        self.assertEqual(list(author3.children), [author1])

    def test_relation(self):
        relation = RelationDescriptor(Book, Author, 'authors_of_book')
        Book.authors = relation
        Author.books = relation

        book1 = Book('Book 1')  # by Author 1 and Author 2
        book2 = Book('Book 2')  # by Author 2 only

        author1 = Author('Author 1')
        author2 = Author('Author 2')  # has 2 books

        self.assertEqual(list(author1.books), [])
        self.assertEqual(list(author2.books), [])
        self.assertEqual(list(book1.authors), [])
        self.assertEqual(list(book2.authors), [])

        book1.authors = [author1, author2]
        self.assertEqual(list(author1.books), [book1])
        self.assertEqual(list(author2.books), [book1])
        self.assertEqual(list(book1.authors), [author1, author2])
        self.assertEqual(list(book2.authors), [])

        author2.books = [book2]
        self.assertEqual(list(author1.books), [book1])
        self.assertEqual(list(author2.books), [book1, book2])
        self.assertEqual(list(book1.authors), [author1, author2])
        self.assertEqual(list(book2.authors), [author2])

        book1.authors = [author1]
        self.assertEqual(list(author1.books), [book1])
        self.assertEqual(list(author2.books), [book2])
        self.assertEqual(list(book1.authors), [author1])
        self.assertEqual(list(book2.authors), [author2])

        author2.books.append(book1)
        self.assertEqual(list(author1.books), [book1])
        self.assertEqual(list(author2.books), [book1, book2])
        self.assertEqual(list(book1.authors), [author1, author2])
        self.assertEqual(list(book2.authors), [author2])
