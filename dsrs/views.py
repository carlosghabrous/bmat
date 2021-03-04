from rest_framework import viewsets
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render

from . import models, serializers, utils
from .forms import SelectDsrsFileForm

import logging
logger = logging.getLogger(__name__)

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

    def get(self, request):
       form_class = self.get_form_class()
       form = self.get_form(form_class)
       return render(request, 'dsrs/upload-dsrs.html', {'form':form})

    def post(self, request, *args, **kwargs):
        form_class  = self.get_form_class()
        form        = self.get_form(form_class)
        files       = request.FILES.getlist('dsr_files')

        if form.is_valid():
            for f in files:
                dsr_records = utils.parse_dsr_file(f.name)

                md = dsr_records['meta']
                curr = models.Currency(name='', symbol='', code=md.currency)
                # curr.save()

                terr = models.Territory(name='', code_2=md.territory, local_currency=curr)
                # terr.save()

                dsr_meta = models.DSR(path=md.path, period_start=md.period_start, period_end=md.period_end, status="INGESTED", territory=terr, currency=curr)
                # dsr_meta.save()

                data = dsr_records['data']
                for record in data: 
                    dsp = models.DSP(dsp_id=record.dsp_id, title=record.title, artists=record.artists, isrc=record.isrc, usages=record.usages, revenue=record.revenue, dsr_id=dsr_meta)
                    # dsp.save()


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

def success(request):
    return HttpResponse('DSR file(s) successfully uploaded')

