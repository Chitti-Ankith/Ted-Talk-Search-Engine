'''

Created on 12 Sep, 2018
Title : TED TALKS SEARCH ENGINE
@author : Eco-Group

'''

#requires downloading nltk,punkt
import webbrowser
import sys
import csv
import pprint
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import math
import string
import tkinter
from tkinter import *
tag =0
corpus = {}
words_lemmatizer=WordNetLemmatizer()
stop_words=stopwords.words('english')
pp=pprint.PrettyPrinter(indent=4)
topresults=[]
n=1
userHistoryScore={}


def exit_program():
    sys.exit(0)
def normalise_corpus():
        final_dict={}
        result=corpus

        for x in result.values():
                #print(x['description'])
                final_tokens=[]
                token=[]
                tokens=nltk.word_tokenize(x['description'])
                for word in tokens:
                        if word.isalnum():
                                temp=word.lower()
                                temp2=words_lemmatizer.lemmatize(temp)
                                if temp2 not in stop_words:
                                        final_tokens.append(temp2)
                        
                final_dict[x['id']]=final_tokens
                              
        return(final_dict)           
        #print(stop_words)

def normalise_query(query):
        final_tokens=[]
        #pp.pprint(query)
        tokens=[]
        tokens=nltk.word_tokenize(query)
                
        for word in tokens:
                if word.isalnum():
                        temp=word.lower()
                        temp2=words_lemmatizer.lemmatize(temp)
                        if temp2 not in stop_words:
                                final_tokens.append(temp2)
        #pp.pprint(final_tokens)                
        return(final_tokens)

def calculate_tf_idf(ted,query):
        N = len(ted)
        
        query_final = {}
        final = {}
        docf = {}
        global userHistoryScore
        tf_final = {} #tf for each word in a doc
        for id,talk in ted.items():   #id gets the tedtalk's unique id and talk is that particular ted ta
               # pp.pprint(talk)
                tf_des = {}    #holds the term freq in the description of the talk
                final[id] = {}
                for word in talk:                       #desc is the description of the talk that has been tokenised
                        final[id][word] = {}
                        if word not in tf_des:
                                if word not in docf:
                                        docf[word] = 1    #updating the docf
                                else:
                                        docf[word] +=1
                                tf_des[word] = 1                
                        else:
                                tf_des[word]+=1
                        
                        final[id][word]['tf'] = 1+math.log(tf_des[word]) 

                        
        for idd,term in final.items():
            sum = 0
            for tf_val,tf1 in term.items():
                sum += tf1['tf']**2
            sum = sum**0.5
            for tf_val,tf1 in term.items():
                final[idd][tf_val]['tf'] /= sum  #Normalising the tf value
            
        for word in query:   #talk is the word in query 
                tf_desc = {}    #holds the term freq in the description of the talk
                query_final[word] = {}  #tf_final[id] = {}
                        
                if word not in tf_desc:
                        tf_desc[word]=1    
                else:
                        tf_desc[word] +=1
                                        
                query_final[word]['tf'] = 1+math.log(tf_desc[word])    

        sum = 0

        for term,freq in query_final.items():
                sum += freq['tf']**2
                
        sum = sum**0.5
       # pp.pprint(query_final )
       # print("\n")
        #pp.pprint(docf)
        for term in query_final:
                if(term in docf):
                    #query_final[term]['tf'] /= sum  #Normalising the tf value to reflect tf_wt
                    query_final[term]['idf'] = math.log(N/docf[term])  #Calculating idf value. Using docf calculated above
                    query_final[term]['wt'] = query_final[term]['tf']*query_final[term]['idf']  #calculating weight(tf*idf)
                else: query_final[term]['idf']=query_final[term]['wt']=0

        tfidf_sum = 0
        for term,tf_val in query_final.items() :
                tfidf_sum += tf_val['wt']**2

        if(tfidf_sum == 0):
                return None

        tfidf_sum = tfidf_sum**0.5
        for term in query_final:
            if(term in query_final):
                query_final[term]['tf_idf'] = query_final[term]['wt']/tfidf_sum  

        #print(query_final)      
        answer = {}         #Holds the cosine scores for each document
        for id in final:
                score = 0
                for word in query:
                        if word in final[id]:
                                score += final[id][word]['tf']*query_final[word]['tf_idf']
                
                        
                answer[id] = score + userHistoryScore[int(id)]
        
        return(sorted(answer.items(), key=lambda kv: kv[1], reverse=True)) #sorts results according to value in reverse order

def main():
        global userHistoryScore
        global n
        with open('tedtalksdata.csv','r',encoding = "utf8") as datafile:
                csv_filereader = csv.reader(datafile)
                next(csv_filereader)
                for row in csv_filereader:
                        corpus[row[1]]={"id":row[1],"description":row[2],"mainspeaker":row[3],"title":row[4],"url":row[5]}
                        userHistoryScore[int(row[1])]=0
        transformed_corpus=normalise_corpus()   #Normalises the corpus
        window =Tk()
        window.title("TED TALKS SEARCH ENGINE")       #initialising the GUI
        window.geometry('1000x1000')
        lbl = Label(window, text="Enter the query")
        lbl.grid(column=0, row=0)
        lb2 =  Label (window, text="")
        lb2.grid(column = 0,row = 30)
        lb3 =  Label (window, text="Enter id to play video")
        lb3.grid(column=0,row = 20 )

        txt = Entry(window,width=10)
        txt.grid(column=1, row=0)
        txt2 = Entry(window,width=10)
        txt2.grid(column = 1,row =20 )
        textarea1= Text(window, width=100,height=35)
        textarea1.grid(row = 50,column=50,  padx=5, pady=5, sticky=W)
        textarea1.insert(INSERT,"  ")
        # query="hello" 
        # print(query)
        
        def clicked():
            lb2.configure(text=" ")
            query=txt.get()          #Getting the query from the txt Entry
            textarea1.delete('1.0',END)  #Clearing the text area
            global tag
            # print(query)
            try:
                    int(query)
            except:
                    ValueError
            else:
                    if(int(query)==-1):    
                            return -1

            #print("inside\n")
            transformed_query = normalise_query(query)
            global topresults
            topresults=calculate_tf_idf(transformed_corpus,transformed_query) # a sorted list
            tag=1
            if( not topresults) or (topresults[0][1]==0): #first value must not be zero
                    textarea1.insert(END,"\n" + "Sorry there are no talks for your query :'(")
            else:    
                    #print("Title:\t Main Speaker:\t Description:")
                    
                    global n 
                    n=1
                    for result in topresults:
                            if(result[1] !=0 and n!=11): #display only if non-zero score
                                    id=result[0] #gety the id of talk
                                    #pp.pprint(corpus[id]) #print it from corpus
                                    k = str(n)
                                    # tt= corpus[id]['title']
                                    textarea1.insert(END,"\n"+"Talk Number  : "+k+"\n"+"Main Speaker:  "+corpus[id]['mainspeaker']+"\n"+ "Title: " + corpus[id]['title'])
									#textarea1.insert(END,"\n")
                                    textarea1.insert(END,"\n"+"Description:")
                                    textarea1.insert(END,"\n"+corpus[id]['description']+"\n")
                                    
                                    
                                    n=n+1
                            else:   

                                    break
        
            lbl.configure(text="Enter next query")

        
        def link1():
            idd = txt2.get()  #getting the id value from the txt2 entry field
            idd2 = int(idd) 
            global n
            global tag
            # print(idd2)
            # pp.pprint(topresults2)
            global topresults
            global corpus
            global userHistoryScore
            # print(topresults)
            if idd2>0 and idd2<n and tag==1:        #Checks whether the value is valid or not 
                docid=topresults[idd2-1][0]
                # pp.pprint(topresults)
                # print(docid)
                userHistoryScore[int(topresults[idd2-1][0])] = userHistoryScore[int(topresults[idd2-1][0])] + topresults[idd2-1][1]**2  #Updating the cosine score if the user selects the video to play
                webbrowser.open_new(corpus[docid]['url'])                                                                               # ^^ View the doc for more.   
                lb2.configure(text= "")
            else:
                lb2.configure(text = "Please enter valid number ")
        btn = Button(window, text="Submit", command=clicked )
        btn2 = Button(window, text = "Enter",command =link1)
        btn2.grid(column = 2, row = 20)
        btn.grid(column=2, row=0)

        window.mainloop()    


if __name__ == '__main__':
        if(main()==-1):
            exit_program()