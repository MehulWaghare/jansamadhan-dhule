from django.apps import AppConfig


class ComplaintsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'complaints'

    def ready(self):
        from django.db.utils import OperationalError
        try:
            from .models import Category

            default_categories = [
                "Water Problem",
                "Road Damage",
                "Electricity Issue",
                "Garbage Issue",
                "Drainage Problem",
                "Street Light Not Working",
            ]

            for cat in default_categories:
                Category.objects.get_or_create(name=cat)

        except OperationalError:
            # database not ready during migrations
            pass