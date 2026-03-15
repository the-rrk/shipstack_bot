#!/usr/bin/env python3
"""
Website Builder Skill Handler

Builds static or full-stack projects, prepares Railway and Supabase handlers,
and can optionally apply the generated changes to a hosted Git repository.
"""

import json
import sys

from wb_pipeline import build_project


def handle(prompt: str, **kwargs) -> dict:
    return build_project(prompt, **kwargs)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python handler.py \"Your project description\"")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])
    result = handle(prompt)

    if result["status"] == "success":
        print("\n✅ Project created successfully!")
        print(f"📁 Local path: {result['path']}")
        print(f"🧩 Project type: {result.get('projectType')}")
        print(f"🚀 Deploy target: {result.get('deployTarget')}")
        if result.get("url"):
            print(f"🌍 Live URL: {result['url']}")
        print(f"🔍 Site name: {result['site_name']}")
        print(json.dumps(result, indent=2))
    elif result["status"] == "selection_required":
        print("\n📚 Repository selection required")
        print(json.dumps(result, indent=2))
    else:
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)
