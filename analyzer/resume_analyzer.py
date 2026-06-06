from utils.resume_utils import analyze_resume_pdf


def analyze_resume_file(resume_file):
    try:
        return analyze_resume_pdf(resume_file), None
    except Exception as exc:
        return None, f'Could not read the uploaded resume PDF: {exc}'
