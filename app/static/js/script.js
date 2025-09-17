





// for the master side bar menu
document.addEventListener('DOMContentLoaded', function () {
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.getElementById('overlay');
  const menuIcon = document.querySelector('.menu-icon');
  const sidebarLinks = document.querySelectorAll('.sidebar a');

  // Toggle sidebar on ☰ click
  menuIcon.addEventListener('click', () => {
    sidebar.classList.toggle('active');
    overlay.classList.toggle('active');
  });

  // Close sidebar when clicking overlay
  overlay.addEventListener('click', () => {
    sidebar.classList.remove('active');
    overlay.classList.remove('active');
  });

  // Close sidebar after clicking a link (mobile)
  sidebarLinks.forEach(link => {
    link.addEventListener('click', () => {
      sidebar.classList.remove('active');
      overlay.classList.remove('active');
    });
  });
});







// fetch the data and show in the graph
fetch('/data')
.then(res => res.json())
.then(data => {
    const ctx = document.getElementById('myChart').getContext('2d');

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.months,
            datasets: [
                {
                    label: 'Expenses',
                    data: data.expenses,
                    borderColor: 'rgba(255, 0, 0, 0.8)',
                    backgroundColor: 'rgba(255, 0, 0, 0.3)',
                    fill: true,
                    tension: 0.4  // smooth curve
                },
                {
                    label: 'Income',
                    data: data.income,
                    borderColor: 'rgba(0, 200, 0, 0.8)',
                    backgroundColor: 'rgba(0, 200, 0, 0.3)',
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom' }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
});



// // toogle profile
const profileBtn = document.getElementById('profileBtn');
const profileDropdown = document.getElementById('profileDropdown');

profileBtn.addEventListener('click', () => {
    profileDropdown.style.display = profileDropdown.style.display === 'block' ? 'none' : 'block';
});

// Close dropdown if clicked outside
window.addEventListener('click', function(e) {
    if (!profileBtn.contains(e.target) && !profileDropdown.contains(e.target)) {
        profileDropdown.style.display = 'none';
    }
});



// for reports

fetch('/expense_data')
.then(response => response.json())
.then(data => {
    const ctx = document.getElementById('expensePie').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: [
                    "#ff6384", "#36a2eb", "#ffce56",
                    "#4bc0c0", "#9966ff", "#ff9f40"
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: "bottom" },
                title: { display: true, text: "Expenses by Category" }
            }
        }
    });
});



fetch('/summary_data')
.then(response => response.json())
.then(data => {
    const ctx = document.getElementById('summaryBar').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Amount (Rs)',
                data: data.values,
                backgroundColor: ['green', 'red', 'blue']
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: true, text: 'Income vs Expense vs Net Saving' }
            },
            scales: { y: { beginAtZero: true } }
        }
    });
});