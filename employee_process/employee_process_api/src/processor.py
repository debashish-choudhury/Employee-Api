from service.dataProcessor import processor_data

def processor_lambda(event, context):
    processor_data(event)