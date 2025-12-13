/**
 * ADMIN.JS - Admin Panel Specific Functions
 * Sidebar, navigation, data tables, charts
 */

const AdminPanel = {
    /**
     * Initialize admin panel
     */
    init() {
        this.initSidebar();
        this.initDropdowns();
        this.initDataTables();
        this.initCharts();
        this.initSearch();
    },

    // =====================================
    // Sidebar Management
    // =====================================

    initSidebar() {
        const sidebar = document.querySelector('.admin-sidebar');
        const toggle = document.querySelector('.sidebar-toggle');
        const overlay = document.querySelector('.admin-overlay');

        if (!sidebar || !toggle) return;

        // Toggle sidebar on mobile
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('show');
            overlay?.classList.toggle('show');
        });

        // Close sidebar when clicking overlay
        overlay?.addEventListener('click', () => {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });

        // Remember sidebar state
        const savedState = Utils.getStorage(AppConfig.STORAGE.SIDEBAR_STATE);
        if (savedState === 'collapsed') {
            sidebar.classList.add('collapsed');
        }

        // Collapse button (desktop)
        const collapseBtn = document.querySelector('.sidebar-collapse-btn');
        collapseBtn?.addEventListener('click', () => {
            const isCollapsed = sidebar.classList.toggle('collapsed');
            Utils.setStorage(AppConfig.STORAGE.SIDEBAR_STATE, isCollapsed ? 'collapsed' : 'expanded');
        });

        // Active menu item
        this.setActiveMenuItem();
    },

    setActiveMenuItem() {
        const currentPath = window.location.pathname;
        document.querySelectorAll('.sidebar-nav .nav-item').forEach(item => {
            const href = item.getAttribute('href');
            if (href && currentPath.includes(href)) {
                item.classList.add('active');
                // Expand parent section if exists
                const section = item.closest('.nav-section');
                section?.classList.add('expanded');
            }
        });
    },

    // =====================================
    // Dropdown Menus
    // =====================================

    initDropdowns() {
        // Initialize Bootstrap dropdowns
        document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach(el => {
            new bootstrap.Dropdown(el);
        });
    },

    // =====================================
    // Data Tables
    // =====================================

    initDataTables() {
        document.querySelectorAll('.admin-table-wrapper').forEach(wrapper => {
            this.setupTableFilters(wrapper);
            this.setupTablePagination(wrapper);
            this.setupTableActions(wrapper);
        });
    },

    setupTableFilters(wrapper) {
        const filters = wrapper.querySelectorAll('.table-filter');
        const table = wrapper.querySelector('.admin-table');

        filters.forEach(filter => {
            filter.addEventListener('change', () => {
                // Trigger filter event
                const filterEvent = new CustomEvent('table:filter', {
                    detail: {
                        field: filter.dataset.field,
                        value: filter.value,
                    },
                });
                wrapper.dispatchEvent(filterEvent);
            });
        });

        // Search input
        const searchInput = wrapper.querySelector('.table-search');
        if (searchInput) {
            const debouncedSearch = Utils.debounce((value) => {
                const searchEvent = new CustomEvent('table:search', {
                    detail: { query: value },
                });
                wrapper.dispatchEvent(searchEvent);
            }, 300);

            searchInput.addEventListener('input', (e) => {
                debouncedSearch(e.target.value);
            });
        }
    },

    setupTablePagination(wrapper) {
        const pagination = wrapper.querySelector('.pagination');
        if (!pagination) return;

        pagination.addEventListener('click', (e) => {
            const pageLink = e.target.closest('.page-link');
            if (!pageLink) return;

            e.preventDefault();
            const page = pageLink.dataset.page;
            
            const pageEvent = new CustomEvent('table:page', {
                detail: { page: parseInt(page) },
            });
            wrapper.dispatchEvent(pageEvent);
        });
    },

    setupTableActions(wrapper) {
        // Bulk selection
        const selectAll = wrapper.querySelector('.select-all');
        const rowCheckboxes = wrapper.querySelectorAll('.row-checkbox');

        selectAll?.addEventListener('change', (e) => {
            rowCheckboxes.forEach(cb => {
                cb.checked = e.target.checked;
            });
            this.updateBulkActions(wrapper);
        });

        rowCheckboxes.forEach(cb => {
            cb.addEventListener('change', () => {
                this.updateBulkActions(wrapper);
            });
        });

        // Action buttons
        wrapper.querySelectorAll('[data-action]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = btn.dataset.action;
                const id = btn.closest('tr')?.dataset.id;
                
                this.handleTableAction(action, id, wrapper);
            });
        });
    },

    updateBulkActions(wrapper) {
        const checkedCount = wrapper.querySelectorAll('.row-checkbox:checked').length;
        const bulkActions = wrapper.querySelector('.bulk-actions');
        const selectedCount = wrapper.querySelector('.selected-count');

        if (bulkActions) {
            bulkActions.style.display = checkedCount > 0 ? 'flex' : 'none';
        }
        if (selectedCount) {
            selectedCount.textContent = checkedCount;
        }
    },

    async handleTableAction(action, id, wrapper) {
        switch (action) {
            case 'view':
                // Navigate to detail page
                window.location.href = `${wrapper.dataset.baseUrl}${id}/`;
                break;

            case 'edit':
                // Navigate to edit page
                window.location.href = `${wrapper.dataset.baseUrl}${id}/edit/`;
                break;

            case 'delete':
                const confirmed = await Utils.confirm(
                    'Bạn có chắc chắn muốn xóa mục này?',
                    { type: 'danger', confirmText: 'Xóa' }
                );
                if (confirmed) {
                    wrapper.dispatchEvent(new CustomEvent('table:delete', {
                        detail: { id },
                    }));
                }
                break;

            case 'toggle-status':
                wrapper.dispatchEvent(new CustomEvent('table:toggle-status', {
                    detail: { id },
                }));
                break;
        }
    },

    // =====================================
    // Charts
    // =====================================

    initCharts() {
        // Initialize charts if Chart.js is loaded
        if (typeof Chart === 'undefined') return;

        // Revenue Chart
        this.initRevenueChart();
        
        // Users Chart
        this.initUsersChart();
        
        // Skills Distribution
        this.initSkillsChart();
    },

    initRevenueChart() {
        const ctx = document.getElementById('revenueChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12'],
                datasets: [{
                    label: 'Doanh thu',
                    data: [],
                    borderColor: '#F47C26',
                    backgroundColor: 'rgba(244, 124, 38, 0.1)',
                    fill: true,
                    tension: 0.4,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: value => Utils.formatCurrency(value),
                        },
                    },
                },
            },
        });
    },

    initUsersChart() {
        const ctx = document.getElementById('usersChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN'],
                datasets: [{
                    label: 'Người dùng mới',
                    data: [],
                    backgroundColor: '#183B56',
                    borderRadius: 4,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                },
            },
        });
    },

    initSkillsChart() {
        const ctx = document.getElementById('skillsChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: AppConfig.SKILLS.map(s => s.label),
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#183B56',
                        '#F47C26',
                        '#28A745',
                        '#17A2B8',
                        '#6F42C1',
                        '#FFC107',
                    ],
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                },
            },
        });
    },

    // =====================================
    // Global Search
    // =====================================

    initSearch() {
        const searchInput = document.querySelector('.admin-search input');
        if (!searchInput) return;

        const debouncedSearch = Utils.debounce(async (query) => {
            if (query.length < 2) return;

            try {
                const results = await ApiClient.get('/admin/search/', { q: query });
                this.showSearchResults(results);
            } catch (error) {
                console.error('Search error:', error);
            }
        }, 300);

        searchInput.addEventListener('input', (e) => {
            debouncedSearch(e.target.value);
        });

        // Close results on click outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.admin-search')) {
                this.hideSearchResults();
            }
        });
    },

    showSearchResults(results) {
        let dropdown = document.querySelector('.search-results-dropdown');
        if (!dropdown) {
            dropdown = document.createElement('div');
            dropdown.className = 'search-results-dropdown';
            document.querySelector('.admin-search').appendChild(dropdown);
        }

        if (results.length === 0) {
            dropdown.innerHTML = '<div class="search-no-results">Không tìm thấy kết quả</div>';
        } else {
            dropdown.innerHTML = results.map(item => `
                <a href="${item.url}" class="search-result-item">
                    <i class="fas ${item.icon}"></i>
                    <div class="search-result-info">
                        <div class="search-result-title">${item.title}</div>
                        <div class="search-result-type">${item.type}</div>
                    </div>
                </a>
            `).join('');
        }

        dropdown.classList.add('show');
    },

    hideSearchResults() {
        document.querySelector('.search-results-dropdown')?.classList.remove('show');
    },

    // =====================================
    // Quick Actions
    // =====================================

    async exportData(format = 'excel') {
        try {
            Utils.showToast('Đang xuất dữ liệu...', 'info');
            const response = await ApiClient.get(`/admin/export/?format=${format}`);
            // Handle file download
            window.location.href = response.download_url;
        } catch (error) {
            Utils.showToast('Lỗi khi xuất dữ liệu', 'error');
        }
    },

    async refreshStats() {
        try {
            const stats = await ApiClient.get('/admin/stats/');
            this.updateStatCards(stats);
        } catch (error) {
            console.error('Error refreshing stats:', error);
        }
    },

    updateStatCards(stats) {
        Object.entries(stats).forEach(([key, value]) => {
            const card = document.querySelector(`[data-stat="${key}"]`);
            if (card) {
                const valueEl = card.querySelector('.stat-value');
                if (valueEl) {
                    valueEl.textContent = Utils.formatNumber(value.current);
                }
                const changeEl = card.querySelector('.stat-change');
                if (changeEl && value.change !== undefined) {
                    changeEl.textContent = `${value.change > 0 ? '+' : ''}${value.change}%`;
                    changeEl.className = `stat-change ${value.change >= 0 ? 'positive' : 'negative'}`;
                }
            }
        });
    },
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize on admin pages
    if (document.body.classList.contains('admin-page')) {
        AdminPanel.init();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdminPanel;
}
