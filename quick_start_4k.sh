#!/bin/bash

# 🎓 LearningBot 4K Cheat Sheets - Quick Start Guide

echo "
╔════════════════════════════════════════════════════════════════╗
║     🎓 LEARNINGBOT 4K CHEAT SHEETS - QUICK START GUIDE         ║
╚════════════════════════════════════════════════════════════════╝
"

# Function to display instructions
show_help() {
    echo "📋 AVAILABLE COMMANDS:"
    echo ""
    echo "  1️⃣  Generate All Cheat Sheets:"
    echo "     python generate_all_4k_cheatsheets.py"
    echo ""
    echo "  2️⃣  Generate Individual Sets:"
    echo "     python generate_4k_cheatsheets.py          # Core modules (5)"
    echo "     python generate_4k_cheatsheets_extended.py # Advanced (6)"
    echo "     python generate_4k_techstack.py            # TechStack (6)"
    echo ""
    echo "  3️⃣  View Generated Files:"
    echo "     ls -lh 4k_cheatsheets/"
    echo ""
    echo "  4️⃣  Open in Finder (macOS):"
    echo "     open 4k_cheatsheets/"
    echo ""
    echo "  5️⃣  View Documentation:"
    echo "     cat 4k_cheatsheets/README.md"
    echo ""
    echo "  6️⃣  Check File Sizes:"
    echo "     du -sh 4k_cheatsheets/"
    echo ""
}

# Function to show collection info
show_collection() {
    echo "📊 COLLECTION INFORMATION:"
    echo ""
    echo "  Total Cheat Sheets: 17"
    echo "  Resolution: 3840 x 2160 (4K UHD)"
    echo "  DPI: 300 (Print Quality)"
    echo "  Format: PNG (Lossless)"
    echo "  Total Size: ~4.8 MB"
    echo ""
    echo "  Categories:"
    echo "    • Core Learning Modules: 5 sheets"
    echo "    • Advanced Technical Skills: 6 sheets"
    echo "    • TechStack Categories: 6 sheets"
    echo ""
}

# Function to show file listing
show_files() {
    if [ -d "4k_cheatsheets" ]; then
        echo "✅ Cheat sheets directory found!"
        echo ""
        echo "📁 Generated Files:"
        ls -1 4k_cheatsheets/*.png 2>/dev/null | while read file; do
            size=$(du -h "$file" | cut -f1)
            name=$(basename "$file")
            echo "   ✓ $name ($size)"
        done
        echo ""
        total_size=$(du -sh 4k_cheatsheets/ 2>/dev/null | cut -f1)
        echo "   Total Directory Size: $total_size"
    else
        echo "❌ 4k_cheatsheets directory not found"
        echo "   Run: python generate_all_4k_cheatsheets.py"
    fi
    echo ""
}

# Function to show use cases
show_usecases() {
    echo "🎯 USE CASES:"
    echo ""
    echo "  📚 Educational:"
    echo "     • Print for classroom reference"
    echo "     • Display on large screens"
    echo "     • Share with study groups"
    echo ""
    echo "  💼 Professional:"
    echo "     • Workspace posters"
    echo "     • Training materials"
    echo "     • Onboarding documentation"
    echo ""
    echo "  🎓 Interview Prep:"
    echo "     • Quick reference during prep"
    echo "     • Certification study"
    echo "     • Architecture discussions"
    echo ""
}

# Function to show specifications
show_specs() {
    echo "⚙️  TECHNICAL SPECIFICATIONS:"
    echo ""
    echo "  Display Compatibility:"
    echo "    ✓ 4K Monitors (3840x2160)"
    echo "    ✓ Projectors (Full HD and above)"
    echo "    ✓ Print (300 DPI)"
    echo "    ✓ Tablets & Large Screens"
    echo ""
    echo "  Software Support:"
    echo "    ✓ Preview (macOS)"
    echo "    ✓ Photos App"
    echo "    ✓ Browsers (Chrome, Safari, Firefox)"
    echo "    ✓ Design Tools (Figma, Photoshop)"
    echo ""
    echo "  File Format:"
    echo "    • Format: PNG (Portable Network Graphics)"
    echo "    • Compression: Lossless"
    echo "    • Color Space: RGB"
    echo "    • Bit Depth: 24-bit (8-bit per channel)"
    echo ""
}

# Function to show learning paths
show_paths() {
    echo "🛤️  SUGGESTED LEARNING PATHS:"
    echo ""
    echo "  📈 Complete ML/AI Path:"
    echo "    1. ML Fundamentals"
    echo "    2. Cloud AI Platform"
    echo "    3. LLM Essentials"
    echo "    4. RAG Essentials"
    echo "    5. MLOps Automation"
    echo ""
    echo "  📊 Data Engineering Path:"
    echo "    1. Data Engineering"
    echo "    2. Feature Engineering"
    echo "    3. BigQuery (TechStack)"
    echo "    4. Apache Spark (TechStack)"
    echo ""
    echo "  🏗️  System Architecture Path:"
    echo "    1. System Design"
    echo "    2. Kubernetes"
    echo "    3. Backend Development"
    echo "    4. MLOps Automation"
    echo ""
    echo "  ☁️  Cloud Platform Path:"
    echo "    1. GCP (TechStack)"
    echo "    2. AWS (TechStack)"
    echo "    3. BigQuery (TechStack)"
    echo "    4. Apache Spark (TechStack)"
    echo ""
}

# Main menu
echo "🎯 WHAT WOULD YOU LIKE TO DO?"
echo ""
echo "  1. Generate all cheat sheets"
echo "  2. View help & commands"
echo "  3. Show collection info"
echo "  4. List generated files"
echo "  5. Show use cases"
echo "  6. Show technical specs"
echo "  7. Show learning paths"
echo "  8. Exit"
echo ""
read -p "Enter choice (1-8): " choice

case $choice in
    1)
        echo ""
        python generate_all_4k_cheatsheets.py
        ;;
    2)
        show_help
        ;;
    3)
        show_collection
        ;;
    4)
        show_files
        ;;
    5)
        show_usecases
        ;;
    6)
        show_specs
        ;;
    7)
        show_paths
        ;;
    8)
        echo "👋 Goodbye!"
        ;;
    *)
        echo "❌ Invalid choice"
        ;;
esac

echo ""
