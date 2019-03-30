from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

from generic.media import Image
from generic.variables import LOGIN_URL, now_str,random, PRODUCTS_FILE_PATH
from generic.views import json_response, invalid_request

from home.models import PinnedProduct

from space.forms import ProductPostForm,ProductUpdateForm
from space.models import Product, ProductMedia, ProductReact,Status


def route(request):
	return redirect('/space/product/all/')


def view(request, uid):
	context = {}
	try:
		product = Product.objects.get(uid = uid)
		media = ProductMedia.objects.filter(product=product)
		related_products = Product.objects.filter(category=product.category).order_by('-time_date')[:10]

		if request.user.is_authenticated:
	
			react_obj = ProductReact.objects.filter(product=product, user=request.user).first()
			if react_obj is not None:
				context['has_react'] = True
				context['current_react'] = react_obj.react
			else:
				context['has_react'] = False


			pin = PinnedProduct.objects.filter(product=product, user=request.user).first()
			if pin is not None:
				context['has_pin'] = True
			else:
				context['has_pin'] = False


		context['product'] = product
		context['media'] = media
		
		context['related_products'] = related_products

		return render(request, 'space/product/single.html', context)
		
	except ObjectDoesNotExist as e:
		return invalid_request(request=request)


def manager(request):
	products = Product.objects.all()
	context = {
		'products' : products
	}

	return render(request, 'space/product/list.html', context)
	


@login_required(login_url=LOGIN_URL)
def create(request):
	context = {}
	if request.method == 'POST':
		form = ProductPostForm(request.POST, request.FILES ,request=request)
		if form.is_valid():
			form.load_images()
			post = form.save()

			status = Status.objects.get(space=post.space)
			status.total_post = status.total_post + 1
			status.save()

			return redirect('/space/product/'+post.uid+'/')

	else:
		form = ProductPostForm(request=request)

	context['form'] = form

	return render(request, 'space/product/create.html',context)


@login_required(login_url=LOGIN_URL)
def update(request, uid):
	try:
		product = Product.objects.get(uid=uid)
		if product.space.owner == request.user:
			context = {}

			if request.method == 'POST':
				form = ProductUpdateForm(request.POST, product=product)
				if form.is_valid():
					product.title = form.cleaned_data['title']
					product.description = form.cleaned_data['description']
					product.price = form.cleaned_data['price']
					product.category = form.cleaned_data['category']
					product.in_stock = form.cleaned_data['in_stock']

					product.save()

					return redirect('/space/product/'+uid+'/')


			form = ProductUpdateForm(product=product)
			media = ProductMedia.objects.filter(product=product)

			context['form'] = form
			context['media'] = media

			return render(request, 'space/product/update.html', context) 


	except ObjectDoesNotExist as e:
		pass

	return invalid_request(request)


@login_required(login_url=LOGIN_URL)
def update_product_media(request, uid, media_id):
	if request.method == 'POST':
		try:
			product = Product.objects.get(uid=uid)
			media = ProductMedia.objects.get(uid=media_id)

			if media.product == product:
				file = request.FILES.get('image', None)

				if file is not None:
					img_src = Image.load(file_stream=file)

					if img_src is not None:
						img_path = Image.save(PRODUCTS_FILE_PATH, img_src)

						Image.delete(media.location)
						media.delete()

						new_media = ProductMedia(location = img_path, product=product)
						new_media.uid = random()
						new_media.save()

						product.logo_url = new_media.location
						product.save()


		except ObjectDoesNotExist as e:
			pass


	return redirect('/space/product/'+uid+'/update/')

