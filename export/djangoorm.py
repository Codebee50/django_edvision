from diagram.models import Diagram, DatabaseTable, DatabaseColumn, Relationship
from django.utils.text import slugify

def get_compatible_datatype(datatype):
    fallback = "models.CharField(max_length=255)"
    field_mapping = {
        "AutoField": "models.AutoField(",
        "BigAutoField": "models.BigAutoField(",
        "BigIntegerField": "models.BigIntegerField(",
        "BinaryField": "models.BinaryField(",
        "BooleanField": "models.BooleanField(",
        "CharField": "models.CharField(max_length=255",
        "DateField": "models.DateField(",
        "DateTimeField": "models.DateTimeField(",
        "DecimalField": "models.DecimalField(max_digits=10, decimal_places=2",
        "DurationField": "models.DurationField(",
        "EmailField": "models.EmailField(",
        "FileField": "models.FileField(upload_to='files/'",
        "FloatField": "models.FloatField()",
        "ImageField": "models.ImageField(upload_to='images/'",
        "IntegerField": "models.IntegerField(",
        "JSONField": "models.JSONField(",
        "PositiveIntegerField": "models.PositiveIntegerField(",
        "SlugField": "models.SlugField(",
        "SmallIntegerField": "models.SmallIntegerField(",
        "TextField": "models.TextField(",
        "TimeField": "models.TimeField(",
        "UUIDField": "models.UUIDField(default=uuid.uuid4, editable=False",
        "XMLField": "models.XMLField(",
        "URLField": "models.URLField(",
    }
    return field_mapping.get(datatype, fallback)

def get_relationship_type(relationship:Relationship):
    rel_type = f"{relationship.from_rel}-to-{relationship.to_rel}"
    return "OneToOneField" if rel_type == 'one-to-one'else "ForeignKey"


def get_table_content(table:DatabaseTable):
    columns = DatabaseColumn.objects.filter(db_table=table)
    content = []
    for column in columns:
        column_name = slugify(column.name)
        relationships = Relationship.objects.filter(from_column=column)
        if relationships.exists():
            rel = relationships.first()
            table_name = rel.to_column.db_table.name.replace(' ', '')
            content_definition = f'    {column_name} = models.{get_relationship_type(rel)}({table_name}, on_delete=models.CASCADE)'
        else:
            content_definition = f'    {column_name} = {get_compatible_datatype(column.datatype)}, null={column.is_nullable}, blank={column.is_nullable})'
        content.append(content_definition)
    return '\n'.join(content)

def export_django(diagram:Diagram):
    statement = "from django.db import models \nimport uuid \n\n"
    tables = DatabaseTable.objects.filter(diagram=diagram)
    for db_table in tables:
        table_name = db_table.name.replace(' ', '')
        statement += f'class {table_name}(models.Model):\n{get_table_content(table=db_table)}\n'
    
    return statement