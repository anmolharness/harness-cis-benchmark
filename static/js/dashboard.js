// Harness CIS Benchmark Dashboard - v1.0.1
console.log('✅ Dashboard JS v1.0.1 loaded');

let currentResults = null;
let categoryChart = null;
let statusChart = null;
let trendsChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ DOM loaded, initializing...');
    loadResults();

    const runBtn = document.getElementById('runScanBtn');
    const refreshBtn = document.getElementById('refreshBtn');

    if (runBtn) {
        runBtn.addEventListener('click', runNewScan);
        console.log('✅ Run scan button attached');
    }

    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadResults);
        console.log('✅ Refresh button attached');
    }

    // Setup filters
    document.getElementById('categoryFilter')?.addEventListener('change', applyFilters);
    document.getElementById('statusFilter')?.addEventListener('change', applyFilters);
    document.getElementById('levelFilter')?.addEventListener('change', applyFilters);
});

async function loadResults() {
    try {
        const response = await fetch('/api/results');
        if (response.ok) {
            const data = await response.json();
            currentResults = data.results;
            updateDashboard();
        } else {
            showMessage('No results available. Click "Run New Scan" to start.', 'info');
        }
    } catch (error) {
        showMessage('Failed to load results: ' + error.message, 'error');
    }
}

async function runNewScan() {
    console.log('🔄 Starting new scan...');

    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('dashboard').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');

    try {
        console.log('📡 Fetching /api/scan...');
        const response = await fetch('/api/scan');
        console.log('📥 Response status:', response.status);

        const data = await response.json();
        console.log('📊 Scan complete! Compliance:', data.compliance.percentage + '%');

        if (response.ok) {
            currentResults = data.results;

            // Update metrics
            document.getElementById('complianceScore').textContent = data.compliance.percentage + '%';
            document.getElementById('compliancePoints').textContent =
                `${data.compliance.passed_points} / ${data.compliance.total_points} points`;
            document.getElementById('passedChecks').textContent = data.compliance.passed_checks;
            document.getElementById('totalChecks').textContent = `out of ${data.compliance.total_checks}`;
            document.getElementById('failedChecks').textContent = data.compliance.failed_checks;

            const criticalFailures = data.results.filter(r => r.result === 'FAIL' && r.level === 3);
            document.getElementById('criticalFailures').textContent = `${criticalFailures.length} critical`;

            const date = new Date(data.timestamp);
            document.getElementById('lastScan').textContent = date.toLocaleTimeString();
            document.getElementById('scanStatus').textContent = date.toLocaleDateString();

            // Update charts
            updateCategoryChart(data.categories);
            updateStatusChart(data.compliance);

            // Update critical failures
            updateCriticalFailures(criticalFailures);

            // Update table
            updateChecksTable(data.results);

            // Populate category filter
            populateCategoryFilter(data.categories);

            // Load trends
            loadTrends();

            // Show dashboard
            console.log('✅ Dashboard updated successfully');
            document.getElementById('dashboard').classList.remove('hidden');
        } else {
            console.error('❌ Scan failed:', data.error);
            showMessage('Scan failed: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('❌ Exception during scan:', error);
        showMessage('Failed to run scan: ' + error.message, 'error');
    } finally {
        document.getElementById('loading').classList.add('hidden');
    }
}

async function updateDashboard() {
    if (!currentResults) return;

    const stats = await fetchStats();

    document.getElementById('complianceScore').textContent = stats.compliance.percentage + '%';
    document.getElementById('compliancePoints').textContent =
        `${stats.compliance.passed_points} / ${stats.compliance.total_points} points`;
    document.getElementById('passedChecks').textContent = stats.compliance.passed_checks;
    document.getElementById('totalChecks').textContent = `out of ${stats.compliance.total_checks}`;
    document.getElementById('failedChecks').textContent = stats.compliance.failed_checks;
    document.getElementById('criticalFailures').textContent =
        `${stats.critical_failures.length} critical`;

    if (stats.timestamp) {
        const date = new Date(stats.timestamp);
        document.getElementById('lastScan').textContent = date.toLocaleTimeString();
        document.getElementById('scanStatus').textContent = date.toLocaleDateString();
    }

    updateCategoryChart(stats.categories);
    updateStatusChart(stats.compliance);
    updateCriticalFailures(stats.critical_failures);
    updateChecksTable(currentResults);
    populateCategoryFilter(stats.categories);
    loadTrends();

    document.getElementById('dashboard').classList.remove('hidden');
}

async function fetchStats() {
    const response = await fetch('/api/stats');
    return await response.json();
}

function updateCategoryChart(categories) {
    const ctx = document.getElementById('categoryChart')?.getContext('2d');
    if (!ctx) return;

    if (categoryChart) categoryChart.destroy();

    const labels = Object.keys(categories);
    const data = labels.map(cat =>
        Math.round((categories[cat].points / categories[cat].max_points) * 100)
    );

    categoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Compliance %',
                data: data,
                backgroundColor: data.map(val =>
                    val >= 80 ? '#00c851' : val >= 60 ? '#ffbb33' : '#ff4444'
                )
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { callback: value => value + '%' }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: { afterLabel: () => 'Click to filter' }
                }
            },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    document.getElementById('categoryFilter').value = labels[elements[0].index];
                    applyFilters();
                    document.getElementById('checksTable')?.scrollIntoView({ behavior: 'smooth' });
                }
            },
            onHover: (event, elements) => {
                event.native.target.style.cursor = elements.length > 0 ? 'pointer' : 'default';
            }
        }
    });
}

function updateStatusChart(compliance) {
    const ctx = document.getElementById('statusChart')?.getContext('2d');
    if (!ctx) return;

    if (statusChart) statusChart.destroy();

    statusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Passed', 'Failed'],
            datasets: [{
                data: [compliance.passed_checks, compliance.failed_checks],
                backgroundColor: ['#00c851', '#ff4444']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'bottom' },
                tooltip: {
                    callbacks: { afterLabel: () => 'Click to filter' }
                }
            },
            onClick: (event, elements) => {
                if (elements.length > 0) {
                    const status = elements[0].index === 0 ? 'PASS' : 'FAIL';
                    document.getElementById('statusFilter').value = status;
                    applyFilters();
                    document.getElementById('checksTable')?.scrollIntoView({ behavior: 'smooth' });
                }
            },
            onHover: (event, elements) => {
                event.native.target.style.cursor = elements.length > 0 ? 'pointer' : 'default';
            }
        }
    });
}

function updateCriticalFailures(failures) {
    const container = document.getElementById('criticalFailuresList');
    if (!container) return;

    const section = document.getElementById('criticalSection');
    if (failures.length === 0) {
        section?.classList.add('hidden');
        return;
    }

    section?.classList.remove('hidden');
    container.innerHTML = failures.map(check => `
        <div class="critical-item">
            <h4>[${check.id}] ${check.description}</h4>
            <p>${check.details}</p>
        </div>
    `).join('');
}

function updateChecksTable(results) {
    const tbody = document.getElementById('checksTableBody');
    if (!tbody) return;

    tbody.innerHTML = results.map(check => {
        const isRemediated = check.remediated === true;
        const statusClass = isRemediated ? 'remediated' : check.result.toLowerCase();
        const statusText = isRemediated ? 'PASS' : check.result;
        const remediationBadge = isRemediated ? '<span class="remediation-badge">✓ REMEDIATED</span>' : '';

        return `
        <tr class="check-row ${isRemediated ? 'remediated-row' : ''}" data-check-id="${check.id}" onclick="toggleCheckDetails('${check.id}')">
            <td><strong>${check.id}</strong></td>
            <td><span class="level-badge level-${check.level}">Level ${check.level}</span></td>
            <td>${check.description}${remediationBadge}</td>
            <td><span class="status-badge status-${statusClass}">${statusText}</span></td>
            <td class="details-preview">${check.details.substring(0, 80)}${check.details.length > 80 ? '...' : ''}</td>
        </tr>
        <tr id="details-${check.id}" class="details-row hidden">
            <td colspan="5">
                <div class="details-content">
                    <h4>📋 Check Details</h4>
                    <p><strong>Finding:</strong> ${check.details}</p>
                    ${getRemediation(check)}
                    <button class="btn btn-primary" onclick="event.stopPropagation(); openCheckModal('${check.id}')">
                        View Full Details
                    </button>
                </div>
            </td>
        </tr>`;
    }).join('');
}

function toggleCheckDetails(checkId) {
    const detailsRow = document.getElementById(`details-${checkId}`);
    document.querySelectorAll('.details-row').forEach(row => {
        if (row.id !== `details-${checkId}`) row.classList.add('hidden');
    });
    detailsRow?.classList.toggle('hidden');
}

function getRemediation(check) {
    const remediations = {
        '1.1': 'Enable SSO in Account Settings → Authentication → Configure SAML/OAuth provider',
        '1.2': 'Enable 2FA in Account Settings → Authentication → Two-Factor Authentication',
        '1.3': 'Configure lockout policy in Account Settings → Authentication → Failed Login Attempts'
    };
    const remediation = remediations[check.id] || 'Refer to Harness documentation for remediation steps';
    return `
        <div class="remediation-box">
            <strong>🔧 Remediation:</strong>
            <p>${remediation}</p>
            <a href="https://docs.harness.io" target="_blank">View Harness Documentation →</a>
        </div>
    `;
}

function openCheckModal(checkId) {
    const check = currentResults?.find(c => c.id === checkId);
    if (!check) return;

    const modal = document.getElementById('checkModal');
    const modalContent = document.getElementById('modalCheckContent');

    modalContent.innerHTML = `
        <h2>[${check.id}] ${check.description}</h2>
        <div class="modal-badges">
            <span class="level-badge level-${check.level}">Level ${check.level}</span>
            <span class="status-badge status-${check.result.toLowerCase()}">${check.result}</span>
        </div>
        <div class="modal-section">
            <h3>📊 Finding</h3>
            <p>${check.details}</p>
        </div>
        ${getRemediation(check)}
    `;

    modal?.classList.remove('hidden');
}

function closeCheckModal() {
    document.getElementById('checkModal')?.classList.add('hidden');
}

window.onclick = function(event) {
    const modal = document.getElementById('checkModal');
    if (event.target === modal) closeCheckModal();
}

function populateCategoryFilter(categories) {
    const filter = document.getElementById('categoryFilter');
    if (!filter) return;

    const options = Object.keys(categories).map(cat =>
        `<option value="${cat}">${cat}</option>`
    ).join('');

    filter.innerHTML = '<option value="">All Categories</option>' + options;
}

function applyFilters() {
    if (!currentResults) return;

    const categoryFilter = document.getElementById('categoryFilter')?.value;
    const statusFilter = document.getElementById('statusFilter')?.value;
    const levelFilter = document.getElementById('levelFilter')?.value;

    const catMap = {
        '1': 'Authentication & Access', '2': 'RBAC & Authorization', '3': 'Secrets & Connectors',
        '4': 'Delegates', '5': 'Pipeline Best Practices', '6': 'Governance',
        '7': 'Cost & Resource Management', '8': 'Deployment Safety',
        '9': 'Monitoring & Alerts', '10': 'Resource Hygiene'
    };

    const filtered = currentResults.filter(check => {
        if (categoryFilter && catMap[check.id.split('.')[0]] !== categoryFilter) return false;
        if (statusFilter && check.result !== statusFilter) return false;
        if (levelFilter && check.level !== parseInt(levelFilter)) return false;
        return true;
    });

    updateChecksTable(filtered);
}

function showMessage(message, type) {
    const errorDiv = document.getElementById('error');
    if (!errorDiv) return;

    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');

    if (type === 'info') {
        errorDiv.style.background = '#e3f2fd';
        errorDiv.style.color = '#1565c0';
        errorDiv.style.border = '2px solid #1565c0';
    }
}

async function loadTrends() {
    try {
        const response = await fetch('/api/trends');
        if (!response.ok) return;

        const data = await response.json();
        if (!data.labels || data.labels.length < 2) {
            document.getElementById('trendsSection')?.classList.add('hidden');
            return;
        }

        document.getElementById('trendsSection')?.classList.remove('hidden');

        const ctx = document.getElementById('trendsChart')?.getContext('2d');
        if (!ctx) return;

        if (trendsChart) trendsChart.destroy();

        trendsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Compliance %',
                    data: data.compliance,
                    borderColor: '#0066cc',
                    backgroundColor: 'rgba(0, 102, 204, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: 'Compliance Trend Over Time' }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { callback: value => value + '%' }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Failed to load trends:', error);
    }
}

console.log('✅ Dashboard JS fully loaded');
