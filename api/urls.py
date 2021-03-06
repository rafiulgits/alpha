from django.urls import path, include
from api.handler import media
from api.views import home
from api.views.space import space, product

urlpatterns = [

	path('user/product_react_list/', product.product_react_list,	 
		name='api_user_product_react_list'),

	path('user/favorite_space_list/', home.user_favorite_space_list, name='api_user_favorite_space_list'),

	path('user/pinned_product_list/', home.user_pinned_product_list, name='api_user_pinned_prodcut_list'),

	path('user/notification/', home.user_notification_list, name='user-notification'),

	path('product/', product.manager, name='product-manager'),

	path('product/<uid>/activity/react/', product.product_react_request, name='react-view'),

	path('product/<uid>/activity/pin/', product.product_pinned_request, name='pin-view'),

	path('space/', space.manager, name='space-manager'),
	
	path('space/<name>/activity/favorite/', space.favorite_request, name='favorite-view'),

	path('media/update/', media.update, name='media-update'),
]