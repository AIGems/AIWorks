import requests, re
import json
import os
import os.path
from flask import Flask, request, Response
from flask_restful import Resource, Api, reqparse
from sqlalchemy import create_engine
from flask_jsonpify import jsonify
from flask_cors import CORS
from rake_nltk import Rake

import nltk
nltk.download('stopwords')
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from string import punctuation
from nltk.probability import FreqDist
from heapq import nlargest
from collections import defaultdict
import time

from aylienapiclient import textapi
sent = textapi.Client("92285aca", "792df91d097ed0171c79984e43132d5d")

app = Flask(__name__)

api = Api(app)
#api = CORS(app, resources={r"/api/*": {"origins": "*"}})


parser = reqparse.RequestParser()
parser.add_argument('query', help='Customer chat text')
parser.add_argument('session_id', help='Unique session ID of Customer chat')
parser.add_argument('result', help='dialogflow integration')
parser.add_argument('length', help='length of keywords to be returned')
parser.add_argument('lang', help='multilingual support')


def json_creator(file,session_id,status,error_type,customer_query,intentID,intentName,isFallBackIntent,action,parameters,bot_response,actionInComplete):
    data = {}
    intent_time=time.strftime('%H:%M:%S', time.localtime())
    if not (os.path.isfile(file)):
        data['session_id'] = session_id
        data['sequence'] = []
    else:
        with open(file,'r') as infile:
            data=json.loads(infile.read())
        
    data['sequence'].append({
            'status' : status,
            'error_type' : error_type,
            'customer_query' : customer_query,
            'intentID' : intentID,
            'intentName' : intentName,
            'isFallBackIntent' : isFallBackIntent,
            'action' : action,
            'parameters' : parameters,
            'bot_response' : bot_response,
            'actionIncomplete' : actionInComplete,
            'intentTime' : intent_time
            })
    
    with open(file, 'w') as outfile:  
        json.dump(data, outfile)
    return(data)
    
    
def load_dirty_json(dirty_json):
    regex_replace = [(r"([ \{,:\[])(u)?'([^']+)'", r'\1"\3"'), (r" False([, \}\]])", r' false\1'), (r" True([, \}\]])", r' true\1')]
    for r, s in regex_replace:
        dirty_json = re.sub(r, s, dirty_json)
    clean_json = json.loads(dirty_json)
    return clean_json


def calculate_sentiment_score(chatlist):
    sentiment_score_list=[]
    for line in chatlist:
        s=sent.Sentiment({'text':line})
        sentiment_score_list.append((s['text'],s['polarity'],s['polarity_confidence']))
    return(sentiment_score_list)
    
#json_creator(file_path,sess_id,status_code,res['status']['errorType'],res['result']['resolvedQuery'],res['result']['metadata']['intentId'],res['result']['metadata']['intentName'],res['result']['metadata']['isFallbackIntent'],res['result']['action'],res['result']['parameters'],res['result']['fulfillment']['speech'])   

#print(sess_id,status_code,res['status']['errorType'],res['result']['resolvedQuery'],res['result']['metadata']['intentId'],res['result']['metadata']['intentName'],res['result']['metadata']['isFallbackIntent'],res['result']['action'],res['result']['parameters'],res['result']['fulfillment']['speech'])

class Summarizer(Resource):
    def post(self):
        """ Drive the process from argument to output """
        args = parser.parse_args()
        query=args['query']
        session_id=args['session_id']
        
        url="https://api.dialogflow.com/v1/query?v=20170712"
        headers = { 'Content-Type' : 'application/json', 'Authorization' : 'Bearer 79a44b392b5c4c7796a11a19690d9969' }
        payload = { 'query' : query , 'lang' : 'en', 'sessionId' : session_id, 'timezone':'America/New_York'}
        file_path="json\\"
        file=file_path+session_id+".json"

        r=requests.post(url,headers=headers, data=json.dumps(payload))
        res=json.loads(r.text)
        print(res)
        data=json_creator(file,res['sessionId'],res['status']['code'],res['status']['errorType'],res['result']['resolvedQuery'],res['result']['metadata']['intentId'],res['result']['metadata']['intentName'],res['result']['metadata']['isFallbackIntent'],res['result']['action'],res['result']['parameters'],res['result']['fulfillment']['speech'],res['result']['actionInComplete'])   
        #return self.summarize(sentence_ranks, sentence_tokens, args.length)
        return(jsonify(data))
        
    def options (self):
        return {'Allow' : 'POST' }, 200, \
        { 'Access-Control-Allow-Origin': '*', \
          'Access-Control-Allow-Methods' : 'POST,GET',
          'Access-Control-Allow-Headers' : 'Content-Type : application/json' }
        
class ChatSummarizer(Resource):
    def post(self):
        """ Drive the process from argument to output """
        args = parser.parse_args()
        query=args['query']
        session_id=args['session_id']
        
        url="https://api.dialogflow.com/v1/query?v=20170712"
        headers = { 'Content-Type' : 'application/json', 'Authorization' : 'Bearer 79a44b392b5c4c7796a11a19690d9969' }
        payload = { 'query' : query , 'lang' : 'en', 'sessionId' : session_id, 'timezone':'America/New_York'}
        file_path="json\\"
        file=file_path+session_id+".json"

        r=requests.post(url,headers=headers, data=json.dumps(payload))
        res=json.loads(r.text)
        print(res)
        data=json_creator(file,res['sessionId'],res['status']['code'],res['status']['errorType'],res['result']['resolvedQuery'],res['result']['metadata']['intentId'],res['result']['metadata']['intentName'],res['result']['metadata']['isFallbackIntent'],res['result']['action'],res['result']['parameters'],res['result']['fulfillment']['speech'],res['result']['actionIncomplete'])   
        js=json.dumps(data)
        return Response(js,headers={'Access-Control-Allow-Origin' : '*' },mimetype='application/json')


class DesignerSummarizer(Resource):
    def post(self):
        """ Drive the process from argument to output """
        args = parser.parse_args()
        query=args['query']
        session_id=args['session_id']
        
        url="https://api.dialogflow.com/v1/query?v=20170712"
        headers = { 'Content-Type' : 'application/json', 'Authorization' : 'Bearer 79a44b392b5c4c7796a11a19690d9969' }
        payload = { 'query' : query , 'lang' : 'en', 'sessionId' : session_id, 'timezone':'America/New_York'}
        file_path="json\\"
        file=file_path+session_id+".json"

        r=requests.post(url,headers=headers, data=json.dumps(payload))
        res=json.loads(r.text)
        print(res)
        data=json_creator(file,res['sessionId'],res['status']['code'],res['status']['errorType'],res['result']['resolvedQuery'],res['result']['metadata']['intentId'],res['result']['metadata']['intentName'],res['result']['metadata']['isFallbackIntent'],res['result']['action'],res['result']['parameters'],res['result']['fulfillment']['speech'],res['result']['actionIncomplete'])   
        output={"bot_response" : res['result']['fulfillment']['speech']}
        js=json.dumps(output)
        return Response(js,headers={'Access-Control-Allow-Origin' : '*' },mimetype='application/json')


        
class GetJsonSummary(Resource):
    def post(self):
        """ Drive the process from argument to output """
        args = parser.parse_args()
        session_id=args['session_id']
        
        file_path="json\\"
        file=file_path+session_id+".json"
        
        if (os.path.isfile(file)):
            with open(file,'r') as infile:
                data=json.loads(infile.read())
                
        return(jsonify(data))
        
class GetJsonGistify(Resource):
    def post(self):
        """ Drive the process from argument to output """
        args = parser.parse_args()
        session_id=args['session_id']
        
        file_path="json\\"
        file=file_path+session_id+".json"
        
        if (os.path.isfile(file)):
            with open(file,'r') as infile:
                data=json.loads(infile.read())

        intents=[]
        intent_text_map={}
        intent_action_map={}
        intent_time_map={}
        
        result = {}
        result['intents'] = []
        
        for item in data['sequence']:
            if item['intentName']!="Default Welcome Intent" and item['actionIncomplete']==False:
                intents.append(item['intentName'])
                if item['intentName'] not in intent_text_map:
                    if item['isFallBackIntent']!="true":
                        intent_text_map[item['intentName']]=[item['bot_response']]
                    else:
                        intent_text_map[item['intentName']]=[item['customer_query']]
                else:
                    if item['isFallBackIntent']!="true":
                        if item['bot_response'] not in intent_text_map[item['intentName']]:
                            intent_text_map[item['intentName']].append(item['bot_response'])
                    else:
                        if item['customer_query'] not in intent_text_map[item['intentName']]:
                            intent_text_map[item['intentName']].append(item['customer_query'])
                            
                intent_action_map[item['intentName']]=item['action']
                if item['intentName'] not in intent_time_map:
                    intent_time_map[item['intentName']]=item['intentTime']
        
        print(intents)
        #intents=list(set(intents))
        #print(intents)
        
        for item in intents:
            result['intents'].append([{
                     'intent':item,
                     'action':intent_action_map[item],
                     'text' : intent_text_map[item],
                     'time' : intent_time_map[item]
                     }])             
     
        #return(jsonify(result))
        js=json.dumps(result)
        return Response(js,headers={'Access-Control-Allow-Origin' : '*' },mimetype='application/json')
    
class GetConversation(Resource):
    def post(self):
        """ Drive the process from argument to output """
        args = parser.parse_args()
        session_id=args['session_id']
        
        file_path="json\\"
        file=file_path+session_id+".json"
        
        if (os.path.isfile(file)):
            with open(file,'r') as infile:
                data=json.loads(infile.read())

        intents=[]
        intent_text_map={}
        
        result = {}
        result['intents'] = []
        text=""
        start_num=0
        
        for item in data['sequence']:
            if item['intentName'] not in intents:
                intents.append(item['intentName'])
            if item['intentName'] not in intent_text_map:
                intent_text_map[item['intentName']]=[item['customer_query']]
                intent_text_map[item['intentName']].append(item['bot_response'])
                text+=item['customer_query']+"\n"
                text+=item['bot_response']+"\n"
            else:
                intent_text_map[item['intentName']].append(item['customer_query'])
                intent_text_map[item['intentName']].append(item['bot_response'])
                text+=item['customer_query']+"\n"
                text+=item['bot_response']+"\n"

        print(intents)

        for item in intents:
            end_num=start_num+len(intent_text_map[item])-1
            result['intents'].append([{
                     'intent':item,
                     'text' : intent_text_map[item],
                     'start' : start_num,
                     'end' : end_num
                     }])
                       
            start_num=end_num+1
        result['conversation']=text
        #return(jsonify(result))
        js=json.dumps(result)
        return Response(js,headers={'Access-Control-Allow-Origin' : '*' },mimetype='application/json')
        
class ClearJsonSummary(Resource):
    def post(self):
        """ Drive the process from argument to output """
        args = parser.parse_args()
        print(args)
        session_id=args['session_id']
        
        file_path="json\\"
        file=file_path+session_id+".json"
        
        if (os.path.isfile(file)):
            os.remove(file)
        data={'file':file,'message':'file deleted'}
                
        return(jsonify(data))
        
class DialogFlowWebhook(Resource):
    def showBill(self,result):
        number=result['parameters']['ANI']
        response="Here are the details for mobile number "+number+": Rent: $60 Excess Data: $8.3 Tax: $3.2 Total: $60.5 . Would you like to pay now? "
        return(response)
        
    def showPlan(self,result):
        response="Plan Name: Freedom $80 Minutes:1500 SMS:200 Data:6GB "
        return(response)
        
    def post(self):
        """ Drive the process from argument to output """
        args = parser.parse_args()
        result=args['result']
        print(result)
        result=result.replace("\'","\"")
        result=re.sub(r'False',r'"false"',result)
        result=json.loads(result)
        if result['action']=="ShowBillDetails":
            response=self.showBill(result)
        elif result['action']=="Plan_Calculate":
            response=self.showPlan(result)
            
        data={'speech' : response, 'displayText':response }
        return(jsonify(data))
        
class SentimentScorer(Resource):
    def post(self):
        args = parser.parse_args()
        session_id=args['session_id']     
        file_path="json\\"
        file=file_path+session_id+".json"
        
        with open(file,'r') as infile:
            data=json.loads(infile.read())
            
        intents=[]
        intent_text_map={}
        intent_sentiment_map={}
        
        for item in data['sequence']:
            if item['intentName']!="Default Welcome Intent":
                intents.append(item['intentName'])
                if item['intentName'] not in intent_text_map:
                    intent_text_map[item['intentName']]=[item['customer_query']]
                else:
                    if item['customer_query'] not in intent_text_map[item['intentName']]:
                        intent_text_map[item['intentName']].append(item['customer_query'])
        #return("<html><body>Hi</body></html>")
        
        for key,value in intent_text_map.items():
            intent_sentiment_map[key]=calculate_sentiment_score(value)
            
        return(jsonify(intent_sentiment_map))
        
class KeywordExtract(Resource):
    def post(self):
        args = parser.parse_args()
        print(args)
        if args['lang']:
            r = Rake(language=args['lang'])
        else:
            r = Rake()
        r.extract_keywords_from_text(args['query'])
        output=r.get_ranked_phrases()[:4]
        #output=jsonify(output)
        js=json.dumps(output)
        return Response(js,headers={'Access-Control-Allow-Origin' : '*' },mimetype='application/json')
        #return(jsonify(r.get_ranked_phrases()[:args['length']]))

api.add_resource(Summarizer, '/summarizer')
api.add_resource(ChatSummarizer, '/chatsummarizer')
api.add_resource(DesignerSummarizer, '/designersummarizer')
api.add_resource(GetJsonSummary, '/get_summary')
api.add_resource(GetJsonGistify, '/get_gistify')
api.add_resource(ClearJsonSummary, '/clear_summary')
api.add_resource(DialogFlowWebhook, '/df_webhook')
api.add_resource(SentimentScorer, '/scoresentiment')
api.add_resource(GetConversation,'/get_conversation')
api.add_resource(KeywordExtract,'/keywords_extract')

if __name__ == '__main__':
    #app.run(debug=True,host='0.0.0.0', port=4000,ssl_context='adhoc')
    app.run(debug=True,host='0.0.0.0', port=4000)
