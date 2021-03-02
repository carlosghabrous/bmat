from django.contrib import admin
from .models import Territory, Currency, DSR, DSP

# Register your models here.

admin.site.register(Territory)
admin.site.register(Currency)
admin.site.register(DSR)
admin.site.register(DSP)
