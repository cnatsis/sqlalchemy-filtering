from enum import Enum

from sqlalchemy import or_, and_, not_

from sqlalchemy_filtering.exceptions import OperatorNotFoundException


class ComparisonOperator:
    OPERATORS = {
        'is': lambda left, right: left.is_(right),
        '==': lambda left, right: left == right,
        'eq': lambda left, right: left == right,

        'is_not': lambda left, right: left.isnot(right),
        '!=': lambda left, right: left != right,
        'ne': lambda left, right: left != right,

        'is_null': lambda left: left.is_(None),
        'is_not_null': lambda left: left.isnot(None),

        '>': lambda left, right: left > right,
        'gt': lambda left, right: left > right,

        '<': lambda left, right: left < right,
        'lt': lambda left, right: left < right,

        '>=': lambda left, right: left >= right,
        'ge': lambda left, right: left >= right,

        '<=': lambda left, right: left <= right,
        'le': lambda left, right: left <= right,

        'like': lambda left, right: left.like(right),
        'not_like': lambda left, right: left.not_like(right),

        'ilike': lambda left, right: left.ilike(right),
        'not_ilike': lambda left, right: left.notilike(right),

        'in': lambda left, right: left.in_(right),
        'not_in': lambda left, right: left.not_in(right),

        'contains': lambda left, right: left.contains(right),
        'any': lambda left, right: left.any(right),

        'match': lambda left, right: left.match(right),
        'starts_with': lambda left, right: left.startswith(right),

        # PostgreSQL specific operators
        '@>': lambda left, right: left.op('@>')(right),  # 'contains' equivalent
        '<@': lambda left, right: left.op('<@')(right),
        '@?': lambda left, right: left.op('@?')(right),
        '@@': lambda left, right: left.op('@@')(right)
    }

    def __init__(self, operator=None):
        if not operator:
            operator = '=='
        if operator not in self.OPERATORS:
            raise OperatorNotFoundException('ComparisonOperator `{}` is not valid.'.format(operator))

        self.operator = operator
        self.function = self.OPERATORS[operator]

    def execute(self, **kwargs):
        return self.OPERATORS.get(self.operator)(**kwargs)


class FilterOperator:
    OPERATORS = {
        # 1. SQLAlchemy function
        # 2. Positional argument produce an "empty" or dynamically generated filter
        # not_ operator takes only one argument as input
        'and': (and_, True),
        'or': (or_, False),
        'not': (not_, None),
    }

    def __init__(self, operator=None):
        if not operator:
            operator = 'and'
        if operator not in self.OPERATORS:
            raise OperatorNotFoundException('FilterOperator `{}` is not valid.'.format(operator))

        self.operator = operator
        self.function = self.OPERATORS[operator]

    def execute(self, *args):
        func, argument = self.OPERATORS.get(self.operator)
        if argument is None:
            # Execute multiple not_ operators with AND clause
            funcs = []
            for arg in args:
                funcs.append(func(arg))
            return and_(True, *funcs)
        else:
            return func(argument, *args)


class SQLDialect(Enum):
    POSTGRESQL = 'postgresql'
    MYSQL = 'mysql'
