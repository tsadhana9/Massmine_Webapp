# analysis/views.py


import enchant
import string
import re
import os
import tempfile
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt; plt.rcdefaults()
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from django_tables2 import RequestConfig
import io
import pandas as pd
import pyreadstat
from datetime import datetime, timedelta
import time
from email.utils import parsedate_tz
# import csv
import json
import dicttoxml
from xml.dom.minidom import parseString
# import xlwt
# from analysis.resources import TweetResource
from analysis import resources
from analysis.resources import StudyTable
from analysis.utils import render_html_to_pdf

from analysis.models import Study
from query.models import Tweet
from django.views.generic.base import TemplateView
import plotly
from plotly import tools as tls
import plotly.offline
import plotly.graph_objs
from pytz import timezone
from collections import defaultdict
from textblob import TextBlob
from django.core.files.storage import default_storage
title = ''
studyId = ''

@login_required
class FreqWordsAnalysis(TemplateView):
	template_name = 'graphH.html'

	def __init__(self, name):
		self.name = name

	def get_context_data(self, **kwargs):	
		context = super().get_context_data(**kwargs)
		dirname = os.path.dirname(__file__)
		filename = os.path.join(dirname, 'stopwords.txt')
		stopFile = open(filename,'r')
		stopWords = stopFile.read().splitlines()
		stopList = set(stopWords)
		isNumber = re.compile('^[0-9]+$')
		global studyId
		global graph_type
		list = Study.objects.all()
		offset = len(studyId)- 10
		addStop = studyId[:offset]
		alsoAddStop = addStop.lower()
		stopList.add(addStop)
		stopList.add(alsoAddStop)
		stopPlural = addStop + 's'
		stopList.add(stopPlural)
		stopPlural = addStop + '\'s'
		stopList.add(stopPlural)
		stopPlural = addStop + 's\''
		stopList.add(stopPlural)
		stopPlural = addStop.lower() + 's'
		stopList.add(stopPlural)
		stopPlural = addStop.lower() + '\'s'
		stopList.add(stopPlural)
		stopPlural = addStop.lower() + 's\''
		stopList.add(stopPlural)
		arr = []
		twList = Study.objects.get(study_id= studyId).tweets.all()


		for y in twList:
			tempText = y.text
			arr.append(tempText)
		texts = []
		d = enchant.Dict("en_US")
		isNumber = re.compile('^[0-9]+$') 
		for text in arr:
			textwords = []
			for word in text.lower().split():
				word = re.sub(r'[^\w\s]','',word)
				word = re.sub(r'\.+$','',word)
				if word == '' or isNumber.search(word) == True or d.check(word) == False or word in addStop or word in alsoAddStop or len(word) == 1:
					word = ''
				if word not in stopList and word!='':
					textwords.append(word)
				texts.append(textwords)

		frequency = defaultdict(int)
		for text in texts:
			for token in text:
				frequency[token] += 1
		top5 = []
		numTimes = []
		for x in range(0,5):
			topWord = sorted(frequency, key=frequency.get, reverse=True)[x]
			numTimes.append(frequency[topWord])
			top5.append(topWord)

		titleG = 'Most associated words with: ' + addStop
		if graph_type == 'bar':
			data = [
				plotly.graph_objs.Bar(
					x=top5,
					y=numTimes,
					opacity = 0.5
				)
			]
		elif graph_type == 'scatter':
			data = [
				plotly.graph_objs.Scatter(
					x=top5,
					y=numTimes,
					mode = 'markers'
				)
			]
		elif graph_type == 'line':
			data = [
				plotly.graph_objs.Line(
					x=top5,
					y=numTimes,
					opacity = 0.5
				)
			]

		
		layout = plotly.graph_objs.Layout(
			autosize=True,
			title=titleG
		)

		plotly_fig = plotly.graph_objs.Figure(data=data, layout=layout) 
		plotly_fig.layout.template = 'simple_white'
		div_fig = plotly.offline.plot(plotly_fig, auto_open=False, output_type='div')
		context['graph'] = div_fig
		return context

@login_required
class SentAnalysis(TemplateView):
	template_name = 'graphH.html'

	def __init__(self, name):
		self.name = name

	def get_context_data(self, **kwargs):	
		context = super().get_context_data(**kwargs)
		global studyId
		global graph_type
		list = Study.objects.all()
		offset = len(studyId)- 10
		keyWord = studyId[:offset]
		arr = []
		twList = Study.objects.get(study_id = studyId).tweets.all()

		pos = 0
		neg = 0
		neutral = 0 
		for y in twList:
			tempText = y.text
			arr.append(tempText)
		for x in arr:
			tb = TextBlob(x)
			if tb.sentiment[0]<0:
				neg += 1 
			elif tb.sentiment[0]==0:
				neutral += 1
			else:              
				pos +=1

		analysis = [pos,neg,neutral]                 

		titleG = 'Overall sentiment of: ' + keyWord
		if graph_type == 'bar':
			data = [
				plotly.graph_objs.Bar(
					x=['positive','negative','neutral'],
					y=analysis,
					opacity = 0.5
				)
			]
		elif graph_type == 'scatter':
			data = [
				plotly.graph_objs.Scatter(
					x=['positive','negative','neutral'],
					y=analysis,
					mode = 'markers'
				)
			]
		elif graph_type == 'line':
			data = [
				plotly.graph_objs.Line(
					x=['positive','negative','neutral'],
					y=analysis,
					opacity = 0.5
				)
			]
		layout = plotly.graph_objs.Layout(
			autosize=True,
			title=titleG
		)

		plotly_fig = plotly.graph_objs.Figure(data=data, layout=layout) 
		plotly_fig.layout.template = 'simple_white'
		div_fig = plotly.offline.plot(plotly_fig, auto_open=False, output_type='div')
		context['graph'] = div_fig
		return context

@login_required
def sent_analysis(request):
	global studyId
	global graph_type
	studyId = request.session['study_select']
	graph_type = request.session.get('graph_type', None)
	title = 'Sentiment Analysis'
	g = SentAnalysis(request)
	context = g.get_context_data()
	context['studyId'] = studyId
	return render(request, 'analysis/graph.html', context)

@login_required
def freq_word(request):
	global studyId
	global graph_type
	studyId = request.session['study_select']
	graph_type = request.session.get('graph_type', None)
	title = 'Frequent Words'
	g = FreqWordsAnalysis(request)
	context = g.get_context_data()
	context['studyId'] = studyId
	return render(request, 'analysis/graph.html', context)

@login_required
def date_graph(request):
	global studyId
	global graph_type
	studyId = request.session['study_select']
	graph_type = request.session.get('graph_type', None)
	g = DateAnalysis(request)
	context = g.get_context_data()
	context['studyId'] = studyId
	return render(request, 'analysis/graph.html', context)


def get_study(request):
	# studyid = request.POST['study_select']
	print('LOG: Entered get_study()')
	studyid = request.session['study_select']
	print('LOG: studid = ' + studyid)
	if len(studyid) == 0:
		print('LOG: Redirecting to analysis/analysis')
		return redirect('/analysis')
	# context = {'study_html': ""}
	# context['study_html'] += ("<table class=\"table table-bordered\"><tr><th>Timestamp/th><th>Username</th><th>Tweet</th><th>Hashtags</th></tr>")	
	# data_current_study = Study.objects.get(study_id=studyid).tweets.all()
	current_study = StudyTable(Study.objects.get(study_id=studyid).tweets.all())
	# print("Number of tweets: "+ str(len(data_current_study)))
	# for _tweet in Study.objects.get(study_id=studyid).tweets.all():
	# 	context['study_html'] += ("<tr><td>"+ str(_tweet.created_at) +"</td><td>"+ str(_tweet.screen_name) +"</td><td>"+ str(_tweet.text) +"</td><td>"+ str(_tweet.hashtags) +"</td></tr>")
	# context['study_html']+=("</table>")
	RequestConfig(request, paginate=False).configure(current_study)

	return render(request, 'analysis/get_study.html', locals())
	# return render(request, 'analysis/get_study.html', context)

@login_required
class DateAnalysis(TemplateView):
	template_name = 'graph.html'

	def __init__(self, name):
		self.name = name

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		global studyId
		global graph_type
		offset = len(studyId)- 10
		keyWord = studyId[:offset]
		arr = []
		twList = Study.objects.get(study_id = studyId).tweets.all()

		for y in twList:
			tempText = y.created_at
			tempText = to_datetime(tempText)
			arr.append(tempText)

		data = {"dates":arr}
		df = pd.DataFrame(data)
        
		frequency = defaultdict(int)
		#creating datetime
		for y in arr:
			frequency[y] += 1
		freq = []  
		df['dates']=pd.to_datetime(df['dates'])
		df.sort_values(by = 'dates')       
		for x in df.dates:
			freq.append(frequency[x])

		x = df.dates
		y = freq

		if graph_type == 'bar':
			stuff_to_display = plotly.graph_objs.Bar(x=x, y=y, name = "Date")
		elif graph_type == 'scatter':
			stuff_to_display = plotly.graph_objs.Scatter(x=x, y=y, mode = "markers", name = "Date")
		elif graph_type == 'line':
			stuff_to_display = plotly.graph_objs.Line(x=x, y=y, name = "Date")

		Title = "Tweets over time for: " + keyWord
		data = plotly.graph_objs.Data([stuff_to_display])
		layout = plotly.graph_objs.Layout(title = Title, xaxis={'title': 'date and time'}, yaxis={'title':'number of tweets'})
		layout.template = 'simple_white'
		figure  = plotly.graph_objs.Figure(data=data, layout=layout)
		div = plotly.offline.plot(figure, auto_open=False, output_type='div')

		context['graph'] = div
		return context

@login_required
def analysis(request):
	context ={'studies_html':""}
	context['studies_html']+=("<table class=\"table table-bordered\"><tr><th>Study ID</th><th>Number of Tweets</th><th>Time Stamp</th><th>User</th><th>Create Analysis</th></tr>")
	user = request.user
	for x in Study.objects.all():
		if str(x.user) == str(user):
			context['studies_html']+=("<tr><td>"+x.study_id[:-10]+"</td><td>"+str(x.count)+"</td><td>"+time.ctime(int(x.study_id[-10:]))+"</td><td>"+x.user+"</td><td><button class=\"btn btn-info btn-sm\" type=\"submit\" name=\"study_select\" value=\""+x.study_id+"\">Create Analysis</button></td></tr>")
	context['studies_html']+=("</table>")
	return render(request, 'analysis/analysis.html', context)


def to_datetime(datestring):
	time_tuple = parsedate_tz(datestring.strip())
	dt = datetime(*time_tuple[:6])
	return dt - timedelta(seconds=time_tuple[-1])


@login_required
def graphs(request, analysis_type):
	request.session['graph_type'] = request.POST.get('graph_type', None) 
	print('LOG: Reache here: graphs(). Type is ' + analysis_type)
	study_select = ''
	try:
		study_select =  request.session['study_select']
	except:
		print('LOG: No data in study_select of request.SESSION')
		print('LOG: Redirecting to List of Analysis list Page')
		return analysis(request)
	print('LOG: Study ID: ' + study_select)

	request.session['tab_1_class'] = ''
	request.session['tab_2_class'] = 'active'
	request.session['tab_3_class'] = ''

	if request.session.get('graph_type', None) == None:	
		request.session['graph_type'] = 'bar'
	print('LOG: ---- graph_type: ' + request.session.get('graph_type', None))

	# Types of Graphs
	### 'line'
	### 'bar'
	### 'scatter'
	
	if analysis_type == "sentiment":
		request.session['analysis_type'] = 'sentiment'
		return sent_analysis(request)
	elif analysis_type == "freq_words":
		request.session['analysis_type'] = 'freq_words'
		return freq_word(request)
	elif analysis_type == "date":
		request.session['analysis_type'] = 'date'
		return date_graph(request)
	else:
		return analysis(request)

@login_required
def view_tweets(request):
	tab = 'view_tweets'
	print('LOG: Reache here: analysis_detail(). Tab is ' + tab)
	study_select = ''
	try:
		try:
			study_select =  request.session['study_select'] = request.POST['study_select']
		except:
			print('LOG: No data in study_select of request.POST')
			study_select = request.session['study_select']
	except:
		print('LOG: No data in study_select of request.SESSION')
		print('LOG: Redirecting to List of Analysis list Page')
		return analysis(request)

	print('LOG: analysis_select: ' + tab)
	print('LOG: Study ID: ' + study_select)
	request.session['tab_1_class'] = ''
	request.session['tab_2_class'] = ''
	request.session['tab_3_class'] = ''
	request.session['analysis_select'] = tab

	if tab == "view_tweets":
		request.session['tab_1_class'] = 'active'
		return get_study(request)
	else:
		request.session['analysis_select'] = 'view_tweets'
		request.session['tab_1_class'] = 'active'
		return get_study(request)

@login_required
def exports(request):
	print('LOG: Reache here: Tab is exports().')
	study_select = ''
	try:
		study_select =  request.session['study_select']
	except:
		print('LOG: No data in study_select of request.SESSION')
		print('LOG: Redirecting to List of Analysis list Page')
		return analysis(request)
	print('LOG: Study ID: ' + study_select)
	request.session['tab_1_class'] = ''
	request.session['tab_2_class'] = ''
	request.session['tab_3_class'] = 'active'

	return render(request, 'analysis/exports.html')

@login_required
def export_clicked(request):
	print('LOG: Clicked Export Button.')
	selected_attributes = request.POST.getlist('check_attributes[]', [])
	selected_format = request.POST.get('check_formats', None)
	print('Selected Attributes: ' + str(selected_attributes))
	print('Selected Format: ' + str(selected_format))
	if selected_format == 'csv':
		return export_csv(request, selected_attributes)
	elif selected_format == 'xlsx':
		return export_excel(request, selected_attributes)
	elif selected_format == 'json':
		return export_json(request, selected_attributes)
	elif selected_format == 'pdf':
		return export_pdf(request, selected_attributes)
	elif selected_format == 'xml':
		return export_xml(request, selected_attributes)
	elif selected_format == 'spss':
		return export_spss(request, selected_attributes)
	else:
		return export_csv(request, selected_attributes)


def export_excel(request, selected_attributes):
	studyid =  request.session['study_select']
	tweet_resource = resources.create_TweetResource(get_attributes_to_export(selected_attributes))
	dataset = tweet_resource.export(Study.objects.get(study_id=studyid).tweets.all())
	response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
	response['Content-Disposition'] = 'attachment; filename="'+ studyid + ' - '  + str(datetime.now()) +'.xls"'
	return response

def export_csv(request, selected_attributes):
	studyid =  request.session['study_select']
	tweet_resource = resources.create_TweetResource(get_attributes_to_export(selected_attributes))
	dataset = tweet_resource.export(Study.objects.get(study_id=studyid).tweets.all())
	response = HttpResponse(dataset.csv, content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="'+ studyid + ' - '  + str(datetime.now()) +'.csv"'
	return response

def export_json(request, selected_attributes):
	studyid =  request.session['study_select']
	tweet_resource = resources.create_TweetResource(get_attributes_to_export(selected_attributes))
	dataset = tweet_resource.export(Study.objects.get(study_id=studyid).tweets.all())
	response = HttpResponse(dataset.json, content_type='application/json')
	response['Content-Disposition'] = 'attachment; filename="'+ studyid + ' - '  + str(datetime.now()) +'.json"'
	return response

def export_pdf(request, selected_attributes):
	studyid =  request.session['study_select']
	tweet_resource = resources.create_TweetResource(get_attributes_to_export(selected_attributes))
	dataset = tweet_resource.export(Study.objects.get(study_id=studyid).tweets.all())
	pdf_data = render_html_to_pdf(dataset.html)
	response = HttpResponse(pdf_data, content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="'+ studyid + ' - '  + str(datetime.now()) +'.pdf"'
	return response

def export_xml(request, selected_attributes):
	studyid =  request.session['study_select']
	tweet_resource = resources.create_TweetResource(get_attributes_to_export(selected_attributes))
	dataset = tweet_resource.export(Study.objects.get(study_id=studyid).tweets.all())
	obj = json.loads(dataset.json)
	xml = dicttoxml.dicttoxml(obj)
	xml_pretty = parseString(xml).toprettyxml()
	response = HttpResponse(xml_pretty, content_type='text/xml')
	response['Content-Disposition'] = 'attachment; filename="'+ studyid + ' - '  + str(datetime.now()) +'.xml"'
	return response

def export_spss(request, selected_attributes):
	studyid =  request.session['study_select']
	tweet_resource = resources.create_TweetResource(get_attributes_to_export(selected_attributes))
	dataset = tweet_resource.export(Study.objects.get(study_id=studyid).tweets.all())
	obj = json.loads(dataset.json)
	df = pd.json_normalize(obj)
	pyreadstat.write_sav(df, 'Data/SPSS/template.sav')
	response = HttpResponse()
	f = default_storage.open('Data/SPSS/template.sav').read()
	# response.write(f)
	response = HttpResponse(f, content_type='application/x-spss-sav')
	response['Content-Disposition'] = 'attachment; filename="'+ studyid + ' - '  + str(datetime.now()) +'.sav"'
	return response


def get_attributes_to_export(selected_attributes):
	attributes = ["screen_name", "text", "created_at", "hashtags", "url", "country"]
	if 'all' in selected_attributes:
		return attributes
	else:
		return selected_attributes


# DECPRECATED: NOT USING THIS
# def export_csv_OLD(request, selected_attributes):
# 	studyid =  request.session['study_select']
# 	response  = HttpResponse(content_type='text/csv')
# 	response['Content-Disposition'] = 'attachment; filename="'+ studyid + ' - '  + str(datetime.now()) +'.csv"'
# 	writer = csv.writer(response)
# 	writer.writerow(['Username', 'Tweet', 'Timestamp', 'Sentiments', 'Hashtags', 'URLs', 'Location'])
# 	current_study_data = Study.objects.get(study_id=studyid).tweets.all()
# 	for item in current_study_data:
# 		writer.writerow([item.screen_name, item.text, item.created_at, '', item.hashtags, item.url, item.country ])
# 	return response


# DECPRECATED: NOT USING THIS
# def export_excel_OLD(request, selected_attributes):
# 	studyid =  request.session['study_select']
# 	response  = HttpResponse(content_type='application/ms-excel')
# 	response['Content-Disposition'] = 'attachment; filename="'+ studyid + ' - '  + str(datetime.now()) +'.xls"'
# 	wb = xlwt.Workbook(encoding='utf-8')
# 	ws = wb.add_sheet('Raw Data')
# 	row_num = 0
# 	font_style = xlwt.XFStyle()
# 	font_style.font.bold = True
# 	columns = ['Username', 'Tweet', 'Timestamp', 'Sentiments', 'Hashtags', 'URLs', 'Location']
# 	for col_num in range(len(columns)):
# 		ws.write(row_num, col_num, columns[col_num], font_style)
	
# 	font_style = xlwt.XFStyle()
# 	current_study_data = Study.objects.get(study_id=studyid).tweets.all()
# 	for item in current_study_data:
# 		row_num += 1
# 		for col_num in range(0, 7):
# 			placeholder = ''
# 			if col_num == 0:
# 				placeholder= item.screen_name
# 			elif col_num == 1:
# 				placeholder = item.text
# 			elif col_num == 2:
# 				placeholder = item.created_at
# 			elif col_num == 3:
# 				placeholder = ''
# 			elif col_num == 4:
# 				placeholder = item.hashtags
# 			elif col_num == 5:
# 				placeholder = item.url
# 			elif col_num == 6:
# 				placeholder = item.country
# 			else:
# 				continue
# 			ws.write(row_num, col_num, placeholder, font_style)
# 	wb.save(response)
# 	return response




# DECPRECATED: NOT USING THIS
# @login_required
# def create_analysis(request):
# 	print('LOG: Reache here: Create_analysis()')
# 	answer = ''
# 	study_select = ''
# 	try:
# 		answer = request.POST['analysis_select']
# 		study_select = request.POST['study_select']
# 		request.session['study_select'] = request.POST['study_select']
# 		request.session['analysis_select'] = request.POST['analysis_select']
# 	except:
# 		print('LOG: Catched Exception in create_analysis.')
# 		answer = 'view_tweets'
# 	print('LOG: analysis_select: ' + answer)
# 	print('LOG: Study ID: ' + study_select)
# 	request.session['tab_1_class'] = ''
# 	request.session['tab_2_class'] = ''
# 	request.session['tab_3_class'] = ''
# 	if answer == "tweet_sent":
# 		request.session['tab_2_class'] = 'active'
# 		return sent_analysis(request)
# 	elif answer == "freq_words":
# 		request.session['tab_2_class'] = 'active'
# 		return freq_word(request)
# 	elif answer == "date":
# 		return graph(request)
# 	elif answer == "view_tweets":
# 		request.session['tab_1_class'] = 'active'
# 		return get_study(request)
# 	else:
# 		request.session['tab_1_class'] = 'active'
# 		return get_study(request)


# analysis/{analysis_select}/ ✔

# How to use static files like .css and .js  ✔
# URl Patterns are not good. Need to re-write URL Patterns ✔
## with this, we can resolve all Django_tables2 problems like pagination and sorting ✔

# Persistant Session ✔
## - analysis_select ✔
## - study_id ✔

# Design Tabs ✔

# Redesign Tweets Table,and Analysis table to look good ✔
# Visualize data TAB ***** ✔
# analysis/analysis <-- Make this page look good like in design documnets ✔
# Need to Re-write Left Navbar - (Tooltip, Material Icons) ✔

# EXPORT
## Export to SPSS (.sav file)
## Write functionality to download formats in JSON, Excel, XML, PDF and CSV  ✔
## Write data into the documents according to the filtered attributes. ✔
## Javascript: 
### When All cicked, uncheck other attributes. ✔
### When other attributes are checked, uncheck All. ✔
### When required fields are selected, give an alert ✔

