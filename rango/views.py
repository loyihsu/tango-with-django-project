from django.shortcuts import render, redirect
from django.urls import reverse

from datetime import datetime

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from rango.bing_search import run_query

def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    
    visitor_cookie_handler(request)

    response = render(request, 'rango/index.html', context=context_dict)    
    return response

def about(request):
    context_dict = {'visits': request.session['visits']}
    return render(request, 'rango/about.html', context_dict)
    # return HttpResponse("<a href=\"/rango/\">Index</a>Rango says here is the about page.")

def search(request):
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)
        
    return render(request, 'rango/search.html', {'result_list': result_list})

def show_category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context=context_dict)

def add_category(request):
    if not request.user.is_authenticated:
        return redirect(reverse('rango:login'))
    
    form = CategoryForm()

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database
            form.save(commit=True)
            return redirect('/rango/')
        else:
            # The supplied form contains errors
            # Just print them to the terminal
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})

def add_page(request, category_name_slug):
    if not request.user.is_authenticated:
        return redirect(reverse('rango:login'))
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect('/rango/')
    
    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug }))
        else:
            print(form.errors)
        
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def restricted(request):
    if not request.user.is_authenticated:
        return redirect(reverse('rango:login'))
    return render(request, 'rango/restricted.html')

def get_server_side_cookie(request, cookie, default_val: None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1')) # Default value is 1.

    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    # If it's been more than a day since the last visit
    if (datetime.now() - last_visit_time).days > 0:
        visits += 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits
