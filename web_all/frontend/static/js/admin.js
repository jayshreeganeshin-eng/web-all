// web_all Admin Panel JavaScript

const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin Panel loaded');
    
    const refreshUsersBtn = document.getElementById('refreshUsersBtn');
    const refreshLogsBtn = document.getElementById('refreshLogsBtn');
    
    if (refreshUsersBtn) {
        refreshUsersBtn.addEventListener('click', loadUsers);
    }
    
    if (refreshLogsBtn) {
        refreshLogsBtn.addEventListener('click', loadAuditLogs);
    }
    
    // Load initial data
    loadStats();
    loadUsers();
    loadAuditLogs();
});

async function loadStats() {
    try {
        // Load users count
        const usersResponse = await fetch(`${API_BASE}/admin/users`);
        if (usersResponse.ok) {
            const users = await usersResponse.json();
            document.getElementById('totalUsers').textContent = users.length;
        }
        
        // Load projects count
        const projectsResponse = await fetch(`${API_BASE}/projects/`);
        if (projectsResponse.ok) {
            const projects = await projectsResponse.json();
            document.getElementById('totalProjects').textContent = projects.length;
        }
        
        // Note: Would need additional endpoints for analyses and content counts
        document.getElementById('totalAnalyses').textContent = '0';
        document.getElementById('totalContent').textContent = '0';
        
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadUsers() {
    const tbody = document.querySelector('#usersTable tbody');
    if (!tbody) return;
    
    try {
        const response = await fetch(`${API_BASE}/admin/users`);
        if (response.ok) {
            const users = await response.json();
            
            if (users.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7">No users found</td></tr>';
                return;
            }
            
            tbody.innerHTML = users.map(user => `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.email}</td>
                    <td>${user.is_admin ? 'Admin' : 'User'}</td>
                    <td>${user.is_active ? 'Active' : 'Inactive'}</td>
                    <td>${new Date(user.created_at).toLocaleDateString()}</td>
                    <td>
                        <button onclick="editUser(${user.id})" class="btn btn-secondary">Edit</button>
                        ${!user.is_admin ? `<button onclick="deleteUser(${user.id})" class="btn">Delete</button>` : ''}
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="7">Error loading users</td></tr>';
        }
    } catch (error) {
        console.error('Error loading users:', error);
        tbody.innerHTML = '<tr><td colspan="7">Error loading users</td></tr>';
    }
}

async function loadAuditLogs() {
    const tbody = document.querySelector('#auditLogsTable tbody');
    if (!tbody) return;
    
    try {
        const response = await fetch(`${API_BASE}/admin/audit-logs`);
        if (response.ok) {
            const logs = await response.json();
            
            if (logs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6">No audit logs found</td></tr>';
                return;
            }
            
            tbody.innerHTML = logs.map(log => `
                <tr>
                    <td>${log.id}</td>
                    <td>User #${log.user_id}</td>
                    <td>${log.action}</td>
                    <td>${log.resource_type || '-'}</td>
                    <td>${log.details ? JSON.stringify(log.details).substring(0, 50) + '...' : '-'}</td>
                    <td>${new Date(log.created_at).toLocaleString()}</td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="6">Error loading audit logs</td></tr>';
        }
    } catch (error) {
        console.error('Error loading audit logs:', error);
        tbody.innerHTML = '<tr><td colspan="6">Error loading audit logs</td></tr>';
    }
}

function editUser(userId) {
    alert(`Edit user ${userId} - Feature coming soon!`);
}

function deleteUser(userId) {
    if (confirm(`Are you sure you want to delete user ${userId}?`)) {
        alert('Delete user feature coming soon!');
    }
}
