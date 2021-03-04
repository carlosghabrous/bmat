from rest_framework             import viewsets

from django.db                  import IntegrityError
from django.http.response       import HttpResponse, HttpResponseBadRequest
from django.views.generic       import TemplateView
from django.views.generic.edit  import FormView
from django.shortcuts           import render

from .                          import models, serializers, utils
from .forms                     import SelectDsrsFileForm

import logging
import pycountry

logger = logging.getLogger(__name__)

class DSRViewSet(viewsets.ModelViewSet):
    queryset = models.DSR.objects.all()
    serializer_class = serializers.DSRSerializer

class DSPViewSet(viewsets.ModelViewSet):
    queryset = models.DSP.objects.all()
    serializer_class = serializers.DSPSerializer

class UploadDsrFilesForm(FormView):
    '''This class is used to dump a form to select compressed/uncompressed DSR files to upload their data into the DB

    The class extends FormView and overwrites the get and post methods. The get method will be executed on the form's first load
    by the user. The post will be executed when the user submits the form. The form allows multiple .gz and or .tsv files to be 
    uploaded at once. The function utils.parse_dsr_file parses each file and returns a dictionary containing its records.
    I have used the dependency pycountry to get the missing data on the Territory and Currency models from the DSR file names'''

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

                currency = pycountry.currencies.get(alpha_3=md.currency)

                if not currency: 
                    '''This is just to show that some action could be taken in case the file names are wrong
                    and the currency is not identified'''
                    pass 

                curr = models.Currency(name=currency.name, symbol=currency.numeric, code=md.currency)
                try:
                    curr.save()

                except IntegrityError as e:
                    '''The Currency model implements a unique constraint to prevent the same currency to be inserted more than once. 
                    The IntegrityError constraint, that could be triggered when trying to insert duplicated records in this table,
                    is catched here and logged (among others). I decided not to re-raise the exception in this case not to prevent
                    the file records to be inserted'''
                    logger.error(str(e))

                country = pycountry.countries.get(alpha_2=md.territory)
                if not country: 
                    '''This is just to show that some action could be taken in case the file names are wrong
                    and the country is not identified'''
                    pass 

                terr = models.Territory(name=country.name, code_2=md.territory, code_3=country.alpha_3, local_currency=curr)
                try:
                    terr.save()

                except IntegrityError as e:
                    '''The Territory model implements a unique constraint to prevent the same territory to be inserted more than once. 
                    The IntegrityError constraint, that could be triggered when trying to insert duplicated records in this table,
                    is catched here and logged (among others). I decided not to re-raise the exception in this case not to prevent
                    the file records to be inserted'''
                    logger.error(str(e))

                dsr_meta = models.DSR(path=md.path, period_start=md.period_start, period_end=md.period_end, status="INGESTED", territory=terr, currency=curr)
                
                try:
                    dsr_meta.save()

                except IntegrityError as e:
                    '''The DSR model implements a unique constraint to prevent the same DSR file meta data to be inserted more than once. 
                    The IntegrityError constraint, that could be triggered when trying to insert duplicated records in this table,
                    is catched here and logged (among others). I decided not to re-raise the exception in this case not to prevent
                    the file records to be inserted'''
                    logger.error(str(e))

                data = dsr_records['data']
                for record in data: 
                    dsp = models.DSP(dsp_id=record.dsp_id, title=record.title, artists=record.artists, isrc=record.isrc, usages=record.usages, revenue=record.revenue, dsr_id=dsr_meta)
                    dsp.save()


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

