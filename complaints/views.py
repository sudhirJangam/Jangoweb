import json

from django.shortcuts import render, redirect
# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
import pymongo
from django.conf import settings
from .forms import  ComplaintForm
from .models import Complaints
from datetime import datetime
from .callBedrock import callBedrock

# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello and welcome to my first <u>Django App</u> project!</h1>")



def crComplaint(request) :
    products= ["prod1", "prod2", "prod3"]
    subproducts= ["prod1", "prod2", "prod3"]
    if(request.method=="POST"):
        complaintDict=request.POST.dict()
        complaintDict.pop('csrfmiddlewaretoken')
        print(complaintDict.keys())
        complaintDict['repoDt']=complaintDict['repoDt']+':00+00:00'
        complaintDict['complaintId']=int(complaintDict['complaintId'])

        print(complaintDict)
        my_client = pymongo.MongoClient(settings.DB_NAME)
        dbname = my_client["complaints_db"]
        collection_name = dbname["Complaints"]
        #mydoc = mycol.find(complaintDict)
        retval=collection_name.insert_one(complaintDict)
        print(retval)
        #return redirect('view/0')


    complaintDict={}
    return render(request,"complaints/create.html", {"complaint":complaintDict, "type":"Create",
                                                         "products":products, "subproducts":subproducts})

def updComplaint(request, id) :
    if(request.method=="POST"):
        complaintDict=request.POST.dict()
        complaintDict.pop('csrfmiddlewaretoken')
        print(complaintDict.keys())

        complaintDict['repoDt']=datetime.strptime(complaintDict['repoDt'],"%Y-%m-%dT%H:%M")
        complaintDict['complaintId']=int(complaintDict['complaintId'])
        #mydoc = mycol.find(myquery)
        print (complaintDict)

        my_client = pymongo.MongoClient(settings.DB_NAME)
        dbname = my_client["complaints_db"]
        collection_name = dbname["Complaints"]
        filter = {'complaintId': complaintDict["complaintId"]}
        update = {'$set': complaintDict }
        updated_doc = collection_name.find_one_and_update(
            filter, update
        )
        #print(updated_doc)
    return redirect(getComplaint, id=id)

def delComplaint(request, id) :
    my_client = pymongo.MongoClient(settings.DB_NAME)
    products= ["prod1", "prod2", "prod3"]
    subproducts= ["prod1", "prod2", "prod3"]
    dbname = my_client["complaints_db"]
    collection_name = dbname["Complaints"]
    myquery = { "complaintId": id }
    #mydoc = mycol.find(myquery)
    retval=collection_name.delete_one(myquery)
    print(retval)
    return redirect(viewComplaints, page=0)





def getComplaint(request, id) :
    my_client = pymongo.MongoClient(settings.DB_NAME)
    products= ["prod1", "prod2", "prod3"]
    subproducts= ["prod1", "prod2", "prod3"]
    dbname = my_client["complaints_db"]
    collection_name = dbname["Complaints"]
    Cluster_collection = dbname["ClusterCenter"]
    myquery = { "complaintId": id }
    #mydoc = mycol.find(myquery)
    data=collection_name.find_one(myquery)
    #print(all_data)
    print(data['repoDt'].isoformat())
    data['repoDt']=data['repoDt'].isoformat()
    Knn=vecsearch( data['embeddings'], collection_name )
    Knnlist=list(Knn)
    KnnC=Clustsearch( data['embeddings'], Cluster_collection )
    KnnClist=list(KnnC)
    print(KnnClist)
    return render(request,"complaints/create.html", {"complaint":data, "type":"Update",
                                  "Knnc":KnnClist,"Knn":Knnlist ,"products":products, "subproducts":subproducts})

def viewComplaints(request, page) :
    elements =page*3

    my_client = pymongo.MongoClient(settings.DB_NAME)
    dbname = my_client["complaints_db"]
    collection_name = dbname["Complaints"]
    myquery = { "address": "Park Lane 38" }
    #mydoc = mycol.find(myquery)
    data_cursor=collection_name.find().skip(elements).limit(3)
    all_data = list(data_cursor)
    count = collection_name.find().explain().get("executionStats", {}).get("nReturned")
    elemRemain =count-elements
    pageRemain=elemRemain/3
    if(pageRemain > 3) :
        pages = [{"no": page, "cls":0} , {"no":  page+1, "cls":1},{"no": page+2, "cls":1}]
    elif(pageRemain>2) :
        pages = [{"no": page, "cls":0} , {"no":  page+1, "cls":1}]
    else:
        pages = [{"no": page, "cls":0} ]

    print(count)
    print(elements)
    print(elemRemain)
    #print(all_data)
    return render(request,"complaints/view.html", {"dataset":all_data,
                                                   "pages":pages, "currPage":page, "pageRemain":pageRemain})



def vecsearch( index, path,embedding_vector, collection ):
    # define pipeline
    pipeline = [
        {
            '$vectorSearch': {
                'index': index,
                'path': path,
                'queryVector': embedding_vector,
                'numCandidates': 150,
                'limit': 5
            }
        }, {
            '$project': {
                '_id': 0,
                'complaintId': 1,
                'product': 1,
                'subProduct': 1,
                'cluster': 1,
                'score': {
                    '$meta': 'vectorSearchScore'
                }
            }
        }
    ]

    # run pipeline
    result = collection.aggregate(pipeline)
    return result

    # print results
    """for i in result:
        print(i)
    """

def vecsearch( embedding_vector, collection ):
    # define pipeline
    pipeline = [
        {
            '$vectorSearch': {
                'index': "vcomp_index",
                'path': "embeddings",
                'queryVector': embedding_vector,
                'numCandidates': 150,
                'limit': 5
            }
        }, {
            '$project': {
                '_id': 0,
                'complaintId': 1,
                'product': 1,
                'cluster': 1,
                'score': {
                    '$meta': 'vectorSearchScore'
                }
            }
        }
    ]

    # run pipeline
    result = collection.aggregate(pipeline)
    return result

    # print results
    """for i in result:
        print(i)
    """

def Clustsearch( embedding_vector, collection ):
    # define pipeline
    pipeline = [
        {
            '$vectorSearch': {
                'index': "vclust_index",
                'path': "centerVec",
                'queryVector': embedding_vector,
                'numCandidates': 150,
                'limit': 3
            }
        }, {
            '$project': {
                '_id': 0,
                'cluster': 1,
                'score': {
                    '$meta': 'vectorSearchScore'
                }
            }
        }
    ]

    # run pipeline
    result = collection.aggregate(pipeline)
    return result

def complaintHelp(request):
    if(request.method=="POST"):
        print("received post")
        complaintText=request.body
        #print(complaintDict.dict().keys())
        #complaintText = complaintDict['complaint']
        print (complaintText)
        #compjson=json.loads(complaintDict)
        #print(compjson)
        #print(compjson['element'])


        #prompt="add more prompts here"+complaintText

        #body.append(prompt)
        modelresp=callBedrock("anthropic.claude-v2",str(complaintText))
        #print(modelresp["content"][0]["text"])
        response = HttpResponse(modelresp["content"][0]["text"], content_type="application/liquid; charset=utf-8")
        print(response)
        return HttpResponse(response)

