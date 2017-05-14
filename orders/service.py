import boto3 
from boto3 import dynamodb 
from boto3.session import Session
import uuid
import json
from datetime import datetime

dynamodb_session = Session(aws_access_key_id='',
          aws_secret_access_key='',
          region_name='us-west-2')

dynamodb = dynamodb_session.resource('dynamodb')

table=dynamodb.Table('order')
table2=dynamodb.Table('menu')
   
def handler(event, context):
    methodtype=event['httpMethod'] 
    if methodtype=='GET':
       response = table.get_item(
           Key={
               "order_id":event['body']['order_id']
                }
             )
       return response['Item']  
    if methodtype=='POST':
        response = table.put_item(
             Item={
                    'menu_id':event['body']['menu_id'],
                    'order_id':event['body']['order_id'],
                    'customer_name':event['body']['customer_name'],
                     'customer_email':event['body']['customer_email'],
                    'order_status':"processing",
                    'order':{ }
                      })
        
        response=table2.get_item(
                Key={
                    'menu_id':event['body']['menu_id']
                })
        result=""
        result+="Hi "+event['body']['customer_name']
        result+=", please choose one of these "
        seq=response['Item']['sequence'][0]
        result+=seq+": "
        val=1
        for i in response['Item'][seq]:
            result+=(" "+str(val)+". "+str(i)+",")
            val+=1
        result=result[:-1]   
       
        return result
    
    if methodtype=='PUT':
        
        inputval=int(event['body']['input'])
        
        response=table.get_item(
                Key={
                    'order_id':event['order_id']
                })
        menuitems=table2.get_item(
                Key={
                    'menu_id':response['Item']['menu_id']
                })
        sequence=menuitems['Item']['sequence']
        seqIndex=0
        for seq in sequence:
            if seq not in response['Item']['order']:
                if inputval<=len(menuitems['Item'][seq]):
                    if seq=='size':
                        res=table.update_item( Key={'order_id':event['order_id'] },ExpressionAttributeNames={"#od": "order" },
                        UpdateExpression= "SET #od.costs = :val1",
                        ExpressionAttributeValues={':val1':menuitems['Item']['price'][inputval-1] })
                        res=table.update_item( Key={'order_id':event['order_id'] },ExpressionAttributeNames={"#od": "order",'#val1':seq },
                        UpdateExpression= "SET #od.#val1 = :val2",
                        ExpressionAttributeValues={':val2':menuitems['Item'][seq][inputval-1] })
                        seqIndex=sequence.index(seq)
                        break
                    else:
                        res=table.update_item( Key={'order_id':event['order_id'] },ExpressionAttributeNames={"#od": "order",'#val1':seq },
                        UpdateExpression= "SET #od.#val1 = :val2",
                        ExpressionAttributeValues={':val2':menuitems['Item'][seq][inputval-1] })
                        seqIndex=sequence.index(seq)
                        break
                
                else:
                    return "We are still updating our menu for more options. for now please choose from available options.."
        
        count=0
        completed=False
        for seq in sequence :
            if response['Item']['order'].has_key(seq):
                count=count+1
        if(count==len(menuitems['Item']['sequence'])-1):
            completed=True
        
        if completed==True:
            presenttime=datetime.now().strftime('%Y-%m-%d@%H:%M:%S')
            res=table.update_item( Key={'order_id':event['order_id'] },ExpressionAttributeNames={"#od": "order" },
                    UpdateExpression= "SET #od.order_time= :val1",
                    ExpressionAttributeValues={':val1':presenttime })
            result="Message: Your order costs $"+response['Item']['order']['costs']+". We will email you when the order is ready. Thank you!"
            return result
        else:
            result=" please choose one of these "
            seq=menuitems['Item']['sequence'][seqIndex+1]
            result+=seq+": "
            val=1
            for i in menuitems['Item'][seq]:
                result+=(" "+str(val)+". "+str(i)+",")
                val+=1
            result=result[:-1]   
            return result
         
