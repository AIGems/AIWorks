#!/usr/bin/env python
# coding: utf-8

# In[228]:


import json 
import nltk
import difflib
from operator import itemgetter
# saved list of telecommunications companies from wikidata API using below query running in https://query.wikidata.org/
# select ?company ?companyLabel
# where {
#   ?company wdt:P452 wd:Q25245117
#   SERVICE wikibase:label {bd:serviceParam wikibase:language "en,en" .}    
# }


chat_transcript = """Welcome to G-Mobile. How may I help you?
I received a text informing my outstanding bill. I would like to know the break-up of my bill.
May I have your mobile number?
9812345678
Here are the details: 
Rent: $50 Excess Data: $8.3 Tax: $2.2 Total: $60.5 
Would you like to pay now?
No
Is there anything else that I can help you with?
I would like to change my plan as I tend to use more data. I also called customer care this morning about the same and it was a frustrating wait for 20 minutes, so I had to hang up.
Are you looking for a plan with more data?
yes
What is your minimum data requirement per day?
Unlimited data
Your current plan has unlimited voice. Would you like to change it?
No
Your current plan has 100 SMS per day. Would you like to change it?
No
Here is the best plan that meets your requirements:
Plan: Freedom-80 Voice: Unlimited SMS: 100 per day Data: Unlimited Rent: $80 
Would you like to switch to this plan?
80 bucks?...T-Mobile offers much cheaper plans.
Please wait while I transfer you to our customer service representative."""

telecom_companies_json = json.loads(open('query.json', encoding='utf-8').read())
telecom_company_list=[]
for item in telecom_companies_json:
    telecom_company_list.append(item['companyLabel'])
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

if __name__ == "__main__":
    output_list=get_competitor_mention_from_chat_transcript(chat_transcript)
    for matched_line_number, chat_competitor_word, competitor_name, probability in output_list:
        print(matched_line_number, chat_competitor_word, competitor_name, probability)

