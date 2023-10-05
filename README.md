# GitHub Actions for Daily Automated Blog Posts

This repository contains a GitHub Actions workflow and a Python script to automate the creation of daily blog posts using the Blogger API. The workflow is scheduled to run daily and publishes a new blog post at a specified time.

[![Daily Automated Actions](https://github.com/raelldottin/paperboy/actions/workflows/daily-run.yml/badge.svg?branch=main)](https://github.com/raelldottin/paperboy/actions/workflows/daily-run.yml) [![CodeQL](https://github.com/raelldottin/paperboy/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/raelldottin/paperboy/actions/workflows/github-code-scanning/codeql)

## GitHub Actions Workflow

The workflow is defined in the `.github/workflows/daily-run.yml` file. It performs the following steps:

1. **Checkout Repository:** Checks out the repository code.
2. **Python Setup:** Sets up the Python environment with version 3.9.
3. **Install Dependencies:** Installs required dependencies defined in `requirements.txt`.
4. **Automate Blog Posts:** Runs the `run.py` script to create blog posts using specified credentials, JSON file, and GitHub repository.

### Workflow Configuration

```yaml
name: Daily Automated Actions

on:
  schedule:
    - cron: '0 14 * * *'
  push:
    branches:
      - main

jobs:
  daily-run:
    name: 'Runs daily'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v2
        with:
          fetch-depth: 2
      - run: git checkout HEAD^2
        if: ${{ github.event_name == 'pull_request' }}
      - name: Setup Python version 3.9
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Automate blog posts
        run: |
          python run.py --credentials '${{ secrets.credentials }}' --json '${{ secrets.json }}' --repo '${{ secrets.repo }}'
```

## Python Script (`run.py`)

The Python script interacts with the Blogger API and creates blog posts based on information provided in a JSON file. Below are key components of the script:

```python
# The content of run.py
# ...

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
        print('Unable to retrieve Blog ID. Exiting.')
        exit(1)

    # Read blog post information from JSON file on GitHub
    github_repo = args.github_repo
    json_file_path = args.json_file
    blog_posts = read_json_file_from_github(github_repo, json_file_path)

    if blog_posts is not None and 'posts' in blog_posts:
        for post in blog_posts['posts']:
            # ...
            # Process and create blog posts based on the script logic
            # ...
```

### Key Script Components

- **Parsing Arguments:** The script parses command-line arguments, including credentials, GitHub repository URL, and JSON file path.
- **Blogger API Initialization:** It initializes the Blogger API client using the provided credentials.
- **Reading Blog Post Information:** The script reads blog post information from a JSON file in the specified GitHub repository.
- **Automating Post Creation:** Based on the scheduled date and time, the script automates the creation of blog posts using the Blogger API.

## Conclusion

With this GitHub Actions workflow and Python script, you can effortlessly schedule and automate your daily blog posts, streamlining your content creation process. Customize the workflow and script to fit your specific requirements and enjoy a more efficient and consistent blogging experience.
