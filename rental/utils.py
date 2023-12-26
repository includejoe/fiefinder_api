from django.db.models import Func


class Acos(Func):
    function = "ACOS"
