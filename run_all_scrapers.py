# Script to run all scrapers

import subprocess

# List of individual scraper scripts to run (in your project folder)
scrapers = [
    "HypZert.ipynb",
    "DIA_ZERT.ipynb",
    "IQ-ZERT.ipynb",
    "SPRENGNETTER.ipynb",
    "BVS.ipynb",
    "IHK.ipynb"
]

print("🚀 Starting all scraper scripts...\n")

for script in scrapers:
    print(f"🔄 Running {script}...")
    try:
        result = subprocess.run(["python", script], check=True, capture_output=True, text=True)
        print(f"✅ {script} completed successfully.\n")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {script}:")
        print(e.stderr)
    print("-" * 50)

print("🎉 All scripts executed.")
