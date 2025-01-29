from django.db import models


class RelationshipTypeChoices(models.TextChoices):
    ONE = 'one', 'One'
    MANY= 'many', 'Many'

class DatabaseTypeChoices(models.TextChoices):
    POSTGRESQL = 'postgresql', 'PostgreSQL'
    MYSQL = 'mysql', 'MySQL'
    SQLITE = 'sqlite', 'SQLite'
    ORACLE = 'oracle', 'oracle'
    DJANGO_ORM = 'djangoorm', 'Django orm'

class VisibilityChoices(models.TextChoices):
    PUBLIC = 'public', 'Public'
    PRIVATE = 'private', 'Private'