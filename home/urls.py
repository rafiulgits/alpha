from django.urls import path,include

from home.views import manage, filtering, pages

urlpatterns = [
	path('', manage.manager , name='view-manager'),
	path('notification/', manage.notification, name='notification'),
	path('notification/<uid>/action/', manage.notification_route, name='notification-route'),
	
	path('trending/', filtering.trending, name='trending'),
	path('search/', filtering.search, name='search'),

	path('about/', pages.about, name='about'),
	path('terms/', pages.terms, name='terms'),
	path('feedback/', pages.feedback, name='feedback'),
	path('privacy-policy/', pages.privacy_policy, name='privacy_policy')
]