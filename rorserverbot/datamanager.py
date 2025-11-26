# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
from pathlib import Path
import logging
from dataclasses import fields, is_dataclass
from typing import Type, TypeVar, List, Optional, Any, get_origin, get_args

import aiosqlite


LOG = logging.getLogger('rorserverbot.dbm')
T = TypeVar('T')


class DataManager:
    """SQLite data manager.

    Example::

        async with DataManager(Path("database.db")) as dm:
            await dm.create_table(MyDataClass)
            obj = MyDataClass(id=1, name="example")
            await dm.insert(obj)
            results = await dm.select_all(MyDataClass)
    """

    TYPE_MAPPING = {
        int: 'INTEGER',
        str: 'TEXT',
        float: 'REAL',
        bool: 'INTEGER',
        bytes: 'BLOB',
    }

    def __init__(self, db_path: Path):
        """
        Initialize the data manager with the given database path.

        :param db_path: Path to the SQLite database file.
        :type db_path: Path
        """
        self.db_path = db_path
        self.connection = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def connect(self):
        LOG.info(f"Connecting to database: {self.db_path}")
        self.connection = await aiosqlite.connect(self.db_path)
        self.connection.row_factory = aiosqlite.Row

    async def close(self):
        LOG.info("Closing database connection")
        if self.connection:
            await self.connection.close()

    def _get_table_name(self, dataclass_type: Type) -> str:
        return dataclass_type.__name__.lower() + 's'

    def _python_type_to_sql(self, python_type: Type) -> str:
        # Handle Optional types
        origin = get_origin(python_type)
        if origin is not None:
            args = get_args(python_type)
            if len(args) > 0:
                python_type = args[0]

        return self.TYPE_MAPPING.get(python_type, 'TEXT')

    async def create_table(self, dataclass_type: Type[T]):
        """
        Create a table for a dataclass if it doesn't exist.

        :param dataclass_type: The dataclass type
        :type dataclass_type: Type[T]

        :return: None
        :rtype: None

        :raises ValueError: If the provided type is not a dataclass
        :rtype: None
        """
        if not is_dataclass(dataclass_type):
            raise ValueError(f"{dataclass_type} is not a dataclass")

        table_name = self._get_table_name(dataclass_type)
        columns = []

        for field in fields(dataclass_type):
            col_name = field.name
            col_type = self._python_type_to_sql(field.type)

            # Make 'id' the primary key if it exists
            if col_name == 'id':
                columns.append(f"{col_name} {col_type} PRIMARY KEY")
            else:
                columns.append(f"{col_name} {col_type}")

        columns_sql = ', '.join(columns)
        create_table_sql = (f"CREATE TABLE IF NOT EXISTS {table_name}"
                            f"({columns_sql})")

        LOG.debug(f"Creating table with SQL: {create_table_sql}")
        await self.connection.execute(create_table_sql)
        await self.connection.commit()

    async def insert(self, obj: T) -> int:
        """
        Insert a dataclass instance into the database.

        :param obj: The dataclass instance to insert.
        :type obj: T

        :return: The ID of the inserted row.
        :rtype: int
        :raises ValueError: If the provided object is not a dataclass instance.
        :rtype: int
        """
        if not is_dataclass(obj):
            raise ValueError(f"{obj} is not a dataclass instance")

        dataclass_type = type(obj)
        table_name = self._get_table_name(dataclass_type)

        # Ensure table exists
        await self.create_table(dataclass_type)

        # Get field names and values
        field_names = [f.name for f in fields(obj)]
        values = [getattr(obj, f.name) for f in fields(obj)]

        # Create INSERT statement
        placeholders = ', '.join(['?' for _ in field_names])
        columns = ', '.join(field_names)
        insert_sql = (f"INSERT INTO {table_name} ({columns}) VALUES"
                      f" ({placeholders})")

        LOG.debug(f"Inserting with SQL: {insert_sql} and values: {values}")

        cursor = await self.connection.execute(insert_sql, values)
        await self.connection.commit()

        return cursor.lastrowid

    async def insert_many(self, objects: List[T]):
        """
        Insert multiple dataclass instances into the database.

        :param objects: List of dataclass instances to insert
        :type objects: List[T]

        :return: None
        :rtype: None
        :raises ValueError: If the provided objects are not dataclass instances
        :rtype: None
        """
        if not objects:
            return

        if not is_dataclass(objects[0]):
            raise ValueError(f"{objects[0]} is not a dataclass instance")

        dataclass_type = type(objects[0])
        table_name = self._get_table_name(dataclass_type)

        # Ensure table exists
        await self.create_table(dataclass_type)

        # Get field names
        field_names = [f.name for f in fields(objects[0])]

        # Create INSERT statement
        placeholders = ', '.join(['?' for _ in field_names])
        columns = ', '.join(field_names)
        insert_sql = (f"INSERT INTO {table_name} ({columns}) VALUES "
                      f"({placeholders})")

        # Get all values
        all_values = []
        for obj in objects:
            values = [getattr(obj, f.name) for f in fields(obj)]
            all_values.append(values)

        LOG.debug(f"Inserting many with SQL: {insert_sql} and values: "
                  f"{all_values}")

        await self.connection.executemany(insert_sql, all_values)
        await self.connection.commit()

    async def update(self, obj: T, where_field: str = 'id'):
        """
        Update a dataclass instance in the database.

        :param obj: The dataclass instance to
        :type obj: T
        :param where_field: The field to use in the WHERE clause
        :type where_field: str
        """
        if not is_dataclass(obj):
            raise ValueError(f"{obj} is not a dataclass instance")

        dataclass_type = type(obj)
        table_name = self._get_table_name(dataclass_type)

        # Get field names and values
        field_list = fields(obj)
        where_value = getattr(obj, where_field)

        # Create SET clause (excluding the where field)
        set_clauses = []
        values = []
        for f in field_list:
            if f.name != where_field:
                set_clauses.append(f"{f.name} = ?")
                values.append(getattr(obj, f.name))

        values.append(where_value)

        update_sql = (f"UPDATE {table_name} SET {', '.join(set_clauses)} "
                      f" WHERE {where_field} = ?")

        LOG.debug(f"Updating with SQL: {update_sql} and values: {values}")

        await self.connection.execute(update_sql, values)
        await self.connection.commit()

    async def delete(self, dataclass_type: Type[T],
                     where_field: str, value: Any):
        """
        Delete records from the database.

        :param dataclass_type: The dataclass type
        :type dataclass_type: Type[T]
        :param where_field: The field to use in the WHERE clause
        :type where_field: str
        :param value: The value to match in the WHERE clause
        :type value: Any

        :return: None
        :rtype: None
        :raises ValueError: If the provided type is not a dataclass
        :rtype: None
        """
        if not is_dataclass(dataclass_type):
            raise ValueError(f"{dataclass_type} is not a dataclass")

        table_name = self._get_table_name(dataclass_type)
        delete_sql = f"DELETE FROM {table_name} WHERE {where_field} = ?"

        LOG.debug(f"Deleting with SQL: {delete_sql} and value: {value}")

        await self.connection.execute(delete_sql, (value,))
        await self.connection.commit()

    async def delete_by_id(self, dataclass_type: Type[T], id_value: Any):
        """
        Delete a record by its ID.

        :param dataclass_type: The dataclass type
        :type dataclass_type: Type[T]
        :param id_value: The ID value to delete
        :type id_value: Any
        :return: None
        :rtype: None
        """
        await self.delete(dataclass_type, 'id', id_value)

    async def select(self, dataclass_type: Type[T],
                     where_field: Optional[str] = None,
                     value: Optional[Any] = None) -> List[T]:
        """
        Select records from the database and return as dataclass instances.

        :param dataclass_type: The dataclass type to select
        :type dataclass_type: Type[T]
        :param where_field: The field to use in the WHERE clause
        :type where_field: Optional[str]
        :param value: The value to match in the WHERE clause
        :type value: Optional[Any]
        :return: List of dataclass instances
        :rtype: List[T]
        """
        if not is_dataclass(dataclass_type):
            raise ValueError(f"{dataclass_type} is not a dataclass")

        table_name = self._get_table_name(dataclass_type)

        if where_field and value is not None:
            select_sql = f"SELECT * FROM {table_name} WHERE {where_field} = ?"
            cursor = await self.connection.execute(select_sql, (value,))
        else:
            select_sql = f"SELECT * FROM {table_name}"
            cursor = await self.connection.execute(select_sql)

        rows = await cursor.fetchall()

        # Convert rows to dataclass instances
        results = []
        for row in rows:
            # Create a dictionary from the row
            row_dict = dict(row)
            # Create dataclass instance
            results.append(dataclass_type(**row_dict))

        LOG.debug(f"Selected {len(results)} records with SQL: {select_sql}")

        return results

    async def select_by_id(self, dataclass_type: Type[T],
                           id_value: Any) -> Optional[T]:
        """
        Select a single record by its ID.

        :param dataclass_type: The dataclass type to select
        :type dataclass_type: Type[T]
        :param id_value: The ID value to select
        :type id_value: Any
        :return: The dataclass instance or None if not found
        :rtype: Optional[T]
        """
        results = await self.select(dataclass_type, 'id', id_value)
        return results[0] if results else None

    async def select_all(self, dataclass_type: Type[T]) -> List[T]:
        """
        Select all records of a given type.

        :param dataclass_type: The dataclass type to select
        :type dataclass_type: Type[T]
        :return: List of dataclass instances
        :rtype: List[T]
        """
        return await self.select(dataclass_type)

    async def execute_query(self, query: str,
                            params: tuple = ()) -> List[aiosqlite.Row]:
        """
        Execute a custom SQL query.

        :param query: The SQL query to execute
        :type query: str
        :param params: The parameters for the SQL query
        :type params: tuple
        :return: List of rows returned by the query
        :rtype: List[aiosqlite.Row]
        """
        LOG.debug(f"Executing query: {query} with params: {params}")
        cursor = await self.connection.execute(query, params)
        return await cursor.fetchall()
