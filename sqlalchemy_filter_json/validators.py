from sqlalchemy import inspect

from sqlalchemy_filter_json.operators import Operator


def _construct_field(obj, field):
    return getattr(obj, field) if hasattr(obj, field) else None


def _construct_value_field(obj, field):
    if hasattr(obj, field):
        attr = getattr(obj, field)
        if isinstance(attr, dict):
            return Filter(attr)
        else:
            return attr
    else:
        return None


class Filter(object):

    def __init__(self, obj) -> None:
        super().__init__()
        self.json_field = _construct_field(obj, 'json_field')
        self.node = _construct_field(obj, 'node')
        self.operator = Operator(_construct_field(obj, 'operator'))
        self.valueType = _construct_field(obj, 'valueType')
        self.values = _construct_value_field(obj, 'values')

    def _get_values_class(self):
        return type(self.values).__name__


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
