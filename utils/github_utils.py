import requests


def fetch_github_profile(username):
    if not username:
        return None, 'GitHub username is required.'

    user_response = requests.get(f'https://api.github.com/users/{username}')
    if user_response.status_code != 200:
        return None, 'GitHub user not found.'

    profile_data = user_response.json()
    repos_response = requests.get(profile_data.get('repos_url', ''))
    if repos_response.status_code != 200:
        return None, 'Could not fetch repositories from GitHub.'

    return {
        'profile_data': profile_data,
        'repos': repos_response.json(),
    }, None


def analyze_github_repos(repos):
    total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
    total_forks = sum(repo.get('forks_count', 0) for repo in repos)
    language_counts = {}
    for repo in repos:
        language = repo.get('language') or 'Unknown'
        language_counts[language] = language_counts.get(language, 0) + 1
    return {
        'total_repos': len(repos),
        'total_stars': total_stars,
        'total_forks': total_forks,
        'language_counts': language_counts,
        'github_score': min(100, len(repos) * 4 + total_stars * 2 + total_forks),
    }
