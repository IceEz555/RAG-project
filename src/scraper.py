import requests
from bs4 import BeautifulSoup
import json

def scrape_recipe(url: str):
    """
    Scrapes a recipe from a given URL by looking for schema.org/Recipe JSON-LD.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find JSON-LD script tags
        scripts = soup.find_all('script', type='application/ld+json')
        
        recipe_data = None
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                # Helper to check type
                def is_recipe(obj):
                    t = obj.get('@type')
                    if isinstance(t, str):
                        return t == 'Recipe'
                    elif isinstance(t, list):
                        return 'Recipe' in t
                    return False

                # Check if it's a list of schemas (graph) or a single one
                if isinstance(data, dict):
                    if is_recipe(data):
                        recipe_data = data
                        break
                    elif '@graph' in data:
                        for item in data['@graph']:
                            if is_recipe(item):
                                recipe_data = item
                                break
                elif isinstance(data, list):
                    for item in data:
                        if is_recipe(item):
                            recipe_data = item
                            break
                            
                if recipe_data:
                    break
            except Exception as e:
                continue
                
        if not recipe_data:
            return "Could not find a recipe format on this page."
            
        # Parse relevant fields
        title = recipe_data.get('name', 'Unknown Recipe')
        ingredients = recipe_data.get('recipeIngredient', [])
        instructions = recipe_data.get('recipeInstructions', [])
        
        # Clean instructions
        cleaned_instructions = []
        if isinstance(instructions, list):
            for step in instructions:
                if isinstance(step, str):
                    cleaned_instructions.append(step)
                elif isinstance(step, dict):
                    cleaned_instructions.append(step.get('text', ''))
        elif isinstance(instructions, str):
            cleaned_instructions.append(instructions)
            
        formatted_output = f"""
Recipe: {title}
        
Ingredients:
{chr(10).join(['- ' + ing for ing in ingredients])}
        
Instructions:
{chr(10).join([f'{i+1}. {step}' for i, step in enumerate(cleaned_instructions)])}
        
Source: {url}
"""
        return formatted_output

    except Exception as e:
        return f"Error scraping recipe: {str(e)}"

if __name__ == "__main__":
    # Test
    print(scrape_recipe("https://www.allrecipes.com/recipe/219634/chef-johns-french-fries/"))
