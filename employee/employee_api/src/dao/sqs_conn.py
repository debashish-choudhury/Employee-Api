import boto3, logging, json

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

def sqs_connection(queue_name):
  sqsClient = boto3.client('sqs')
  sqs_queue_url = sqsClient.get_queue_url(QueueName=queue_name)['QueueUrl']

  return {
    "client": sqsClient,
    "url": sqs_queue_url
  }

def sqs_send_message(sqsClient, sqs_queue_url, data):
  return sqsClient.send_message(
      QueueUrl=sqs_queue_url,
      MessageBody = json.dumps(data)
  )