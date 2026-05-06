// web_all Dashboard JavaScript

const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', function() {
    console.log('User Dashboard loaded');
    
    // Modal functionality
    const modal = document.getElementById('projectModal');
    const newProjectBtn = document.getElementById('newProjectBtn');
    const closeBtn = document.querySelector('.close');
    const projectForm = document.getElementById('projectForm');
    
    if (newProjectBtn) {
        newProjectBtn.addEventListener('click', () => {
            modal.style.display = 'block';
        });
    }
    
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    if (projectForm) {
        projectForm.addEventListener('submit', handleCreateProject);
    }
    
    // Load data
    loadProjects();
    loadSeoAnalyses();
    loadContentGenerations();
});

async function handleCreateProject(e) {
    e.preventDefault();
    
    const projectData = {
        name: document.getElementById('projectName').value,
        url: document.getElementById('projectUrl').value,
        description: document.getElementById('projectDesc').value,
        clone_mode: document.getElementById('cloneMode').value,
        use_tor: document.getElementById('useTor').checked
    };
    
    try {
        const response = await fetch(`${API_BASE}/projects/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(projectData)
        });
        
        if (response.ok) {
            const project = await response.json();
            alert('Project created successfully!');
            document.getElementById('projectModal').style.display = 'none';
            document.getElementById('projectForm').reset();
            loadProjects();
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error creating project:', error);
        alert('Failed to create project');
    }
}

async function loadProjects() {
    const projectsList = document.getElementById('projectsList');
    if (!projectsList) return;
    
    try {
        const response = await fetch(`${API_BASE}/projects/`);
        if (response.ok) {
            const projects = await response.json();
            
            if (projects.length === 0) {
                projectsList.innerHTML = '<p>No projects yet. Create your first project!</p>';
                return;
            }
            
            projectsList.innerHTML = `
                <div class="projects-grid">
                    ${projects.map(project => `
                        <div class="feature-card">
                            <h3>${project.name}</h3>
                            <p><strong>URL:</strong> ${project.url}</p>
                            <p><strong>Status:</strong> <span class="status-${project.status}">${project.status}</span></p>
                            <p><strong>Mode:</strong> ${project.clone_mode}</p>
                            <div class="card-actions">
                                <button onclick="analyzeSEO('${project.url}', ${project.id})" class="btn btn-secondary">Analyze SEO</button>
                                <button onclick="viewProject(${project.id})" class="btn">View Details</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            projectsList.innerHTML = '<p>Error loading projects</p>';
        }
    } catch (error) {
        console.error('Error loading projects:', error);
        projectsList.innerHTML = '<p>Error loading projects</p>';
    }
}

async function loadSeoAnalyses() {
    const analysesList = document.getElementById('seoAnalysesList');
    if (!analysesList) return;
    
    // For now, show placeholder - would need an endpoint to list all analyses
    analysesList.innerHTML = '<p>SEO analyses will appear here after you run an analysis.</p>';
}

async function loadContentGenerations() {
    const contentList = document.getElementById('contentList');
    if (!contentList) return;
    
    // For now, show placeholder
    contentList.innerHTML = '<p>Generated content will appear here after you generate content.</p>';
}

async function analyzeSEO(url, projectId) {
    try {
        const response = await fetch(`${API_BASE}/seo/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url, project_id: projectId })
        });
        
        if (response.ok) {
            const analysis = await response.json();
            alert(`SEO Analysis started! Analysis ID: ${analysis.id}`);
            loadSeoAnalyses();
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        console.error('Error starting SEO analysis:', error);
        alert('Failed to start SEO analysis');
    }
}

function viewProject(projectId) {
    // Navigate to project details page or show modal
    alert(`Viewing project ${projectId} - Feature coming soon!`);
}
