// dashboard.js
document.addEventListener('DOMContentLoaded', function () {
  // Sidebar toggle (for small screens)
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.querySelector('.sidebar');
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.style.display = (sidebar.style.display === 'none' ? 'block' : 'none');
    });
  }

  // Theme toggle (dark / light) using localStorage
  const themeToggle = document.getElementById('themeToggle');
  function setTheme(theme) {
    if (theme === 'dark') {
      document.documentElement.classList.add('theme-dark');
      document.cookie = "theme=dark; path=/";
    } else {
      document.documentElement.classList.remove('theme-dark');
      document.cookie = "theme=; path=/; max-age=0";
    }
  }
  // initial theme from localStorage or cookie
  const initial = localStorage.getItem('theme') || (document.cookie.includes('theme=dark') ? 'dark' : 'light');
  setTheme(initial);
  if (themeToggle) themeToggle.addEventListener('click', () => {
    const now = (localStorage.getItem('theme') === 'dark') ? 'light' : 'dark';
    localStorage.setItem('theme', now);
    setTheme(now);
  });

  // Chart data from template (window.DASHBOARD)
  const dash = window.DASHBOARD || {};
  const lineCtx = document.getElementById('lineChart');
  if (lineCtx && dash.incomeLabels && dash.incomeValues) {
    new Chart(lineCtx.getContext('2d'), {
      type: 'line',
      data: {
        labels: dash.incomeLabels,
        datasets: [{
          label: 'Income',
          data: dash.incomeValues,
          borderColor: '#2c82f6',
          backgroundColor: 'rgba(44,130,246,0.08)',
          tension: 0.35,
          pointRadius: 3,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: '#f2f4f7' } }
        }
      }
    });
  }

  const donutCtx = document.getElementById('donutChart');
  if (donutCtx && dash.budgetLabels && dash.budgetValues) {
    new Chart(donutCtx.getContext('2d'), {
      type: 'doughnut',
      data: {
        labels: dash.budgetLabels,
        datasets: [{
          data: dash.budgetValues,
          backgroundColor: ['#2c82f6','#1cc88a','#f6c23e','#e74c3c','#6c5ce7'],
          borderWidth: 0
        }]
      },
      options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
    });
  }
});
