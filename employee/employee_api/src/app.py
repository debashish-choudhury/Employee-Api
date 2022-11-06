
from service.handler import handler_lambda

def lambda_handler(event, context):
    return handler_lambda(event)
