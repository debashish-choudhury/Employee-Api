import json
from employee.employee_api.src.dao.sqs_conn import sqs_connection, sqs_send_message, LOGGER

def handler_lambda(event):
  try:
    LOGGER.info("Calling SQS connect from handler lambda")
    sqs_conn = sqs_connection("EmployeeQueue")
    sqsClient = sqs_conn['client']
    sqs_queue_url = sqs_conn['url']

    LOGGER.info("Sending message to SQS")
    data = json.loads(event['body'])
    response = sqs_send_message(sqsClient, sqs_queue_url, data)

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
      LOGGER.info("Message sent successfuly")
    else:
      LOGGER.info("Message NOT sent to sqs ", response["ResponseMetadata"]["HTTPStatusCode"])

    return {
      "statusCode": response["ResponseMetadata"]["HTTPStatusCode"],
      "body": "Success"
    }
  except Exception as error:
    LOGGER.error("Exception %s", error)
