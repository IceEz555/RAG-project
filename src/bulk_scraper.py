import requests
from bs4 import BeautifulSoup
import os
from scraper import scrape_recipe
import time

def get_recipe_links(category_url, max_pages=1):
    """
    Crawls an AllRecipes category page to find recipe links.
    """
    links = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    current_url = category_url
    
    print(f"Crawling: {current_url}")
    try:
        response = requests.get(current_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # AllRecipes specific logic (card links)
        # Note: Selectors change often, this is a generic attempt for 'standard' cards
        anchors = soup.find_all('a', href=True)
        
        for a in anchors:
            href = a['href']
            # Filter for recipe URLs
            if '/recipe/' in href and 'allrecipes.com' in href:
                if href not in links:
                    links.append(href)
            elif '/recipe/' in href and href.startswith('http'):
                 if href not in links:
                    links.append(href)
                    
    except Exception as e:
        print(f"Error crawling {category_url}: {e}")
        
    return links[:10]  # Limit to 10 for demo purposes

def bulk_scrape(category_url, output_dir="data"):
    """
    Finds recipes in a category and saves them to text files.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Finding recipes in: {category_url}")
    links = get_recipe_links(category_url)
    print(f"Found {len(links)} potential recipes.")
    
    count = 0
    for link in links:
        print(f"Scraping: {link}")
        content = scrape_recipe(link)
        
        if "Error" not in content and "Recipe:" in content:
            # Create a valid filename
            filename = link.split('/')[-2] if link.split('/')[-2] else "recipe"
            filepath = os.path.join(output_dir, f"{filename}.txt")
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"Saved: {filepath}")
            count += 1
        else:
            print("Skipped (Invalid format)")
        
        time.sleep(1) # Be polite
        
    print(f"Successfully added {count} new recipes to {output_dir}/")

if __name__ == "__main__":
    # Example: Chicken Recipes
    bulk_scrape("https://www.allrecipes.com/recipes/201/meat-and-poultry/chicken/")
