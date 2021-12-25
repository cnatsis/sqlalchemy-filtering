import enum

from sqlalchemy import inspect

from sqlalchemy_filter_json.operators import Operator


def _construct_field(obj, field):
    return str(obj[field]) if field in obj else None


def __cast_value_field(obj, field):
    attr = getattr(obj, field)
    if isinstance(attr, dict):
        return Filter(attr)
    else:
        return attr


def _construct_value_field(obj, field, class_type):
    # if hasattr(obj, field):
    if field in obj:
        if type(obj[field]) is list:
            # list of dict objects or simple list
            values = []
            for o in obj[field]:
                if type(o) is dict:
                    if class_type is Filter.__name__:
                        values.append(Filter(o))
                    elif class_type is Sort.__name__:
                        values.append(Sort(o))
                    else:
                        values.append(o)
                else:
                    values.append(o)
            return values
        else:
            # dict or str cases
            return _construct_field(obj, field)
    else:
        return None


def _construct_filter_object(obj):
    expressions = []

    if obj and obj['filter']:
        # If no operator exists, add the 'and' operator.
        # if not any(filter_operator in obj['filter'].keys() for filter_operator in FilterOperator.OPERATORS.keys()):
        if type(obj['filter']) == list:
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


class FilterRequest(object):

    def __init__(self, request) -> None:
        super().__init__()
        self.filter: dict = _construct_filter_object(request)


class Filter(object):

    def __init__(self, obj) -> None:
        super().__init__()
        self.field: str = _construct_field(obj, 'field')
        self.node: str = _construct_field(obj, 'node')
        self.operator: Operator = Operator(_construct_field(obj, 'operator'))
        self.valueType: str = _construct_field(obj, 'valueType')
        self.value = _construct_value_field(obj, 'value', Filter.__name__)

    def _get_values_class(self):
        return type(self.value).__name__


class SortRequest(object):
    def __init__(self, request) -> None:
        super().__init__()
        self.sort: [Sort] = _construct_value_field(request, 'sort', Sort.__name__)


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
