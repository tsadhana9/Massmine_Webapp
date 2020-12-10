from import_export import resources
from import_export.fields import Field
import django_tables2
from dateutil.parser import parse
from query.models import Tweet


def create_TweetResource(model_fields):
    class TweetResource(resources.ModelResource):
        class Meta:
            model = Tweet
            # created_at = Field(attribute='created_at', column_name='Timestamp')
            # screen_name = Field(attribute='screen_name', column_name='Username')
            # text = Field(attribute='text', column_name='Tweet')
            # hashtags = Field(attribute='hashtags', column_name='Hashtag')
            fields = model_fields #("screen_name", "text", "created_at", "hashtags", "url", "country")
    return TweetResource()



class StudyTable(django_tables2.Table):
	created_at = django_tables2.Column(verbose_name = 'Timestamp')
	screen_name = django_tables2.Column(verbose_name = 'Username')
	text = django_tables2.Column(verbose_name = 'Tweet')
	hashtags = django_tables2.Column(verbose_name = 'Hashtag')


	def render_created_at(self, value):
		return parse(value).strftime('%m/%d/%Y')

	def render_screen_name(self, value):
		return "@" + value

	def render_hashtags(self, value):
		return "#" + value
	
	class Meta:
		attrs = {"id": "table_tweets"}
		model = Tweet
		template_name = 'django_tables2/bootstrap.html'
		sequence = ("created_at", "screen_name", "text", "hashtags",)
		# fields = ("created_at", "screen_name", "text", "hashtags")