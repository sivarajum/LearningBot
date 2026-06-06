# TechStack Learning Hub - Static Website

A beautiful, modern static website for browsing and learning from the TechStack documentation, featuring full Mermaid diagram support.

## Features

- 🎨 **Beautiful Modern Design** - Inspired by sparkbyexamples.com and data-flair.training
- 📊 **Mermaid Diagram Support** - All Visual.md files with Mermaid diagrams render beautifully
- 🔍 **Search & Filter** - Easy navigation through 150+ technologies
- 📱 **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- 🎯 **Category Organization** - Technologies organized by category (DevOps, Data Engineering, GCP, etc.)
- 📚 **Multiple Documentation Views** - Visual guides, practical guides, interview Q&A, and more

## File Structure

```
14-TechStack/
├── website.html          # Main landing page
├── tech-page.html        # Individual technology documentation page
├── styles.css            # Main stylesheet
├── tech-page.css         # Technology page specific styles
├── app.js                # Main page JavaScript
├── tech-page.js          # Technology page JavaScript
└── README-WEBSITE.md     # This file
```

## Quick Start

### Option 1: Using Python HTTP Server (Recommended)

```bash
# Navigate to the TechStack directory
cd 14-TechStack

# Python 3
python3 -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000
```

Then open your browser and navigate to:
```
http://localhost:8000/website.html
```

### Option 2: Using Node.js http-server

```bash
# Install http-server globally (if not already installed)
npm install -g http-server

# Navigate to the TechStack directory
cd 14-TechStack

# Start the server
http-server -p 8000
```

Then open:
```
http://localhost:8000/website.html
```

### Option 3: Using VS Code Live Server

1. Install the "Live Server" extension in VS Code
2. Right-click on `website.html`
3. Select "Open with Live Server"

## Usage

### Main Page (website.html)

- **Browse Technologies**: Scroll through categories or use the filter buttons
- **Search**: Use the search box to find specific technologies
- **Filter**: Click category buttons to filter technologies
- **Click Cards**: Click on any technology card to view its documentation

### Technology Page (tech-page.html)

- **Navigation**: Use the sidebar to switch between different documentation types:
  - Visual Guide (Visual.md)
  - What is it? (what.md)
  - Practical Guide (guide.md)
  - Interview Q&A (Interview.md)
  - Learning Roadmap (roadmap.md)

- **Mermaid Diagrams**: All Mermaid diagrams in Visual.md files are automatically rendered
- **Code Highlighting**: Code blocks are syntax-highlighted
- **Responsive**: Works on all screen sizes

## Technologies Covered

### DevOps & Infrastructure
- Docker, Kubernetes, Terraform, GitHub Actions, Jenkins, Monitoring

### Data Engineering
- Apache Spark, Apache Airflow, Python, Scala, Java, SQL, Kafka

### Google Cloud Platform
- BigQuery, Cloud Storage, Vertex AI, Cloud Run, Cloud Functions, Dataflow, and 20+ more services

### AI & Machine Learning
- scikit-learn, TensorFlow, PyTorch, MLflow, Weights & Biases, Jupyter

### Generative AI & LLMs
- OpenAI GPT, LangChain, Vector Databases, Embeddings, RAG, LLMs, LLMOps

### Frontend Technologies
- React, TypeScript, Streamlit, Material-UI, D3.js

### Backend Technologies
- FastAPI, Node.js, Python, Redis, SQLite

### Databases
- PostgreSQL, MongoDB, Neo4j, Elasticsearch, Redis, BigQuery

### Tools & Libraries
- VS Code, Jupyter, Git, Pandas, NumPy, Matplotlib, Seaborn, Plotly

## Mermaid Diagram Support

The website fully supports all Mermaid diagram types:
- Flowcharts (`graph TD`, `graph LR`, etc.)
- Sequence diagrams
- Class diagrams
- State diagrams
- Gantt charts
- Pie charts
- And more...

All diagrams are automatically rendered with beautiful styling and are responsive.

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera

## Notes

- **Local Server Required**: Due to browser security (CORS), you must run a local server. Direct file access won't work for loading markdown files.
- **Markdown Files**: The website loads `.md` files directly, so ensure all documentation files are in their expected locations.
- **Mermaid Version**: Uses Mermaid.js v10+ for diagram rendering.

## Customization

### Colors

Edit `styles.css` and modify the CSS variables in `:root`:

```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #10b981;
    /* ... */
}
```

### Adding Technologies

Edit `app.js` and add technologies to the `technologies` object:

```javascript
const technologies = {
    'your-category': [
        { 
            name: 'Technology Name', 
            path: 'path/to/tech', 
            icon: 'fas fa-icon', 
            description: 'Description' 
        }
    ]
};
```

## Troubleshooting

### Diagrams Not Rendering

1. Check browser console for errors
2. Ensure Mermaid.js is loaded (check Network tab)
3. Verify markdown syntax is correct
4. Try refreshing the page

### Markdown Files Not Loading

1. Ensure you're running a local server (not opening files directly)
2. Check file paths are correct
3. Verify files exist in the expected locations
4. Check browser console for CORS errors

### Styles Not Applying

1. Clear browser cache
2. Check that `styles.css` is loaded
3. Verify file paths in HTML are correct

## Future Enhancements

- [ ] Pre-render markdown to HTML for faster loading
- [ ] Add dark mode support
- [ ] Add print-friendly styles
- [ ] Add PDF export functionality
- [ ] Add search within documentation
- [ ] Add bookmark/favorite functionality

## Credits

Design inspired by:
- [Spark By Examples](https://sparkbyexamples.com/)
- [Data Flair Training](https://data-flair.training/)

## License

This website is part of the LearningBot project.

