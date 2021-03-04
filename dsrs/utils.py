import gzip
from collections  import namedtuple
from datetime     import datetime
from pathlib      import Path

DATA_DIR = Path(__file__).parent.parent.absolute() / 'data'

dsr_record_fields  = ('dsp_id', 'title', 'artists', 'isrc', 'usages', 'revenue')
DsrRecord          = namedtuple('DsrRecord', dsr_record_fields, defaults=(None,) * len(dsr_record_fields))

dsr_meta_fields    = ('path', 'territory', 'currency', 'period_start', 'period_end')
DsrMetaData        = namedtuple('DsrMetaData', dsr_meta_fields)

def _reformat_date(date):
    dobj = datetime.strptime(date, '%Y%m%d')
    return datetime.strftime(dobj, '%Y-%m-%d')

def _handle_gzip_file(file_name):
    with gzip.open(file_name, 'r') as fh:
        return _handle_tsv_file_with_handler(fh, file_name, compressed=True)

def _handle_tsv_file(file_name):
    with open(file_name) as fh:
        return _handle_tsv_file_with_handler(fh, file_name)

def _handle_tsv_file_with_handler(fh, file_name, compressed=False):
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
        dsr_record = DsrRecord(*decoded_line.strip().split('\t'))
        dsr_records['data'].append(dsr_record)

    return dsr_records


_file_handlers = {
    '.gz' : _handle_gzip_file,
    '.tsv' : _handle_tsv_file
}


def parse_dsr_file(file_name):
    file_path = Path(file_name)

    try:
        record_list = _file_handlers[file_path.suffix](Path(DATA_DIR) / file_name)

    except KeyError:
        raise KeyError(f'Cannot handle files of extension {file_path.suffix}')

    else:
        return record_list
