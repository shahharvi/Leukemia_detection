document.addEventListener('DOMContentLoaded', function() {
  // Initial data load
  loadAnalyticsData();
  
  // Event listener for filter button
  document.getElementById('apply-filters').addEventListener('click', function() {
      loadAnalyticsData();
  });
  
  function loadAnalyticsData() {
      // Get filter values
      const dateRange = document.getElementById('date-range').value;
      const typeFilter = document.getElementById('type-filter').value;
      
      // Fetch data from the backend with filters
      fetch(`/api/analytics?date_range=${dateRange}&type=${typeFilter}`)
          .then(response => response.json())
          .then(data => {
              updateMetrics(data.metrics);
              renderCharts(data.charts);
          })
          .catch(error => {
              console.error('Error fetching analytics data:', error);
          });
  }
  
  function updateMetrics(metrics) {
      // Update metric values
      document.getElementById('total-cases').textContent = metrics.total_cases;
      document.getElementById('all-cases').textContent = metrics.all_cases;
      document.getElementById('aml-cases').textContent = metrics.aml_cases;
      document.getElementById('apl-cases').textContent = metrics.apl_cases;
  }
  
  function renderCharts(chartData) {
      // Monthly chart
      renderMonthlyChart(chartData.monthly);
      
      // Yearly chart
      renderYearlyChart(chartData.yearly);
      
      // Weekly chart
      renderWeeklyChart(chartData.weekly);
      
      // Type distribution chart
      renderTypeDistributionChart(chartData.type_distribution);
  }
  
  function renderMonthlyChart(data) {
      const ctx = document.getElementById('monthly-chart').getContext('2d');
      
      // Destroy existing chart if it exists
      if (window.monthlyChart) {
          window.monthlyChart.destroy();
      }
      
      // Create new chart
      window.monthlyChart = new Chart(ctx, {
          type: 'line',
          data: {
              labels: data.labels,
              datasets: [
                  {
                      label: 'ALL',
                      data: data.all,
                      borderColor: '#3366CC',
                      backgroundColor: 'rgba(51, 102, 204, 0.1)',
                      borderWidth: 2,
                      tension: 0.3,
                      fill: true
                  },
                  {
                      label: 'AML',
                      data: data.aml,
                      borderColor: '#DC3912',
                      backgroundColor: 'rgba(220, 57, 18, 0.1)',
                      borderWidth: 2,
                      tension: 0.3,
                      fill: true
                  },
                  {
                      label: 'APL',
                      data: data.apl,
                      borderColor: '#FF9900',
                      backgroundColor: 'rgba(255, 153, 0, 0.1)',
                      borderWidth: 2,
                      tension: 0.3,
                      fill: true
                  }
              ]
          },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                  legend: {
                      position: 'top',
                  },
                  tooltip: {
                      mode: 'index',
                      intersect: false,
                  }
              },
              scales: {
                  y: {
                      beginAtZero: true,
                      title: {
                          display: true,
                          text: 'Number of Cases'
                      }
                  },
                  x: {
                      title: {
                          display: true,
                          text: 'Month'
                      }
                  }
              }
          }
      });
  }
  
  function renderYearlyChart(data) {
      const ctx = document.getElementById('yearly-chart').getContext('2d');
      
      // Destroy existing chart if it exists
      if (window.yearlyChart) {
          window.yearlyChart.destroy();
      }
      
      // Create new chart
      window.yearlyChart = new Chart(ctx, {
          type: 'bar',
          data: {
              labels: data.labels,
              datasets: [
                  {
                      label: 'ALL',
                      data: data.all,
                      backgroundColor: 'rgba(51, 102, 204, 0.7)',
                  },
                  {
                      label: 'AML',
                      data: data.aml,
                      backgroundColor: 'rgba(220, 57, 18, 0.7)',
                  },
                  {
                      label: 'APL',
                      data: data.apl,
                      backgroundColor: 'rgba(255, 153, 0, 0.7)',
                  }
              ]
          },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                  legend: {
                      position: 'top',
                  },
                  tooltip: {
                      mode: 'index',
                      intersect: false,
                  }
              },
              scales: {
                  y: {
                      beginAtZero: true,
                      title: {
                          display: true,
                          text: 'Number of Cases'
                      }
                  },
                  x: {
                      title: {
                          display: true,
                          text: 'Year'
                      }
                  }
              }
          }
      });
  }
  
  function renderWeeklyChart(data) {
      const ctx = document.getElementById('weekly-chart').getContext('2d');
      
      // Destroy existing chart if it exists
      if (window.weeklyChart) {
          window.weeklyChart.destroy();
      }
      
      // Create new chart
      window.weeklyChart = new Chart(ctx, {
          type: 'line',
          data: {
              labels: data.labels,
              datasets: [
                  {
                      label: 'ALL',
                      data: data.all,
                      borderColor: '#3366CC',
                      borderWidth: 2,
                      pointRadius: 3,
                      pointBackgroundColor: '#3366CC'
                  },
                  {
                      label: 'AML',
                      data: data.aml,
                      borderColor: '#DC3912',
                      borderWidth: 2,
                      pointRadius: 3,
                      pointBackgroundColor: '#DC3912'
                  },
                  {
                      label: 'APL',
                      data: data.apl,
                      borderColor: '#FF9900',
                      borderWidth: 2,
                      pointRadius: 3,
                      pointBackgroundColor: '#FF9900'
                  }
              ]
          },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                  legend: {
                      position: 'top',
                  }
              },
              scales: {
                  y: {
                      beginAtZero: true,
                      title: {
                          display: true,
                          text: 'Number of Cases'
                      }
                  },
                  x: {
                      title: {
                          display: true,
                          text: 'Week'
                      }
                  }
              }
          }
      });
  }
  
  function renderTypeDistributionChart(data) {
      const ctx = document.getElementById('type-distribution-chart').getContext('2d');
      
      // Destroy existing chart if it exists
      if (window.typeDistributionChart) {
          window.typeDistributionChart.destroy();
      }
      
      // Create new chart
      window.typeDistributionChart = new Chart(ctx, {
          type: 'doughnut',
          data: {
              labels: ['ALL', 'AML', 'APL'],
              datasets: [{
                  data: [data.all, data.aml, data.apl],
                  backgroundColor: [
                      'rgba(51, 102, 204, 0.7)',
                      'rgba(220, 57, 18, 0.7)',
                      'rgba(255, 153, 0, 0.7)'
                  ],
                  borderWidth: 1
              }]
          },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                  legend: {
                      position: 'right',
                  },
                  tooltip: {
                      callbacks: {
                          label: function(context) {
                              const label = context.label || '';
                              const value = context.raw || 0;
                              const total = context.dataset.data.reduce((a, b) => a + b, 0);
                              const percentage = Math.round((value / total) * 100);
                              return `${label}: ${value} (${percentage}%)`;
                          }
                      }
                  }
              }
          }
      });
  }
});