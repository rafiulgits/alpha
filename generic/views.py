from django.shortcuts import HttpResponse,render
from django.template import loader


def response(request, template_name, context={}):
	html = loader.get_template(template_name)
	return HttpResponse(html.render(context, request))


def invalid_request(request, context={}):
	return render(request, 'generic/invalid_request.html', context)