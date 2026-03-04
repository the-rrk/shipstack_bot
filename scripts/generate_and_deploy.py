
#!/usr/bin/env python3
"""
Prompt to Project: Generate a static website from a prompt and deploy to Vercel.

Usage:
    python scripts/generate_and_deploy.py "Create a portfolio website for a photographer"
    
Environment variables required:
    OPENAI_API_KEY_1 or OPENAI_API_KEY - OpenAI API key
    VERCEL_TOKEN - Vercel deployment token
"""

import os
import sys
import json
import uuid
import subprocess
import re
from pathlib import Path

# Try to import openai
try:
    from openai import OpenAI
except ImportError:
    print("OpenAI library not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
    from openai import OpenAI

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key not in os.environ:
                        os.environ[key] = value

load_env()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_1") or os.getenv("OPENAI_API_KEY")
VERCEL_TOKEN = os.getenv("VERCEL_TOKEN")
PROJECTS_DIR = Path(__file__).parent.parent / "projects"

# Ensure projects directory exists
PROJECTS_DIR.mkdir(exist_ok=True)


def generate_website_content(prompt: str) -> dict:
    """Use OpenAI to generate website content based on the prompt."""
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY_1 or OPENAI_API_KEY in .env")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    system_prompt = """You are a web content generator. Given a user's request, generate content for a modern static website.
    
Return a JSON object with the following structure:
{
    "site_name": "Name of the website",
    "title": "Main headline for the hero section",
    "subtitle": "Subtitle/tagline for the hero section",
    "cta_text": "Call to action button text",
    "features": [
        {"title": "Feature 1 Title", "description": "Feature 1 description"},
        {"title": "Feature 2 Title", "description": "Feature 2 description"},
        {"title": "Feature 3 Title", "description": "Feature 3 description"}
    ],
    "contact_text": "Text for the contact section",
    "primary_color": "A hex color code that fits the theme (e.g., #3498db)",
    "gradient_start": "Gradient start color for hero (e.g., #2c3e50)",
    "gradient_end": "Gradient end color for hero (e.g., #3498db)"
}

Make the content relevant, professional, and tailored to the user's request.
Only return valid JSON, no other text."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    content = response.choices[0].message.content
    # Clean up potential markdown code blocks
    content = re.sub(r'^```json\s*', '', content)
    content = re.sub(r'\s*```$', '', content)
    
    return json.loads(content)


def create_html(content: dict) -> str:
    """Generate HTML from content dictionary."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content["site_name"]}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header class="hero">
        <div class="container">
            <h1 class="hero-title">{content["title"]}</h1>
            <p class="hero-subtitle">{content["subtitle"]}</p>
            <a href="#contact" class="btn">{content["cta_text"]}</a>
        </div>
    </header>

    <section id="features" class="features">
        <div class="container">
            <h2 class="section-title">What We Offer</h2>
            <div class="feature-grid">
                <div class="feature-card">
                    <h3>{content["features"][0]["title"]}</h3>
                    <p>{content["features"][0]["description"]}</p>
                </div>
                <div class="feature-card">
                    <h3>{content["features"][1]["title"]}</h3>
                    <p>{content["features"][1]["description"]}</p>
                </div>
                <div class="feature-card">
                    <h3>{content["features"][2]["title"]}</h3>
                    <p>{content["features"][2]["description"]}</p>
                </div>
            </div>
        </div>
    </section>

    <section id="contact" class="contact">
        <div class="container">
            <h2 class="section-title">Get In Touch</h2>
            <p>{content["contact_text"]}</p>
            <form class="contact-form">
                <input type="text" placeholder="Your Name" required>
                <input type="email" placeholder="Your Email" required>
                <textarea placeholder="Your Message" rows="5" required></textarea>
                <button type="submit" class="btn">Send Message</button>
            </form>
        </div>
    </section>

    <footer>
        <div class="container">
            <p>&copy; 2026 {content["site_name"]}. All rights reserved.</p>
        </div>
    </footer>
    <script src="script.js"></script>
</body>
</html>'''


def create_css(content: dict) -> str:
    """Generate CSS from content dictionary."""
    primary_color = content.get("primary_color", "#3498db")
    gradient_start = content.get("gradient_start", "#2c3e50")
    gradient_end = content.get("gradient_end", "#3498db")
    
    return f''':root {{
    --primary-color: {primary_color};
    --text-color: #333;
    --bg-color: #f9f9f9;
    --card-bg: #fff;
}}

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: var(--text-color);
    background-color: var(--bg-color);
    line-height: 1.6;
}}

.container {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 20px;
}}

.btn {{
    display: inline-block;
    background: var(--primary-color);
    color: #fff;
    padding: 12px 30px;
    text-decoration: none;
    border: none;
    border-radius: 30px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}}

.btn:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.3);
}}

.hero {{
    background: linear-gradient(135deg, {gradient_start}, {gradient_end});
    color: #fff;
    padding: 120px 0;
    text-align: center;
    min-height: 60vh;
    display: flex;
    align-items: center;
}}

.hero-title {{
    font-size: 3.5rem;
    margin-bottom: 20px;
    font-weight: 700;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}}

.hero-subtitle {{
    font-size: 1.3rem;
    margin-bottom: 40px;
    opacity: 0.95;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}}

.section-title {{
    text-align: center;
    margin-bottom: 50px;
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--text-color);
}}

.features {{
    padding: 80px 0;
}}

.feature-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
}}

.feature-card {{
    background: var(--card-bg);
    padding: 40px 30px;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    text-align: center;
    transition: all 0.3s ease;
}}

.feature-card:hover {{
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}}

.feature-card h3 {{
    margin-bottom: 15px;
    font-size: 1.4rem;
    color: var(--primary-color);
}}

.feature-card p {{
    color: #666;
    line-height: 1.8;
}}

.contact {{
    padding: 80px 0;
    background: linear-gradient(180deg, #fff 0%, var(--bg-color) 100%);
    text-align: center;
}}

.contact > .container > p {{
    max-width: 600px;
    margin: 0 auto 40px;
    color: #666;
    font-size: 1.1rem;
}}

.contact-form {{
    max-width: 500px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 20px;
}}

.contact-form input,
.contact-form textarea {{
    padding: 15px 20px;
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
    font-family: inherit;
}}

.contact-form input:focus,
.contact-form textarea:focus {{
    outline: none;
    border-color: var(--primary-color);
}}

footer {{
    background: {gradient_start};
    color: #fff;
    text-align: center;
    padding: 30px 0;
}}

footer p {{
    opacity: 0.9;
}}

@media (max-width: 768px) {{
    .hero-title {{
        font-size: 2.5rem;
    }}
    
    .hero-subtitle {{
        font-size: 1.1rem;
    }}
    
    .section-title {{
        font-size: 2rem;
    }}
}}'''


def create_js() -> str:
    """Generate JavaScript for the website."""
    return '''// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Form submission handler
document.querySelector('.contact-form')?.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const data = Object.fromEntries(formData.entries());
    
    // Show success message
    const btn = this.querySelector('button');
    const originalText = btn.textContent;
    btn.textContent = 'Message Sent!';
    btn.style.background = '#27ae60';
    
    // Reset form
    this.reset();
    
    // Restore button after 3 seconds
    setTimeout(() => {
        btn.textContent = originalText;
        btn.style.background = '';
    }, 3000);
});

// Add scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards
document.querySelectorAll('.feature-card').forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(card);
});

console.log('Website loaded successfully!');
'''


def create_project(prompt: str) -> tuple[str, Path]:
    """Create a project with generated content."""
    print(f"🎨 Generating website content for: {prompt}")
    
    # Generate content using OpenAI
    content = generate_website_content(prompt)
    print(f"✅ Content generated: {content['site_name']}")
    
    # Create project directory
    project_id = str(uuid.uuid4())[:8]
    project_name = re.sub(r'[^a-z0-9-]', '-', content['site_name'].lower())[:30]
    project_folder = f"{project_name}-{project_id}"
    project_path = PROJECTS_DIR / project_folder
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Generate and save files
    print("📝 Creating HTML...")
    html_content = create_html(content)
    (project_path / "index.html").write_text(html_content)
    
    print("🎨 Creating CSS...")
    css_content = create_css(content)
    (project_path / "styles.css").write_text(css_content)
    
    print("⚙️ Creating JavaScript...")
    js_content = create_js()
    (project_path / "script.js").write_text(js_content)
    
    print(f"✅ Project created at: {project_path}")
    return project_id, project_path


def deploy_to_vercel(project_path: Path) -> str:
    """Deploy the project to Vercel and return the URL."""
    if not VERCEL_TOKEN:
        raise ValueError("VERCEL_TOKEN not found in environment variables")
    
    print("🚀 Deploying to Vercel...")
    
    # Run vercel deploy command
    result = subprocess.run(
        ["vercel", "--prod", "--yes", "--token", VERCEL_TOKEN],
        cwd=project_path,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Deployment error: {result.stderr}")
        raise RuntimeError(f"Vercel deployment failed: {result.stderr}")
    
    # Extract URL from output
    output = result.stdout.strip()
    # The URL is usually the last line or contains https://
    lines = output.split('\n')
    url = None
    for line in reversed(lines):
        line = line.strip()
        if line.startswith('https://'):
            url = line
            break
    
    if not url:
        # Try to find URL in the output
        url_match = re.search(r'https://[^\s]+\.vercel\.app[^\s]*', output)
        if url_match:
            url = url_match.group(0)
    
    if not url:
        print(f"Full output: {output}")
        raise RuntimeError("Could not extract deployment URL from Vercel output")
    
    print(f"✅ Deployed successfully!")
    return url


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate_and_deploy.py \"Your website description\"")
        print("\nExample:")
        print('  python generate_and_deploy.py "Create a portfolio website for a photographer"')
        sys.exit(1)
    
    prompt = " ".join(sys.argv[1:])
    
    print("=" * 60)
    print("🌐 Prompt to Project - Website Generator & Deployer")
    print("=" * 60)
    print()
    
    try:
        # Step 1: Generate the website
        project_id, project_path = create_project(prompt)
        print()
        
        # Step 2: Deploy to Vercel
        url = deploy_to_vercel(project_path)
        print()
        # Derive global URL from project folder name (matches handler logic)
        project_folder = project_path.name  # e.g. "simple-test-page-323f0c27"
        global_url = f"https://{project_folder}.vercel.app"
        url =global_url
        # Final output
        print("=" * 60)
        print("🎉 SUCCESS!")
        print("=" * 60)
        print(f"📁 Local path: {project_path}")
        print(f"🌍 Live URL:   {global_url}")
        print("=" * 60)
        
        return url
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
