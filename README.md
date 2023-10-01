# Automated Blog Post Creation

This GitHub Action automates the process of creating daily blog posts using the Blogger API. The action is scheduled to run every day at 2 pm UTC.

[![Daily Automated Actions](https://github.com/raelldottin/paperboy/actions/workflows/daily-run.yml/badge.svg)](https://github.com/raelldottin/paperboy/actions/workflows/daily-run.yml)

## Workflow

The workflow is defined in the `.github/workflows/daily-automation.yml` file:

```yaml
name: Daily Automated Actions
on:
  schedule:
    - cron: '0 14 * * *'

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
          python run.py --credentials "${{ secrets.credentials }}" --json "${{ secrets.json }}" --repo "${{ secrets.repo }}"
```

### Steps:

1. **Checkout Repository:** The action checks out the repository code.
2. **Python Setup:** It sets up the Python environment with version 3.9.
3. **Install Dependencies:** Installs the required dependencies defined in `requirements.txt`.
4. **Automate Blog Posts:** Runs the `run.py` script to automate the creation of blog posts using the specified credentials, JSON file, and GitHub repository.

## Python Script (`run.py`)

The Python script `run.py` is responsible for interacting with the Blogger API and creating blog posts. It reads blog post information from a JSON file in the specified GitHub repository and schedules posts based on the specified date and time.

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
        print("Unable to retrieve Blog ID. Exiting.")
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

## Configuration

Ensure that the necessary secrets (`credentials`, `json`, `repo`) are configured in the GitHub repository to enable secure communication and access to the required resources.

Feel free to customize the workflow and script according to your specific requirements.
