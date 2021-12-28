import enum

from sqlalchemy import inspect

from sqlalchemy_filtering.exceptions import FieldNotFoundException
from sqlalchemy_filtering.operators import ComparisonOperator


def _construct_field(obj, field):
    if field in obj:
        return obj[field] if type(obj[field]) in _get_numeric_types() else str(obj[field])
    else:
        return None


def __cast_value_field(obj, field):
    attr = getattr(obj, field)
    if isinstance(attr, dict):
        return Filter(attr)
    else:
        return attr


def _construct_value_field(obj, field, class_type):
    if field in obj:
        if type(obj[field]) is list:
            # list of dict objects or simple list
            values = []
            for o in obj[field]:
                if type(o) is dict and class_type in (Filter, Sort):
                    values.append(class_type(o))
                else:
                    values.append(o)
            return values
        else:
            # dict or str cases
            if isinstance(obj[field], dict) and class_type in (Filter, Sort):
                return class_type(obj[field])
            else:
                return _construct_field(obj, field)
    else:
        return None


def _construct_filter_object(obj):
    expressions = []

    if obj and type(obj['filter']) == list:
        # If no operator exists, add the 'and' operator.
        for expression in obj['filter']:
            expressions.append(Filter(expression))
        return {
            "and": expressions
        }
    # Create Filter object
    for key in obj['filter'].keys():
        for expression in obj['filter'][key]:
            expressions.append(Filter(expression))
        obj['filter'][key] = expressions
    return obj['filter']


def _get_numeric_types():
    return float, int, complex


class FilterRequest(object):

    def __init__(self, request) -> None:
        super().__init__()
        self.filter: dict = _construct_filter_object(request)


class Filter(object):

    def __init__(self, obj) -> None:
        super().__init__()
        self.field: str = _construct_field(obj, 'field')
        self.node: str = _construct_field(obj, 'node')
        self.operator: ComparisonOperator = ComparisonOperator(_construct_field(obj, 'operator'))
        self.value = _construct_value_field(obj, 'value', Filter)

    def _get_values_class(self):
        return type(self.value).__name__


class SortRequest(object):
    def __init__(self, request) -> None:
        super().__init__()
        self.sort: [Sort] = _construct_value_field(request, 'sort', Sort)


class Sort(object):

    def __init__(self, obj) -> None:
        super().__init__()
        self.field: str = _construct_field(obj, 'field')
        self.node: str = _construct_field(obj, 'node')
        self.direction: SortDirection = SortDirection(obj['direction'].upper())
        if 'nullLast' in obj:
            self.nullsLast: bool = bool(_construct_field(obj, 'nullsLast'))
        else:
            self.nullsLast: bool = False


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
            raise FieldNotFoundException('Field `{}` not found in model `{}`.'.format(self.field, self.model))
        return getattr(self.model, self.field)

    def get_model_field_info(self):
        inspect_mapper = inspect(self.model)
        columns = inspect_mapper.columns
        details = [
            {
                "name": c.key,
                "type": c.type.python_type
            }
            for c in columns._all_columns
        ]
        return details

    def get_model_field_names(self):
        return inspect(self.model).columns.keys()
