import os, sys
import json
from ast import literal_eval
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
from cloudinary.api import delete_resources_by_tag, resources_by_tag
import configparser
config = configparser.ConfigParser()
config.read('cfg.ini')


def cloudinary_config():
	cloudinary.config(
	  cloud_name = config['CLOUDINARY']['cloud_name'].encode('utf8'),  
	  api_key = config['CLOUDINARY']['api_key'].encode('utf8'),
	  api_secret = config['CLOUDINARY']['api_secret'].encode('utf8')  
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



