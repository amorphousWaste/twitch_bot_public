"""Database Utils."""

import aiofiles
import aiosqlite
import os
import traceback

from datetime import datetime
from typing import Callable, Optional

from configs import config_utils

from log import LOG


def database_decorator(func: Callable) -> Callable:
    """Commit plugin data to the database.

    Args:
        func (function): Function to run.

    Returns:
        decorated (function): The decorated function output.
    """

    async def decorated(plugin: object, bot: object) -> None:
        """Run the main function of the plugin.

        Args:
            bot (TwitchBot): The bot instance running the plugin.
            plugin (plugin): The plugin being called.
        """
        plugin_name = plugin.__class__.__name__
        user = plugin.user
        has_table = hasattr(plugin, 'TABLE')
        has_fields = hasattr(plugin, 'FIELDS')

        if has_table:
            last_row = await bot.db.get_last_row(plugin.TABLE)
        else:
            last_row = await bot.db.get_last_row(plugin_name)
        LOG.debug('db decorator last_row: {}'.format(dict(last_row)))

        # Run the plugin function.
        function_update_dict = await func(plugin, last_row=last_row)

        # Skip updating the database if the update dict is -1.
        if function_update_dict == -1:
            return

        update_dict = {
            'last_user_id': user['id'],
            'last_run': str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        }

        if has_table and has_fields:
            # Update default plugin table first.
            await bot.db.insert(plugin_name, update_dict)

            # Append the update dict with values from the plugin.
            update_dict.update(function_update_dict)
            # Update the plugin specific table.
            await bot.db.insert(plugin.TABLE, update_dict)

        elif not has_table and has_fields:
            # Append the update dict with values from the plugin.
            update_dict.update(function_update_dict)
            # Update default plugin table with added values..
            await bot.db.insert(plugin_name, update_dict)

        else:
            # Only update default plugin table.
            await bot.db.insert(plugin_name, update_dict)

    return decorated


def check_database_response(func: Callable) -> Callable:
    """Decorator to check the response from the database."""

    async def wrapper(*args, **kwargs) -> object:
        """Check database response code."""
        # Sanitize the arguments.
        args = [
            a.strip().replace(' ', '_') if isinstance(a, str) else a
            for a in args
        ]
        kwargs = {
            k: v.strip().replace(' ', '_') if isinstance(v, str) else v
            for (k, v) in kwargs.items()
        }

        # Ensure the response from the database did not error out.
        try:
            result = await func(*args, **kwargs)

        except Exception as e:
            LOG.error(
                'Unable to communicate properly with database: {}'.format(
                    getattr(e, 'message', repr(e))
                )
            )
            # If the level is 'debug', print the traceback as well.
            if LOG.level == 0:
                traceback.print_exc()
                result = None

        return result

    return wrapper


class Database(object):
    """Database interaction object."""

    def __init__(self) -> None:
        """Init."""
        super(Database, self).__init__()

    async def init(self) -> None:
        """Async init."""
        self.twitch_config = await config_utils.load_config_file('bot_config')
        self.db_path = os.path.join(
            os.path.dirname(__file__), self.twitch_config.get('database_path')
        )

        self.connection = await self._connect_to_db()
        self.connection.row_factory = aiosqlite.Row
        self.cursor = await self.connection.cursor()

        await self._create_default_tables()

        return self

    @check_database_response
    async def _connect_to_db(self, path: str = None):
        """Connect to the database.

        Args:
            path (str): Path to the database.
                If not specified, use the default database path.

        Returns:
            connection (sqlite3.Connection): Connection to the database.
        """
        db_path = path or self.db_path
        LOG.debug(f'Connecting to database at: {db_path}')
        return await aiosqlite.connect(db_path)

    @check_database_response
    async def read(
        self,
        table: str,
        columns: Optional[list] = None,
        queries: Optional[dict] = None,
        select_all: Optional[bool] = False,
    ) -> dict:
        """Read from the database.

        Args:
            table (str): Table name.
            columns (list, optional): Columns to select.
                Default is '*' (all).
            queries (dict, optional): Specific fields and values to search for.
                These are merged with an AND.
            select_all (bool, optional): Whether or not to limit the records.
                Default is False: Select only the latest.
                True returns all data.

        Returns:
            data (list|None): Row(s) from the database in the form:
                [sqlite3.Row1, sqlite3.Row2, sqlite3.Row3, ...]
                If no data is found, None is returned.
        """
        if not columns:
            columns = '*'
        else:
            columns = ', '.join(columns)

        if select_all:
            limit = ''
        else:
            limit = ' LIMIT 1'

        if queries:
            fields = []

            for key in queries:
                fields.append('{} = "{}"'.format(key, queries[key]))

            where = ' WHERE {}'.format(' AND '.join(fields))
        else:
            where = ''

        cmd = f'SELECT {columns} FROM {table}{where} ORDER BY id DESC{limit};'
        await self.cursor.execute(cmd)
        data = await self.cursor.fetchall()

        if data and not select_all:
            data = data[0]

        return data

    @check_database_response
    async def read_range(
        self, table: str, ranges: list, columns: Optional[list] = None
    ) -> dict:
        """Read a range of values from the database.

        Args:
            table (str): Table name.
            ranges (list): List of ranges to search in the form:
                [
                    {'key': key, 'start': start_value, 'end': end_value},
                    {'key': key, 'start': start_value, 'end': end_value},
                ]
            columns (list, optional): Columns to select.
                Default is '*' (all).

        Returns:
            data (list|None): Row(s) from the database in the form:
                [sqlite3.Row1, sqlite3.Row2, sqlite3.Row3, ...]
                If no data is found, None is returned.
        """
        if not columns:
            columns = '*'
        else:
            columns = ', '.join(columns)

        fields = []

        for search_range in ranges:
            key = search_range.get('key')
            start = search_range.get('start')
            end = search_range.get('end')
            fields.append(f'{key} >= "{start}" AND {key} <= "{end}"')

        where = 'WHERE {}'.format(' AND '.join(fields))

        cmd = f'SELECT {columns} FROM {table} {where};'
        await self.cursor.execute(cmd)
        data = await self.cursor.fetchall()

        return data

    @check_database_response
    async def commit(self) -> None:
        """Commit to database."""
        await self.connection.commit()

    @check_database_response
    async def close(self) -> None:
        """Close database."""
        await self.connection.close()

    @check_database_response
    async def insert(self, table: str, data: dict) -> None:
        """Add a new entry into the database.

        Args:
            table (str): Table name.
            data (dict): Dictionary of column: value.
        """
        fields = []
        values = []

        for key in data:
            fields.append(key)
            values.append(str(data[key]))

        cmd = 'INSERT INTO {table}({fields}) VALUES("{values}")'.format(
            table=table,
            fields=', '.join(fields),
            values='", "'.join(values),
        )

        await self.cursor.execute(cmd)
        await self.commit()

    @check_database_response
    async def update(self, table: str, data: dict, conditions: dict) -> None:
        """Update the database.

        Args:
            table (str): Table name.
            data (dict): Dictionary of column: value.
            conditions (dict): Target of the update(s) (corresponds to rows).
        """
        fields = []
        targets = []

        for data_key in data:
            fields.append('{} = "{}"'.format(data_key, data[data_key]))

        for condition_key in conditions:
            targets.append(
                '{} = "{}"'.format(condition_key, conditions[condition_key])
            )

        cmd = 'UPDATE {table} SET {fields} WHERE {targets}'.format(
            table=table,
            fields=', '.join(fields),
            targets=', '.join(targets),
        )

        await self.cursor.execute(cmd)
        await self.commit()

    @check_database_response
    async def delete(self, table: str, conditions: dict) -> None:
        """Delete a row from the database.

        Args:
            table (str): Table name.
            conditions (dict): Target of the update(s) (corresponds to rows).
        """
        targets = []
        for condition_key in conditions:
            targets.append(
                '{} = "{}"'.format(condition_key, conditions[condition_key])
            )

        cmd = 'DELETE FROM {table} WHERE {targets}'.format(
            table=table,
            targets=', '.join(targets),
        )

        await self.cursor.execute(cmd)
        await self.commit()

    @check_database_response
    async def create_table(self, name: str, fields: dict = None) -> None:
        """Create a table in the database.

        Args:
            name (str): Table name.
            fields (dict): Dictionary of fields: data types.
                If not given, only defaults will be used.
        """
        base_cmd = [
            'id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT',
            'last_user_id INTEGER NOT NULL',
            'last_run TEXT DEFAULT "1970-01-01 00:00:00"',
        ]

        if not fields:
            fields = {}

        for key in fields:
            data_types = fields[key]
            base_cmd.append(f'{key} {data_types}')

        cmd = (
            f'CREATE TABLE IF NOT EXISTS {name} ('
            + ', '.join(base_cmd)
            + ', FOREIGN KEY(last_user_id) REFERENCES users(id));'
        )
        await self.cursor.execute(cmd)
        await self.commit()

    @check_database_response
    async def drop_table(self, name: str) -> None:
        """Drop a table from the database.

        Args:
            name (str): Table name.
        """
        cmd = f'DROP TABLE {name};'
        await self.cursor.execute(cmd)
        await self.commit()

    @check_database_response
    async def _backup_db(self) -> None:
        """Backup the database."""
        time = str(datetime.now())
        backup_db_path = os.path.join(
            os.path.dirname(self.db_path), f'backup_{time}.db'
        )
        backup_db = await self._connect_to_db(backup_db_path)
        await self.connection.backup(backup_db)

    @check_database_response
    async def _create_default_tables(self) -> None:
        """Create the users table."""
        db_script = os.path.join(
            os.path.dirname(__file__), 'create_tables.sql'
        )
        async with aiofiles.open(db_script, 'r') as in_file:
            await self.cursor.executescript(await in_file.read())

    @check_database_response
    async def _get_tables(self) -> list:
        """Get all the tables.

        Returns:
            (list): List of tables in the database.
        """
        await self.cursor.execute(
            'SELECT name FROM sqlite_master WHERE type="table";'
        )
        return [table[0] for table in await self.cursor.fetchall()]

    @check_database_response
    async def count_rows(self, table: str) -> int:
        """Count the number of rows in a table.

        Args:
            table (str): Table name.

        Returns:
            (int): The number of rows in the table.
        """
        result = await self.cursor.execute(f'SELECT COUNT(*) FROM {table}')
        return (await result.fetchone())[0]

    @check_database_response
    async def add_column(
        self, table: str, column: str, data_type: str
    ) -> None:
        """Add a column to a table.

        Args:
            table (str): Table name.
            column (str): Column name to add.
            data_type (str): Data type of the new column.
        """
        cmd = f'ALTER TABLE {table} ADD {column} {data_type};'
        await self.cursor.execute(cmd)

    async def get_last_row(self, table: str) -> dict:
        """Get the last row from the table.

        Args:
            table (str): Table name.

        Returns:
            data (list|None): Row(s) from the database in the form:
                [sqlite3.Row1, sqlite3.Row2, sqlite3.Row3, ...]
                If no data is found, None is returned.
        """
        if table not in await self._get_tables():
            LOG.warning(f'No table named {table}.')
            last_row = ()
        else:
            last_row = await self.read(table)

        return last_row
