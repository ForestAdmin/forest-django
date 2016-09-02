from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from django.db import models
from forest.services import filter_generator
from forest.services import utils


def _get_filters(params):
    filters = []
    for item in params.get('filters', []):
        filters.append(filter_generator.get(item['field'], item['value']))

    all_filters = utils.merge_dicts(*filters)
    return all_filters


def _get_custom_select(params):
    select = {}
    group_by_date_field = params.get('group_by_date_field')
    time_range = params.get('time_range')
    if time_range == 'Day':
        select['day'] = 'date(%s)' % group_by_date_field
    elif time_range == 'Month':
        select['month'] = "extract(month FROM %s)" % group_by_date_field
        select['year'] = "extract(year FROM %s)" % group_by_date_field
    elif time_range == 'Year':
        select['year'] = "extract(year FROM %s)" % group_by_date_field
    elif time_range == 'Week':
        select['week'] = "date_trunc('week', %s)" % group_by_date_field

    return select


def _get_aggregate(params):
    aggregate = params.get('aggregate')
    if aggregate == 'Week':
        aggregate = 'WeekCount'
    return getattr(models, aggregate)


def _format_data(data, params):
    time_range = params.get('time_range')
    day = 1
    month = 1

    for item in data:
        if time_range == 'Day':
            date = item.pop('day')
            day = date.day
            month = date.month
            year = date.year
        elif time_range == 'Month':
            month = int(item.pop('month'))
            year = int(item.pop('year'))
        elif time_range == 'Year':
            year = int(item.pop('year'))
        elif time_range == 'Week':
            date = item.pop('week')
            year = date.year
            month = date.month
            day = date.day

        item['label'] = "%d-%02d-%02d" % (year, month, day)
        item['values'] = { 'value': item.pop('value') }

    _sort_data_by_date(data)
    _fill_empty_date(data, params)


def _sort_data_by_date(data):
    data.sort(key=lambda item:item['label'])


def _label_to_datetime(label):
    return datetime.strptime(label, '%Y-%m-%d')


def _datetime_to_label(date):
    return date.strftime('%Y-%m-%d')


def _find_by_label(data, label):
    return any(item['label'] == label for item in data)


def _fill_empty_date(data, params):
    time_range = params.get('time_range')
    relativedelta_param = { '%ss' % time_range.lower(): 1 }
    start_date = _label_to_datetime(data[0]['label'])
    end_date = _label_to_datetime(data[-1]['label'])
    while start_date < end_date:
        start_date = start_date + relativedelta(**relativedelta_param)
        label = _datetime_to_label(start_date)
        item = _find_by_label(data, label)
        if not item:
            data.append({ 'label': label, 'values': { 'value': 0 } })

    _sort_data_by_date(data)


def perform(params, model_name):
    model = utils.get_model_class(model_name)
    filters = _get_filters(params)
    select = _get_custom_select(params)
    values = select.keys()
    aggregate = _get_aggregate(params)
    query = model.objects.filter(**filters).extra(select=select).values(*values)
    query = query.annotate(value=aggregate(params.get('group_by_date_field')))
    data = list(query)
    _format_data(data, params)
    return { 'value': data }


