import httplib, urllib, base64, json

headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': 'c9dae5eec5e044cc8cdbe028f4a4d87d',
}

personGroupId = 'users'

def face_detect(image_url):
    params =urllib.urlencode({
        # Request parameters
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false'
    })

    body = '{"url":"%s"}'% image_url
    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/detect?%s" % params, body, headers)
        response = conn.getresponse()
        print response.status, response.reason
        data = response.read()
        print(data)
        conn.close()
        obj = json.loads(data)
        print obj[0]['faceId']
        return obj[0]['faceId']
    except Exception as e:
        print("Error: %s" % e.message)



def create_person_group():
    params = urllib.urlencode({
    'personGroupId' : 'group1' 
    })

    body = '{}'

    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("PUT", "/face/v1.0/persongroups/{personGroupId}?%s" % params,body, headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("Error: %s" % e.message)


def get_persons():

    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("GET", "/face/v1.0/persongroups/%s/persons?" % personGroupId, "", headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data)
        print(data)
        persons=[]
        for row in data:
            persons.append({'name':row['name'],'personId':row['personId']})
        conn.close()

        return persons
    except Exception as e:
        print("Error: %s" % e.message)

def create_person(pname,udata):
    params = urllib.urlencode({
        'personGroupId' : personGroupId
    })
    persons=get_persons()
    
    for row in persons:
        if pname == row['name']:
            print 'Person already exist'
            return row['personId']

        
    
    body = '{"name":"%s","userData":"%s"}' % (pname,udata)
    
    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/persongroups/%s/persons?" % personGroupId, body, headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data)
        print(data)
        print('Person Created: %s'% pname)
        print('Person Id: %s' % data['personId'])
        conn.close()
        return data['personId']
    except Exception as e:
        print("Error: %s" % e.message)        



def add_person_face(personId,image_url):
    

    body = '{"url":"%s"}'% image_url
    
    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/persongroups/%s/persons/%s/persistedFaces?" %(personGroupId,personId), body, headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data)
        #print data
        print('Face Id %s' % data['persistedFaceId'])
        conn.close()
    except Exception as e:
        print(e)    


def face_identify(faceId):
    

    #faceIds_str='['+" ".join('"'+str(x)+'",' for x in faceIds)+']'
    body = '{ "personGroupId":"%s","faceIds":["%s"]}' % (personGroupId, faceId)
    print body
    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/identify?" , body, headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data)
        print(data)
        pid=data[0]['candidates'][0]['personId']
        #print(pid)
        conn.close()
        return pid
    except Exception as e:
        print("Error: %s" % e.message) 

def train():
    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/persongroups/%s/train?" % personGroupId, "", headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("Error: %s" % e.message)           



#if __name__ == '__main__':
    #fid =face_detect('http://res.cloudinary.com/aish/image/upload/v1488457817/SmartMirror/aishwarya/6.jpg')        
    #print fid
    #print create_person('aishwarya_mittal','Aishwarya Mittal')
    #url='http://res.cloudinary.com/aish/image/upload/v1488721372/SmartMirror/dataset/aishwarya_mittal/img_1.jpg'
    #pid='7b1f2956-8635-4ce0-bfff-bf76afccc899'
    #add_person_face(pid,url)
    #face_identify('3885e697-f922-4e39-800c-1b7e0387bbf7')