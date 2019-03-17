from django.urls import path

from account.api.views import (UserProductReactList, UserFavoriteSpaceList,
	UserPinnedProductList, user_thumbnail_update)

from home.api.views import PinnedProductsViewList,NotificationAViewList

from space.api.views import SpaceBanner

urlpatterns = [

	path('user/<ac_id>/product_react_list/', UserProductReactList.as_view(), 
		name='api_user_product_react_list'),

	path('user/<ac_id>/favorite_space_list/', UserFavoriteSpaceList.as_view(), 
		name='api_user_favorite_space_list'),

	path('user/<ac_id>/pinned_product_list/', UserPinnedProductList.as_view(), 
		name='api_user_pinned_prodcut_list'),

	path('user/<ac_id>/pinned_product_view/', PinnedProductsViewList.as_view(),
		name='api_pinned_product_list_view'),

	path('user/<ac_id>/thumbnail/', user_thumbnail_update, name='user-thumbnail-name'),

	path('user/<ac_id>/notification/', NotificationAViewList.as_view(), name='user-notification'),


	path('space/banner/', SpaceBanner.as_view(), name='space-banner'),
]