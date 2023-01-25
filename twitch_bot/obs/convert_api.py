#!/usr/bin/env python

"""Generate the API classes from the JSON documentation.
Only 'requests' and 'events' are processed, 'typedefs' are unneeded.
"""

import black
import json
import os
import re

from datetime import datetime
from black.mode import TargetVersion
from urllib.request import urlopen

BLACK_FILE_MODE = black.FileMode(
    target_versions=set([TargetVersion.PY39]),
    line_length=79,
    string_normalization=False,
)
IMPORT_URL = 'https://raw.githubusercontent.com/Palakis/obs-websocket/4.x-current/docs/generated/comments.json'  # noqa
OUTPUT_DIR = os.path.abspath(os.path.dirname(__file__))
PARAM_RE = re.compile(
    r'(?P<type1>[a-zA-Z]+)(\<(?P<subtype>[a-zA-Z]+)\>)?(\s\|\s(?P<type2>[a-zA-Z]+))?(\s\((?P<optional>optional)\))?'  # noqa
)


class Property(object):
    """Property object."""

    def __init__(self, name: str, param_type: str, description: str) -> None:
        """Init."""
        super(Property, self).__init__()

        self.name = name
        self.clean_name = clean_name(self.name)

        matches = re.match(PARAM_RE, param_type)
        match_dict = matches.groupdict() if matches else {}
        self.type = self._get_type(match_dict.get('type1', ''))
        self.type2 = self._get_type(match_dict.get('type2', ''))
        self.subtype = match_dict.get('subtype', '')
        self.optional = True if match_dict.get('optional', '') else False
        self.description = description.strip()

    def _get_type(self, param_type: str) -> str:
        """Convert parameter type to python type if possible.

        Args:
            param_type (str): Parameter type.

        Returns:
            (Any): The corresponding python type.
        """
        types = {
            'array': 'list',
            'boolean': 'bool',
            'double': 'int',
            'integer': 'int',
            'object': 'object',
            'number': 'int',
            'string': 'str',
        }
        if str(param_type).lower() in types.keys():
            return types[param_type.lower()]
        else:
            return param_type

    def __str__(self) -> str:
        """String representation."""
        str_repr = []

        dict_repr = self.__dict__()
        for key in dict_repr:
            str_repr.append(f'{key}: {dict_repr[key]}')

        return ', '.join(str_repr)

    def __dict__(self) -> dict:
        """Dictionary representation."""
        return {
            'name': self.name,
            'clean_name': self.clean_name,
            'type': self.type,
            'type2': self.type2,
            'subtype': self.subtype,
            'description': self.description,
            'optional': self.optional,
        }


class Argument(Property):
    """Argument class."""

    def __init__(self, data: dict) -> None:
        """Init.

        Args:
            data (dict): Argument data.
        """
        super(Argument, self).__init__(
            name=data.get('name', ''),
            param_type=data.get('type', ''),
            description=data.get('description', ''),
        )


class Return(Property):
    """Return class."""

    def __init__(self, data: dict) -> None:
        """Init.

        Args:
            data (dict): Return data.
        """
        super(Return, self).__init__(
            name=data.get('name', ''),
            param_type=data.get('type', ''),
            description=data.get('description', ''),
        )


class OBSCall(object):
    """OBS call object."""

    def __init__(self, api_def: dict) -> None:
        """Init.

        Args:
            api_def (dict): Definition of an API call.
        """
        super(OBSCall, self).__init__()

        self.api = api_def.get('api', '')
        self.category = api_def.get('category', '')
        self.description = api_def.get('description', '').strip()
        self.name = api_def.get('name', '')
        self.clean_name = clean_name(self.name)
        self.since = api_def.get('since', '')

        self.args = sorted(
            [Argument(a) for a in api_def.get('params', [])],
            key=lambda aa: (aa.optional, aa.name),
        )
        self.returns = sorted(
            [Return(r) for r in api_def.get('returns', [])],
            key=lambda rr: (rr.name),
        )

    def __str__(self) -> str:
        """String representation."""
        str_repr = []

        dict_repr = self.__dict__()
        for key in dict_repr:
            str_repr.append(f'{key}: {dict_repr[key]}')

        return ', '.join(str_repr)

    def __dict__(self) -> dict:
        """Dictionary representation."""
        return {
            'api': self.api,
            'category': self.category,
            'description': self.description,
            'name': self.name,
            'since': self.since,
            'args': [str(a) for a in self.args],
            'returns': [str(r) for r in self.returns],
        }


def download_json() -> dict:
    """Download the API json file.

    Returns:
        data (dict): API data as a dictionary.
    """
    print(f'Downloading {IMPORT_URL} ...')
    with urlopen(IMPORT_URL) as url_file:
        data = json.loads(url_file.read().decode('utf-8'))

    return data


def clean_name(name: str) -> str:
    """Clean the name of the property.

    Args:
        name (str): Given name.

    Returns:
        name (str): Cleaned name.
    """
    for char in ['-', '.', ' ', '*']:
        name = name.replace(char, '_')
    return name


def create_calls(data: dict) -> dict[list]:
    """Turn the json data into call objects.

    Args:
        data (dict): JSON API data.

    Returns:
        calls (dict[list]): Dictionary of OBSCall objects.
    """
    calls = {'requests': [], 'events': []}
    for category in calls.keys():
        call_list = []
        for section in data[category]:
            for api_def in data[category][section]:
                call = OBSCall(api_def)
                call_list.append(call)

        calls[category] = sorted(call_list, key=lambda c: c.name)

    return calls


def write_to_file(category: str, data: dict) -> None:
    """Write data to the appropriate files.

    Args:
        category (str): Category of file.
        data (dict): Data to write.
    """
    to_write = black.format_str('\n'.join(data), mode=BLACK_FILE_MODE)
    with open(os.path.join(OUTPUT_DIR, f'obs_{category}.py'), 'w') as in_file:
        in_file.write(to_write)


def write_header(category: str) -> list[str]:
    """Write the document header.

    Args:
        category (str): Category name.

    Returns:
        header (list): Header as a joinable list.
    """
    header = []
    header.append(
        '# Auto-generated by the generate_classes.py file on: '
        '{}. #\n'.format(datetime.now().strftime('%Y/%m/%d'))
    )

    header.append('from typing import Optional\n')
    header.append(f'from obs.obs_base_classes import Base{category.title()}')
    header.append('\n')

    return header


def write_docstring(call: OBSCall) -> list[str]:
    """Write the class docstring for the given call.

    Args:
        call (OBSCall): Current call.

    Returns:
        docstring (list): Docstring as a joinable list.
    """
    docstring = []
    docstring.append(f'    \"\"\"{call.description}')

    if call.args:
        docstring.append('\n    Args:')
        for arg in call.args:
            arg_text = f'        {arg.name} ({arg.type}'

            if arg.type2:
                arg_text += f' | {arg.type2}'

            if arg.optional:
                arg_text += ', optional'

            arg_text += ')'

            arg_text += f': {arg.description}'
            docstring.append(f'{arg_text}')

    if call.returns:
        docstring.append('\n    Returns:')

        for ret in call.returns:
            docstring.append(
                f'        {ret.name} ({ret.type}): {ret.description}'
            )

    docstring.append('    \"\"\"\n')

    return docstring


def convert_api():
    """Generates the necessary classes."""
    data = download_json()
    print('Generating python files...')

    calls = create_calls(data)

    for category in calls.keys():
        write_data = []
        write_data.extend(write_header(category))

        for call in calls[category]:
            write_data.append(f'class {call.name}(Base{category.title()}):')
            write_data.extend(write_docstring(call))

            write_data.append('    def __init__(self):')
            write_data.append('        \"\"\"Init.\"\"\"\n')
            write_data.append(f'        super({call.name}, self).__init__()')

            write_data.append(
                '    async def init({}):'.format(
                    ", ".join(
                        ['self']
                        + [
                            f'{a.clean_name}: {a.type}'
                            for a in call.args
                            if not a.optional
                        ]
                        + [
                            f'{a.clean_name}: Optional[{a.type}] = None'
                            for a in call.args
                            if a.optional
                        ],
                    )
                )
            )
            write_data.append('        \"\"\"Async init.\"\"\"\n')
            write_data.append(f'        self.name = \'{call.name}\'')

            for ret in call.returns:
                write_data.append(
                    f'        self.data_in[\'{ret.name}\'] = None'
                )

            for arg in call.args:
                write_data.append(
                    f'        self.data_out[\'{arg.name}\'] = {arg.clean_name}'
                )

            write_data.append('        return self')

            for ret in call.returns:
                def_string = f'    async def get_{ret.clean_name}(self):'
                if ret == call.returns[0]:
                    def_string = '\n' + def_string
                write_data.append(def_string)

                return_str = f'        return self.data_in[\'{ret.name}\']'
                if ret != call.returns[-1]:
                    return_str += '\n'
                write_data.append(return_str)

            write_data.append('\n')

        write_to_file(category, write_data)

    print('Done.')


if __name__ == '__main__':
    convert_api()
