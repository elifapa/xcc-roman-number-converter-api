import structlog
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from xcc_roman_converter.cli import convert_arabic, convert_roman
from datetime import datetime

from xcc_roman_converter_api.storage import storage
from xcc_roman_converter_api.dtype_mapper import mapper
from xcc_roman_converter_api.config import PG_SCHEMA, PG_POST_TABLE, configure_logging

configure_logging()
logger = structlog.get_logger()

app = FastAPI()


class Payload(BaseModel):
    request: str
    response: str
    operation_type: str
    timestamp: str


@app.get("/")
async def root():
    return {"message": "Hello Elif!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/easyconvert/from_roman/{input}", response_model=Payload)
async def convert_from_roman(input):
    """
    Convert Roman numeral to Arabic numeral.
    Log the response to the Postgres instance.
    """
    output = convert_roman(input)

    if output is None:
        raise HTTPException(
            status_code=400, detail=f"Conversion failed. Output:{output}"
        )

    operation_type = "roman_to_arabic"
    timestamp = datetime.now().isoformat()

    payload = {
        "request": input.upper(),
        "response": str(output) if output is not None else output,
        "operation_type": operation_type,
        "timestamp": timestamp,
    }
    column_types = mapper.infer_column_types(payload)

    try:
        storage.create_table_if_not_exists(
            PG_SCHEMA, PG_POST_TABLE, column_types, add_pk=True
        )
        storage.insert(PG_SCHEMA, PG_POST_TABLE, payload)
        logger.info(
            f"Data inserted successfully into {PG_SCHEMA}.{PG_POST_TABLE}",
            payload=payload,
        )

    except Exception as e:
        logger.error("Error inserting data", error=str(e), payload=payload)

    return payload


@app.post("/easyconvert/from_arabic/{input}", response_model=Payload)
async def convert_from_arabic(input):
    """
    Convert Arabic numeral to Roman numeral.
    Log the response to the Postgres instance.
    """

    output = convert_arabic(input)

    if output is None:
        raise HTTPException(
            status_code=400, detail=f"Conversion failed. Output:{output}"
        )

    operation_type = "arabic_to_roman"
    timestamp = datetime.now().isoformat()

    payload = {
        "request": str(input),
        "response": output if output is not None else output,
        "operation_type": operation_type,
        "timestamp": timestamp,
    }

    column_types = mapper.infer_column_types(payload)

    try:
        storage.create_table_if_not_exists(
            PG_SCHEMA, PG_POST_TABLE, column_types, add_pk=True
        )
        storage.insert(PG_SCHEMA, PG_POST_TABLE, payload)
        logger.info(
            f"Data inserted successfully into {PG_SCHEMA}.{PG_POST_TABLE}",
            payload=payload,
        )

    except Exception as e:
        logger.error("Error inserting data", error=str(e), payload=payload)

    return payload


@app.get("/easyconvert/get/responses")
async def get_responses(limit: int = Query(50, ge=1, le=50)):
    """
    Get responses from the database with a user-specified limit, capped at 50 rows.

    Args:
        limit (int): Maximum number of rows to fetch. Defaults to 50. Must be between 1 and 50.

    Returns:
        dict: A dictionary containing the fetched responses.
    """
    responses = storage.get_all(PG_SCHEMA, PG_POST_TABLE, limit=limit)
    return {"responses": responses}


def main() -> None:
    print("Hello from xcc-roman-converter-api!")
    app()
