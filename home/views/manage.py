from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render

from generic.query import pinned_product_objects
from generic.variables import LOGIN_URL
from generic.views import json_response

from home.models import Favorite, PinnedProduct,Notification
from space.models import Product

def index(request):
	# filter limited order
	context = {}

	products = Product.objects.all()
	trending_products = products
	recent_products = Product.objects.all().order_by('-uid')[:10]
	pinned_products = products
	related_products = products

	if request.user.is_authenticated:
		favorite = Favorite.objects.filter(user=request.user).order_by('-uid')[:7]
		context['favorite'] = favorite
		
		pinned_products = pinned_product_objects(request.user, 10)
		context['pinned_products'] = pinned_products

	context['trending_products'] = trending_products
	context['recent_products'] = recent_products
	context['related_products'] = related_products

	return render(request, 'home/manage/index.html', context)


def manager(request):
	if request.method == 'GET':
		what = request.GET.get('filter',None)
		if what is not None:
			what = what.lower()
			if what == 'pinned-products':
				return render(request, 'home/filtering/pinned.html', {})

	return index(request)


@login_required(login_url=LOGIN_URL)
def notification(request):
	context = {}
	return render(request, 'home/manage/notification.html', context)


@login_required(login_url=LOGIN_URL)
def notification_status_changle(request, uid):
	try:
		notification = Notification.objects.get(uid=uid)

		if notification.user.phone == request.user.phone:
			seen = request.GET.get('seen', None)
			print(seen)
			if seen is not None:
				seen = seen.lower()
				if seen == 'false':
					notification.seen = False
					return _update_user_notification_status(request, notification)

				elif seen == 'true':
					notification.seen = True
					return _update_user_notification_status(request, notification)
					
	except ObjectDoesNotExist as e:
		pass

	return json_response(request, {}, 'invalid')




def _update_user_notification_status(request, notification):
	notification.save()

	user_unseen_notification = Notification.objects.filter(user=request.user, seen=False)
	if user_unseen_notification.exists():
		request.user.has_notification = True
		request.user.save()

	else:
		request.user.has_notification = False
		request.user.save()

	return json_response(request, {}, 'done')
