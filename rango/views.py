from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views import View
from django.utils.decorators import method_decorator

from datetime import datetime

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserProfileForm
from rango.bing_search import run_query

class CookieHandler:
    def get_server_side_cookie(self, request, cookie, default_val: None):
        val = request.session.get(cookie)
        if not val:
            val = default_val
        return val
    def visitor_cookie_handler(self, request):
        visits = int(self.get_server_side_cookie(request, 'visits', '1')) # Default value is 1.

        last_visit_cookie = self.get_server_side_cookie(request, 'last_visit', str(datetime.now()))
        last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

        # If it's been more than a day since the last visit
        if (datetime.now() - last_visit_time).days > 0:
            visits += 1
            request.session['last_visit'] = str(datetime.now())
        else:
            request.session['last_visit'] = last_visit_cookie

        request.session['visits'] = visits

class IndexView(View):
    def get(self, request):
        category_list = Category.objects.order_by('-likes')[:5]
        page_list = Page.objects.order_by('-views')[:5]

        context_dict = {}
        context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
        context_dict['categories'] = category_list
        context_dict['pages'] = page_list

        response = render(request, 'rango/index.html', context=context_dict)    
        return response

class AboutView(View):
    def get(self, request):
        context_dict = {}
        CookieHandler().visitor_cookie_handler(request)
        context_dict['visits'] = request.session['visits']
        return render(request, 'rango/about.html', context_dict)

class SearchView(View):
    def get(self, request):
        return render(request, 'rango/search.html')
    
    def post(self, request):
        result_list = []
        query = request.POST['query'].strip()
        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)
        
        return render(request, 'rango/search.html', {'result_list': result_list})

class ShowCategoryView(View):
    def get(self, request, category_name_slug):
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
    def post(self, request, category_name_slug):
        context_dict = {}
        try:
            category = Category.objects.get(slug=category_name_slug)
            pages = Page.objects.filter(category=category)
            context_dict['pages'] = pages
            context_dict['category'] = category
        except Category.DoesNotExist:
            context_dict['category'] = None
            context_dict['pages'] = None

        query = request.POST['query'].strip()
        context_dict['result_list'] = Page.objects.filter(category=category, title__contains=query)
        return render(request, 'rango/category.html', context=context_dict)

class AddCategoryView(View):
    @method_decorator(login_required)
    def get(self, request):
        form = CategoryForm()
        return render(request, 'rango/add_category.html', {'form': form})
    
    @method_decorator(login_required)
    def post(self, request):
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
        else:
            print(form.errors)
        return render(request, 'rango/add_category', {'form': form})

class AddPageView(View):
    def get(self, request, category_name_slug):
        if not request.user.is_authenticated:
            return redirect(reverse('rango:login'))
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None

        if category is None:
            return redirect('/rango/')
        
        form = PageForm()
        context_dict = {'form': form, 'category': category}
        return render(request, 'rango/add_page.html', context=context_dict)

    def post(self, request, category_name_slug):
        if not request.user.is_authenticated:
            return redirect(reverse('rango:login'))
        try:
            category = Category.objects.get(slug=category_name_slug)
        except Category.DoesNotExist:
            category = None

        if category is None:
            return redirect('/rango/')
        
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

class RestrictedView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('rango:login'))
        return render(request, 'rango/restricted.html')

class GotoView(View):
    def get(self, request):
        page_id = request.GET.get('page_id', '')
        if page_id == '':
            return redirect('/rango/')
        
        page = Page.objects.get(id=page_id)
        page.views += 1
        page.save()
        
        return redirect(page.url)

class RegisterProfileView(View):
    def get(self, request):
        form = UserProfileForm()
        context_dict = {'form': form }
        return render(request, 'rango/profile_registration.html', context_dict)        
    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES)
        
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
            
        context_dict = {'form': form}
        return render(request, 'rango/profile_registration.html', context_dict)
