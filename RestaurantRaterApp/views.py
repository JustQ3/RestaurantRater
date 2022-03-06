from django.shortcuts import render
from django.http import HttpResponse
from RestaurantRaterApp.forms import UserProfileForm, UserForm
from RestaurantRaterApp.models import Restaurant, user_client
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

def home(request):
    restaurants_list = list(Restaurant.objects.all())

    restaurants_list.sort(reverse=True, key = lambda x: x.rating)

    context_dict = {"restaurants_list":restaurants_list[:10],
                    "titlemessage":"Check out the Restaurant Rater top ten!",}

    return render(request, 'RestaurantRaterApp/home.html', context=context_dict)

def show_restaurant(request, restaurant_id):
    context_dict = {}
    try:
        
        restaurant = Restaurant.objects.get(restaurant_id=restaurant_id)

        context_dict['restaurant'] = restaurant
        context_dict['reviews']=restaurant.comments
    except Restaurant.DoesNotExist:
  
        context_dict['restaurant'] = None
       
    return render(request, 'RestaurantRaterApp/restaurant.html', context=context_dict)

def explore(request, sort):
    restaurants_list = list(Restaurant.objects.all())
    sort_options = sort_by(restaurants_list, sort)

    context_dict = {"restaurants_list": restaurants_list,
                    "titlemessage": "Explore the Restaurant Rater records!",
                    "sort": sort,
                    "sort_opts":sort_options}
    return render(request, 'RestaurantRaterApp/explore.html', context=context_dict)

@login_required
def favourites(request, sort):
    this_user=request.user
    favourites = list(Restaurant.objects.all()) #TODO: list(this_user.liked_restaurants.all())
    sort_options = sort_by(favourites, sort)
    
    context_dict = {"restaurants_list": favourites,
                    "titlemessage": "View your favourite restaurants!",
                    "sort": sort,
                    "sort_opts":sort_options}
    return render(request, 'RestaurantRaterApp/favourites.html', context=context_dict)

#helper function for explore and favourites views
def sort_by(list, sort):
    if sort == "alphabetical":
        list.sort(key = lambda x: x.name)
    elif sort == "distance":
        #TODO: sort by distance from user
        pass
    elif sort == "rating":
        list.sort(reverse=True, key = lambda x: x.rating)
    return ["alphabetical", "distance", "rating"]

@login_required
def add_restaurant(request):
    form = RestaurantForm()
   
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        
        if form.is_valid():
       
            restaurant=form.save(commit=True)
            print(restaurant,restaurant.id)
            request.user.owner_status=True
           
        return redirect('/restaurantraterapp/')
    else:
      
        print(form.errors)

    return render(request, 'restaurantraterapp/add_restaurant.html', {'form': form})

@login_required
def profile(request):
    context_dict = {}

    this_user=request.user
    favorites = list(this_user.liked_restaurants.all())
    
    context_dict['restaurants_list']=favorites
    restaurants = Restaurant.objects.get(comment[username]==this_user.username)
    for restaurant in restaurants:
        for com in restaurant.comment:
            if com == this_user.username:
                comments.append(restaurant.comment[com] )
    context_dict['comments']= comments   
    
    return render(request, 'RestaurantRaterApp/profile.html', context=context_dict)

def signup(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            prof = profile_form.save(commit=False)
            prof.user = user
            if 'picture' in request.FILES:
                prof.picture = request.FILES['picture']
            prof.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    context_dict = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered}
    return render(request, 'RestaurantRaterApp/signup.html', context_dict)

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('RestaurantRaterApp:home'))
            else:
                return HttpResponse("Your RestaurantRaterApp account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'RestaurantRaterApp/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('RestaurantRaterApp:home'))