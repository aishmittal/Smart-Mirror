import os, sys
import json
from ast import literal_eval
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from cloudinary.api import delete_resources_by_tag, resources_by_tag

CLOUDINARY_URL='cloudinary://648234412851627:iymOumw1AhoRajqW6FPwZkJCMbo@aish'
baseDir = 'http://res.cloudinary.com/aish/image/upload/v1488457817/SmartMirror/'
def cloudinary_config():
	cloudinary.config(
	  cloud_name = 'aish',  
	  api_key = '648234412851627',  
	  api_secret = 'iymOumw1AhoRajqW6FPwZkJCMbo'  
	)

def upload_person_image(imagePath,imageName,personName):
	cloudinary_config()
	imageName=os.path.splitext(imageName)[0]
	res=cloudinary.uploader.upload(imagePath, public_id = 'SmartMirror/dataset/'+personName+'/'+imageName)
	#print 'url:'+ res['secure_url'] + '\n'
	#return response

def upload_image(imagePath,imageName):
	cloudinary_config()
	imageName=os.path.splitext(imageName)[0]
	res=cloudinary.uploader.upload(imagePath, public_id = 'SmartMirror/tmp/'+imageName)
	#print res
	#return response



