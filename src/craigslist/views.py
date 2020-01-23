import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from requests.compat import quote_plus

from .models import Search

BASE_CRAIGSLIST_URL = 'https://manila.craigslist.org/search/?query={}'
BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'


# Create your views here.
def home(request):
    return render(request, 'base.html')


def new_search(request):
    search = request.POST.get('search')

    Search.objects.create(search=search)

    lookup_url = BASE_CRAIGSLIST_URL.format(quote_plus(search))

    response = requests.get(lookup_url)

    data = response.text

    soup = BeautifulSoup(data, features='html.parser')

    post_listings = soup.find_all('li', {'class': 'result-row'})

    postings = []

    for post in post_listings:
        post_anchor = post.find(class_='result-title')
        post_url = post_anchor.get('href')
        post_title = post_anchor.text

        price_element = post.find(class_='result-price')
        if price_element:
            post_price = price_element.text
        else:
            post_price = 'n/a'

        data_ids = post.find(class_='result-image').get('data-ids')
        if data_ids:
            post_image_id = data_ids.split(',')[0].split(':')[1]
            post_image_url = BASE_IMAGE_URL.format(post_image_id)
        else:
            post_image_url = 'https://craigslist.org/images/peace.jpg'

        post_listing = {
            'post_title': post_title,
            'post_url': post_url,
            'post_price': post_price,
            'post_image_url': post_image_url
        }

        postings.append(post_listing)

    context = {'search': search, 'postings': postings}

    return render(request, 'craigslist/new-search.html', context)
