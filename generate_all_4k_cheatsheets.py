#!/usr/bin/env python3
"""
Master 4K Cheat Sheet Generator - Generates ALL cheat sheets
Run this script to regenerate all 17 professional 4K cheat sheets
"""

import subprocess
import sys
from pathlib import Path

def run_generator(script_name, description):
    """Run a generator script and handle output"""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            cwd=Path(__file__).parent,
            capture_output=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  🎓 LEARNINGBOT 4K CHEAT SHEET MASTER GENERATOR")
    print("="*60)
    print("\n📊 This script generates ALL 17 professional 4K cheat sheets:")
    print("   • 5 Core Learning Modules")
    print("   • 6 Advanced Technical Skills")
    print("   • 6 TechStack Categories")
    print(f"\n📁 Output: ./4k_cheatsheets/")
    print(f"⏱️  Estimated time: ~15-30 seconds")
    print(f"💾 Total size: ~5 MB\n")
    
    input("Press Enter to start generation...\n")
    
    generators = [
        ("generate_4k_cheatsheets.py", 
         "🎯 Generating Core Learning Modules (5 sheets)"),
        ("generate_4k_cheatsheets_extended.py", 
         "🛠️  Generating Advanced Technical Skills (6 sheets)"),
        ("generate_4k_techstack.py", 
         "☁️  Generating TechStack Cheat Sheets (6 sheets)"),
    ]
    
    successful = 0
    failed = 0
    
    for script, description in generators:
        if run_generator(script, description):
            successful += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"  ✅ GENERATION COMPLETE")
    print(f"{'='*60}\n")
    print(f"📊 Results:")
    print(f"   ✓ Successful: {successful}/{len(generators)}")
    print(f"   ✗ Failed: {failed}/{len(generators)}\n")
    
    # Display summary
    output_dir = Path(__file__).parent / "4k_cheatsheets"
    if output_dir.exists():
        pngs = list(output_dir.glob("*.png"))
        readme = list(output_dir.glob("README.md"))
        
        print(f"📁 Output Directory: {output_dir.absolute()}")
        print(f"   • PNG Files: {len(pngs)}")
        print(f"   • Documentation: {len(readme)}")
        
        total_size = sum(f.stat().st_size for f in output_dir.glob("*")) / (1024 * 1024)
        print(f"   • Total Size: {total_size:.1f} MB\n")
        
        print("📋 Generated Cheat Sheets:")
        for f in sorted(pngs):
            size_kb = f.stat().st_size / 1024
            print(f"   ✓ {f.name} ({size_kb:.0f} KB)")
        
        if readme:
            print(f"\n📖 Documentation: 4k_cheatsheets/README.md")
            print("   Run: cat 4k_cheatsheets/README.md")
    
    print(f"\n🎉 All 17 4K cheat sheets are ready!\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Generation cancelled by user")
        sys.exit(1)
