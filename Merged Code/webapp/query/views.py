# query/views.py

from django.shortcuts import render
from django.core.management import call_command
from django.http import HttpResponse
from django.urls import reverse
from query.models import Tweet
from analysis.models import Study
from accounts.models import Profile
from subprocess import Popen, PIPE
from django.contrib.auth.decorators import login_required
from geopy.geocoders import Nominatim
import pexpect
import subprocess
import os
import json
import time
#### 11/17/2020 ####
from textblob import TextBlob
from django.views.generic.base import TemplateView
from datetime import date, datetime
import easy_date
#import date_converter
#### 11/17/2020 ####

def index(request):
	 render(request, 'index.html')

def request_page(request):
	return render(request, 'query/query.html', {})

def validate_massmine(request):

	my_profile = instance=request.user.profile
	consumer_key = my_profile.consumer_key
	consumer_secret = my_profile.consumer_secret
	access_token = my_profile.access_token
	access_token_secret = my_profile.access_token_secret

	child = pexpect.spawn('massmine --task=twitter-auth')
	child.expect('[No]')
	child.sendline('yes')
	child.expect('Consumer key:')
	child.sendline(consumer_key)
	child.expect('Consumer secret:')
	child.sendline(consumer_secret)
	child.expect('Access token')
	child.sendline(access_token)
	child.expect('Access token secret')
	child.sendline(access_token_secret)
	#child.wait()
	#exit status should be 0 on a success, 1 on a fail. signal status is if something else interrupted the command.
	return(child.exitstatus)
	#return(0)



def validate_massmine_facebook(request):

	my_profile_fbook = instance_fbook=request.user.profile
	app_id = my_profile_fbook.app_id
	app_secret = my_profile_fbook.app_secret
	access_token = my_profile_fbook.access_token
	child1 = pexpect.spawn('massmine --task=facebook-auth')
	child1.expect('[No]')
	child1.sendline('yes')
	child1.expect('app ID')
	child1.sendline(app_id)
	child1.expect('app Secret')
	child1.sendline(app_secret)
	child1.expect('Access token')
	child1.sendline(access_token)

	child1.wait()
	#exit status should be 0 on a success, 1 on a fail. signal status is if something else interrupted the command.
	return(child1.exitstatus)
	#return(0)


def validate_massmine_instagram(request):

	my_profile_insta = instance_insta=request.user.profile
	client_id = my_profile_insta.app_id
	client_secret = my_profile_insta.app_secret
	access_token_insta = my_profile_insta.access_token
	child2 = pexpect.spawn('massmine --task=instagram-auth')
	child2.expect('[No]')
	child2.sendline('yes')
	child2.expect('Client Id')
	child2.sendline(client_id)
	child2.expect('Client Secret')
	child2.sendline(client_secret)
	child2.expect('Access token')
	child2.sendline(access_token_insta)
	child2.wait()
	#exit status should be 0 on a success, 1 on a fail. signal status is if something else interrupted the command.
	return(child2.exitstatus)


def validate_massmine_youtube(request):

	my_profile_ytube = instance_ytube=request.user.profile
	client_id = my_profile_ytube.app_id
	client_secret = my_profile_ytube.app_secret
	#oauth_client_id = my_profile_ytube.oauth_client_id
	#oauth_client_secret = my_profile_ytube.oauth_client_secret
	refresh_token_ytube = my_profile_ytube.access_token
	child3 = pexpect.spawn('massmine --task=youtube-auth')
	child3.expect('[No]')
	child3.sendline('yes')
	child3.expect('Client Id')
	child3.sendline(client_id)
	child3.expect('Client Secret')
	child3.sendline(client_secret)
	child3.expect('refresh token')
	child3.sendline(refresh_token_ytube)
	child3.wait()
	#exit status should be 0 on a success, 1 on a fail. signal status is if something else interrupted the command.
	return(child3.exitstatus)



def validate_massmine_tumblr(request):

	my_profile_tumblr = instance_tumblr=request.user.profile
	consumer_key = my_profile_tumblr.consumer_key
	consumer_secret = my_profile_tumblr.consumer_secret
	access_token = my_profile_tumblr.access_token
	access_token_secret = my_profile_tumblr.access_token_secret

	child4 = pexpect.spawn('/usr/bin/massmine/./massmine --task=tumblr-auth')
	child4.expect('[No]')
	child4.sendline('yes')
	child4.expect('Consumer key:')
	child4.sendline(consumer_key)
	child4.expect('Consumer secret:')
	child4.sendline(consumer_secret)
	child4.expect('Access token')
	child4.sendline(access_token)
	child4.expect('Access token secret')
	child4.sendline(access_token_secret)
	child4.wait()
	#exit status should be 0 on a success, 1 on a fail. signal status is if something else interrupted the command.
	return(child4.exitstatus)
	#return(0)

@login_required
def make_query(request):

	if (validate_massmine(request) == 1):
		return render(request, 'query/query_error.html', {})

	else:
		keyword = request.POST.get('keyword')
		mydropdown1=request.POST.get('mydropdown1')
		keyword2 = request.POST.get('keyword2')
		mydropdown2 = request.POST.get('mydropdown2')
		keyword3 = request.POST.get('keyword3')
		count = request.POST.get('count')
		location = request.POST.get('location')
		geolocator = Nominatim(user_agent='my_user_agent')
		Location = geolocator.geocode(location)
		p2=Location.latitude
		p1=Location.longitude
		p3 = str(p1)+","+str(p2)+","+str(p1+1)+","+str(p2+1)
		#### 11/17/2020 ###
		From = request.POST.get("From")
		To = request.POST.get("To")
		my_time = datetime.min.time()

		#new_from_date = easy_date.convert_from_string(From,'%yyyy-%mm-%dd','%yyyy-%mm-%dd')
		from_1 = datetime.fromisoformat(From)
		#new_to_date = easy_date.convert_from_string(To,'%mm-%dd-%yyyy','%yyyy-%mm-%dd')
		to_1 = datetime.fromisoformat(To)

		#### 11/17/2020 ####


		command = 'massmine --task=twitter-stream --geo=' + str(p3) + ' --count=' + '"' + count + '"' + ' --query=' + '"' + keyword + '"' + '"' + mydropdown1 + '"' + keyword2 + '"' + mydropdown2 + '"' + keyword3 + '"' + str(from_1) + '"' + str(to_1)
		#command = '/usr/bin/massmine/./massmine --task=twitter-stream --geo='  + str(p3) +' --count=' + '"' + count + '"' + ' --query=' + '"' + keyword + '"'
		#command = '/usr/bin/massmine/./massmine --task=twitter-stream --geo=35.2272,-80.843083 --count=' + '"' + count + '"' + ' --query=' + '"' + keyword + '"'
		#command = r"/usr/bin/massmine/./massmine --task=twitter-stream --query=facts --count=30 --dur='2019-10-11 14:30:00'"
		#command = '/usr/bin/massmine/./massmine --task=twitter-stream --geo=-74,40,-73,41 --count=' + '"' + count + '"' + ' --query=' + '"' + keyword + '"'
		#command = '/usr/bin/massmine/./massmine --task=twitter-stream  --dur=''2019-10-11 14:30:00'' --count=' + '"' + count + '"' + ' --query=' + '"' + keyword + '"'

		#command = '/usr/bin/massmine/./massmine --task=twitter-search --count=' + count + ' --query=' + '"'+keyword+'"' +
		#command = '/usr/bin/massmine/./massmine --task=twitter-stream --count=' + count + ' --query=' + '"' + keyword+ '"'
		#command = '/usr/bin/massmine/./massmine --task=twitter-stream --count=' + count + ' --query=' + '"' + keyword + '"' + '--dur= 2015-10-11 14:30:00' + 'geo = -74'


		for key, value in request.POST.items():
			if key.startswith('customElementInput'):
				customId = key.split('customElementInput',1)[1]
				customDDValue = request.POST.get('customElementDD' + customId)
				customInputValue = request.POST.get('customElementInput' + customId)
				print(customDDValue + ":   " + customInputValue)
				command = command + '"' + customDDValue + '"' + customInputValue


		stdout = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout

		output = stdout.readlines()
		#stdout.writelines(output)
		hshtg = None
		keyword = keyword.replace(' ','_')
		new_study = Study(user=str(request.user),study_id=keyword+str(int(time.time())), count=count)
		new_study.save()

		for i in output:
			string = i.decode("utf-8")
			data = json.loads(string)

			try:

				for key,value in data.items():
					if (key == 'id_str'):
						tid = value
	
					if (key == 'created_at'):
						ca = value
					if (key == 'text'):
						txt = value
					if (key == 'source'):
						src = value
					if (key == 'truncated'):
						trunc = value
					if (key == 'retweet_count'):
						re_count = value
					if (key == 'metadata'):
						for key,value in data['metadata'].items():
							if (key == 'iso_language_code'):
								language = value
							else:
								language = 'en'
					else:
						language = 'en'
					if (key == 'entities'):
						for key,value in data['entities'].items():
							if (key == 'hashtags'):
								for n in data['entities']['hashtags']:
									hshtg  = n['text']
					if (key == 'user'):
						for key,value in data['user'].items():
							if (key == 'id_str'):
								uid = value
							if (key == 'location'):
								cntry = value

							if (key == 'name'):
								nme = value
							if (key == 'screen_name'):
								scr_name= value
							if (key == 'url'):
								u = value
							if (key == 'description'):
								desc = value
							if (key == 'verified'):
								verify = value
							if (key == 'followers_count'):
								fol_count = value
							if (key == 'listed_count'):
								list_count = value
							if (key == 'favourites_count'):
								fav_count = value
							if (key == 'statuses_count'):
								tw_count = value
							if (key == 'utc_offset'):
								utc_off = value
							if (key == 'friends_count'):
								fr_count = value
							if (key == 'time_zone'):
								tz = value
							if (key == 'geo_enabled'):
								geo_en = value
					if (key == 'in_reply_to_status_id_str'):
						reply_sid = value
					if (key == 'in_reply_to_user_id_str'):
						reply_uid = value
					if (key == 'in_reply_to_screen_name'):
						reply_scrname = value

				##print(txt)
				textBlob = TextBlob(txt)

				if textBlob.sentiment[0] < 0:
					sentimentvalue = textBlob.sentiment[0]
				elif textBlob.sentiment[0] == 0:
					sentimentvalue = textBlob.sentiment[0]
				else:
					sentimentvalue = textBlob.sentiment[0]
				#sentimentvalue = "test"
				new_study.tweets.create(tweet_id_str=tid,created_at=ca,text=txt,device=src,truncated=trunc,
						retweet_count=re_count,lang=language, country=cntry,user_id_str=uid,name=nme,
						screen_name=scr_name,in_reply_to_status_id_str=reply_sid,in_reply_to_user_id_str=reply_uid,
						in_reply_to_screen_name=reply_scrname,hashtags=hshtg,url=u,
						description=desc,verified=verify,followers_count = fol_count,friends_count=fr_count,
						listed_count=list_count,favourites_count=fav_count,num_tweets=tw_count,
						utc_offset=utc_off,time_zone=tz,geo_enabled=geo_en,sentiment=sentimentvalue)

			except Exception as e:
				print(e)
			
		return render(request, 'query/query_complete.html', {})
#lang=language#lang=language
