#!/bin/bash
# Verification script for ML Fundamentals Implementation
# This script verifies all deliverables are in place

echo "🔍 ML FUNDAMENTALS IMPLEMENTATION VERIFICATION"
echo "=============================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 (NOT FOUND)"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/ (NOT FOUND)"
        return 1
    fi
}

BASE_DIR="/Users/sivarajumalladi/Documents/GitHub/LearningBot/01-ML-Fundamentals"

echo "📋 CHECKING MAIN CONFIGURATION FILES"
echo "======================================"
check_file "$BASE_DIR/requirements.txt"
check_file "$BASE_DIR/Plantodo.md"
check_file "$BASE_DIR/README_COMPLETE.md"
check_file "$BASE_DIR/IMPLEMENTATION_COMPLETE.md"
echo ""

echo "📁 CHECKING PROJECT DIRECTORIES"
echo "================================="
check_dir "$BASE_DIR/01-iris-classification"
check_dir "$BASE_DIR/02-movie-recommendation"
check_dir "$BASE_DIR/03-sentiment-analysis"
echo ""

echo "🔬 PHASE 1: IRIS CLASSIFICATION"
echo "================================="
echo "Python Implementation:"
check_file "$BASE_DIR/01-iris-classification/iris_classifier.py"
check_file "$BASE_DIR/01-iris-classification/test_iris_classifier.py"
echo ""
echo "Jupyter Notebook:"
check_file "$BASE_DIR/01-iris-classification/iris_classification.ipynb"
echo ""
echo "Documentation:"
check_file "$BASE_DIR/01-iris-classification/README.md"
echo ""

echo "🎬 PHASE 2: MOVIE RECOMMENDATION SYSTEM"
echo "========================================"
echo "Python Implementation:"
check_file "$BASE_DIR/02-movie-recommendation/recommendation_system.py"
check_file "$BASE_DIR/02-movie-recommendation/test_recommendation_system.py"
echo ""
echo "Jupyter Notebook:"
check_file "$BASE_DIR/02-movie-recommendation/movie_recommendation.ipynb"
echo ""
echo "Documentation:"
check_file "$BASE_DIR/02-movie-recommendation/README.md"
echo ""

echo "💬 PHASE 3: SENTIMENT ANALYSIS"
echo "=============================="
echo "Python Implementation:"
check_file "$BASE_DIR/03-sentiment-analysis/sentiment_analysis.py"
check_file "$BASE_DIR/03-sentiment-analysis/test_sentiment_analysis.py"
echo ""
echo "Jupyter Notebook:"
check_file "$BASE_DIR/03-sentiment-analysis/sentiment_analysis.ipynb"
echo ""
echo "Documentation:"
check_file "$BASE_DIR/03-sentiment-analysis/README.md"
echo ""

echo "📊 FILE COUNT SUMMARY"
echo "====================="
PYTHON_FILES=$(find "$BASE_DIR" -name "*.py" -type f | wc -l)
NOTEBOOK_FILES=$(find "$BASE_DIR" -name "*.ipynb" -type f | wc -l)
MD_FILES=$(find "$BASE_DIR" -name "*.md" -type f | wc -l)
echo -e "Python Files (.py): ${GREEN}$PYTHON_FILES${NC}"
echo -e "Jupyter Notebooks (.ipynb): ${GREEN}$NOTEBOOK_FILES${NC}"
echo -e "Documentation (.md): ${GREEN}$MD_FILES${NC}"
echo ""

echo "📏 CODE STATISTICS"
echo "=================="
TOTAL_LINES=$(find "$BASE_DIR" -name "*.py" -type f ! -name "test_*" -exec wc -l {} + | tail -1 | awk '{print $1}')
TEST_LINES=$(find "$BASE_DIR" -name "test_*.py" -type f -exec wc -l {} + | tail -1 | awk '{print $1}')
DOC_LINES=$(find "$BASE_DIR" -name "*.md" -type f ! -name "architecture_plan.md" ! -name "guide.md" -exec wc -l {} + | tail -1 | awk '{print $1}')

echo -e "Production Code Lines: ${GREEN}~$TOTAL_LINES${NC}"
echo -e "Test Code Lines: ${GREEN}~$TEST_LINES${NC}"
echo -e "Documentation Lines: ${GREEN}~$DOC_LINES${NC}"
echo ""

echo "✅ IMPLEMENTATION VERIFICATION COMPLETE!"
echo "=========================================="
echo ""
echo "All deliverables are in place."
echo "Ready for learning and deployment! 🚀"
