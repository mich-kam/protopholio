from django.apps import AppConfig


class PortfolioConfig(AppConfig):
    name = "portfolio"

    def ready(self):
        # Le thème Unfold n'affiche « Ajouter » que si cet attribut est vrai.
        from django.contrib.admin.options import ModelAdmin

        ModelAdmin.show_add_link = True
        ModelAdmin.list_filter_submit = True
        ModelAdmin.warn_unsaved_form = True
