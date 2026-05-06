// Dashboard JavaScript - Main Application Logic

class DashboardApp {
    constructor() {
        this.apiBase = '/api';
        this.currentUser = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadCurrentUser();
        this.initializeCharts();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Mobile sidebar toggle
        const menuToggle = document.getElementById('menu-toggle');
        const sidebar = document.getElementById('sidebar');
        
        if (menuToggle && sidebar) {
            menuToggle.addEventListener('click', () => {
                sidebar.classList.toggle('active');
            });
        }

        // Modal handling
        document.querySelectorAll('[data-modal]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = btn.dataset.modal;
                this.openModal(modalId);
            });
        });

        document.querySelectorAll('.modal-close').forEach(btn => {
            btn.addEventListener('click', () => {
                this.closeAllModals();
            });
        });

        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.closeAllModals();
                }
            });
        });

        // Form submissions
        document.querySelectorAll('.ajax-form').forEach(form => {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        });

        // Tab switching
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => this.switchTab(e));
        });

        // Delete confirmations
        document.querySelectorAll('[data-confirm-delete]').forEach(btn => {
            btn.addEventListener('click', (e) => this.confirmDelete(e));
        });
    }

    async loadCurrentUser() {
        try {
            const response = await fetch(`${this.apiBase}/auth/me`);
            if (response.ok) {
                this.currentUser = await response.json();
                this.updateUserInfo();
            }
        } catch (error) {
            console.log('User not logged in or API not available');
        }
    }

    updateUserInfo() {
        if (!this.currentUser) return;
        
        const userNameEl = document.getElementById('user-name');
        const userRoleEl = document.getElementById('user-role');
        const userAvatarEl = document.getElementById('user-avatar');
        
        if (userNameEl) userNameEl.textContent = this.currentUser.username || 'Admin';
        if (userRoleEl) userRoleEl.textContent = this.currentUser.role || 'Administrator';
        if (userAvatarEl) userAvatarEl.textContent = (this.currentUser.username || 'A')[0].toUpperCase();
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
        }
    }

    closeAllModals() {
        document.querySelectorAll('.modal-overlay.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner" style="width:16px;height:16px;border-width:2px;"></span> Processing...';
        }

        try {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            const response = await fetch(form.action, {
                method: form.method || 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert('Success!', result.message || 'Operation completed successfully', 'success');
                this.closeAllModals();
                form.reset();
                this.refreshData();
            } else {
                this.showAlert('Error', result.detail || 'Something went wrong', 'danger');
            }
        } catch (error) {
            this.showAlert('Error', error.message || 'Network error occurred', 'danger');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = submitBtn.dataset.originalText || 'Submit';
            }
        }
    }

    switchTab(e) {
        const tab = e.target;
        const tabGroup = tab.parentElement;
        const tabId = tab.dataset.tab;
        
        // Remove active class from all tabs
        tabGroup.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        
        // Hide all tab content
        const container = tabGroup.parentElement;
        container.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
        });
        
        // Show selected tab content
        const targetContent = document.getElementById(tabId);
        if (targetContent) {
            targetContent.classList.remove('hidden');
        }
    }

    async confirmDelete(e) {
        e.preventDefault();
        const btn = e.target;
        const itemId = btn.dataset.itemId;
        const itemType = btn.dataset.itemType;
        const deleteUrl = btn.dataset.deleteUrl;

        if (!confirm(`Are you sure you want to delete this ${itemType}? This action cannot be undone.`)) {
            return;
        }

        try {
            const response = await fetch(deleteUrl, {
                method: 'DELETE',
            });

            if (response.ok) {
                this.showAlert('Success', `${itemType} deleted successfully`, 'success');
                this.refreshData();
            } else {
                const result = await response.json();
                this.showAlert('Error', result.detail || 'Failed to delete', 'danger');
            }
        } catch (error) {
            this.showAlert('Error', error.message, 'danger');
        }
    }

    showAlert(title, message, type = 'info') {
        const alertContainer = document.getElementById('alert-container');
        if (!alertContainer) return;

        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            <strong>${title}</strong>
            <span>${message}</span>
        `;

        alertContainer.appendChild(alert);

        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    }

    async refreshData() {
        // Refresh stats
        await this.loadStats();
        
        // Refresh tables
        await this.loadProjects();
        await this.loadTasks();
    }

    async loadStats() {
        try {
            const response = await fetch(`${this.apiBase}/dashboard/stats`);
            if (response.ok) {
                const stats = await response.json();
                this.updateStats(stats);
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    }

    updateStats(stats) {
        const statElements = {
            'total-projects': stats.total_projects || 0,
            'total-tasks': stats.total_tasks || 0,
            'completed-tasks': stats.completed_tasks || 0,
            'pending-tasks': stats.pending_tasks || 0,
        };

        Object.entries(statElements).forEach(([id, value]) => {
            const el = document.getElementById(id);
            if (el) {
                el.textContent = value.toLocaleString();
            }
        });
    }

    async loadProjects() {
        try {
            const response = await fetch(`${this.apiBase}/projects`);
            if (response.ok) {
                const projects = await response.json();
                this.renderProjectsTable(projects);
            }
        } catch (error) {
            console.error('Failed to load projects:', error);
        }
    }

    renderProjectsTable(projects) {
        const tbody = document.getElementById('projects-table-body');
        if (!tbody) return;

        tbody.innerHTML = projects.map(project => `
            <tr>
                <td>
                    <div class="font-weight-600">${project.name}</div>
                    <div class="text-sm text-gray-500">${project.description || 'No description'}</div>
                </td>
                <td>
                    <span class="badge badge-${project.status === 'active' ? 'success' : project.status === 'pending' ? 'warning' : 'danger'}">
                        ${project.status}
                    </span>
                </td>
                <td>${new Date(project.created_at).toLocaleDateString()}</td>
                <td>
                    <div class="progress" style="width: 100px;">
                        <div class="progress-bar" style="width: ${project.progress || 0}%"></div>
                    </div>
                    <div class="text-sm mt-1">${project.progress || 0}%</div>
                </td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="dashboard.editProject(${project.id})">Edit</button>
                    <button class="btn btn-sm btn-danger" data-confirm-delete data-item-id="${project.id}" data-item-type="project" data-delete-url="/api/projects/${project.id}">Delete</button>
                </td>
            </tr>
        `).join('');
    }

    async loadTasks() {
        try {
            const response = await fetch(`${this.apiBase}/tasks`);
            if (response.ok) {
                const tasks = await response.json();
                this.renderTasksTable(tasks);
            }
        } catch (error) {
            console.error('Failed to load tasks:', error);
        }
    }

    renderTasksTable(tasks) {
        const tbody = document.getElementById('tasks-table-body');
        if (!tbody) return;

        tbody.innerHTML = tasks.map(task => `
            <tr>
                <td>
                    <div class="font-weight-600">${task.title}</div>
                    <div class="text-sm text-gray-500">${task.project_name || 'No project'}</div>
                </td>
                <td><span class="badge badge-${task.priority === 'high' ? 'danger' : task.priority === 'medium' ? 'warning' : 'primary'}">${task.priority}</span></td>
                <td><span class="badge badge-${task.status === 'completed' ? 'success' : task.status === 'in_progress' ? 'warning' : 'primary'}">${task.status.replace('_', ' ')}</span></td>
                <td>${task.assignee || 'Unassigned'}</td>
                <td>${task.due_date ? new Date(task.due_date).toLocaleDateString() : 'No due date'}</td>
                <td>
                    <button class="btn btn-sm btn-secondary" onclick="dashboard.editTask(${task.id})">Edit</button>
                    <button class="btn btn-sm btn-danger" data-confirm-delete data-item-id="${task.id}" data-item-type="task" data-delete-url="/api/tasks/${task.id}">Delete</button>
                </td>
            </tr>
        `).join('');
    }

    initializeCharts() {
        // Chart initialization can be added here if using a charting library
        console.log('Charts initialized');
    }

    startAutoRefresh() {
        // Auto-refresh data every 30 seconds
        setInterval(() => {
            this.refreshData();
        }, 30000);
    }

    editProject(id) {
        // Open edit modal for project
        this.openModal('edit-project-modal');
        // Load project data
        fetch(`${this.apiBase}/projects/${id}`)
            .then(res => res.json())
            .then(project => {
                document.getElementById('edit-project-id').value = project.id;
                document.getElementById('edit-project-name').value = project.name;
                document.getElementById('edit-project-description').value = project.description || '';
                document.getElementById('edit-project-status').value = project.status;
            });
    }

    editTask(id) {
        // Open edit modal for task
        this.openModal('edit-task-modal');
        // Load task data
        fetch(`${this.apiBase}/tasks/${id}`)
            .then(res => res.json())
            .then(task => {
                document.getElementById('edit-task-id').value = task.id;
                document.getElementById('edit-task-title').value = task.title;
                document.getElementById('edit-task-priority').value = task.priority;
                document.getElementById('edit-task-status').value = task.status;
            });
    }
}

// Initialize dashboard app
const dashboard = new DashboardApp();

// Utility functions
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        dashboard.showAlert('Copied!', 'Text copied to clipboard', 'success');
    }).catch(err => {
        dashboard.showAlert('Error', 'Failed to copy', 'danger');
    });
}

// Export for use in other scripts
window.dashboard = dashboard;
