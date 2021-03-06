from account.models import Account

from api.serializer_models.space.product import ( ProductSerializer, ProductReactSerializer,
	ProductSerializerForReact)
from api.serializer_models.home import PinnedProductDetailSerializer
from api.handler import activity
from api.handler.tokenization import decode as token_decode

from django.contrib.postgres.search import SearchVector
from django.core.exceptions import ObjectDoesNotExist

from generic.constants import PRODUCT_PAGINATION_SIZE, MAX_TRENDING_PRODUCT
from generic.crypto import hashing_into_int

from home.models import PinnedProduct

from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from space.models import Product, ProductReact, Category, Space
from space.models import _PRODDUCT_CATEGORY_KEY_DIC as category_key



@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def product_react_list(request, format=None):
	token = request.GET.get('token', None)
	if token is None:
		raise NotFound('invalid request')
	data = token_decode(token)
	if data is None:
		raise NotFound('invalid request')
	if request.user.id != data['user_id']:
		raise PermissionDenied('access denied')
	result = ProductReact.objects.filter(user_id=data['user_id']).order_by('-time_date')
	serializer = ProductReactSerializer(result, many=True)
	return Response(serializer.data)



@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def product_react_request(request, uid, format=None):
	token = request.GET.get('token', None)
	what = request.GET.get('react', None)
	if token is None:
		raise NotFound('request not found')
	data = token_decode(token)
	if data is None:
		raise None('invalid request')
	if request.user.id != data['user_id']:
		raise PermissionDenied('access denied')
	if what is None:
		try:
			result = Product.objects.get(uid=uid)
			serializer = ProductSerializerForReact(result)
			return Response(serializer.data)
		except ObjectDoesNotExist as e:
			raise NotFound('request not found') 

	result = activity.handle_react(request.user, uid , what)
	if result is None:
		raise NotFound('request not found')

	serializer = ProductSerializerForReact(result)
	return Response(serializer.data)



@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def product_pinned_request(request, uid, format=None):
	token = request.GET.get('token', None)
	req = request.GET.get('req', None)
	if token is None:
		raise NotFound('request not found')
	data = token_decode(token)
	if data is None:
		raise None('invalid request')
	if request.user.id != data['user_id']:
		raise PermissionDenied('access denied')
	req = req.upper()
	result = activity.handle_pin(request.user, uid, req)
	if not result:
		raise NotFound('request not found')
	return Response({'response' : True});



@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@renderer_classes((JSONRenderer,))
def manager(request, format=None):
	token = request.GET.get('token', None)
	if token is None:
		raise NotFound('invalid request')
	data = token_decode(token)
	if data is None:
		raise NotFound('invalid request')
	if request.user.id != data['user_id']:
		raise PermissionDenied('access denied')

	category = request.GET.get('category', None)
	query = request.GET.get('query', None)
	pinned_by = request.GET.get('pinned_by', None)
	space = request.GET.get('space', None)

	page = request.GET.get('page', None)
	page = __clean_value(page)

	serializer = None

	if category is not None:
		serializer = __category_filter(category, page=page)

	elif query is not None:
		serializer = __query_filter(query, page=page)

	elif pinned_by is not None:
		serializer = __user_pinned_filter(data['user_id'], page=page, request=request)

	elif space is not None:
		serializer = __space_product(space, page=page)

	else:
		serializer = __all_products(page)

	if serializer:
		return Response(serializer.data)

	raise NotFound('invalid request')




def __clean_value(value):
	if value is not None:
		if value.isdigit():
			return abs(int(value))
	return None




def __category_filter(category, **kwargs):
	try:
		category = category.lower()
		key = category_key.get(category)

		page = kwargs.get('page', None)

		if page is None:
			return None

		if page is None and limit is None:
			return None

		category_obj = Category.objects.get(name__iexact=key)

		offset = page*PRODUCT_PAGINATION_SIZE
		result = Product.objects.filter(category_id=category_obj.id)[offset:offset+PRODUCT_PAGINATION_SIZE]

		serializer = ProductSerializer(result, many=True)
		return serializer

	except ObjectDoesNotExist as e:
		return None



def __user_pinned_filter(user_id, **kwargs):
	try:
		user = Account.objects.get(id=user_id)
		request = kwargs.get('request', None)
		if request is None:
			return None

		if request.user.id != user.id:
			raise PermissionDenied('access denied')

		page = kwargs.get('page', None)

		if page is None:
			return None

		offset = page * PRODUCT_PAGINATION_SIZE
		result = PinnedProduct.objects.filter(user_id=user_id)[offset:offset+PRODUCT_PAGINATION_SIZE]		
		serializer = PinnedProductDetailSerializer(result, many=True)
		
		return serializer

	except ObjectDoesNotExist as e:
		return None



def __query_filter(query, **kwargs):
	query = query.lower()

	limit = kwargs.get('limit', None)
	page = kwargs.get('page', None)

	if page is None:
		return None

	if query == 'trending':

		if page==0:
			result = Product.objects.order_by('-time_date').order_by('-react_good')[0:MAX_TRENDING_PRODUCT]
		else:
			result = Product.objects.none()			

		serializer = ProductSerializer(result, many=True)
		return serializer

	elif len(query) > 0:

		offset = page * PRODUCT_PAGINATION_SIZE
		result = Product.objects.annotate(search=SearchVector('title', 'description',
			'space__name')).filter(search=query)[offset:offset+PRODUCT_PAGINATION_SIZE]

		serializer = ProductSerializer(result, many=True)
		return serializer

	return None



def __space_product(space_name, **kwargs):
	space = None
	try:
		space = Space.objects.get(code=hashing_into_int(space_name))
	except ObjectDoesNotExist as e:
		return None

	limit = kwargs.get('limit', None)
	page = kwargs.get('page', None)

	if page is None:
		return None

	offset = page*PRODUCT_PAGINATION_SIZE
	result = Product.objects.filter(space_id=space.id)[offset:offset+PRODUCT_PAGINATION_SIZE]	
	serializer = ProductSerializer(result, many=True)
	return serializer



def __all_products(page):
	if page is None:
		return None

	offset = page*PRODUCT_PAGINATION_SIZE
	result = Product.objects.all()[offset:offset+PRODUCT_PAGINATION_SIZE]
	return ProductSerializer(result, many=True)
