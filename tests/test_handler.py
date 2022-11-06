from urllib import request
import pytest
import requests
import json
from unittest import mock, result
from employee.employee_api.src.service.handler import handler_lambda
from employee.employee_api.src.dao.sqs_conn import sqs_connection, sqs_send_message
from employee_process.employee_process_api.src.service.dataProcessor import processor_data
from employee.employee_api.src.dao.sqs_conn import LOGGER
from employee_process.employee_process_api.src.dao.db_conn import db_connection, dynamodb_post
from moto import mock_dynamodb, mock_sqs
import boto3

@pytest.fixture()
def apigw_event():
    """ Generates API GW Event"""

    return {
        "body": '{"EmployeeSummary": {"TableEntry": [{"Id": "000123", "Name": "Chadd Smith", "Designation": "Software Engineer", "Address": {"TemporaryAddress": {"StreetNumber": "2463", "StreetName": "Sw 153rd Dr", "City": "Beaverton", "Region": "Oregon", "PostalCode": "97006", "Country": "USA"}, "PermanentAddress": {"StreetNumber": "8963", "StreetName": "Fw 151rd Dr", "City": "Beaverton", "Region": "Oregon", "PostalCode": "97006", "Country": "USA"}}, "BloodGroup": "B+ve", "Age": "22"}, {"Id": "000124", "Name": "Ben Bruser", "Designation": "Senior Software Engineer", "Address": {"TemporaryAddress": {"StreetNumber": "1263", "StreetName": "Sw 153rd Dr", "City": "Beaverton", "Region": "Oregon", "PostalCode": "97006", "Country": "USA"}, "PermanentAddress": {"StreetNumber": "7263", "StreetName": "Fw 151rd Dr", "City": "Beaverton", "Region": "Oregon", "PostalCode": "97006", "Country": "USA"}}, "BloodGroup": "B+ve", "Age": "22"}]}}',
        "resource": "/{proxy+}",
        "requestContext": {
            "resourceId": "123456",
            "apiId": "1234567890",
            "resourcePath": "/{proxy+}",
            "httpMethod": "POST",
            "requestId": "c6af9ac6-7b61-11e6-9a41-93e8deadbeef",
            "accountId": "123456789012",
            "identity": {
                "apiKey": "",
                "userArn": "",
                "cognitoAuthenticationType": "",
                "caller": "",
                "userAgent": "Custom User Agent String",
                "user": "",
                "cognitoIdentityPoolId": "",
                "cognitoIdentityId": "",
                "cognitoAuthenticationProvider": "",
                "sourceIp": "127.0.0.1",
                "accountId": "",
            },
            "stage": "prod",
        },
        "queryStringParameters": {"foo": "bar"},
        "headers": {
            "Via": "1.1 08f323deadbeefa7af34d5feb414ce27.cloudfront.net (CloudFront)",
            "Accept-Language": "en-US,en;q=0.8",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Mobile-Viewer": "false",
            "X-Forwarded-For": "127.0.0.1, 127.0.0.2",
            "CloudFront-Viewer-Country": "US",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Upgrade-Insecure-Requests": "1",
            "X-Forwarded-Port": "443",
            "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
            "X-Forwarded-Proto": "https",
            "X-Amz-Cf-Id": "aaaaaaaaaae3VYQb9jd-nvCd-de396Uhbp027Y2JvkCPNLmGJHqlaA==",
            "CloudFront-Is-Tablet-Viewer": "false",
            "Cache-Control": "max-age=0",
            "User-Agent": "Custom User Agent String",
            "CloudFront-Forwarded-Proto": "https",
            "Accept-Encoding": "gzip, deflate, sdch",
        },
        "pathParameters": {"proxy": "/examplepath"},
        "httpMethod": "POST",
        "stageVariables": {"baz": "qux"},
        "path": "/examplepath",
    }


@pytest.fixture()
def processor_event():
    return {
        'Records': [
            {'messageId': 'b2fbc38c-0348-4d5a-9ac3-4fbe6962bcb0',
             'receiptHandle': 'AQEBTak05LTg2QggqZ18zemOW4yH+XaewsHvlL3nBDZ8LrljqAjty1X5jMYzswm4t8oQO2sY78euPpKmcwYtt8PajBiOy2USfzXlffx9Hjlt6/rxh9EPTiEUIkd0gSK1cRdDo78PjlSIk6s9nbKdMV1/8e0UsN2tW6PINrTBdfEgXTPQtAGFisKmHd3+71G1eKf54pDeNoYLKpBLntb9yZN4aYYYy1+GrfH9TGpmW1nQg7iN5KVl732s43mu+IMq3cN0rf25E2POWQH6VpVTdwhoaWhdHIFGegqi705D7tV6Cmc+2cELber+imdpuLz374oMW7Se8EyE/PnUZhRlgZfMpY9QpMAlPt4AVfK/XwlDkyZ4C8Deu9hvtk2qc8ilBl0fm2/69aQaMDEN2aBHEQ7DZw==',
             'body': '{"EmployeeSummary": {"TableEntry": [{"Id": "000123", "Name": "Chadd Smith", "Designation": "Software Engineer", "Address": {"TemporaryAddress": {"StreetNumber": "2463", "StreetName": "Sw 153rd Dr", "City": "Beaverton", "Region": "Oregon", "PostalCode": "97006", "Country": "USA"}, "PermanentAddress": {"StreetNumber": "8963", "StreetName": "Fw 151rd Dr", "City": "Beaverton", "Region": "Oregon", "PostalCode": "97006", "Country": "USA"}}, "BloodGroup": "B+ve", "Age": "22"}, {"Id": "000124", "Name": "Ben Bruser", "Designation": "Senior Software Engineer", "Address": {"TemporaryAddress": {"StreetNumber": "1263", "StreetName": "Sw 153rd Dr", "City": "Beaverton", "Region": "Oregon", "PostalCode": "97006", "Country": "USA"}, "PermanentAddress": {"StreetNumber": "7263", "StreetName": "Fw 151rd Dr", "City": "Beaverton", "Region": "Oregon", "PostalCode": "97006", "Country": "USA"}}, "BloodGroup": "B+ve", "Age": "22"}]}}',
             'attributes': {
                 'ApproximateReceiveCount': '1',
                 'SentTimestamp': '1658149174380',
                 'SenderId': 'AROAWRPHG6FFH727UWLBW:employee-HandlerLambda-zvihoEzGp7Er', 'ApproximateFirstReceiveTimestamp': '1658149174385'
             },
                'messageAttributes': {},
                'md5OfBody': '0a777cb46d265229ba727a96a3559c06',
                'eventSource': 'aws:sqs',
                'eventSourceARN': 'arn:aws:sqs:ap-south-1:449845850442:EmployeeQueue',
                'awsRegion': 'ap-south-1'
             }
        ]
    }


@mock.patch("employee.employee_api.src.service.handler")
def test_lambda_handler(mock_request, apigw_event):
    mock_request = mock.Mock(name="test handler lambda",
                             **{"json.return_value": {"statusCode": 200}})

    ret = handler_lambda(apigw_event)
    LOGGER.info(ret)
    print(ret)
    assert ret["statusCode"] == 200


@mock.patch("employee_process.employee_process_api.src.service.dataProcessor")
def test_lambda_processor(mock_request, processor_event):
    mock_request = mock.Mock(
        name="test processor lambda", return_value="000123")

    ret = processor_data(processor_event)

    assert ret[0]['Id'] == "000123"


@mock_dynamodb
def test_dynamodb():
    table_name = 'test'
    dynamodb = boto3.resource('dynamodb', 'ap-south-1')

    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'Id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'Designation',
                'KeyType': 'RANGE'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'Id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'Designation',
                'AttributeType': 'S'
            },

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    item = [
        {'Id': '000123', 'Name': 'Chadd Smith', 'Designation': 'Software Engineer', 'Address': {'TemporaryAddress': {'StreetNumber': '2463', 'StreetName': 'Sw 153rd Dr', 'City': 'Beaverton', 'Region': 'Oregon', 'PostalCode': '97006', 'Country': 'USA'}, 'PermanentAddress': {'StreetNumber': '8963', 'StreetName': 'Fw 151rd Dr', 'City': 'Beaverton', 'Region': 'Oregon', 'PostalCode': '97006', 'Country': 'USA'}}, 'BloodGroup': 'B+ve', 'Age': '22'}, {
            'Id': '000124', 'Name': 'Ben Bruser', 'Designation': 'Senior Software Engineer', 'Address': {'TemporaryAddress': {'StreetNumber': '1263', 'StreetName': 'Sw 153rd Dr', 'City': 'Beaverton', 'Region': 'Oregon', 'PostalCode': '97006', 'Country': 'USA'}, 'PermanentAddress': {'StreetNumber': '7263', 'StreetName': 'Fw 151rd Dr', 'City': 'Beaverton', 'Region': 'Oregon', 'PostalCode': '97006', 'Country': 'USA'}}, 'BloodGroup': 'B+ve', 'Age': '22'}
    ]

    table = db_connection(table_name)['table']
    dynamodb_post(item, table)

    table = dynamodb.Table(table_name)
    response = table.get_item(
        Key={
            'Id': '000123',
            'Designation': 'Software Engineer'
        }
    )
    if 'Item' in response:
        item = response['Item']

    assert item["Id"] == "000123"


@mock_sqs
def test_sqs_send_message():
    data = {
        'EmployeeSummary': {'TableEntry': [{'Id': '000123', 'Name': 'Chadd Smith', 'Designation': 'Software Engineer', 'Address': {'TemporaryAddress': {'StreetNumber': '2463', 'StreetName': 'Sw 153rd Dr', 'City': 'Beaverton', 'Region': 'Oregon', 'PostalCode': '97006', 'Country': 'USA'}, 'PermanentAddress': {'StreetNumber': '8963', 'StreetName': 'Fw 151rd Dr', 'City': 'Beaverton', 'Region': 'Oregon', 'PostalCode': '97006', 'Country': 'USA'}}, 'BloodGroup': 'B+ve', 'Age': '22'}, {'Id': '000124', 'Name': 'Ben Bruser', 'Designation': 'Senior Software Engineer', 'Address': {'TemporaryAddress': {'StreetNumber': '1263', 'StreetName': 'Sw 153rd Dr', 'City': 'Beaverton', 'Region': 'Oregon', 'PostalCode': '97006', 'Country': 'USA'}, 'PermanentAddress': {'StreetNumber': '7263', 'StreetName': 'Fw 151rd Dr', 'City': 'Beaverton', 'Region': 'Oregon', 'PostalCode': '97006', 'Country': 'USA'}}, 'BloodGroup': 'B+ve', 'Age': '22'}]}
    }

    sqs = boto3.client('sqs')
    sqs.create_queue(QueueName='test-skype-sender')
    sqs = sqs_connection('test-skype-sender')
    res = sqs_send_message(sqs['client'], sqs['url'], data)

    assert res["ResponseMetadata"]["HTTPStatusCode"] == 200


@mock.patch('requests.post')
def test_api_post(mock_post):
    mock_post.return_value.status_code = 200

    actual = calling_api()
    assert actual == 200

    


def calling_api():
    json_data = {
        "EmployeeSummary": {
            "TableEntry": [
                {
                    "Id": "000123",
                    "Name": "Chadd Smith",
                    "Designation": "Software Engineer",
                    "Address": {
                        "TemporaryAddress": {
                            "StreetNumber": "2463",
                            "StreetName": "Sw 153rd Dr",
                            "City": "Beaverton",
                            "Region": "Oregon",
                            "PostalCode": "97006",
                            "Country": "USA"
                        },
                        "PermanentAddress": {
                            "StreetNumber": "8963",
                            "StreetName": "Fw 151rd Dr",
                            "City": "Beaverton",
                            "Region": "Oregon",
                            "PostalCode": "97006",
                            "Country": "USA"
                        }
                    },
                    "BloodGroup": "B+ve",
                    "Age": "22"
                },
                {
                    "Id": "000124",
                    "Name": "Ben Bruser",
                    "Designation": "Senior Software Engineer",
                    "Address": {
                        "TemporaryAddress": {
                            "StreetNumber": "1263",
                            "StreetName": "Sw 153rd Dr",
                            "City": "Beaverton",
                            "Region": "Oregon",
                            "PostalCode": "97006",
                            "Country": "USA"
                        },
                        "PermanentAddress": {
                            "StreetNumber": "7263",
                            "StreetName": "Fw 151rd Dr",
                            "City": "Beaverton",
                            "Region": "Oregon",
                            "PostalCode": "97006",
                            "Country": "USA"
                        }
                    },
                    "BloodGroup": "B+ve",
                    "Age": "22"
                }
            ]
        }
    }
    result = requests.post('https://msrquokz51.execute-api.ap-south-1.amazonaws.com/Prod/employee', data=json.dumps(json_data))

    return result.status_code