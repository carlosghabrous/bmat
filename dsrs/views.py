from rest_framework import viewsets
from django.http.response import HttpResponse, HttpResponseBadRequest

from . import models, serializers


class DSRViewSet(viewsets.ModelViewSet):
    queryset = models.DSR.objects.all()
    serializer_class = serializers.DSRSerializer

class DSPViewSet(viewsets.ModelViewSet):
    queryset = models.DSP.objects.all()
    serializer_class = serializers.DSPSerializer

def import_dsrs(request):
    return HttpResponse('hello')


def percentile(request, value):
    output, err_msg = '', ''

    if value < 1 or value > 100:
        err_msg = f'Percentile value {value} is not allowed! Values should be within (1-100) range'
        return HttpResponseBadRequest(err_msg)

    #TODO: extract from DB, calculate the percentile, and convert to EUR
    return HttpResponse(f'user requested percentile {value}')
