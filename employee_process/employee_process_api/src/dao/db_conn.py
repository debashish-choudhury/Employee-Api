import boto3
import logging

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def db_connection(table_name):
  ddb = boto3.resource('dynamodb')
  table = ddb.Table(table_name)

  return {
    "table": table
  }

def dynamodb_post(employee_list, table):
  for employee in employee_list:
    res = table.put_item(Item = employee)
  return res
  