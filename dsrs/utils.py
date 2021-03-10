import ast
import gzip
import requests
from collections  import namedtuple
from datetime     import datetime
from pathlib      import Path

DATA_DIR = Path(__file__).parent.parent.absolute() / 'data'


class DsrRecord:
    '''FROM CARLOS: This class represents a DSR's file row.
    
    The only particularity is that usages and revenue have been set as keyword arguments. This is because DSR files can
    contain an empty value for these fields. In order to feed something correct to the database, these fields are initialized
    by default to their 'null' values, 0 and 0.0, respectively. 
    '''

    def __init__(self, dsp_id, title, artists, isrc, usages=0, revenue=0.0):
        self.dsp_id   = dsp_id
        self.title    = title
        self.artists  = artists
        self.isrc     = isrc
        self.usages   = usages 
        self.revenue  = revenue

    def __repr__(self):
        return f'<DsrRecord(dsp_id={self.dsp_id}, title={self.title}, artists={self.artists}, isrc={self.isrc}, usages={self.usages}, revenue={self.revenue})>'

'''FROM CARLOS: A namedtuple collection to store the DSR file metadata'''
dsr_meta_fields    = ('path', 'territory', 'currency', 'period_start', 'period_end')
DsrMetaData        = namedtuple('DsrMetaData', dsr_meta_fields)


def _reformat_date(date):
    '''FROM CARLOS: Reformats dates into an appropriate format'''
    dobj = datetime.strptime(date, '%Y%m%d')
    return datetime.strftime(dobj, '%Y-%m-%d')

def _handle_gzip_file(file_name):
    '''FROM CARLOS: Handles compressed files'''
    with gzip.open(file_name, 'r') as fh:
        return _handle_tsv_file_with_handler(fh, file_name, compressed=True)

def _handle_tsv_file(file_name):
    '''FROM CARLOS: Handles uncompressed files'''
    with open(file_name) as fh:
        return _handle_tsv_file_with_handler(fh, file_name)

def _handle_tsv_file_with_handler(fh, file_name, compressed=False):
    '''FROM CARLOS: Shared code between compressed/uncompressed files'''
    dsr_records = dict()

    _, _, territory, currency, rest = file_name.name.split('_')
    period_start, period_end_dirty = rest.split('-')
    period_end = period_end_dirty.split('.')[0]

    ps = _reformat_date(period_start)
    pe = _reformat_date(period_end)

    dsr_meta_data = DsrMetaData(file_name.parents[0], territory, currency, ps, pe)
    dsr_records['meta'] = dsr_meta_data
    dsr_records['data'] = list()

    for line in fh.readlines():
        decoded_line = line if not compressed else line.decode()
        if 'dsp_id' in decoded_line:
            continue

        dsr_record = DsrRecord(*decoded_line.strip().split('\t'))
        dsr_records['data'].append(dsr_record)

    return dsr_records


'''FROM CARLOS: "kind-of-factory" implemented with a dictionary'''
_file_handlers = {
    '.gz' : _handle_gzip_file,
    '.tsv' : _handle_tsv_file
}


def parse_dsr_file(file_name):
    '''FROM CARLOS: Returns a record list from the parsed .tsv files'''
    file_path = Path(file_name)

    try:
        record_list = _file_handlers[file_path.suffix](Path(DATA_DIR) / file_name)

    except KeyError:
        raise KeyError(f'Cannot handle files of extension {file_path.suffix}')

    else:
        return record_list


def get_conversion_factor(from_currency, to_currency):
    '''FROM CARLOS: Gets the conversion rates for certain currencies'''
    conversion_query_string = from_currency + '_' + to_currency
    conversion = requests.get(f'https://free.currconv.com/api/v7/convert?q={conversion_query_string}&compact=ultra&apiKey=6cd9d6b95b3d077a16dc').text
    return ast.literal_eval(conversion).get(conversion_query_string, 0)
