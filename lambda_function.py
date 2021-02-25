# in fritzbox 
# https://url-of-lambda?ipaddress=<ipaddr>&ip6address=<ip6addr>&domainname=<domain>&username=<username>&password=<pass>

# dummy test string
# https://url-of-lambda/dyndns?ipaddress=127.0.0.2&domainname=dyn-domain&ip6address=1&username=test&password=...

from __future__ import print_function
import json
import os
import boto3
import logging
from botocore.exceptions import ClientError
from datetime import datetime

awsRegion = 'eu-central-1' # change to your region
s3Bucket = '...' # your bucket for the files config.json and history.json
s3KeyConfig = 'config.json'
s3KeyUsage = 'history.json'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
s3Client = boto3.client('s3', awsRegion)

def getRoute53ZoneId(domainName, userName, password):
    try:
        s3Object = s3Client.get_object(Bucket=s3Bucket, Key=s3KeyConfig)
        streamingBody = s3Object['Body']
        jsonObject = json.loads(streamingBody.read())
        jsonEntry = jsonObject[domainName]
        if jsonEntry["password"] == password :
            return jsonEntry["route53ZoneId"]
        else:
            logger.warn("wrong password" + password)
            return 
    except ClientError as e:
        logger.error(e)

def append2Usagefile(domainName, ipAddress, ip6Address, status):
    # new entry to be added
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    jsonEntry = {
        timestampStr:  {
            "domainName": domainName,
            "ipAddress" : ipAddress,
            "ip6Address" : ip6Address,
            "status" : status
        }
    }
    
    # read current file and append or create new file
    try:
        s3Object = s3Client.get_object(Bucket=s3Bucket, Key=s3KeyUsage)
        streamingBody = s3Object['Body']
        jsonObject = json.loads(streamingBody.read())
        
        # append new entry
        jsonObject.update(jsonEntry)
    except ClientError as e:
        logger.error(e.response)
        if e.response['Error']['Code'] == "NoSuchKey":
            jsonObject = jsonEntry
        else:
            raise
    

    # write file
    s3Client.put_object(
        Body=(bytes(json.dumps(jsonObject).encode('UTF-8'))),
        Bucket=s3Bucket, Key=s3KeyUsage
    )
    
    # this works also to write to s3
    #s3 = boto3.resource('s3')
    #s3object = s3.Object(s3Bucket, s3KeyUsage)
    #s3object.put(
    #    Body=(bytes(json.dumps(json_data).encode('UTF-8')))
    #)
    return "OK " + timestampStr
    
def updateRoute53(route53ZoneId, domainName, ipAddress, ip6Address):
    route53Client = boto3.client(
        'route53',
        region_name=awsRegion
    )
    
    route53Client.change_resource_record_sets(
        HostedZoneId=route53ZoneId,
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domainName + ".",
                        'Type': 'A',
                        'TTL': 60,
                        'ResourceRecords': [
                            {
                                'Value': ipAddress
                            }
                        ]
                    }
                }
            ]
        }
    )    
    
    route53Client.change_resource_record_sets(
        HostedZoneId=route53ZoneId,
        ChangeBatch={
            'Changes': [
                {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domainName + ".",
                        'Type': 'AAAA',
                        'TTL': 60,
                        'ResourceRecords': [
                            {
                                'Value': ip6Address
                            }
                        ]
                    }
                }
            ]
        }
    )    
    

# lambda proxy must be activated to have access to queryStringParameters
def lambda_handler(event, context):
    logger.info('## dyndns started ...')
    ipAddress = event['queryStringParameters']['ipaddress']
    ip6Address = event['queryStringParameters']['ip6address']
    domainName = event['queryStringParameters']['domainname']
    userName = event['queryStringParameters']['username']
    password = event['queryStringParameters']['password']

    #logger.info(event)
    logger.info("ipAddresses:" + ipAddress + " " + ip6Address)
    logger.info("domainName:" + domainName)

    # check domain username and password in config file
    # domain name in route53 ends with "." !!!!
    # if found in config file the route53ZoneId is returned 
    route53ZoneId = getRoute53ZoneId(domainName + ".", userName, password)
    # not found -> finish here
    if route53ZoneId is None :
        append2Usagefile(domainName, ipAddress, ip6Address, "error. input data could not be verified")
        return {        
            'statusCode': 400
        }
    # update route53 for the domain    
    else:
        updateRoute53(route53ZoneId, domainName, ipAddress, ip6Address)

        return {        
            'statusCode': 200,
            'body':  append2Usagefile(domainName , ipAddress, ip6Address, "ok")  
        }

