from django.urls import path

from space.views import manage,product
from space.api import views




urlpatterns = [
	path('<name>/', manage.index, name='space_index'),
	path('product/api/<pk>/', views.ProductView.as_view()),
	path('create/', manage.create, name='space_create'),
	path('product/create/', product.create, name='product_create'),
	path('product/<uid>/', product.single, name='product_view'),
	path('product/react/', product.react, name='product_react'),
	path('product/list/', views.ProductListView.as_view())
]