from rest_framework             import viewsets

from django.core                import serializers as core_serializers
from django.db                  import IntegrityError
from django.db.models           import Case, DecimalField, F, Sum, When
from django.http.response       import HttpResponse, HttpResponseBadRequest
from django.views.generic       import TemplateView
from django.views.generic.edit  import FormView
from django.shortcuts           import render

from .                          import models, serializers, utils
from .forms                     import SelectDsrsFileForm

import datetime
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
    '''FROM CARLOS: This class is used to dump a form to select compressed/uncompressed DSR files to upload their data into the DB

    The class extends FormView and overwrites the get and post methods. The get method will be executed on the form's first load
    by the user. The post will be executed when the user submits the form. The form allows multiple .gz and or .tsv files to be 
    uploaded at once. The function utils.parse_dsr_file parses each file and returns a dictionary containing its records.
    I have used the dependency pycountry to get the missing data on the Territory and Currency models from the DSR file names.
    
    Some static files (html and css) have also been added in their simplest forms, just to show that the form could be stylized
    as much as it is desired to'''

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
                    '''FROM CARLOS: This is just to show that some action could be taken in case the file names are wrong
                    and the currency is not identified'''
                    pass 

                curr = models.Currency(name=currency.name, symbol=currency.numeric, code=md.currency)
                try:
                    curr.save()

                except IntegrityError as e:
                    '''FROM CARLOS: The Currency model implements a unique constraint to prevent the same currency to be inserted more than once. 
                    The IntegrityError constraint, that could be triggered when trying to insert duplicated records in this table,
                    is catched here and logged (among others). I decided not to re-raise the exception in this case not to prevent
                    the file records to be inserted'''
                    logger.error(str(e))

                country = pycountry.countries.get(alpha_2=md.territory)
                if not country: 
                    '''FROM CARLOS: This is just to show that some action could be taken in case the file names are wrong
                    and the country is not identified'''
                    pass 

                terr = models.Territory(name=country.name, code_2=md.territory, code_3=country.alpha_3, local_currency=curr)
                try:
                    terr.save()

                except IntegrityError as e:
                    '''FROM CARLOS: The Territory model implements a unique constraint to prevent the same territory to be inserted more than once. 
                    The IntegrityError constraint, that could be triggered when trying to insert duplicated records in this table,
                    is catched here and logged (among others). I decided not to re-raise the exception in this case not to prevent
                    the file records to be inserted'''
                    logger.error(str(e))

                dsr_meta = models.DSR(path=md.path, period_start=md.period_start, period_end=md.period_end, status="INGESTED", territory=terr, currency=curr)
                
                try:
                    dsr_meta.save()

                except IntegrityError as e:
                    '''FROM CARLOS: The DSR model implements a unique constraint to prevent the same DSR file meta data to be inserted more than once. 
                    The IntegrityError constraint, that could be triggered when trying to insert duplicated records in this table,
                    is catched here and logged (among others). I decided not to re-raise the exception in this case not to prevent
                    the file records to be inserted'''
                    logger.error(str(e))

                data = dsr_records['data']
                for record in data: 
                    dsp = models.DSP(dsp_id=record.dsp_id, title=record.title, artists=record.artists, isrc=record.isrc, usages=record.usages, revenue=record.revenue, dsr_id=dsr_meta)
                    dsp.save()


            # Redirects to success URL
            return self.form_valid(form)

        else:
            return self.form_invalid(form)

def _validate_territory(territory):
    msg = ''

    if not territory:
        return msg

    country = pycountry.countries.get(alpha_2=territory)
    if not country:
        msg = f'Country {territory} not found. Use its two-character length code'

    return msg

def _validate_currency(currency):
    msg = ''

    if not currency: 
        return msg

    country_currency = pycountry.currencies.get(alpha_3=currency)
    if not country_currency:
        msg = f'Currency {currency} not found. Use its three-character length code'

    return msg

def _validate_date(a_date):
    msg = ''

    if not a_date:
        return msg

    try:
        datetime.datetime.strptime(a_date, '%Y-%m-%d')

    except ValueError:
        msg = 'Incorrect date format. Change it to YYYY-MM-DD and repeat the request'

    return msg

def percentile(request, percentile_value):
    '''FROM CARLOS: Implements the /dsrs/resources/<percentile> open API endpoint

    First, the request is validated, and a bad request returned if parameters are not correct. 
    Correct parameters are added into a dictionary that is later on used to filter the QuerySet records from the DSP table. 
    All different currencies from these records are retrieved, in order to get the respective conversion factors into EUR. 
    The exchange rates and the revenue in EUR are calculated and added to the QuerySet, in order not to load this 
    to memory. 

    Finally, the appropriate records are selected and returned in JSON format. 
    '''
    err_msg = ''

    if percentile_value < 1 or percentile_value > 100:
        err_msg = f'Percentile value {percentile_value} is not allowed! Values should be within (1-100) range'
        return HttpResponseBadRequest(err_msg)

    # Extract parameters from URL
    territory     = request.GET.get('territory', '')
    currency      = request.GET.get('currency', '')
    period_start  = request.GET.get('period_start', '')
    period_end    = request.GET.get('period_end', '')

    filter_dict = dict()
    
    # Territory
    if territory:
        err_msg = _validate_territory(territory)

        if err_msg: 
            return HttpResponseBadRequest(err_msg)

        filter_dict.update({'dsr_id__territory__code_2':territory})

    # Validate currency
    if currency:
        err_msg = _validate_currency(currency)
        if err_msg:
            return HttpResponseBadRequest(err_msg)

        filter_dict.update({'dsr_id__currency__code':currency})

    # Validate dates are in correct formats
    if period_start:
        err_msg = _validate_date(period_start)

        if err_msg:
            return HttpResponseBadRequest(err_msg)

        filter_dict.update({'dsr_id__period_start__gte':period_start})

    if period_end:
        err_msg = _validate_date(period_end)

        if err_msg:
            return HttpResponseBadRequest(err_msg)

        filter_dict.update({'dsr_id__period_end__lte':period_end})    

    # Make a copy of the filtered queryset
    dsps_query_set     = models.DSP.objects.filter(**filter_dict).all()
    unique_currencies  = dsps_query_set.values('dsr_id__currency__code').distinct().all()
    
    # Get the conversion factors we need
    conversion_factors = dict()
    conversion_factors.update({'EUR':1})

    for unique_c in unique_currencies:
        from_currency, to_currency = unique_c['dsr_id__currency__code'], 'EUR'
        conversion_factors.update({from_currency : utils.get_conversion_factor(from_currency, to_currency)})

    # Add exchange rate to queryset
    whens = [When(dsr_id__currency__code=k, then=v) for k, v in conversion_factors.items()]
    qs_with_exchange_rate = dsps_query_set.annotate(exchange_rate=Case(*whens, default=0, output_field=DecimalField()))

    # Add revenue in EUR
    qs_with_revenue_eur = qs_with_exchange_rate.annotate(revenue_eur=F('revenue') * F('exchange_rate')).order_by('-revenue_eur')

    # Calculate total revenue EUR
    target_percentile = (percentile_value/100) * float(qs_with_revenue_eur.aggregate(Sum('revenue_eur'))['revenue_eur__sum'])
    amount_so_far = 0

    count = 0
    for record in qs_with_revenue_eur:
        if amount_so_far <= target_percentile:
            count += 1
            amount_so_far += float(record.revenue_eur)

        else:
            break

    data = core_serializers.serialize('json', qs_with_revenue_eur[0:count])
    return HttpResponse(data, content_type='application/json')

def success(request):
    '''FROM CARLOS: Simple redirect after the form's post'''
    return HttpResponse('DSR file(s) successfully uploaded')

