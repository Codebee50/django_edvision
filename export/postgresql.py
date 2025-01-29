from diagram.models import Diagram, Relationship, DatabaseColumn, DatabaseTable
from django.utils.text import slugify

def get_compatible_datatype(datatype):
    if datatype == 'varchar': 
        return "VARCHAR(255)"
    
    if datatype == 'timestamptz':
        return "TIMESTAMP(0) WITHOUT TIME ZONE"
    return datatype.upper()

def get_primary_key_alter(table):
    primary_column = DatabaseColumn.objects.filter(is_primary_key=True, db_table=table).first()
    if primary_column:
        return f'ALTER TABLE "{table.name}" ADD PRIMARY KEY("{primary_column.name}");\n'
    return '\n'
    
def get_table_content(table):
    columns = DatabaseColumn.objects.filter(db_table=table)
    content= []
    for column in columns:
        not_null = "NULL" if column.is_nullable else "NOT NULL"
        content_definition = f'"{column.name}" {get_compatible_datatype(column.datatype)} {not_null}'
        content.append(content_definition)
    return ',\n'.join(content)

def get_relationships(diagram):
    relationships = Relationship.objects.filter(diagram=diagram)
    stmt = ''
    for rel in relationships:
        from_table_name = rel.from_column.db_table.name
        to_table_name = rel.to_column.db_table.name
        rel_name = f"{slugify(from_table_name)}_{slugify(to_table_name)}_foreign" 
        
        stmt += f'ALTER TABLE "{from_table_name}" ADD CONSTRAINT "{rel_name}" FOREIGN KEY("{rel.from_column.name}") REFERENCES "{to_table_name}"("{rel.to_column.name}");\n'
    return stmt

def export_postgres(diagram:Diagram):
    statement = ''
    tables = DatabaseTable.objects.filter(diagram=diagram)
    for db_table in tables:
        statement += f'CREATE TABLE "{db_table.name}"(\n \
            {get_table_content(table=db_table)}\n \
                );\n'
        
        primary_key_alter = get_primary_key_alter(db_table)
        statement += primary_key_alter
    relationships_alters = get_relationships(diagram)
    statement +=relationships_alters
        
    return statement