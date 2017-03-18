import httplib, urllib, base64, json
import configparser
config = configparser.ConfigParser()
config.read('cfg.ini')

headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': config['MSFACE']['api_key'],
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
        data = response.read()
        conn.close()
        obj = json.loads(data)
        print "FaceID: " + obj[0]['faceId']
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
        print e


def create_person(pname,udata):
    params = urllib.urlencode({
        'personGroupId' : personGroupId
    })
    # persons=get_persons()
    
    # for row in persons:
    #     if pname == row['name']:
    #         return row['personId']    
    body = '{"name":"%s","userData":"%s"}' % (pname,udata)
    
    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/persongroups/%s/persons?" % personGroupId, body, headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data)
        conn.close()
        if not data['personId']:
            return ''
        else:    
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
        print data
        conn.close()
    except Exception as e:
        print(e)    


def face_identify(faceId):
    

    #faceIds_str='['+" ".join('"'+str(x)+'",' for x in faceIds)+']'
    body = '{ "personGroupId":"%s","faceIds":["%s"]}' % (personGroupId, faceId)
    #print body
    try:
        print "Face Identify in MSFace"
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/identify?" , body, headers)
        response = conn.getresponse()
        data = response.read()
        data = json.loads(data)
        pid=data[0]['candidates'][0]['personId']
        print "PID: " + pid
        
        if not pid:
            return ''
        #print(pid)
        conn.close()
        return pid
    except Exception as e:
        print("Error: %s" % e.message)
        return '' 

def train():
    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        conn.request("POST", "/face/v1.0/persongroups/%s/train?" % personGroupId, "", headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception as e:
        print("Error: %s" % e.message)           



# if __name__ == '__main__':
    # add_person_face('a484672a-0791-475b-aa77-772a107ae0fc','http://res.cloudinary.com/aish/image/upload/v1489463899/SmartMirror/dataset/aish/img_3.jpg')
    # get_persons()
    # create_person('test','')
    # face_detect('http://res.cloudinary.com/aish/image/upload/v1489463901/SmartMirror/dataset/aish/img_1.jpg')
    #fid =face_detect('http://res.cloudinary.com/aish/image/upload/v1488457817/SmartMirror/aishwarya/6.jpg')        
    #print fid
    #print create_person('aishwarya_mittal','Aishwarya Mittal')
    #url='http://res.cloudinary.com/aish/image/upload/v1488721372/SmartMirror/dataset/aishwarya_mittal/img_1.jpg'
    #pid='7b1f2956-8635-4ce0-bfff-bf76afccc899'
    #add_person_face(pid,url)
    #face_identify('3885e697-f922-4e39-800c-1b7e0387bbf7')