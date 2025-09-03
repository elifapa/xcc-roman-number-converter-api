
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, List, Tuple

class PostgreSQLDTypeMapper:
    """Maps Python/Pandas dtypes to PostgreSQL column types"""
    
    # Core mapping for Python types to PostgreSQL
    PYTHON_TO_POSTGRES = {
        int: 'BIGINT',
        float: 'DOUBLE PRECISION',
        str: 'TEXT',
        bool: 'BOOLEAN',
        bytes: 'BYTEA',
        datetime: 'TIMESTAMP',
        date: 'DATE',
        Decimal: 'NUMERIC',
        type(None): 'TEXT',  # Default for None/null values
    }

    @classmethod
    def map_python_type(cls, value: Any) -> str:
        """Map a Python value to PostgreSQL type"""
        python_type = type(value)
        return cls.PYTHON_TO_POSTGRES.get(python_type, 'TEXT')
    
    @classmethod
    def infer_column_types(cls, data: dict) -> Dict[str, str]:
        """
        Infer PostgreSQL column types from data
        """
        column_types = {}
        

        # Single record - infer from values
        for col, value in data.items():
            column_types[col] = cls.map_python_type(value)

        return column_types
    
# Global mapper
mapper = PostgreSQLDTypeMapper()