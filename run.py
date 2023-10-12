import json
import argparse
from io import StringIO
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime
import requests
import logging

# Blogger API scopes
SCOPES = ["https://www.googleapis.com/auth/blogger"]


def authenticate(scopes, client_secret, credentials_json):
    flow = InstalledAppFlow.from_client_config(client_secret, scopes)
    credentials = flow.run_local_server(port=0)

    # Save the credentials for the next run
    credentials_data = credentials.to_json()
    credentials_json.write(credentials_data)

    return credentials


def create_blog_post(service, blog_id, title, content):
    post_body = {
        "kind": "blogger#post",
        "blog": {
            "id": blog_id,
        },
        "title": title,
        "content": content,
    }

    try:
        posts = service.posts()
        request = posts.insert(blogId=blog_id, body=post_body)
        response = request.execute()
        logging.info(f'New blog post created with ID: {response["id"]}')
    except Exception as e:
        logging.error(f"Error creating blog post: {str(e)}")


def get_existing_post_titles(service, blog_id):
    try:
        posts = service.posts().list(blogId=blog_id).execute()
        existing_titles = set(post["title"] for post in posts.get("items", []))
        return existing_titles
    except Exception as e:
        logging.error(f"Error fetching existing post titles: {str(e)}")
        return set()


def get_github_file_content(repo_url, file_path):
    github_raw_url = f"https://raw.githubusercontent.com/{repo_url}/master/{file_path}"
    response = requests.get(github_raw_url)
    if response.status_code == 200:
        return response.text
    else:
        logging.info(f"Error fetching content from GitHub: {response.text}")
        return None


def read_json_file_from_github(repo_url, file_path):
    content = get_github_file_content(repo_url, file_path)
    if content:
        try:
            return json.loads(content)
        except Exception as e:
            logging.error(f"Error parsing JSON content: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Create a new blog post.")
    parser.add_argument(
        "--client-secret",
        type=json.loads,
        help="Client secret JSON as a string",
        required=True,
    )
    parser.add_argument(
        "--credentials-json",
        type=json.loads,
        help="Credentials JSON as a string",
        required=True,
    )
    parser.add_argument(
        "--blog-id",
        type=str,
        help="Blog ID",
        required=True,
    )
    parser.add_argument(
        "--github-repo",
        type=str,
        help="GitHub repository URL",
        required=True,
    )
    parser.add_argument(
        "--json-file",
        type=str,
        help="JSON file with pending blog posts",
        required=True,
    )

    args = parser.parse_args()

    credentials_data = StringIO()
    if "token" in args.credentials_json:
        # For OAuth 2.0 credentials
        credentials_data.write(json.dumps(args.credentials_json))
    else:
        # For service account credentials
        json.dump(args.credentials_json, credentials_data)

    credentials_data.seek(0)
    credentials = Credentials.from_authorized_user_info(
        json.loads(credentials_data.read()), SCOPES
    )

    # Initialize the Blogger API client
    blogger_service = build("blogger", "v3", credentials=credentials)

    # Get JSON data from GitHub repo
    github_repo = args.github_repo
    json_file = args.json_file
    json_data = read_json_file_from_github(github_repo, json_file)

    if json_data is not None and "posts" in json_data:
        existing_titles = get_existing_post_titles(blogger_service, args.blog_id)
        for post in json_data["posts"]:
            title = post.get("title")
            content = post.get("content")
            post_date_str = post.get("post_date")

            if title and content and post_date_str:
                # Check if the title already exists
                if title in existing_titles:
                    logging.info(f'Skipping duplicate blog post with title "{title}"')
                else:
                    post_date = datetime.strptime(post_date_str, "%Y-%m-%dT%H:%M:%S")
                    current_time = datetime.now()

                    if post_date > current_time:
                        time_difference = (post_date - current_time).total_seconds()
                        logging.info(
                            f"Waiting for {time_difference} seconds until {post_date}"
                        )

                    else:
                        create_blog_post(blogger_service, args.blog_id, title, content)
            else:
                logging.info(
                    f"Skipping post with missing title, content, or post_date: {post}"
                )


if __name__ == "__main__":
    main()
