import enum

from sqlalchemy import inspect

from sqlalchemy_filter_json.operators import Operator


def _construct_field(obj, field):
    return obj[field] if field in obj else None
    # return getattr(obj, field) if hasattr(obj, field) else None


def __cast_value_field(obj, field):
    attr = getattr(obj, field)
    if isinstance(attr, dict):
        return Filter(attr)
    else:
        return attr


def _construct_value_field(obj, field):
    # if hasattr(obj, field):
    if field in obj:
        if type(obj[field]) is list:
            # list of dict objects or simple list
            values = []
            for o in obj[field]:
                if type(o) is dict:
                    values.append(Filter(o))
                else:
                    values.append(o)
            return values
        else:
            # dict or str cases
            return _construct_field(obj, field)
    else:
        return None


class FilterRequest(object):

    def __init__(self, request) -> None:
        super().__init__()
        self.filter: [Filter] = _construct_value_field(request, 'filter')
        self.sort: [Sort] = _construct_value_field(request, 'sort')


class Filter(object):

    def __init__(self, obj) -> None:
        super().__init__()
        self.json_field: str = str(_construct_field(obj, 'json_field'))
        self.node: str = str(_construct_field(obj, 'node'))
        self.operator: Operator = Operator(_construct_field(obj, 'operator'))
        self.valueType: str = str(_construct_field(obj, 'valueType'))
        self.value = _construct_value_field(obj, 'value')

    def _get_values_class(self):
        return type(self.value).__name__


class Sort(object):

    def __init__(self, obj) -> None:
        super().__init__()
        self.json_field: str = str(_construct_field(obj, 'json_field'))
        self.node: str = str(_construct_field(obj, 'node'))
        self.direction: SortDirection = SortDirection(obj['direction'].upper())
        self.nullsLast: bool = bool(_construct_field(obj, 'nullsLast'))


class SortDirection(enum.Enum):
    ASC = 'ASC'
    DESC = 'DESC'


class SQLAlchemyField(object):

    def __init__(self, model, field) -> None:
        super().__init__()
        self.model = model
        self.field = field

    def get_field(self):
        if self.field not in self.get_model_field_names():
            raise Exception('Field `{}` not found model `{}`'.format(self.field, self.model))
        return getattr(self.model, self.field)

    def get_model_field_info(self):
        inspect_mapper = inspect(self.model)
        columns = inspect_mapper.columns
        details = []
        for c in columns._all_columns:
            elem = {
                "name": c.key,
                "type": c.type.python_type
            }
            details.append(elem)
        return details

    def get_model_field_names(self):
        return inspect(self.model).columns.keys()
