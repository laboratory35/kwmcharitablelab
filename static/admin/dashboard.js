// Check authentication status
async function checkAuth() {
    try {
        const response = await fetch('/admin/check-auth');
        if (!response.ok) {
            window.location.href = '/';
            return false;
        }
        const data = await response.json();
        return data.authenticated;
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/';
        return false;
    }
}

// Format date to readable string
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Update dashboard statistics
async function updateStats() {
    try {
        const response = await fetch('/api/admin/stats');
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/';
                return;
            }
            throw new Error('Failed to fetch stats');
        }
        const data = await response.json();
        
        document.getElementById('totalBookings').textContent = data.total_bookings;
        document.getElementById('todayBookings').textContent = data.today_bookings;
        document.getElementById('pendingTests').textContent = data.pending_tests;
    } catch (error) {
        console.error('Error fetching stats:', error);
        showError('Failed to load statistics');
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger';
    errorDiv.textContent = message;
    document.querySelector('main').prepend(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

// Update recent bookings table
async function updateRecentBookings() {
    try {
        const response = await fetch('/api/admin/recent-bookings');
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/';
                return;
            }
            throw new Error('Failed to fetch bookings');
        }
        const bookings = await response.json();
        
        const tbody = document.getElementById('recentBookings');
        tbody.innerHTML = '';
        
        bookings.forEach(booking => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${formatDate(booking.created_at)}</td>
                <td>${booking.name}</td>
                <td>${booking.test_type}</td>
                <td>${booking.phone}</td>
                <td><span class="status-badge status-${booking.status.toLowerCase()}">${booking.status}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="viewBooking(${booking.id})">View</button>
                    <button class="btn btn-sm btn-outline-success" onclick="updateStatus(${booking.id}, 'completed')">Complete</button>
                    <button class="btn btn-sm btn-outline-danger" onclick="updateStatus(${booking.id}, 'cancelled')">Cancel</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error('Error fetching recent bookings:', error);
        showError('Failed to load recent bookings');
    }
}

// View booking details
async function viewBooking(id) {
    try {
        const response = await fetch(`/api/admin/booking/${id}`);
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/';
                return;
            }
            throw new Error('Failed to fetch booking details');
        }
        const booking = await response.json();
        
        // Create and show modal with booking details
        const modal = new bootstrap.Modal(document.getElementById('bookingModal'));
        document.getElementById('bookingDetails').innerHTML = `
            <p><strong>Name:</strong> ${booking.name}</p>
            <p><strong>Email:</strong> ${booking.email}</p>
            <p><strong>Phone:</strong> ${booking.phone}</p>
            <p><strong>Test Type:</strong> ${booking.test_type}</p>
            <p><strong>Preferred Date:</strong> ${formatDate(booking.preferred_date)}</p>
            <p><strong>Message:</strong> ${booking.message || 'N/A'}</p>
            <p><strong>Status:</strong> ${booking.status}</p>
            <p><strong>Created At:</strong> ${formatDate(booking.created_at)}</p>
        `;
        modal.show();
    } catch (error) {
        console.error('Error fetching booking details:', error);
        showError('Failed to load booking details');
    }
}

// Update booking status
async function updateStatus(id, status) {
    if (!confirm(`Are you sure you want to mark this booking as ${status}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/admin/booking/${id}/status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status })
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/';
                return;
            }
            throw new Error('Failed to update status');
        }
        
        // Refresh the dashboard data
        updateStats();
        updateRecentBookings();
    } catch (error) {
        console.error('Error updating status:', error);
        showError('Failed to update booking status');
    }
}

// Export data to CSV
function exportData() {
    window.location.href = '/api/admin/export';
}

// Refresh dashboard data
function refreshData() {
    updateStats();
    updateRecentBookings();
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication first
    const isAuthenticated = await checkAuth();
    if (!isAuthenticated) return;

    // Initialize the dashboard
    updateStats();
    updateRecentBookings();
    
    // Refresh data every 5 minutes
    setInterval(refreshData, 300000);
});
