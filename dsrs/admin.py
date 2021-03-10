from django.contrib import admin
from .models import Territory, Currency, DSR, DSP

# Register your models here.

'''FROM CARLOS: 
Models added here to be able to check the DB content and perform simple actions on its records
'''

admin.site.register(Territory)
admin.site.register(Currency)
admin.site.register(DSR)
admin.site.register(DSP)
