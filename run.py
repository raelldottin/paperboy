import os
import argparse
from google.oauth2 import service_account
from googleapiclient.discovery import build
import time
import functools
import requests
import json
from datetime import datetime

# Initialize the Blogger API client
base_url = 'https://www.googleapis.com/blogger/v3'

def parse_args():
    parser = argparse.ArgumentParser(description='Create a new blog post.')
    parser.add_argument('--credentials', type=str, help='Credentials file content as a JSON string', required=True)
    parser.add_argument('--github-repo', type=str, help='GitHub repository URL', required=True)
    parser.add_argument('--json-file', type=str, help='JSON file containing blog post information', required=True)
    return parser.parse_args()

def get_blogger_service(credentials):
    credentials = service_account.Credentials.from_service_account_info(credentials)
    return build('blogger', 'v3', credentials=credentials)

def get_blog_id(blogger_service):
    try:
        blogs = blogger_service.blogs().listByUser(userId='self').execute()
        if 'items' in blogs and blogs['items']:
            return blogs['items'][0]['id']
    except Exception as e:
        print(f'Error retrieving blog ID: {str(e)}')
    return None

def rate_limited(requests_per_minute):
    interval = 60 / requests_per_minute

    def decorator(func):
        last_request_time = 0

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_request_time
            current_time = time.time()
            time_since_last_request = current_time - last_request_time
            if time_since_last_request < interval:
                time_to_wait = interval - time_since_last_request
                time.sleep(time_to_wait)
            last_request_time = time.time()
            return func(*args, **kwargs)

        return wrapper

    return decorator

# Rate limit the create_blog_post function to 1 request per minute
@rate_limited(1)
def create_blog_post(blogger_service, title, content, blog_id):
    post_body = {
        'kind': 'blogger#post',
        'blog': {
            'id': blog_id,
        },
        'title': title,
        'content': content,
    }

    try:
        posts = blogger_service.posts()
        request = posts.insert(blogId=blog_id, body=post_body)
        response = request.execute()
        print(f'New blog post created with ID: {response["id"]}')
    except Exception as e:
        print(f'Error creating blog post: {str(e)}')

def get_github_file_content(repo_url, file_path):
    github_api_url = f'https://api.github.com/repos/{repo_url}/contents/{file_path}'
    response = requests.get(github_api_url)
    if response.status_code == 200:
        content_base64 = response.json()['content']
        return base64.b64decode(content_base64).decode('utf-8')
    else:
        print(f'Error fetching content from GitHub: {response.text}')
        return None

def read_json_file_from_github(repo_url, file_path):
    content = get_github_file_content(repo_url, file_path)
    if content:
        try:
            return json.loads(content)
        except Exception as e:
            print(f'Error parsing JSON content: {str(e)}')
    return None

# Example usage
if __name__ == '__main__':
    args = parse_args()

    # Use the contents of the credentials file as a string
    credentials_str = args.credentials

    # Initialize the Blogger API client
    blogger_service = get_blogger_service(credentials_str)

    # Get the Blog ID
    blog_id = get_blog_id(blogger_service)
    if blog_id is None:
        print("Unable to retrieve Blog ID. Exiting.")
        exit(1)

    # Read blog post information from JSON file on GitHub
    github_repo = args.github_repo
    json_file_path = args.json_file
    blog_posts = read_json_file_from_github(github_repo, json_file_path)

    if blog_posts is not None and 'posts' in blog_posts:
        for post in blog_posts['posts']:
            title = post.get('title')
            content = post.get('content')
            post_date_str = post.get('post_date')

            if title and content and post_date_str:
                post_date = datetime.strptime(post_date_str, '%Y-%m-%dT%H:%M:%S')
                current_time = datetime.now()

                if post_date > current_time:
                    time_difference = (post_date - current_time).total_seconds()
                    print(f"Waiting for {time_difference} seconds until {post_date}")
                    time.sleep(time_difference)

                create_blog_post(blogger_service, title, content, blog_id)
            else:
                print(f"Skipping post with missing title, content, or post_date: {post}")
