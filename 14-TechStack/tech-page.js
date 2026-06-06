// Technology Page JavaScript - Handles markdown loading and mermaid rendering

// Initialize Mermaid
mermaid.initialize({ 
    startOnLoad: false, // We'll initialize manually after content loads
    theme: 'default',
    themeVariables: {
        primaryColor: '#2563eb',
        primaryTextColor: '#fff',
        primaryBorderColor: '#1e40af',
        lineColor: '#4b5563',
        secondaryColor: '#10b981',
        tertiaryColor: '#f59e0b',
        noteBkgColor: '#fef3c7',
        noteTextColor: '#92400e'
    },
    flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
        curve: 'basis'
    },
    sequence: {
        diagramMarginX: 50,
        diagramMarginY: 10,
        actorMargin: 50,
        width: 150,
        height: 65,
        boxMargin: 10,
        boxTextMargin: 5,
        noteMargin: 10,
        messageMargin: 35
    }
});

// Get path from URL parameter
function getPathFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('path') || '';
}

// Get technology name from path
function getTechName(path) {
    const parts = path.split('/');
    return parts[parts.length - 1] || path;
}

// Update page title and breadcrumb
function updatePageInfo(path, docType = 'Visual') {
    const techName = getTechName(path);
    const title = `${techName} - ${docType} Guide`;
    document.title = title;
    document.getElementById('page-title').textContent = `${techName} ${docType} Guide`;
    document.getElementById('breadcrumb-path').textContent = path;
}

// Load markdown file
async function loadMarkdownFile(path, filename) {
    const fullPath = `${path}/${filename}`;
    // Fallback: when server is started from repo root instead of 14-TechStack
    const fallbackPath = `14-TechStack/${path}/${filename}`;
    const loadingEl = document.getElementById('loading');
    const contentEl = document.getElementById('content-area');
    const errorEl = document.getElementById('error-message');
    
    loadingEl.style.display = 'block';
    contentEl.style.display = 'none';
    errorEl.style.display = 'none';
    
    try {
        let response = await fetch(fullPath);

        // Retry once with fallback when server root is the repo root
        if (!response.ok && !path.startsWith('14-TechStack/')) {
            response = await fetch(fallbackPath);
        }

        if (!response.ok) {
            throw new Error(`Failed to load ${filename} (tried: ${fullPath}${path.startsWith('14-TechStack/') ? '' : `, ${fallbackPath}`})`);
        }
        
        const markdown = await response.text();
        await renderMarkdown(markdown);
        
        loadingEl.style.display = 'none';
        contentEl.style.display = 'block';
        
        return true;
    } catch (error) {
        console.error('Error loading markdown:', error);
        loadingEl.style.display = 'none';
        errorEl.style.display = 'block';
        return false;
    }
}

// Render markdown with mermaid support
async function renderMarkdown(markdown) {
    const contentEl = document.getElementById('content-area');
    
    // Configure marked options
    marked.setOptions({
        breaks: true,
        gfm: true,
        highlight: function(code, lang) {
            if (lang && hljs.getLanguage(lang)) {
                try {
                    return hljs.highlight(code, { language: lang }).value;
                } catch (err) {
                    console.error('Highlight error:', err);
                }
            }
            return hljs.highlightAuto(code).value;
        }
    });
    
    // Process mermaid diagrams before rendering
    const processedMarkdown = await processMermaidDiagrams(markdown);
    
    // Convert markdown to HTML
    const html = marked.parse(processedMarkdown);
    contentEl.innerHTML = html;
    
    // Initialize mermaid diagrams
    await initializeMermaidDiagrams();
}

// Process mermaid diagrams in markdown
async function processMermaidDiagrams(markdown) {
    // Find all mermaid code blocks
    const mermaidRegex = /```mermaid\n([\s\S]*?)```/g;
    const matches = [...markdown.matchAll(mermaidRegex)];
    
    let processedMarkdown = markdown;
    let diagramIndex = 0;
    
    matches.forEach(match => {
        const diagramCode = match[1];
        const placeholder = `MERMAID_DIAGRAM_${diagramIndex}`;
        processedMarkdown = processedMarkdown.replace(
            match[0],
            `<div class="mermaid" data-diagram-index="${diagramIndex}">${diagramCode}</div>`
        );
        diagramIndex++;
    });
    
    return processedMarkdown;
}

// Initialize mermaid diagrams
async function initializeMermaidDiagrams() {
    const mermaidElements = document.querySelectorAll('.mermaid');
    
    if (mermaidElements.length === 0) {
        return;
    }
    
    // Render each mermaid diagram
    mermaidElements.forEach(async (element, index) => {
        try {
            const diagramCode = element.textContent.trim();
            const id = `mermaid-${index}-${Date.now()}`;
            element.id = id;
            
            // Render the diagram
            const { svg } = await mermaid.render(id, diagramCode);
            element.innerHTML = svg;
        } catch (error) {
            console.error('Mermaid rendering error:', error);
            element.innerHTML = `
                <div style="padding: 20px; color: #ef4444; text-align: center;">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Error rendering diagram: ${error.message}</p>
                    <pre style="text-align: left; margin-top: 10px; font-size: 0.8rem;">${element.textContent}</pre>
                </div>
            `;
        }
    });
}

// Setup sidebar navigation
function setupSidebarNavigation(path) {
    const sidebarLinks = document.querySelectorAll('.sidebar-menu a[data-doc]');
    
    sidebarLinks.forEach(link => {
        link.addEventListener('click', async (e) => {
            e.preventDefault();
            
            // Update active state
            sidebarLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            // Determine which file to load
            const docType = link.dataset.doc;
            let filename;
            
            switch(docType) {
                case 'visual':
                    filename = 'Visual.md';
                    break;
                case 'what':
                    filename = 'what.md';
                    break;
                case 'guide':
                    filename = 'guide.md';
                    break;
                case 'interview':
                    filename = 'Interview.md';
                    break;
                case 'roadmap':
                    filename = 'roadmap.md';
                    break;
                default:
                    filename = 'Visual.md';
            }
            
            // Update page info
            const docTypeName = docType.charAt(0).toUpperCase() + docType.slice(1);
            updatePageInfo(path, docTypeName);
            
            // Load the file
            await loadMarkdownFile(path, filename);
            
            // Scroll to top
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });
}

// Setup header action buttons
function setupActionButtons(path) {
    const visualLink = document.getElementById('visual-link');
    const guideLink = document.getElementById('guide-link');
    const interviewLink = document.getElementById('interview-link');
    
    if (visualLink) {
        visualLink.href = `tech-page.html?path=${encodeURIComponent(path)}&doc=visual`;
    }
    if (guideLink) {
        guideLink.href = `tech-page.html?path=${encodeURIComponent(path)}&doc=guide`;
    }
    if (interviewLink) {
        interviewLink.href = `tech-page.html?path=${encodeURIComponent(path)}&doc=interview`;
    }
}

// Initialize page
async function initializePage() {
    const path = getPathFromURL();
    const params = new URLSearchParams(window.location.search);
    const docType = params.get('doc') || 'visual';
    
    if (!path) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error-message').style.display = 'block';
        return;
    }
    
    // Determine which file to load
    let filename;
    let docTypeName;
    
    switch(docType) {
        case 'visual':
            filename = 'Visual.md';
            docTypeName = 'Visual';
            break;
        case 'what':
            filename = 'what.md';
            docTypeName = 'What is it?';
            break;
        case 'guide':
            filename = 'guide.md';
            docTypeName = 'Guide';
            break;
        case 'interview':
            filename = 'Interview.md';
            docTypeName = 'Interview';
            break;
        case 'roadmap':
            filename = 'roadmap.md';
            docTypeName = 'Roadmap';
            break;
        default:
            filename = 'Visual.md';
            docTypeName = 'Visual';
    }
    
    // Update page info
    updatePageInfo(path, docTypeName);
    
    // Setup navigation
    setupSidebarNavigation(path);
    setupActionButtons(path);
    
    // Set active sidebar item
    const activeLink = document.querySelector(`.sidebar-menu a[data-doc="${docType}"]`);
    if (activeLink) {
        document.querySelectorAll('.sidebar-menu a').forEach(l => l.classList.remove('active'));
        activeLink.classList.add('active');
    }
    
    // Load the markdown file
    await loadMarkdownFile(path, filename);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePage);
} else {
    initializePage();
}

