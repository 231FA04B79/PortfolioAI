import re
import random

def generate_ai_summary(profile, skills, projects):
    """
    Generates a professional resume summary using profile, skills, and projects data.
    """
    title = profile.professional_title or "Software Developer"
    skills_names = [s.name for s in skills[:4]]
    proj_names = [p.title for p in projects[:2]]
    
    if not skills_names:
        skills_names = ["modern software technologies", "web development"]
        
    skills_str = ", ".join(skills_names[:-1]) + " and " + skills_names[-1] if len(skills_names) > 1 else skills_names[0]
    
    if proj_names:
        proj_str = f" Demonstrated successful application delivery through projects such as {', '.join(proj_names)}."
    else:
        proj_str = ""
        
    summary = (
        f"Highly motivated and result-driven {title} with expertise in {skills_str}. "
        f"Possesses a strong foundation in designing, developing, and deploying scalable software systems.{proj_str} "
        f"Adept at collaborating in team environments to solve complex engineering challenges and optimize application performance."
    )
    return summary

def improve_ai_wording(text):
    """
    Improves description text using high-impact recruiter action verbs.
    """
    if not text:
        return ""
    
    replacements = {
        r'\b(?:built|made|created|developed)\b': 'Engineered and deployed',
        r'\b(?:used|worked with|utilized)\b': 'Leveraged',
        r'\b(?:did|worked on|led)\b': 'Spearheaded',
        r'\b(?:helped with|assisted)\b': 'Collaborated on',
        r'\b(?:fixed|solved|debugged)\b': 'Optimized and resolved',
        r'\b(?:learned|learnt)\b': 'Acquired expertise in',
        r'\b(?:added|integrated)\b': 'Successfully integrated',
        r'\b(?:changed|edited)\b': 'Refactored',
        r'\b(?:managed|handled)\b': 'Orchestrated',
    }
    
    improved = text
    for pat, rep in replacements.items():
        improved = re.sub(pat, rep, improved, flags=re.IGNORECASE)
        
    # Ensure it starts with a capital letter
    if improved:
        improved = improved[0].upper() + improved[1:]
    return improved

def highlight_ai_strengths(skills, certifications):
    """
    Identifies and formats 3-5 core strengths based on skills and certs.
    """
    strengths = []
    skill_names = [s.name.lower() for s in skills]
    
    # 1. Algorithmic skill
    if any(s in skill_names for s in ['python', 'c++', 'java', 'go', 'rust']):
        strengths.append("Algorithmic Problem Solving")
        
    # 2. Web systems
    if any(s in skill_names for s in ['django', 'react', 'node.js', 'angular', 'vue', 'flask', 'fastapi']):
        strengths.append("Full-Stack Web Engineering")
        
    # 3. Databases
    if any(s in skill_names for s in ['postgresql', 'mysql', 'mongodb', 'sqlite', 'redis', 'sql']):
        strengths.append("Database Design & Normalization")
        
    # 4. Cloud infrastructure
    if any(s in skill_names for s in ['aws', 'docker', 'kubernetes', 'cloud', 'gcp']):
        strengths.append("Containerization & Cloud Infrastructure")
        
    # 5. Fallback or generic strengths
    if len(strengths) < 3:
        strengths.append("Agile Software Delivery")
        strengths.append("RESTful API Development")
        
    # Add certification indicators
    for cert in certifications[:2]:
        strengths.append(f"Certified: {cert.certificate_name}")
        
    return strengths[:4]
