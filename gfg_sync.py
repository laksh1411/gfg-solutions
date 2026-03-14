import requests
import os
import json
import time

# Configuration from Environment Variables
GFG_USERNAME = os.getenv('GFG_USERNAME')
GFG_COOKIE = os.getenv('GFG_COOKIE')

if not GFG_USERNAME or not GFG_COOKIE:
    print("Error: GFG_USERNAME and GFG_COOKIE must be set in Environment Variables.")
    exit(1)

# API Endpoints
PROFILE_URL = f"https://practiceapi.geeksforgeeks.org/api/v1/user/{GFG_USERNAME}/all-solved-problems/"
SUBMISSION_URL = "https://practiceapi.geeksforgeeks.org/api/v1/submissions/{id}/"

headers = {
    'Cookie': GFG_COOKIE,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

def fetch_solved_problems():
    try:
        response = requests.get(PROFILE_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get('results', [])
    except Exception as e:
        print(f"Error fetching solved problems: {e}")
        return []

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
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"Saved: {file_path}")

def main():
    problems = fetch_solved_problems()
    if not problems:
        print("No solved problems found or access denied.")
        return

    for problem in problems:
        problem_name = problem.get('problem_name')
        difficulty = problem.get('difficulty', 'Unknown')
        latest_submission_id = problem.get('latest_submission_id')
        
        if not latest_submission_id:
            continue

        # Check if already exists to avoid redundant calls
        dir_path = os.path.join(difficulty.capitalize(), problem_name.replace(" ", "_"))
        if os.path.exists(dir_path):
            continue

        print(f"Fetching code for: {problem_name}")
        code, language = fetch_submission_code(latest_submission_id)
        
        if code and language:
            save_solution(problem_name, difficulty, code, language)
            time.sleep(1) # Graceful delay

if __name__ == "__main__":
    main()
