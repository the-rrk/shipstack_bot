---
name: website_builder
description: "Generate a complete static website from a prompt and deploy it to Vercel. Use when: user asks to build, create, or make a website, landing page, portfolio, or any static web page. Returns the live hosted URL. NOT for: dynamic web apps, backend APIs, or database-driven sites."
metadata:
  {
    "openclaw":
      {
        "emoji": "🌐",
        "requires": { "bins": ["python3", "vercel"], "env": ["VERCEL_TOKEN", "OPENAI_API_KEY_1"] },
      },
  }
---

# Website Builder & Deployer

Generate beautiful static websites from natural language prompts and deploy them instantly to Vercel.

## When to Use

✅ **USE this skill when:**

- "Build me a website for..."
- "Create a landing page for..."
- "Make a portfolio site for..."
- "Generate a homepage for my business"
- Any request to create and host a static website

## When NOT to Use

❌ **DON'T use this skill when:**

- User wants a dynamic web app with backend
- User needs database integration
- User wants to edit an existing website
- User just wants HTML code (not hosted)

## Command

Run the website builder handler with the user's prompt (using the project's virtual environment):

```bash
.venv/bin/python skills/website_builder/handler.py "<user's website description>"
```

### Example

**User:** "Build me a portfolio website for a photographer named Alex who specializes in landscape photography"

```bash
.venv/bin/python skills/website_builder/handler.py "Build a portfolio website for a photographer named Alex who specializes in landscape photography"
```

### Output

The script returns:

- `✅ Website created successfully!`
- `📁 Local path: projects/<project-name>-<id>/`
- `🌍 Live URL: https://<project>.vercel.app`

## What Gets Generated

The handler creates a complete website with:

1. **index.html** - Modern, responsive HTML with:
   - Hero section with title and tagline
   - Features/services section (3 cards)
   - Contact form section
   - Footer

2. **styles.css** - Professional CSS with:
   - Custom color scheme based on the theme
   - Gradient hero background
   - Responsive design
   - Smooth animations

3. **script.js** - Interactive JavaScript:
   - Smooth scrolling
   - Form handling
   - Scroll animations

## Response Format

After running the command, respond to the user with:

```
✅ I've created and deployed your website!

🌍 **Live URL:** [paste the URL here]
📁 **Local files:** [paste the path]

The site includes:
- [Brief description of what was generated]
- Hero section with your tagline
- Features/services showcase
- Contact form
- Responsive mobile design

You can visit your live site now at the URL above!
```

## Requirements

- `python3` - Python 3.x interpreter
- `vercel` - Vercel CLI for deployment
- `VERCEL_TOKEN` - Vercel API token (in .env)
- `OPENAI_API_KEY_1` - OpenAI API key for content generation (in .env)

## Notes

- The website is deployed to Vercel's free tier
- Each generation creates a unique project folder
- Colors and content are AI-generated based on the prompt
- Sites are fully responsive and mobile-friendly
