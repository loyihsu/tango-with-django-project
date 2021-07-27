from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    # Construct a dictionary to pass to the template engine as its content.
    # Key should match that of the template.
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    
    # Return a rendered response to the client using the method from shortcuts
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    return render(request, 'rango/about.html')
    # return HttpResponse("<a href=\"/rango/\">Index</a>Rango says here is the about page.")
