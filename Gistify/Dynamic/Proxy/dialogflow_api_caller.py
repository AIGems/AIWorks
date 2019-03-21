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
import difflib
from operator import itemgetter

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


telecom_companies_json = json.loads(open('query.json', encoding='utf-8').read())
telecom_company_list=[]
for tele_item in telecom_companies_json:
    telecom_company_list.append(tele_item['companyLabel'])
global stop_words
stop_words=['G-mobile', 'G-Mobile', 'g-mobile', 'gmobile','Gmobile', 'GMobile', 'Are', 'The', 'the', 'is', 
            'too', 'plan', 'much', 'for', 'data', 'more',"a","about","all","and","are", 'mobile',
            "as","at","back","be","because","been","but","can","can't","come","could", 'Mobile',
            'G-mobiles', 'G-Mobiles', 'g-mobiles', 'gmobiles','Gmobiles', 'GMobiles', 'Mobiles', 'mobiles',
            "did","didn't","do","don't","for","from","get","go","going","good","got",
            "had","have","he","her","here","he's","hey","him","his","how","I","if","I'll",
            "I'm","in","is","it","it's","just","know","like","look","me","mean","my","no",
            "not","now","of","oh","OK","okay","on","one","or","out","really","right","say",
            "see","she","so","some","something","tell","that","that's","the","then","there",
            "they","think","this","time","to","up","want","was","we","well","were","what",
            "when","who","why","will","with","would","yeah","yes","you","your","you're"]


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


def session_add(file,session_id):
	with open(file,'w') as fwrite:
		fwrite.write(session_id+"\n")

def session_retrieve(file):
	with open(file,'r') as fread:
		session=fread.readlines()[0].split("\n")[0]
	print(session)
	return(session)
    
    
def load_dirty_json(dirty_json):
    regex_replace = [(r"([ \{,:\[])(u)?'([^']+)'", r'\1"\3"'), (r" False([, \}\]])", r' false\1'), (r" True([, \}\]])", r' true\1')]
    for r, s in regex_replace:
        dirty_json = re.sub(r, s, dirty_json)
    clean_json = json.loads(dirty_json)
    return clean_json


def calculate_sentiment_score(chatlist,indexlist):
    sentiment_score_list=[]
    print(indexlist)
    index=0
    for line in chatlist:
        s=sent.Sentiment({'text':line})
        print(s)
        if s['polarity']=="negative":
            sentiment_score_list.append((s['text'],s['polarity'],s['polarity_confidence'],indexlist[index]))
        index=index+1
    return(sentiment_score_list)

def read_text(text):
    """ Read the file at designated path and throw exception if unable to do so """ 
    try:
        formatted_text=[]
        #with open(path, 'r') as file:
        #    text=file.read()
        print("inside read text")
        print(text)
        print("splitting text based on new line")
        text_lines=text.split("\n")
        print(text_lines)
        for line in text_lines:
            if line and line[-1] not in list(punctuation):
                line=line+"."
                
            formatted_text.append(line)
        text="\n".join(formatted_text)
        print("Conversation : ")
        print(text)
        return text
    
    except IOError as e:
        print("Fatal Error: File ({}) could not be locaeted or is not readable.".format(path))

def sanitize_input(data):
    """ 
    Currently just a whitespace remover. More thought will have to be given with how 
    to handle sanitzation and encoding in a way that most text files can be successfully
    parsed
    """
    replace = {
        ord('\f') : ' ',
        ord('\t') : ' ',
        ord('\n') : ' ',
        ord('\r') : None
    }

    return data.translate(replace)

def tokenize_content(content):
    stop_words=list(set(stopwords.words('english')))+list(punctuation)
    words=word_tokenize(content.lower())
    
    return([sent_tokenize(content),[word for word in words if word not in stop_words] ])

def score_tokens(filterd_words, sentence_tokens):
    """
    Builds a frequency map based on the filtered list of words and 
    uses this to produce a map of each sentence and its total score
    """
    word_freq = FreqDist(filterd_words)

    ranking = defaultdict(int)

    for i, sentence in enumerate(sentence_tokens):
        for word in word_tokenize(sentence.lower()):
            if word in word_freq:
                ranking[i] += word_freq[word]

    return ranking

def summarize(ranks, sentences, length):
    """
    Utilizes a ranking map produced by score_token to extract
    the highest ranking sentences in order after converting from
    array to string.  
    """
    if int(length) > len(sentences): 
        print("Error, more sentences requested than available. Use --l (--length) flag to adjust.")
        exit()

    indexes = nlargest(int(length), ranks, key=ranks.get)
    final_sentences = [sentences[j] for j in sorted(indexes)]
    return ' '.join(final_sentences)


def get_competitor_mention_distance(INPUT_CHAT_SENTENCE):
    INPUT_CHAT_SENTENCE = INPUT_CHAT_SENTENCE.replace(",", " ")
    INPUT_CHAT_SENTENCE = INPUT_CHAT_SENTENCE.replace(".", " ")
    chat_list=INPUT_CHAT_SENTENCE.split()
    chat_list=[word for word in chat_list if word not in stop_words]


    max_distance=0
    max_word=None
    max_company=None
    distance_list=[] 
    for word in chat_list:
        for company in telecom_company_list:
            distance = difflib.SequenceMatcher(None,word,company).ratio()*100
            distance_list.append((word, company, distance))
            if int(distance) > int(max_distance): 
                max_word=word
                max_company=company
                max_distance=distance
    #print("Distance between %s and %s: %s" % (max_word, max_company, max_distance))
    return (max_word, max_company, max_distance)

def get_competitor_mention_by_threshold(INPUT_CHAT_SENTENCE, threshold=60):
    chat_word, company_name, prob = get_competitor_mention_distance(INPUT_CHAT_SENTENCE)
    if prob>=threshold:
        return (chat_word, company_name, prob)
    else:
        return None

def get_competitor_mention_from_chat_transcript(chat_transcript, threshold=60):
    result_list=[]
    for line_number, line in enumerate(chat_transcript.splitlines()):
        if get_competitor_mention_by_threshold(line, threshold=threshold):
            chat_word, company_name, prob = get_competitor_mention_by_threshold(line, threshold=threshold)
            matched_line_number=line_number 
            result_list.append((matched_line_number, chat_word, company_name, prob))
    return result_list


class NotesSummarizer(Resource):
    def post(self):
        """ Drive the process from argument to output """ 
        args = parser.parse_args()
        content = read_text(args['query'])
        content = sanitize_input(content)
    
        sentence_tokens, word_tokens = tokenize_content(content)  
        sentence_ranks = score_tokens(word_tokens, sentence_tokens)
        #print("\nSummary :")
        #return self.summarize(sentence_ranks, sentence_tokens, args.length)
        data=summarize(sentence_ranks, sentence_tokens, args['length'])
        data=data.replace("I","Customer")
        data=data.replace("My","Customer")
        data=data.replace("my","Customer")
        data=data.replace("Your","Customer")
        data=data.replace("your","Customer")
        data=data.replace("You","Customer")
        data=data.replace("you","Customer")


        js=json.dumps(data)
        return Response(js,headers={'Access-Control-Allow-Origin' : '*' },mimetype='application/json')
    
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
        session_file=file_path+"session.txt"

        #session_add(session_file,session_id)
        r=requests.post(url,headers=headers, data=json.dumps(payload))
        res=json.loads(r.text)
        print(res)
        data=json_creator(file,res['sessionId'],res['status']['code'],res['status']['errorType'],res['result']['resolvedQuery'],res['result']['metadata']['intentId'],res['result']['metadata']['intentName'],res['result']['metadata']['isFallbackIntent'],res['result']['action'],res['result']['parameters'],res['result']['fulfillment']['speech'],res['result']['actionIncomplete'])  
        js=json.dumps(data)
        return Response(js,headers={'Access-Control-Allow-Origin' : '*' },mimetype='application/json')

class AddSession(Resource):
    def post(self):
        """ Drive the process from argument to output """
        args = parser.parse_args()
        session_id=args['session_id']
        
        file_path="json\\"
        session_file=file_path+"session.txt"

        session_add(session_file,session_id)
        data={'result':'success'}
        js=json.dumps(data)
        return Response(js,headers={'Access-Control-Allow-Origin' : '*' },mimetype='application/json')

class RetrieveSession(Resource):
    def get(self):
        """ Drive the process from argument to output """    
        file_path="json\\"
        session_file=file_path+"session.txt"

        session=session_retrieve(session_file)
        data={'session_id':session}
        print(data)
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
        intent_parameters_map={}
        
        result = {}
        result['intents'] = []
        
        for item in data['sequence']:
            if item['intentName']!="Default Welcome Intent" and item['actionIncomplete']==False:
                intents.append(item['intentName'])
                intent_parameters_map[item['intentName']]=item['parameters']
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
                     'time' : intent_time_map[item],
                     'parameters': intent_parameters_map[item]
                     }])             
     
        #return(jsonify(result))
        js=json.dumps(result)
        return Response(js,headers={'Access-Control-Allow-Origin' : '*' },mimetype='application/json')
    
class GetConversation(Resource):
    def post(self):
        """ Drive the process from argument to output """
        args = parser.parse_args()
        session_id=args['session_id']
        print(session_id)
        
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


class GetActionableIndicators(Resource):
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
		competitor_count=0
		previous_interaction_count=0
		negative_sentiment_count=0

		result = {}
		result['actions'] = []
		text=""
		start_num=0
	    
		for count,item in enumerate(data['sequence']):
			print(item['customer_query'])
			if 'T-MOBILE' in item['customer_query'].upper():
				print("entering competitor")
				competitor=True
				competitor_count=count*2

			if 'CALLED' in item['customer_query'].upper():
				print("entering previous interaction")
				previous_interaction=True
				previous_interaction_count=count*2

			if 'FRUSTRATING' in item['customer_query'].upper():
				print("entering negative sentiment")
				negative_sentiment=True
				negative_sentiment_count=count*2

		result['actions'].append({'competitor':{'presence':'yes','index':competitor_count},'previous_interaction':{'presence':'yes','index':previous_interaction_count},'sentiment':{'presence':'yes','index':negative_sentiment_count}})

		js=json.dumps(result)
		return Response(js,headers={'Access-Control-Allow-Origin' : '*' },mimetype='application/json')


class CompetitorIndicator(Resource):
    def post(self):
        """ Drive the process from argument to output """
        args = parser.parse_args()
        session_id=args['session_id']
        
        file_path="json\\"
        file=file_path+session_id+".json"
        
        if (os.path.isfile(file)):
            with open(file,'r') as infile:
                data=json.loads(infile.read())

        result = {}
        result['competitors'] = []
        threshold=60
      
        for count,item in enumerate(data['sequence']):
            print(item['customer_query'])
            if get_competitor_mention_by_threshold(item['customer_query'], threshold=threshold):
                chat_word, company_name, prob = get_competitor_mention_by_threshold(item['customer_query'], threshold=threshold)
                competitor_count=count*2
                result['competitors'].append({'competitor':{'competitor_name':company_name,'index':competitor_count,'reference':chat_word,'probability':prob}})

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
        number=result['parameters']['MobileNumber']
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
        elif result['action']=="ShowPlan":
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
        intent_line_map={}
        intent_sentiment_map={}
        
        for count,item in enumerate(data['sequence']):
            if item['intentName']!="Default Welcome Intent":
                intents.append(item['intentName'])
                if item['intentName'] not in intent_text_map:
                    intent_text_map[item['intentName']]=[item['customer_query']]
                    intent_line_map[item['intentName']]=[count*2]
                else:
                    if item['customer_query'] not in intent_text_map[item['intentName']]:
                        intent_text_map[item['intentName']].append(item['customer_query'])
                        intent_line_map[item['intentName']].append(count*2)
        #return("<html><body>Hi</body></html>")
        
        for key,value in intent_text_map.items():
            intent_sentiment_map[key]=calculate_sentiment_score(value,intent_line_map[key])

        js=json.dumps(intent_sentiment_map)
        return Response(js,headers={'Access-Control-Allow-Origin' : '*' },mimetype='application/json')
        
        
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

api.add_resource(ChatSummarizer, '/chatsummarizer')
api.add_resource(DesignerSummarizer, '/designersummarizer')
api.add_resource(GetJsonSummary, '/get_summary')
api.add_resource(GetJsonGistify, '/get_gistify')
api.add_resource(ClearJsonSummary, '/clear_summary')
api.add_resource(DialogFlowWebhook, '/df_webhook')
api.add_resource(SentimentScorer, '/scoresentiment')
api.add_resource(GetConversation,'/get_conversation')
api.add_resource(KeywordExtract,'/keywords_extract')
api.add_resource(GetActionableIndicators,'/get_signals')
api.add_resource(AddSession,'/add_session')
api.add_resource(RetrieveSession,'/retrieve_session')
api.add_resource(NotesSummarizer,'/summarize_notes')
api.add_resource(CompetitorIndicator,'/competitor')

if __name__ == '__main__':
    #app.run(debug=True,host='0.0.0.0', port=4000,ssl_context='adhoc')
    app.run(debug=True,host='0.0.0.0', port=4000)
