#!/bin/bash
echo "=== Checking for missing documentation files ==="
echo ""
for dir in $(find . -type d -name "interactive-*.html" 2>/dev/null | sed 's|/interactive-.*||' | sort -u); do
    # Check if directory exists and has interactive HTML
    if [ -d "$dir" ] && [ -f "$dir/interactive-"*.html 2>/dev/null ]; then
        missing=()
        [ ! -f "$dir/what.md" ] && missing+=("what.md")
        [ ! -f "$dir/Visual.md" ] && missing+=("Visual.md")
        [ ! -f "$dir/Interview.md" ] && missing+=("Interview.md")
        
        if [ ${#missing[@]} -gt 0 ]; then
            echo "❌ $dir - Missing: ${missing[*]}"
        else
            echo "✅ $dir - Complete"
        fi
    fi
done
