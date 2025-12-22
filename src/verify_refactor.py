from main_logic import get_answer

def test_refactor():
    print("Testing Refactor...")
    try:
        response, sources = get_answer("Hello", thread_id="1")
        print(f"General Response: {response}")
        
        response, sources = get_answer("Chicken recipe", thread_id="1")
        print(f"Cooking Response: {response}")
        print("Refactor Success!")
    except Exception as e:
        print(f"Refactor Failed: {e}")

if __name__ == "__main__":
    test_refactor()
