import csv
from dagster import op
from security import safe_requests


@op(config_schema={"url": str})
def download_csv(context):
    response = safe_requests.get(context.op_config["url"])
    lines = response.text.split("\n")
    return [row for row in csv.DictReader(lines)]
