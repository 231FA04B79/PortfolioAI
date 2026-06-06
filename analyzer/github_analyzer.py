from utils.github_utils import fetch_github_profile, analyze_github_repos


def analyze_github_user(username):
    github_data, error = fetch_github_profile(username)
    if error:
        return None, error

    repo_analysis = analyze_github_repos(github_data['repos'])
    return {
        'profile_data': github_data['profile_data'],
        **repo_analysis,
    }, None
