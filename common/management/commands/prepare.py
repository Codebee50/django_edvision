from django.core.management.base import BaseCommand
from export.models import SupportedExportFormat

class Command(BaseCommand):
    help = "Prepare resources or configuration."
    

    def handle(self, *args, **options):
        export_options = [
            {
                "id": 1,
                "name": "Postgresql",
                "image": "/images/e-options/postgress.png",
                "extension": ".sql",
            },
            {
                "id": 2,
                "name": "MySQL",
                "image": "/images/e-options/mysql.png",
                "extension": ".sql",
            },
            {
                "id": 3,
                "name": "SQL Server",
                "image": "/images/e-options/sql-server.png",
                "extension": ".sql",
            },
            {
                "id": 4,
                "name": "Oracle",
                "image": "/images/e-options/oracle.png",
                "extension": ".sql",
            },
            {
                "id": 5,
                "name": "Django ORM",
                "image": "/images/e-options/django.png",
                "extension": ".py",
            },
            {
                "id": 6,
                "name": "GORM",
                "image": "/images/e-options/gorm.png",
                "extension": ".go",
            },
        ]
        
        for export_option in export_options:
            s_format, created = SupportedExportFormat.objects.get_or_create(
                name=export_option["name"],
                defaults={
                    "fe_image_url": export_option["image"],
                    "extension": export_option["extension"],
                }
            )
            if created:
                print('Created supported export format: ', s_format.name)    
            else:
                print('Supported export format already exists: ', s_format.name)
                
        self.stdout.write(self.style.SUCCESS("Preparation complete."))
