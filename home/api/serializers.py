from home.models import Notification

from space.models import Product

from rest_framework.serializers import ModelSerializer



class ProductSerializer(ModelSerializer):
	class Meta:
		model = Product
		fields = ('uid', 'title', 'price', 'logo_url','react_good', 'react_bad', 'react_fake')



class NotificationSerializer(ModelSerializer):
	class Meta:
		model = Notification
		fields = ('uid', 'unix_time', 'label', 'title', 'message', 'seen', 'action')