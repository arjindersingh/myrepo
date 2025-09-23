""" from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'


    def ready(self):
        # ✅ Register signals
        ""         import accounts.signals.academiyear
        import accounts.signals.institute
        import accounts.signals.wing
        import accounts.signals.menu
        import accounts.signals.usersetting
        import accounts.signals.userprofile
        import accounts.signals.usersetting
        import accounts.signals.department
        import accounts.signals.subject
        import accounts.signals.academiyear
        import accounts.signals.jobcategory
        import accounts.signals.employmentstatus ""
 """