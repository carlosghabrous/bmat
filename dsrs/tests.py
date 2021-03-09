from django.test import Client, TestCase
from dsrs.models import DSR, Territory, Currency

from random import randint

# Create your tests here.
class DsrTests(TestCase):
    
    def setUp(self):
        # Add data into the DB (ideally, much more, this is just a sample)
        currency   = Currency(name='Euro', symbol='8888', code='EUR')
        territory  = Territory(name='Spain', code_2='ES', code_3='ESP', local_currency=currency)
        currency.save()
        territory.save()

        dsr_model_data = {'path':'some/random/path', 'period_start':'2020-01-01', 'period_end':'2020-01-31', 'status':'FAILED', 'territory':territory, 'currency':currency}
        DSR.objects.create(**dsr_model_data)

        # Get client
        self.client = Client()


    def test_get_all_dsr_records_returns_OK_code(self):
        response = self.client.get('/dsrs/')
        self.assertEqual(response.status_code, 200)

    def test_get_all_dsr_records_length_is_correct(self):
        response = self.client.get('/dsrs/', HTTP_ACCEPT='application/json')    
        dsr_records_number_db = DSR.objects.filter(pk=1).count()
        dsr_records_number_get_response = len(response.json())

        self.assertEqual(dsr_records_number_db, dsr_records_number_get_response)

    def test_get_single_dsr_record_returns_OK_code(self):
        response = self.client.get('/dsrs/', HTTP_ACCEPT='application/json')
        number_records = len(response.data)

        dsr_record_number = randint(1, number_records)
        dsr_record = self.client.get(f'/dsrs/{dsr_record_number}/', HTTP_ACCEPT='application/json')
        self.assertEqual(dsr_record.status_code, 200)

    def test_get_invalid_dsr_record_returns_404_response(self):
        response = self.client.get('/dsrs/', HTTP_ACCEPT='application/json')
        number_records = len(response.json())

        dsr_record = self.client.get(f'/dsrs/{number_records + 1}/', HTTP_ACCEPT='application/json')
        self.assertEqual(dsr_record.status_code, 404)

    def test_get_percentile_within_range_returns_OK_response(self):
        percentile = randint(1, 100)
        response = self.client.get(f'/resources/percentile/{percentile}/', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

    def test_get_percentile_out_of_range_returns_404_response(self):
        percentile = 101
        response = self.client.get(f'/resources/percentile/{percentile}/', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 400)

        percentile = 0
        response = self.client.get(f'/resources/percentile/{percentile}/', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 400)

    def test_get_percentile_limit_values_returns_OK_response(self):
        percentile = 1
        response = self.client.get(f'/resources/percentile/{percentile}/', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 400)

        percentile = 100
        response = self.client.get(f'/resources/percentile/{percentile}/', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 400)

    def test_get_percentile_with_query_params_returns_OK_response(self):
        percentile = randint(1, 100)
        response = self.client.get(f'/resources/percentile/{percentile}/', {'country':'ES', 'currency':'EUR', 'period_start':'2020-01-01', 'period_end':'2020-01-30'}, HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, 200)

        
        

