from api.handler.tokenization import decode as token_decode

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect

from generic.constants import LOGIN_URL
from generic.crypto import get_api_token
from generic.views import invalid_request


from home.models import Favorite, PinnedProduct,Notification
from space.models import Product,Category,Status, _PRODDUCT_CATEGORY_KEY_DIC,Space

from uuid import uuid1


def index(request):
	context = {}

	categories = Category.objects.all()
	context['categories'] = categories

	mens_category = categories.get(name=_PRODDUCT_CATEGORY_KEY_DIC['men-fashion'])
	womens_category = categories.get(name=_PRODDUCT_CATEGORY_KEY_DIC['women-fashion'])
	gadets_category = categories.get(name=_PRODDUCT_CATEGORY_KEY_DIC['gadget-accessories'])

	recent_products = Product.objects.filter(in_stock=True).values(
		'uid', 'title', 'price', 'react_good', 'react_bad', 'react_fake', 'logo_url', 'space__name').order_by(
		'-time_date')[:8]

	most_goods_products = Product.objects.values(
		'uid', 'title', 'price', 'react_good', 'react_bad', 'react_fake', 'logo_url', 'space__name').order_by(
		'-react_good')[:4]


	top_mens_products = Product.objects.filter(category_id=mens_category.id).values(
		'uid', 'title', 'price', 'react_good', 'react_bad', 'react_fake', 'logo_url', 'space__name').order_by(
		'-react_good')[:4]


	top_womens_products = Product.objects.filter(category_id=womens_category.id).values(
		'uid', 'title', 'price', 'react_good', 'react_bad', 'react_fake', 'logo_url', 'space__name').order_by(
		'-react_good')[:4]


	top_gadgets_products = Product.objects.filter(category_id=gadets_category.id).values(
		'uid', 'title', 'price', 'react_good', 'react_bad', 'react_fake', 'logo_url', 'space__name').order_by(
		'-react_good')[:4]


	top_spaces = Status.objects.values('space__name', 'space__logo', 'total_pinned','total_favorite',
		 'rating', 'total_post').order_by('-rating')[:8]


	context['recent_products'] = recent_products
	context['most_goods_products'] = most_goods_products
	context['top_mens_products'] = top_mens_products
	context['top_womens_products'] = top_womens_products
	context['top_gadgets_products'] = top_gadgets_products
	context['top_spaces'] = top_spaces
	
	return render(request, 'home/manage/index.html', context)


def manager(request):
	return index(request)


@login_required(login_url=LOGIN_URL)
def explore(request):
	space_list = Space.objects.all()
	token = get_api_token(request)
	context = {
		'space_list' : space_list,
		'token' : token
	}

	return render(request, 'home/manage/explore.html', context)


@login_required(login_url=LOGIN_URL)
def explore_product(request):
	context = {}
	has_attribute = False

	if request.method == 'GET':
		category = request.GET.get('category', None)
		token = get_api_token(request)
		context['token'] = token

		if category is not None:
			has_attribute = True
			context['category'] = category

	context['has_attribute'] = has_attribute

	return render(request, 'home/manage/explore_product.html', context)



@login_required(login_url=LOGIN_URL)
def notification(request):
	context = {}
	if request.method == 'GET':
		query = request.GET.get('query', None)
		if query:
			query = query.lower()
			context['query'] = query
		else:
			context['query'] = 'all'

	token = get_api_token(request)
	context['token'] = token
	return render(request, 'home/manage/notification.html', context)


@login_required(login_url=LOGIN_URL)
def notification_route(request, uid):
	if request.method != 'GET':
		return invalid_request(request)

	token = request.GET.get('token', None)
	action = request.GET.get('action', None)

	if token is None or action is None:
		return invalid_request(request)

	data = token_decode(token)
	if data is None:
		return invalid_request(request)

	user_id = data['user_id']
	if request.user.id != user_id:
		return invalid_request(request)

	item = Notification.objects.filter(uid=uid, user_id=user_id).first()
	if item is None:
		return invalid_request(request)

	item.seen = True
	item.save()

	remain_notification = Notification.objects.filter(seen=False, user_id=user_id).count()
	if remain_notification == 0:
		request.user.has_notification = False
		request.user.save()

	return redirect(action)
