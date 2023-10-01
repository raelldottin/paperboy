import httplib2
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Your Blogger blog ID
blog_id = "YOUR_BLOG_ID"

# Your API credentials JSON file
credentials_file = "your_credentials.json"

# Initialize the Blogger API client
scopes = ["https://www.googleapis.com/auth/blogger"]
credentials = service_account.Credentials.from_service_account_file(
    credentials_file, scopes=scopes
)
blogger_service = build("blogger", "v3", credentials=credentials)

# Function to create a new blog post


def create_blog_post(title, content):
    post_body = {
        "kind": "blogger#post",
        "blog": {
            "id": blog_id,
        },
        "title": title,
        "content": content,
    }

    try:
        posts = blogger_service.posts()
        request = posts.insert(blogId=blog_id, body=post_body)
        response = request.execute()
        print(f'New blog post created with ID: {response["id"]}')
    except Exception as e:
        print(f"Error creating blog post: {str(e)}")


# Example usage
if __name__ == "__main__":
    title = "Your Blog Post Title"
    content = "The content of your blog post goes here. This can be the response from ChatGPT."

    create_blog_post(title, content)
