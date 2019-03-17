from generic.query import pinned_product_objects

from home.api.serializers import ProductSerializer,NotificationSerializer
from home.models import PinnedProduct, Notification

from rest_framework.exceptions import PermissionDenied,NotFound
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from space.models import Product


class PinnedProductsViewList(ListAPIView):
	serializer_class = ProductSerializer
	permission_classes = (IsAuthenticated,)

	def get_queryset(self):
		request = self.request
		if not request.user.is_authenticated:
			raise NotFound('request not found')
		ac_id = self.kwargs['ac_id']
		if request.user.phone != ac_id:
			raise PermissionDenied('invalid request for this user')
		else:
			queryset = pinned_product_objects(request.user)
			return queryset




class NotificationAViewList(ListAPIView):
	serializer_class = NotificationSerializer
	permission_classes = (IsAuthenticated,)

	def get_queryset(self):
		user = self.request.user
		if not user.is_authenticated:
			raise NotFound('request not found')
		ac_id = self.kwargs['ac_id']
		if user.phone != ac_id:
			raise PermissionDenied('invalid request for this user')

		else:
			queryset = Notification.objects.filter(user=user).order_by('-uid')
			return queryset
