import json
from employee_process.employee_process_api.src.dao.db_conn import db_connection, dynamodb_post, LOGGER

def processor_data(event):
  try:
    LOGGER.info("Connecting to db")
    table = db_connection("employees")['table']
    res = None
    record = event['Records'][0]
    payload = json.loads(record["body"])
    employeeList = payload['EmployeeSummary']['TableEntry']
    LOGGER.info("Inserting data into table")
    res = dynamodb_post(employeeList, table)
    LOGGER.info("Data added to table, ", res)

    return employeeList

  except Exception as error:
    LOGGER.error("Exception %s", error)