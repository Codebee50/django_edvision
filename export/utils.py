from django.conf import settings
import os


def write_destination(statement="", filename=""):
    export_dir = settings.EXPORT_DIR
    export_path = f"{export_dir}/{filename}"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    with open(export_path, 'w', encoding='utf-8') as destination:
        destination.write(statement)
    
    return export_path