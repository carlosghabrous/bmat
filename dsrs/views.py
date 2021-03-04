from rest_framework import viewsets
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.generic.edit import FormView

from . import models, serializers
from .forms import SelectDsrsFileForm


class DSRViewSet(viewsets.ModelViewSet):
    queryset = models.DSR.objects.all()
    serializer_class = serializers.DSRSerializer

class DSPViewSet(viewsets.ModelViewSet):
    queryset = models.DSP.objects.all()
    serializer_class = serializers.DSPSerializer

class UploadDsrFilesForm(FormView):
    form_class     = SelectDsrsFileForm
    template_name  = 'dsrs/upload-dsrs.html'
    success_url    = 'success/'

    def post(self, request, *args, **kwargs):
        form_class  = self.get_form_class()
        form        = self.get_form(form_class)
        files       = request.FILES.getlist('dsr_files')

        if form.is_valid():
            for f in files:
                pass 

            return self.form_valid(form)

        else:
            return self.form_invalid(form)


def percentile(request, value):
    output, err_msg = '', ''

    if value < 1 or value > 100:
        err_msg = f'Percentile value {value} is not allowed! Values should be within (1-100) range'
        return HttpResponseBadRequest(err_msg)

    #TODO: extract from DB, calculate the percentile, and convert to EUR
    return HttpResponse(f'user requested percentile {value}')
