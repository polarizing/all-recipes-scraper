from bs4 import BeautifulSoup
import urllib.request
import json
import time
import re
from pprint import pprint

# REGEX HANDLING
def strip_non_numeric(s):
	return re.sub("[^0-9]", "", s)

# Reformat file handling ...
def getRecipeLinks():
	with open ('page_links.txt', 'r') as PAGE_LINKS:
		links = [link.strip() for link in PAGE_LINKS]

	f = open('recipe_links.txt', 'w') # overwrites the file
	f = open('recipe_links.txt', 'a') # appends to file

	for idx, link in enumerate(links): 
		r = urllib.request.urlopen(link).read()
		soup = BeautifulSoup(r, "html.parser")
		js = soup.find('script', type='application/ld+json').text.strip('<script>')
		
		with open ('links.json', 'w') as WRITE_JSON_LINKS:
			WRITE_JSON_LINKS.write(js)

		with open('links.json', 'r') as JSON_LINKS:
			data = json.load(JSON_LINKS)
			for e in data['itemListElement']:
				print (e['url'] + "\n" + "Writing Data ... ")
				f.write(e['url'] + "\n")
		print ("Link: ", str(idx + 1))

	print ("All done.")

def getRecipeSoup(link):
	r = urllib.request.urlopen(link).read()
	return BeautifulSoup(r, 'html.parser')

def getRecipeID(soup):
	return soup.find('recipe-signup')['data-id']

def getRecipeTitle(soup):
	return soup.find('h1', class_='recipe-summary__h1').text

def getRecipeImage(soup):
	try:
		return soup.find('img', class_='rec-photo')['src']
	except:
		return ""

def getCalorieCount(soup):
	return soup.find('span', class_='calorie-count').text

def getServingCount(soup):
	return soup.find('meta', id='metaRecipeServings')['content']

def getRecipeRating(soup):
	return soup.find('div', class_='rating-stars')['data-ratingstars']

def getReviewCount(soup):
	try:
		return soup.find('span', class_='review-count').text
	except TypeError:
		return ""

def getMadeCount(soup):
	try:
		return soup.find('div', class_='total-made-it')['data-ng-init']
	except TypeError:
		return ""

# returns list of ingredients
def getRecipeIngredients(soup):
	return [ingredient.text.strip() for ingredient in soup.find_all('span', {'itemprop':'ingredients'})]

def getPrepTime(soup):
	try:
		return soup.find('time', {'itemprop':'prepTime'})['datetime']
	except TypeError:
		return ""

def getCookTime(soup):
	try:
		return soup.find('time', {'itemprop':'cookTime'})['datetime']
	except TypeError:
		return ""

def getTotalTime(soup):
	try:
		return soup.find('time', {'itemprop':'totalTime'})['datetime']
	except TypeError:
		return ""

def getRecipeDirections(soup):
	directions = soup.find_all('span', class_="recipe-directions__list--item")
	return [step.text for idx, step in enumerate(directions) if idx < len(directions) - 1] #accounts for extra empty step in 

if __name__ in "__main__":
	# getRecipeLinks()
	export = open ('recipe_data.json', 'w') # rewrite file
	export = open ('recipe_data.json','a')

	recipe = {}

	with open ('recipe_links.txt', 'r') as RECIPE_LINKS:
		recipe_links = [link.strip() for link in RECIPE_LINKS]

	# Exports Data in MongoDB JSON-friendly format
	for recipe_link in recipe_links:
		try:
			soup = getRecipeSoup(recipe_link)
			title = getRecipeTitle(soup)
			recipe_id = getRecipeID(soup)
			recipe_image = getRecipeImage(soup)
			print ("Scraping: ", title, "\tID: ", recipe_id)
			rating = getRecipeRating(soup)
			review_count = getReviewCount(soup)
			made_it_count = strip_non_numeric(getMadeCount(soup))
			calories = strip_non_numeric(getCalorieCount(soup))
			servings = getServingCount(soup)
			ingredients = getRecipeIngredients(soup)
			prep_time = getPrepTime(soup)
			cook_time = getCookTime(soup)
			total_time = getTotalTime(soup)
			instructions = getRecipeDirections(soup)

			recipe['Title'] = title
			recipe['Recipe Image'] = recipe_image
			recipe['Rating'] = float(rating)
			recipe['Review Count'] = int(review_count)
			recipe['Made It Count'] = int(made_it_count)
			recipe['Calories'] = int(calories)
			recipe['Servings'] = int(servings)
			recipe['Ingredients'] = ingredients
			recipe['Prep Time'] = prep_time
			recipe['Cook Time'] = cook_time
			recipe['Total Time'] = total_time
			recipe['Instructions'] = instructions
			print ('Successfully scraped.')
			export.write(json.dumps(recipe) + "\n")

		except:
			print ("Could not extract data.")

