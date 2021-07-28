from django.shortcuts import render
from django.http import HttpResponse

from rango.models import Category

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list

    # Return a rendered response to the client using the method from shortcuts
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    return render(request, 'rango/about.html')
    # return HttpResponse("<a href=\"/rango/\">Index</a>Rango says here is the about page.")
