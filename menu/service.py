import boto3 
from boto3 import dynamodb 
from boto3.session import Session
import uuid
import json


dynamodb_session = Session(aws_access_key_id='',
          aws_secret_access_key='',
          region_name='us-west-2')

dynamodb = dynamodb_session.resource('dynamodb')

table=dynamodb.Table('menu')

   
def handler(event, context):

   methodtype=event['httpMethod']
   if methodtype=='POST':
       response = table.put_item(
       Item = {
            "menu_id" : event['body']['menu_id'],
            "store_name" : event['body']['store_name'],
            "selection" : event['body']['selection'],
            "size" : event['body']['size'],
            "price" : event['body']['price'],
            "sequence" : event['body']['sequence'],
            "store_hours" : event['body']['store_hours']
       
                 })
       return "POSTED"
   elif methodtype=='GET':
       response = table.get_item(
           Key={
               "menu_id":event['body']['menu_id']
                }
             )
       return response['Item']

   elif methodtype=="DELETE":
       table.delete_item(
           Key={"menu_id": event['body']['menu_id']}
         )  
       return "DELETED"  
   elif methodtype=="PUT":
       attributes = event['body'].keys()
       for k in attributes:
           if str(k)!= 'menu_id':
               table.update_item(Key={ "menu_id":event['params']['menu_id']
                         },UpdateExpression= 'set ' + str(k) + '= :s',ExpressionAttributeValues={ ':s' : event['body'][str(k)] }
        )
       return "UPDATED" 
   else:
       return "Invalid operation please choose from POST,PUT,DELETE,GET" 
