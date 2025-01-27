import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RestaurantRater.settings')
current_dir = os.getcwd()

import django
from django.core.files import File

django.setup()

from django.contrib.auth.models import User
from RestaurantRaterApp.models import user_client, Restaurant


# Clears media folder to prevent memory issues
def clear():
    media_dir = f"{current_dir}/media"
    try:
        for folder in os.listdir(media_dir):
            for file in os.listdir(f"{media_dir}/{folder}"):
                os.remove(f"{media_dir}/{folder}/{file}")
            os.rmdir(f"{media_dir}/{folder}")
    except NotADirectoryError:
        pass


print("Media Folder Cleared")


def add_restaurant(name: str, street_number: int, street: str, city: str, description: str, restaurant_id: str,
                   comments: dict):
    r = Restaurant.objects.get_or_create(name=name, restaurant_id=restaurant_id, street_number=street_number,
                                         street=street,
                                         city=city, description=description, comments=comments)[0]
    # Adds images from lib to restaurant
    images = os.listdir(os.path.join(current_dir, "PopulateData", "images", restaurant_id))
    r.img1.save(os.path.join(name, "img1.jpg"),
                File(open(os.path.join(current_dir, "PopulateData", "images", restaurant_id, images[0]), "rb")))
    r.img2.save(os.path.join(name, "img2.jpg"),
                File(open(os.path.join(current_dir, "PopulateData", "images", restaurant_id, images[1]), "rb")))
    r.img3.save(os.path.join(name, "img3.jpg"),
                File(open(os.path.join(current_dir, "PopulateData", "images", restaurant_id, images[2]), "rb")))
    r.save()
    return r


def add_user(username: str, street_number: int, street: str, city: str, liked_restaurants: list,
             rated_restaurants: dict, password: str, email: str, name: str,
             surname: str, owner_status=False, owned_restaurants=[]):
    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()

    u = \
        user_client.objects.get_or_create(user=user, name=name, surname=surname, street_number=street_number,
                                          street=street,
                                          city=city,
                                          rated_restaurants=rated_restaurants, owner_status=owner_status)[0]
    u.save()

    u.update_distances_dict()

    # Adds ratings
    for restaurant in rated_restaurants.keys():
        rates(u.name, restaurant)

    # Adds liked restaurants
    for restaurant in liked_restaurants:
        likes(u.name, restaurant)

    # Adds Owner's Restaurants
    if owner_status:
        for restaurant in owned_restaurants:
            owns(u.name, restaurant)

    return u


def rates(user: str, restaurant: str):
    # Creates link between user and restaurant
    user_obj = user_client.objects.get(name=user)
    restaurant_obj = Restaurant.objects.get(restaurant_id=restaurant)
    user_obj.rates.add(restaurant_obj)
    # Appends rating to ratings list which overall rating calculated from
    restaurant_obj.ratings.append(user_obj.rated_restaurants[restaurant_obj.restaurant_id])
    if user_obj.user.username not in restaurant_obj.comments.keys() and restaurant_obj.restaurant_id in user_obj.rated_restaurants.keys():
        restaurant_obj.comments[user_obj.user.username] = ""

    restaurant_obj.save()


def owns(user: str, restaurant: str):
    # Creates link between user and restaurant
    user_obj = user_client.objects.get(name=user)
    restaurant_obj = Restaurant.objects.get(restaurant_id=restaurant)
    user_obj.owned_restaurants.add(restaurant_obj)


def likes(user: str, restaurant: str):
    # Creates link between user and restaurant
    user_obj = user_client.objects.get(name=user)
    restaurant_obj = Restaurant.objects.get(restaurant_id=restaurant)
    user_obj.liked_restaurants.add(restaurant_obj)


def populate():
    # Restaurant data, list of dictionaries
    restaurant_data = [
        # Alchemilla - 1
        {"name": "Alchemilla",
         "street_number": 1126,
         "street": "Argyle Street",
         "city": "Glasgow",
         "description": "Seasonal Mediterranean plates and natural wine.",
         "id": "alchemilla",
         "comments": {
             "Mark.E": """The restaurant is a cute little intimate location in the interesting area of 
             finnieston. The lighting, ambiance and staff were great and serve the restaurant 
             well. """,
             "Matt.W": """Out-of-the-ordinary small plates. Tasty food and friendly service in a hip 
            setting. Plenty of dishes to choose from. A couple of items on the menu may seem shocking at 
            first. You will be rewarded for being adventurous. """,
             "Danny.M": """Service is wonderful, and the ingredients were fresh and nicely presented, and there is a 
             lot of attention going into the dishes, but it's just not my cup of tea as I found the flavours really 
             bland. Portions are also small, so keep that in mind. I wouldn't come back for the food, but it's worth 
             checking out for yourself """

         }
         },
        # Julie's Kopitiam - 2
        {"name": "Julie's Kopitiam",
         "street_number": 556,
         "street": "Dumbarton Road",
         "city": "Glasgow",
         "description": "Comfort food done right",
         "id": "julies-kopitiam",
         "comments": {
             "Thom.O": """I've enjoyed eating here in the past but £40 for rice, an egg, a chicken leg,
            some cucumber and 3 chickpea fritters is excessive. There is just no attempt to compete at all with the
            great curry houses et al of Glasgow.""",
             "Andy.P": """Fantastic, food was authentic in flavour. The small restaurant has a great vibe
            and the staff were friendly. Good prices. What a gem of a place.""",
             "Danny.M": """Have had some good meals from here but also some pretty disappointing ones. Takeaway this
            evening was overpriced, small in proportion and a let-down across the board. You would hope for more
            consistency. """
         }
         },
        # Kimchi Cult - 3
        {"name": "Kimchi Cult",
         "street_number": 14,
         "street": "Chancellor St",
         "city": "Glasgow",
         "description": "Korean-style fast food in Glasgow’s West End.",
         "id": "kimchi-cult",
         "comments": {"Nicola.H": """My wife and I tried this tonight after hearing good things and got the Korean 
         Chicken burger, bibimbap and tofu. The food was generally tasty their crispy chicken and sauce was good!""",
                      "Michael.G": """Working in Glasgow, went 3 times in a week. What more can I say. Outstanding""",
                      "Andy.P": """Portion sizes are much smaller now - it is a depressing story for many such 
                        places. Two months ago, their portions were generous and now they are absolutely the 
                        opposite- I won’t be back """
                      }
         },
        # Ox and Finch - 4
        {"name": "Ox and Finch",
         "street_number": 920,
         "street": "Sauchiehall Street",
         "city": "Glasgow",
         "description": "The small plates trend is done very well at this slick Sauchiehall Street restaurant.",
         "id": "ox-and-finch",
         "comments": {"Michael.G": """The food served at Ox and Finch, Glasgow is immensely delicious, of the right 
         portion and reasonably priced. You must not give amiss to this place. The service is just superb and there 
         is a variety of meat, vegetables to choose from. You will surely enjoy your meal as I did.""",
                      "Andy.P": """I just love this place and visit on every occasion I'm in Glasgow. The food and 
                      wines are 1st class foods done extremely well. I've been going here for 6+years and I have 
                      never once felt disappointed. Staff and venue are great,will help you with any diet query,
                      same goes for the wines for matching foods."""}
         },
        # Bilson Eleven - 5
        {"name": "Bilson Eleven",
         "street_number": 10,
         "street": "Annfield Place",
         "city": "Glasgow",
         "description": "A five- or even eight-course fine-dining odyssey.",
         "id": "bilson-eleven",
         "comments": {"Thom.O": """What an unbelievable night that was last night at this restaurant. The food, 
         the service and the wine was absolutely sublime. Just an absolutely unbelievable experience and I certainly 
         would recommend this place to anyone who loves their wine and their fine dining experiences.""",

                      "Michael.G": """Our favourite restaurant in Glasgow . Thank you Nick for a absolute creative 
                      menu visually , sensory & fabulously tasting. Mark,  your front of house was all that we come 
                      to expect, informative, interesting and totally  engrossed in your knowledge of the wines & the 
                      menu, thanks gents"""}
         },
        # Cail Bruich - 6
        {"name": "Cail Bruich",
         "street_number": 725,
         "street": "great Western",
         "city": "Glasgow",
         "description": "Très bon Franco-Scottish cooking.",
         "id": "cail-bruich",
         "comments": {"Jeremy.S": """This was our first visit to Cail Bruich. Food and service was excellent, 
         what you'd expect from a Michelin star restaurant. Staff are very knowledgeable about the dishes they serve. 
         We had the chefs tasting menu and was great. Very disappointed by the manner in which a dessert was served, 
         far from Michelin standard or any acceptable standard. This was dealt with at the time with a manager.""",

                      "Matt.W": """Came here for my birthday. I had the tasting menu with wines to match. The wines 
                      did not pair well with the food at all and were particularly expensive and very small measures 
                      (£72 for four very small glasses). You could drive home from this meal without being over the 
                      limit. I've eaten in some wonderful Michelin Starred restaurants and some great AA Rosette 
                      places. This is neither. The restaurant was cold when I visited and the champagne was the worst 
                      I have ever had anywhere. I don't often leave bad reviews but this was a meal for two that cost 
                      close to £500 and wasn't worth it at all. I've spent more in other places but always felt that 
                      I got value for money. I wouldn't go back again."""}
         },
        # Hanoi Bike Shop -7
        {"name": "The Hanoi Bike Shop",
         "street_number": 8,
         "street": "Ruthven Ln",
         "city": "Glasgow",
         "description": "A fresh, casual, canteen-style Vietnamese restaurant.",
         "id": "the-hanoi-bike-shop",
         "comments": {"Matt.W": """We arrived at the Hanoi Bike Shop with much anticipation, joined by our Vietnamese 
         friend. The decor is superb, beautifully decorated. Ordered the spring rolls - delish, followed by a beef 
         pho, average, and my wife got the red duck curry - excellent. I asked for a Vietnamese iced coffee with 
         condensed milk and got a classic iced coffee - disappointed. Our food arrived quickly and the service was 
         good.""",
                      "Mark.E": """Nice cosy interior with an upstairs seating. The shop is easy to find thanks to 
                      the bright signs. The decor of the shop is very nicely done. However the food is quite 
                      disappointing, from an Asian’s point of view. The pho was very disappointing, the portion was 
                      big and all but the taste and correct pho noodles was not satisfactory. They have a lot of side 
                      dishes to eat with their drinks, maybe it’s better for it’s drinks instead of a dinner."""}
         },
        # The Gannet - 8
        {"name": "The Gannet",
         "street_number": 1155,
         "street": "Argyle Street",
         "city": "Glasgow",
         "description": "A slice of Brooklyn-esque cool on the Finnieston ‘strip’.",
         "id": "the-gannet",
         "comments": {"Mark.E": """Friendly service. A menu that reads better than it delivers for some courses. 
         Disappointing lack of stornoway black pudding on what was a well cooked duck scotch egg. The fillet of beef 
         was tough and served with 2 small rectangles of mushroom and a trickle of well cooked sauce...it could have 
         been a great dish. The salted caramel fondant however was amazing.  I'd expect better from a 3 AA rosette 
         restaurant to be honest.""",

                      "Jeff.D": """So I was little torn about this review. The service was very good, the ambience 
                      was lovely, the drinks selection was excellent and the food was good. The problem lies in the 
                      pricing, when you are charging £24 a main the food needs to be better than good; it needs to be 
                      excellent. They hit the mark with both the starters and the deserts, but the found the mains a 
                      little lacking. All in all if you are going to treat yourself there are better options than the 
                      Gannet.""",

                      "Andy.P": """Main served 50 minutes after starter and luke warm on a roasting plate (how can 
                      that be you ask? Cause they replated it I assume).  Dessert took another 45 mins and they didnt 
                      bring our coffee as requested. Then they put the balance of our gift voucher onto a new voucher 
                      but made the valid until date today! It's probably a superb restaurant, but we had a very poor 
                      version of it."""}
         },
        # The Finnieston - 9
        {"name": "The Finnieston",
         "street_number": 1125,
         "street": "Argyle Street",
         "city": "Glasgow",
         "description": "Proudly sourced Scottish seafood and gins at a suitably rustic Argyle Street location.",
         "id": "the-finnieston",
         "comments": {"Matt.W": """Expensive for what you get. Carafe of house wine, half litre at £14 is cheaky. 
         Pleasant enough atmosphere but really stuffy responses when it came to trying to get food. Only permitted 
         food at designated tables. No snacks or small plates served anywhere else. Doesn't make sense.""",

                      "Jeff.D": """This was the first place I visited when I moved to Glasgow a year ago. It is our 
                      favourite place to catch up with friends since then. The food is really good and I'm really 
                      missing their bay leaf elderflower gin on these cold October nights. Can't wait for them to 
                      reopen so we can visit again. If someone ever asks me to recommend a good gastropub  in Glasgow 
                      this is the place to go.""",

                      "Andy.P": """The worst bar I've ever been to. The rudest staff who cannot even pour a pint. I 
                      never complain but it was so bad that I decided to tell the manager who was even ruder and 
                      totally unprofessional. Really awful pretentious place. Just wish I could give zero stars!"""}
         },
        # Stravaigin - 10
        {"name": "Stravaigin",
         "street_number": 28,
         "street": "Gibson Street",
         "city": "Glasgow",
         "description": "Pub grub staples done very well at a hip West End restaurant.",
         "id": "stravaigin",
         "comments": {"Michael.G": """Great staff, very attentive and polite waitress but the food omg. Thai curry 
         was full of fish sauce, veggie haggis tasted sour ( as it was off ). Not happy, would not recommend and will 
         not be back.""",

                      "Rose.S": """£25 for 2 breakfasts and 2 small coffees, feel a bit ripped off as there was only 
                      1 bacon rasher, 1 egg, potato scone, square sausage, link sausage, black pudding, mushrooms and 
                      very small portion of beans, wasn't keen on the sausage and the egg had that horrible 
                      undercooked white stuff on it. Fast service and nice pub.""",

                      "Danny.M": """Good God in heaven. I didn't think it was possible to describe haggis as juicy, 
                      but Stravaigin have done something magical. It was like an umami punch in the tongue and mama 
                      liked it. Best plate of haggis I've ever had in my life. I literally made myself keep eating 
                      past the point that I was full. Nice staff and cool atmosphere as well, but honestly if they 
                      served this haggis behind a dumpster I would come back."""}
         },
        # The Patric Duck Club - 11
        {"name": "Patrick Duck Club",
         "street_number": 27,
         "street": "Hyndland Street",
         "city": "Glasgow",
         "description": "A quirky diner proving you can cook duck in A LOT of different ways.",
         "id": "patrick-duck-club",
         "comments": {"Thom.O": """First time visit, booking in advance particularly at weekends is advised. The food 
         and service were excellent. I had a starter, main and dessert (shown in pics) and all courses were delicious.
         Highly recommended!""",
                      "Colin": """Burger was tasteless unfortunately, Ndjua sauce tasted like cold tinned tomatoes 
                      with no seasoning... Not a good plate of food, real shame as I wanted to like this place, 
                      lovely setting and staff friendly, food just not up to scratch at all."""}
         },
        # Number 16 - 12
        {"name": "Number 16",
         "street_number": 16,
         "street": "Byres Road",
         "city": "Glasgow",
         "description": "A Euro-bistro in a Byres Road bolthole.",
         "id": "number-16",
         "comments": {"Rose.S": """Absolutely sensational. Fantastic food, really creative, delicious and not dainty 
         for the quality. Service was excellent too.""",
                      "Jeremy.S": """The food was presented nicely and the restaurant was cosy hence the star but was 
                      very let down by the flavours which were so bland they resembled hospital food. I booked the table
                       for my boyfriends birthday after seeing all the positive reviews. We were both dissapointed and 
                       the waitress didn't bother asking us how we found the food."""}
         },
        # Spanish Butcher - 13
        {"name": "Spanish Butcher",
         "street_number": 1055,
         "street": "Sauchiehall Street",
         "city": "Glasgow",
         "description": "Premium Spanish meat served in New York loft-style interiors.",
         "id": "spanish-butcher",
         "comments": {"Mark.E": """It does steaks and it does steaks very well indeed. Staff are very friendly and 
         helpful, and take great care in explaining the complexities of ordering your steak. Lighting is subdued, 
         the atmosphere is relaxed. It is not cheap but you're getting prime cuts of beef your money.""",
                      "Jeremy.S": """Absolutely brilliant restaurant, one of my favourites in Glasgow! Great 
                      cocktails, the steaks are fantastic, but the pork cheek is next level""",
                      "Colin": """Beautiful interior, service outstanding. Let down by food. Ordered burgers. Less 
                      than average, very dry, a teaspoon of relish, chips were like frozen skinny fries. Would I eat 
                      here again? Definitely not."""}
         },
        # Beat 6 - 14
        {"name": "Beat 6",
         "street_number": 10,
         "street": "Whitehall Street",
         "city": "Glasgow",
         "description": """A new venture from the team behind Six by Nico, which donates 100% of its profits to the
                        Beatson Cancer Charity.""",
         "id": "beat-6",
         "comments": {"Jeff.D": """Had the vegetarian tasting menu and it was so good. Super friendly staff in a 
         place with a lovely atmosphere.  Will definitely go back""",

                      "Colin": """Food was delicious and plated well. The only dish I wasn't a fan of was the beef 
                      tartare - not the fault of the staff. They apologised and offered me the veggie option which 
                      was kind. Wine pairing is highly recommended.""",
                      "Matt.W": """Great experience, fantastic staff and lovely atmosphere. The food was just as 
                      tasty as when we've tried it at Six by Nico before. Highly recommended.""",

                      "Danny.M": """Every plate was a delight. The Tartare was brilliant. Star of the show for me was 
                      the Fregola Sarda. Amazing value for such great food. Lovely staff who pace things just right. 
                      A great experience"""}
         },
        # Glorisa -15
        {"name": "Glorisa",
         "street_number": 1321,
         "street": "Argyle Street",
         "city": "Glasgow",
         "description": "For fresh Mediterranean flavours from the chef who brought us Alchemilla.",
         "id": "glorisa",
         "comments": {"Thom.O": """Small plates sharing menu. Short list of options, all done very well with 
         interesting interpretations of some of my favourite tapas dishes. Menu changes frequently, which means I'm 
         highly likely to return several times!""",
                      "Rose.S": """Just simply one of the best meals we've had in Glasgow for some time. Standout 
                      dish was the pork chop...service was spot on too. Man we are really spoilt for choice in the 
                      west end now for 10/10 places.""",
                      "Jeremy.S": """The venue and staff are nice but the food simply wasn't for me. Not my style and 
                      for me it wasn't tasty."""}
         },
        # Crabshakk - 16
        {"name": "Crabshakk",
         "street_number": 1114,
         "street": "Argyle Street",
         "city": "Glasgow",
         "description": "One of the city’s best seafood restaurants with a daily specials board that’s always worth a gander.",
         "id": "crabshakk",
         "comments": {"Andy.P": """Excellent seafood restaurant, it’s a go to for seafood lovers. We had scallops in 
         brown butter, cockles with samphire then halibut as a main course and few oysters as a “treat” (just 
         because) Everything was cooked perfectly. I do recommend book a table as it is quite busy. By the time we 
         were there I saw 2 deliveries of fish and sea food, so always fresh, good quality!""",
                      "Michael.G": """Food was absolutely amazing, lovely and fresh. The staff were very attentive 
                      and friendly. A little tight for space at the bar seats but then again we didn't reserve a 
                      table. Overall a great experience.""",
                      "Jeremy.S": """Truly exceptional meal, fantastic food and service, the scallops are probably 
                      the best we've ever had. Will definitely go back. Highly recommended.""",
                      "Nicola.H": """I had the halibut and my husband had langoustine. Just delicious.  Can't praise 
                      this place enough. Brilliant food and staff were so friendly and attentive. Had chocolate cake 
                      for dessert. More like a mousse with banana ice cream. Yum. """,
                      "Danny.M": """Not just incredibly tasty & fresh food, the service was impeccable. We were 
                      served by such a happy waitress who was very knowledgeable about the menu which really added to 
                      our experience at crabshakk. Not the first time, and won’t be the last. """
                      }
         },
        # Stereo - 17
        {"name": "Stereo",
         "street_number": 22,
         "street": "Renfield Lane",
         "city": "Glasgow",
         "description": "Bar and gig venue with gig posters for wallpaper, a vegan menu and a leftfield events calendar.",
         "id": "stereo",
         "comments": {"Matt.W": """Quite possibly the worst bar staff in Glasgow.  We visited Stereo last night with 
         a few friends.  We had a great night upstairs and then made the mistake of going downstairs. We ordered two 
         drinks and then realised we couldn't pay with our card.  We had no cash so I went to the cash machine.  
         While away my wife stayed at the bar.  On my return the bar man only gave us one of the drinks I had 
         ordered.  When I asked for the other he said they had already given it to us.  They hadn't and it was 
         nowhere to be seen.  I fail to see why they would have given us one drink we hadn't paid for.  After a long 
         argument and the intervention on the other bar man who was similarly clueless we had to pay for the drink 
         they hadn't served us in order to get served and avoid getting kicked out.  Awful customer service from two 
         complete idiots.""",
                      "Thom.O": """We used to enjoy Stereo until we made the mistake of visiting last night.  The 
                      staff downstairs were the worst we have ever experienced in Glasgow.  Rude, clueless idiots.""",
                      "Rose.S": """Poor service and over priced, if you like eating sawdust sitting on school 
                      furniture... You might like it.... And don't start me on the staff. One star is too much .. but 
                      it won't let me give less""",
                      "Nicola.H": """They kicked me out for being "too pinging" I would say that's debatable. Great 
                      night ruined by snide grasses. Bar staff friendly""",
                      }
         },

        # Gaga - 18
        {"name": "Gaga",
         "street_number": 566,
         "street": "Dumbarton Road",
         "city": "Glasgow",
         "description": "South East Asian dishes, delicious cocktails and plenty of soul.",
         "id": "gaga",
         "comments": {"Michael.G": """Tasty food, very friendly and accommodating staff. Will be back in future. Also 
         dog friendly!""",
                      "Jeff.D": """Were in the area, needed somewhere to eat Found this place. Very good. Food was 
                      tasty, staff nice. When in area again we will stop there again for lunch. It was fairly busy, 
                      trendy wee place in Partick""",
                      "Colin": """Absolutely brilliant meal here at GaGa! Service, decor, atmosphere all on point and 
                      great for the area to have this alongside the Thornwood and other places. Will definitely be 
                      back!""",
                      "Danny.M": """What can I say, from the minute I walked in the the door ,Mark was so welcoming, 
                      the vibes were just perfect and the staff amazing Food 10/10, Staff 12/10 . Can't wait to bring 
                      the dogs. My new Local x""",
                      }
         },

        # Chinaskis - 19
        {"name": "Chinaskis",
         "street_number": 239,
         "street": "North Street",
         "city": "Glasgow",
         "description": "Proper sleeves-rolled-up plates and (of course) a formidable drinks selection at a US-style "
                        "dive.",
         "id": "chinaskis",
         "comments": {"Mark.E": """Best bar in Glasgow! Not cheap but plenty of ambience and decent bar food too. 
         Outdoor space has been improved with heaters and roofing now.""",
                      "Jeremy.S": """Great spot to drop by for a drink or two. Nice heated outdoor area if you cant 
                      get inside. Friendly staff and great atmosphere.""",
                      "Colin": """Great wee bar with a huge amount of outdoor space. Can recommend their own brews, 
                      they're decent. Good food too.""",
                      "Nicola.H": """Amazing pub with fantastic food, on par with many high end restaurants in my 
                      opinion. Large outdoor area perfect for summer and a cosy candle lit  interior for winter. Only 
                      downside is a small selection of cider :(""",
                      }
         },
        # The Hug and Pint - 20
        {"name": "The Hug and Pint",
         "street_number": 171,
         "street": "Great Western Road",
         "city": "Glasgow",
         "description": "Creative contemporary vegan dining to wolf down before a gig.",
         "id": "the-hug-and-pint",
         "comments": {"Mark.E": """Zero enforcement of mask wearing at the venue. I have not felt so unsafe since 
         covid first came to the country. Not even a verbal reminder coming in that masks are mandatory and crammed 
         full to the point of shoving. Gig was good, won’t be back.""",
                      "Andy.P": """This place is pitiful. The drinks are way overpriced, considering what the place 
                      offers. The gig venue is tiny, like the size of two bedrooms. Totally cramped and sounds awful. 
                      I don't even know if it's legal, the venue seems like a fire hazard. I've pretty much 
                      blacklisted this place. I'll never go back.""",
                      }
         },

    ]
    # User data, list of dictionaries
    user_data = [
        # Mark Edwards
        {"username": "Mark.E",
         "street_number": 21,
         "street": "Beith Street",
         "city": "Glasgow",
         "liked_restaurants": ["alchemilla", "spanish-butcher", "beat-6"],
         "rated_restaurants": {"alchemilla": 4, "julies-kopitiam": 2, "stravaigin": 3, "patrick-duck-club": 2,
                               "number-16": 1, "spanish-butcher": 4, "beat-6": 5, "glorisa": 3, "cail-bruich": 1,
                               "the-finnieston": 2, "the-gannet": 3, "the-hanoi-bike-shop": 1, "chinaskis": 5,
                               "the-hug-and-pint": 1},
         "password": "Mark123",
         "email": "mark@gmail.com",
         "name": "Mark",
         "surname": "Edwards",
         "owner_status": False,
         "owned_restaurants": []
         },
        # Matthew Wainwright
        {"username": "Matt.W",
         "street_number": 164,
         "street": "Buchanan St",
         "city": "Glasgow",
         "liked_restaurants": ["alchemilla", "julies-kopitiam", "the-hanoi-bike-shop"],
         "rated_restaurants": {"alchemilla": 5, "julies-kopitiam": 5, "kimchi-cult": 3, "ox-and-finch": 1,
                               "spanish-butcher": 2, "beat-6": 5, "glorisa": 1, "cail-bruich": 2, "the-finnieston": 2,
                               "the-gannet": 3, "the-hanoi-bike-shop": 4, "stereo": 1},
         "password": "Matt123",
         "email": "matt@gmail.com",
         "name": "Matthew",
         "surname": "Wainwright",
         "owner_status": False,
         "owned_restaurants": []
         },
        # Thomas Oldman
        {"username": "Thom.O",
         "street_number": 161,
         "street": "Duke St",
         "city": "Glasgow",
         "liked_restaurants": ["alchemilla", "patrick-duck-club", "beat-6", "glorisa"],
         "rated_restaurants": {"alchemilla": 4, "julies-kopitiam": 3, "bilson-eleven": 5, "stravaigin": 3,
                               "patrick-duck-club": 4, "number-16": 2, "spanish-butcher": 1, "beat-6": 4, "glorisa": 5,
                               "the-gannet": 2, "the-hanoi-bike-shop": 3, "stereo": 2},
         "password": "Thom123",
         "email": "thom@gmail.com",
         "name": "Thomas",
         "surname": "Oldman",
         "owner_status": False,
         "owned_restaurants": []
         },
        # Michael Gunning
        {"username": "Michael.G",
         "street_number": 477,
         "street": "Duke St",
         "city": "Glasgow",
         "liked_restaurants": ["alchemilla"],
         "rated_restaurants": {"alchemilla": 4, "julies-kopitiam": 2, "kimchi-cult": 4, "ox-and-finch": 5,
                               "bilson-eleven": 4, "stravaigin": 2, "patrick-duck-club": 3, "crabshakk": 4, "gaga": 5},
         "password": "Matt123",
         "email": "matt@gmail.com",
         "name": "Michael",
         "surname": "Gunning",
         "owner_status": False,
         "owned_restaurants": []
         },
        # Andy Peterson
        {"username": "Andy.P",
         "street_number": 394,
         "street": "Great Western Rd",
         "city": "Glasgow",
         "liked_restaurants": ["the-finnieston"],
         "rated_restaurants": {"kimchi-cult": 3, "ox-and-finch": 5, "bilson-eleven": 4, "stravaigin": 2,
                               "patrick-duck-club": 4, "cail-bruich": 3, "the-finnieston": 2, "the-gannet": 1,
                               "the-hanoi-bike-shop": 2,
                               "crabshakk": 4, "the-hug-and-pint": 1},
         "password": "Andy123",
         "email": "andy@gmail.com",
         "name": "Andy",
         "surname": "Peterson",
         "owner_status": False,
         "owned_restaurants": []
         },
        # Rose Street
        {"username": "Rose.S",
         "street_number": 8,
         "street": "Cresswell Ln",
         "city": "Glasgow",
         "liked_restaurants": ["alchemilla", "number-16", "beat-6", "the-finnieston"],
         "rated_restaurants": {"alchemilla": 4, "julies-kopitiam": 4, "stravaigin": 3, "patrick-duck-club": 2,
                               "number-16": 4, "spanish-butcher": 3, "beat-6": 4, "glorisa": 2, "the-finnieston": 4,
                               "the-gannet": 3, "the-hanoi-bike-shop": 2, "stereo": 1},
         "password": "Rose123",
         "email": "rose@gmail.com",
         "name": "Rose",
         "surname": "Street",
         "owner_status": False,
         "owned_restaurants": []
         },
        # Jeremy Stevenson
        {"username": "Jeremy.S",
         "street_number": 1620,
         "street": "Great Western Rd",
         "city": "Glasgow",
         "liked_restaurants": ["spanish-butcher"],
         "rated_restaurants": {"stravaigin": 2, "patrick-duck-club": 4, "number-16": 2, "spanish-butcher": 5,
                               "beat-6": 5, "glorisa": 1, "cail-bruich": 4, "the-finnieston": 3,
                               "the-hanoi-bike-shop": 2,
                               "crabshakk": 5, "chinaskis": 5, "the-hug-and-pint": 1},
         "password": "Jem123",
         "email": "jeremy@gmail.com",
         "name": "Jeremy",
         "surname": "Stevenson",
         "owner_status": False,
         "owned_restaurants": []
         },
        # Jeff Dalton
        {"username": "Jeff.D",
         "street_number": 108,
         "street": "Queen Margaret Dr",
         "city": "Glasgow",
         "liked_restaurants": ["alchemilla", "julies-kopitiam", "beat-6", "glorisa", "the-finnieston"],
         "rated_restaurants": {"alchemilla": 5, "julies-kopitiam": 4, "kimchi-cult": 3, "ox-and-finch": 1,
                               "stravaigin": 3, "patrick-duck-club": 2, "beat-6": 5, "glorisa": 4, "cail-bruich": 3,
                               "the-finnieston": 4, "the-gannet": 3, "the-hanoi-bike-shop": 3, "gaga": 4},
         "password": "Jeff123",
         "email": "jeff@gmail.com",
         "name": "Jeff",
         "surname": "Dalton",
         "owner_status": False,
         "owned_restaurants": []
         },
        # Colin McNair - Owner
        {"username": "Colin",
         "street_number": 1,
         "street": "Cathcart Rd",
         "city": "Glasgow",
         "liked_restaurants": ["patrick-duck-club", "glorisa"],
         "rated_restaurants": {"patrick-duck-club": 3, "number-16": 3, "spanish-butcher": 3, "beat-6": 4, "glorisa": 5,
                               "gaga": 3, "chinaskis": 4, "the-hug-and-pint": 1},
         "password": "Colin123",
         "email": "colin@gmail.com",
         "name": "Colin",
         "surname": "McNair",
         "owner_status": True,
         "owned_restaurants": ["alchemilla", "julies-kopitiam", "kimchi-cult", "ox-and-finch", "bilson-eleven",
                               "crabshakk"]
         },
        # Nicola Hamill - Owner
        {"username": "Nicola.H",
         "street_number": 530,
         "street": "Victoria Rd",
         "city": "Glasgow",
         "liked_restaurants": ["alchemilla"],
         "rated_restaurants": {"alchemilla": 4, "julies-kopitiam": 3, "kimchi-cult": 3, "the-hanoi-bike-shop": 2,
                               "crabshakk": 5, "stereo": 2, "chinaskis": 4},
         "password": "Nicola123",
         "email": "nichola@gmail.com",
         "name": "Nicola",
         "surname": "Hamill",
         "owner_status": True,
         "owned_restaurants": ["stravaigin", "patrick-duck-club", "number-16", "spanish-butcher", "beat-6", "gaga",
                               "the-hug-and-pint"]
         },
        # Danny Macpherson - Owner
        {"username": "Danny.M",
         "street_number": 316,
         "street": "Calder St",
         "city": "Glasgow",
         "liked_restaurants": ["stravaigin", "spanish-butcher", "glorisa"],
         "rated_restaurants": {"stravaigin": 4, "patrick-duck-club": 3, "number-16": 3, "beat-6": 5, "glorisa": 5,
                               "crabshakk": 4, "gaga": 2},
         "password": "Danny123",
         "email": "danny@gmail.com",
         "name": "Danny",
         "surname": "Macpherson",
         "owner_status": True,
         "owned_restaurants": ["glorisa", "cail-bruich", "the-finnieston", "the-gannet", "the-hanoi-bike-shop",
                               "stereo", "chinaskis", "spanish-butcher"]

         }]

    for restaurant in restaurant_data:
        add_restaurant(restaurant["name"], restaurant["street_number"], restaurant["street"], restaurant["city"],
                       restaurant["description"], restaurant["id"], restaurant["comments"])
        r = Restaurant.objects.get(name=restaurant["name"])
        print(f"Created restaurant {r}")

    for user in user_data:
        add_user(user["username"], user["street_number"], user["street"], user["city"], user["liked_restaurants"],
                 user["rated_restaurants"],
                 user["password"], user["email"], user["name"], user["surname"], user["owner_status"],
                 user["owned_restaurants"])
        u = user_client.objects.get(name=user["name"])
        print(f"Created user {u}")
        if u.owner_status:
            print(f"User owns: {u.owned_restaurants_list}")


def populate_test():
    mark = {"username": "Mark.E",
            "street_number": 21,
            "street": "Beith Street",
            "city": "Glasgow",
            "liked_restaurants": ["alchemilla"],
            "rated_restaurants": {"alchemilla": 4, "kimchi-cult": 5},
            "password": "Mark123",
            "email": "mark@gmail.com",
            "name": "Mark",
            "surname": "Edwards",
            "owner_status": False,
            "owned_restaurants": []
            }
    nichola = {"username": "Nicola.H",
               "street_number": 530,
               "street": "Victoria Rd",
               "city": "Glasgow",
               "liked_restaurants": ["alchemilla", "kimchi-cult"],
               "rated_restaurants": {"alchemilla": 4, "kimchi-cult": 5},
               "password": "Nicola123",
               "email": "nichola@gmail.com",
               "name": "Nicola",
               "surname": "Hamill",
               "owner_status": True,
               "owned_restaurants": ["alchemilla"]
               }
    colin = {"username": "Colin",
             "street_number": 1,
             "street": "Cathcard Rd",
             "city": "Glasgow",
             "liked_restaurants": ["kimchi-cult"],
             "rated_restaurants": {"kimchi-cult": 5},
             "password": "Colin123",
             "email": "colin@gmail.com",
             "name": "Colin",
             "surname": "McNair",
             "owner_status": False,
             "owned_restaurants": []
             }

    restaurant_data_alc = {"name": "Alchemilla",
                           "street_number": 1126,
                           "street": "Argyle Street",
                           "city": "Glasgow",
                           "description": "Seasonal Mediterranean plates and natural wine.",
                           "id": "alchemilla",
                           "comments": {
                               "Mark.E": """The restaurant is a cute little intimate location in the interesting area of 
                 finnieston. The lighting, ambiance and staff were great and serve the restaurant 
                 well. """,
                           }
                           }
    restaurant_data_kc = {"name": "Kimchi Cult",
                          "street_number": 14,
                          "street": "Chancellor St",
                          "city": "Glasgow",
                          "description": "Korean-style fast food in Glasgow’s West End.",
                          "id": "kimchi-cult",
                          "comments": {"Nicola.H": """My wife and I tried this tonight after hearing good things and 
                          got the Korean Chicken burger, bibimbap and tofu. The food was generally tasty their crispy 
                          chicken and sauce was good!""",
                                       "Michael.G": """Working in Glasgow, went 3 times in a week. What more can I 
                                       say. Outstanding""",
                                       "Andy.P": """Portion sizes are much smaller now - it is a depressing story for 
                                       many such places. Two months ago, their portions were generous and now they 
                                       are absolutely the opposite- I won’t be back """
                                       }}
    add_restaurant(name=restaurant_data_alc["name"], street_number=restaurant_data_alc["street_number"],
                   street=restaurant_data_alc["street"], city=restaurant_data_alc["city"],
                   description=restaurant_data_alc["description"],
                   restaurant_id=restaurant_data_alc["id"], comments=restaurant_data_alc["comments"])

    add_restaurant(name=restaurant_data_kc["name"], street_number=restaurant_data_kc["street_number"],
                   street=restaurant_data_kc["street"], city=restaurant_data_kc["city"],
                   description=restaurant_data_kc["description"],
                   restaurant_id=restaurant_data_kc["id"], comments=restaurant_data_kc["comments"])

    add_user(mark["username"], mark["street_number"], mark["street"], mark["city"],
             mark["liked_restaurants"],
             mark["rated_restaurants"],
             mark["password"], mark["email"], mark["name"], mark["surname"], mark["owner_status"],
             mark["owned_restaurants"])

    add_user(nichola["username"], nichola["street_number"], nichola["street"], nichola["city"],
             nichola["liked_restaurants"], nichola["rated_restaurants"], nichola["password"], nichola["email"],
             nichola["name"], nichola["surname"],
             nichola["owner_status"],
             nichola["owned_restaurants"])

    add_user(colin["username"], colin["street_number"], colin["street"], colin["city"],
             colin["liked_restaurants"], colin["rated_restaurants"], colin["password"], colin["email"],
             colin["name"], colin["surname"],
             colin["owner_status"],
             colin["owned_restaurants"])


if __name__ == "__main__":
    print("Starting Rango population script")
    clear()
    populate()
    print("Population finished")
