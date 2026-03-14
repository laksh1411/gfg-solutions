import requests
import os
import json
import time

# Configuration from Environment Variables
GFG_HANDLE = os.getenv('GFG_HANDLE')
GFG_COOKIE = os.getenv('GFG_COOKIE')

if not GFG_HANDLE or not GFG_COOKIE:
    print("Error: GFG_HANDLE and GFG_COOKIE must be set in Environment Variables.")
    exit(1)

# API Endpoints
BASE_PROFILE_URL = f"https://practiceapi.geeksforgeeks.org/api/v1/user/{GFG_HANDLE}/all-solved-problems/"
SUBMISSION_URL = "https://practiceapi.geeksforgeeks.org/api/v1/submissions/{id}/"

headers = {
    'Cookie': GFG_COOKIE,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

def fetch_solved_problems():
    all_problems = []
    url = BASE_PROFILE_URL
    page_count = 1

    while url:
        print(f"Fetching page {page_count}...")
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            all_problems.extend(results)
            
            # Update URL for the next page
            url = data.get('next')
            page_count += 1
            
            if url:
                time.sleep(1) # Delay between page requests
        except Exception as e:
            print(f"Error fetching solved problems on page {page_count}: {e}")
            break
            
    return all_problems

def fetch_submission_code(submission_id):
    try:
        url = SUBMISSION_URL.format(id=submission_id)
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('code'), data.get('language')
    except Exception as e:
        print(f"Error fetching code for submission {submission_id}: {e}")
        return None, None

def save_solution(problem_name, difficulty, code, language):
    ext_map = {
        'cpp': 'cpp',
        'java': 'java',
        'python': 'py',
        'python3': 'py',
        'javascript': 'js',
        'c': 'c'
    }
    ext = ext_map.get(language.lower(), 'txt')
    
    # Create directory structure: Difficulty/ProblemName/solution.ext
    dir_path = os.path.join(difficulty.capitalize(), problem_name.replace(" ", "_"))
    os.makedirs(dir_path, exist_ok=True)
    
    file_path = os.path.join(dir_path, f"solution.{ext}")
    
    # Don't overwrite if file already exists to save time/noise
    if os.path.exists(file_path):
        return

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"Saved: {file_path}")

def main():
    problems = fetch_solved_problems()
    if not problems:
        print("No solved problems found or access denied. Check if GFG_HANDLE and GFG_COOKIE are correct.")
        return

    print(f"Found {len(problems)} total solved problems. Checking for new solutions...")

    for problem in problems:
        problem_name = problem.get('problem_name')
        difficulty = problem.get('difficulty', 'Unknown')
        latest_submission_id = problem.get('latest_submission_id')
        
        if not latest_submission_id:
            continue

        # Check if already exists to avoid redundant calls
        clean_name = problem_name.replace(" ", "_")
        dir_path = os.path.join(difficulty.capitalize(), clean_name)
        
        # We also check for the file in save_solution, but skipping here avoids a network call
        if os.path.exists(dir_path):
            continue

        print(f"Fetching code for: {problem_name}")
        code, language = fetch_submission_code(latest_submission_id)
        
        if code and language:
            save_solution(problem_name, difficulty, code, language)
            time.sleep(0.5) # Small delay to be polite

if __name__ == "__main__":
    main()
