import unittest

from ..models import Model, RelationDescriptor


class Book(Model):
    def __init__(self, name):
        super(Book, self).__init__()
        self.name = name


class Author(Model):
    def __init__(self, name):
        super(Author, self).__init__()
        self.name = name


class ModelsTestCase(unittest.TestCase):
    def test_relation(self):
        relation = RelationDescriptor(Book, Author, 'authors_of_book')
        Book.authors = relation
        Author.books = relation

        book1 = Book('Book 1')  # by Author 1 and Author 2
        book2 = Book('Book 2')  # by Author 2 only

        author1 = Author('Author 1')
        author2 = Author('Author 2')  # has 2 books

        book1.authors = [author1, author2]
        author2.books = [book2]

        self.assertEqual(list(author2.books), [book1, book2])
        self.assertEqual(list(author1.books), [book1])
        self.assertEqual(list(book2.authors), [author2])
        self.assertEqual(list(book1.authors), [author1, author2])

        # let's test disconnections
        book1.authors = [author1]

        self.assertEqual(list(author2.books), [book2])
        self.assertEqual(list(author1.books), [book1])
        self.assertEqual(list(book2.authors), [author2])
        self.assertEqual(list(book1.authors), [author1])

        author2.books.append(book1)
        self.assertEqual(list(author2.books), [book1, book2])
        self.assertEqual(list(author1.books), [book1])
        self.assertEqual(list(book2.authors), [author2])
        self.assertEqual(list(book1.authors), [author1, author2])
