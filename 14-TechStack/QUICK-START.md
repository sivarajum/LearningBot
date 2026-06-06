# Quick Start Guide - TechStack Learning Hub

## 🚀 Get Started in 3 Steps

### Step 1: Start Local Server

**On macOS/Linux:**
```bash
cd 14-TechStack
./start-server.sh
```

**On Windows:**
```bash
cd 14-TechStack
start-server.bat
```

**Or manually:**
```bash
python3 -m http.server 8000
```

### Step 2: Open Browser

Navigate to:
```
http://localhost:8000/website.html
```

### Step 3: Explore!

- Browse technologies by category
- Use search to find specific tools
- Click any technology card to view documentation
- View beautiful Mermaid diagrams in Visual guides

## 📁 Key Files

- `website.html` - Main landing page (beautiful static site)
- `index.html` - Interactive demos hub (existing)
- `tech-page.html` - Individual technology documentation viewer
- `styles.css` - Main stylesheet
- `app.js` - Main page functionality
- `tech-page.js` - Documentation page functionality

## 🎨 Features

✅ Beautiful modern design  
✅ Full Mermaid diagram support  
✅ Search and filter functionality  
✅ Responsive design (mobile-friendly)  
✅ Category organization  
✅ Multiple documentation views  

## 📚 Documentation Types

Each technology can have:
- **Visual.md** - Architecture diagrams and visual guides
- **what.md** - Conceptual overview
- **guide.md** - Practical guide with code examples
- **Interview.md** - Interview questions and answers
- **roadmap.md** - Learning roadmap

## 🔍 Navigation

- **Main Page**: Browse all technologies
- **Category Filters**: Click buttons to filter by category
- **Search**: Type in search box to find technologies
- **Technology Cards**: Click to view documentation
- **Sidebar**: Switch between documentation types

## ⚠️ Important Notes

1. **Local Server Required**: You must run a local server (not open files directly)
2. **CORS**: Browser security requires a server for loading markdown files
3. **Markdown Files**: Ensure all `.md` files are in their expected locations

## 🐛 Troubleshooting

**Diagrams not showing?**
- Check browser console for errors
- Ensure Mermaid.js loaded (check Network tab)
- Refresh the page

**Files not loading?**
- Make sure you're using a local server
- Check file paths are correct
- Verify files exist

**Styles not working?**
- Clear browser cache
- Check CSS file is loaded
- Verify file paths

## 📖 More Information

See `README-WEBSITE.md` for detailed documentation.

