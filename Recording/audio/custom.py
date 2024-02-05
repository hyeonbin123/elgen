from django.db import models

class CustomDateTimeField(models.DateTimeField):
    def value_to_string(self, obj):
        val = self.value_from_object(obj)
        print('val: ', val)
        if val:
            val.replace(microsecond=0)
            return val.isoformat()
        return ''