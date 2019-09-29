from decimal import Decimal, DivisionImpossible
import copy


def float_to_decimal(input):
    return convert(input, 'to_decimal')


def decimal_to_float(input):
    return convert(input, 'to_float')


def convert(input, conversion):
    """Convert value or values in dict/list from/to Decimal."""

    output = copy.deepcopy(input)
    if isinstance(output, dict):
        convert_in_dict(output, conversion)
    if isinstance(output, list):
        convert_in_list(output, conversion)
    else:
        if conversion == 'to_float':
            if isinstance(output, Decimal):
                try:
                    if output % 1 == 0:
                        output = int(output)
                    else:
                        output = float(output)
                except DivisionImpossible:
                    output = float(output)
        elif conversion == 'to_decimal':
            if (isinstance(output, (int, float, complex)) and
                not isinstance(output, bool)):
                output = Decimal(output)
    return output


def convert_in_dict(dict_, conversion):
    for k, v in dict_.items():
        dict_[k] = convert(v, conversion)


def convert_in_list(list_, conversion):
    for i, v in enumerate(list_):
        list_[i] = convert(v, conversion)
