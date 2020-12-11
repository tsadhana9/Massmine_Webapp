# analysis/urls.py

from django.conf.urls import url
from analysis import views

# SET THE NAMESPACE!
app_name = 'analysis'

urlpatterns=[
    url(r'^analysis/$',views.analysis,name='analysis'),
    url(r'^graphs/(?P<analysis_type>\w{0,20})/$',views.graphs,name='graphs'),
    url(r'^view_tweets/$',views.view_tweets,name='view_tweets'),
    url(r'^export_csv/', views.export_csv, name='export_csv'),
    url(r'^export_excel/', views.export_excel, name='export_excel'),
    url(r'^exports/', views.exports, name='exports'),
    url(r'^export_clicked/', views.export_clicked, name='export_clicked'),
    # url(r'^graph/$', views.graph, name = 'graph'),
    # url(r'^create_analysis/',views.create_analysis,name='create_analysis'),
]

