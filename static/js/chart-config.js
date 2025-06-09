/**
 * Initialize radar charts for player comparison
 */
function initRadarCharts() {
    const radarChartContainers = document.querySelectorAll('.radar-chart-container');
    if (!radarChartContainers.length || typeof Chart === 'undefined') return;
    
    // Get player data from the page
    const player1Data = getPlayerStatsData('player1');
    const player2Data = getPlayerStatsData('player2');
    
    if (!player1Data || !player2Data) return;
    
    // Create radar chart for each container
    radarChartContainers.forEach(container => {
        const canvas = document.createElement('canvas');
        container.appendChild(canvas);
        
        const ctx = canvas.getContext('2d');
        
        new Chart(ctx, {
            type: 'radar',
            data: {
                labels: Object.keys(player1Data.stats).map(key => formatStatLabel(key)),
                datasets: [
                    {
                        label: player1Data.name,
                        data: Object.values(player1Data.stats),
                        backgroundColor: 'rgba(0, 180, 255, 0.2)',
                        borderColor: 'rgba(0, 180, 255, 1)',
                        pointBackgroundColor: 'rgba(0, 180, 255, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(0, 180, 255, 1)'
                    },
                    {
                        label: player2Data.name,
                        data: Object.values(player2Data.stats),
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(255, 99, 132, 1)'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        pointLabels: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-color'),
                            font: {
                                size: 12
                            }
                        },
                        ticks: {
                            backdropColor: 'transparent',
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-color')
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: getComputedStyle(document.documentElement).getPropertyValue('--text-color'),
                            font: {
                                size: 12
                            },
                            boxWidth: 30
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.raw}`;
                            }
                        }
                    }
                }
            }
        });
    });
}

/**
 * Extract player stats data from the DOM
 * @param {string} playerClass - Class identifier for the player (player1 or player2)
 * @returns {object|null} Player data object or null if not found
 */
function getPlayerStatsData(playerClass) {
    // Find player card element
    const playerCard = document.querySelector(`.${playerClass}-card`);
    if (!playerCard) return null;
    
    // Get player name
    const playerName = playerCard.querySelector('.player-name').textContent.trim();
    
    // Get all stat rows
    const statRows = playerCard.querySelectorAll('.stat-row');
    if (!statRows.length) return null;
    
    // Extract stats into an object
    const stats = {};
    statRows.forEach(row => {
        const label = row.querySelector('.stat-label').textContent.trim();
        const valueText = row.querySelector(`.${playerClass}-stat`).textContent.trim();
        const value = parseFloat(valueText);
        
        if (!isNaN(value)) {
            // Convert label to camelCase for object key
            const key = label.toLowerCase()
                .replace(/[^\w\s]/gi, '')
                .replace(/\s+(.)/g, (match, group) => group.toUpperCase())
                .replace(/\s/g, '')
                .replace(/^(.)/, (match, group) => group.toLowerCase());
            
            stats[key] = value;
        }
    });
    
    return {
        name: playerName,
        stats: stats
    };
}

/**
 * Format stat label for better display in chart
 * @param {string} key - Stat key in camelCase
 * @returns {string} Formatted label
 */
function formatStatLabel(key) {
    // Convert camelCase to space-separated words
    return key
        // Insert a space before all uppercase letters
        .replace(/([A-Z])/g, ' $1')
        // Convert first character to uppercase
        .replace(/^./, str => str.toUpperCase())
        // Trim any extra spaces
        .trim();
}

/**
 * Create bar charts for comparing specific stats
 * @param {string} containerId - ID of the container element for the chart
 * @param {string} stat - Name of the stat to compare
 * @param {object} player1 - First player data
 * @param {object} player2 - Second player data
 */
function createBarChart(containerId, stat, player1, player2) {
    const container = document.getElementById(containerId);
    if (!container || typeof Chart === 'undefined') return;
    
    const canvas = document.createElement('canvas');
    container.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    
    // Format stat display name
    const statDisplay = stat
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase())
        .trim();
    
    // Get the stat values
    const value1 = player1[stat] || 0;
    const value2 = player2[stat] || 0;
    
    // Create the chart
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: [player1.name, player2.name],
            datasets: [{
                label: statDisplay,
                data: [value1, value2],
                backgroundColor: [
                    'rgba(0, 180, 255, 0.7)',
                    'rgba(255, 99, 132, 0.7)'
                ],
                borderColor: [
                    'rgba(0, 180, 255, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-color')
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-color')
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-color')
                    }
                }
            }
        }
    });
}
