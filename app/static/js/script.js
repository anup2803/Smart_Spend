// ===== Theme Toggle =====
function toggleTheme() {
    const body = document.body;
    const button = document.getElementById("themeToggle");

    let newTheme;
    if (body.classList.contains("light")) {
        body.classList.replace("light", "dark");
        newTheme = "dark";
        button.textContent = "☀️"; // sun icon
    } else {
        body.classList.replace("dark", "light");
        newTheme = "light";
        button.textContent = "🌙"; // moon icon
    }

    // Save to localStorage
    localStorage.setItem("theme", newTheme);

    // Save to backend (user-specific)
    fetch("/settings/theme", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ theme: newTheme }),
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme") || "light";
    document.body.classList.add(savedTheme);
    document.getElementById("themeToggle").textContent =
        savedTheme === "dark" ? "☀️" : "🌙";
});


// ===== Sidebar toggle =====
document.addEventListener("DOMContentLoaded", function() {
  const menuIcon = document.querySelector(".menu-icon");
  const sidebar = document.querySelector(".sidebar");
  const overlay = document.getElementById("overlay");

  menuIcon.addEventListener("click", function() {
    if (window.innerWidth <= 768) {
      // Mobile toggle
      sidebar.classList.toggle("active");
      overlay.classList.toggle("active");
    } else {
      // Desktop toggle
      sidebar.classList.toggle("hidden");
    }
  });

  overlay.addEventListener("click", function() {
    sidebar.classList.remove("active");
    overlay.classList.remove("active");
  });
});



// ===== Profile dropdown =====
const profileBtn = document.getElementById('profileBtn');
const profileDropdown = document.getElementById('profileDropdown');

profileBtn.addEventListener('click', () => {
    profileDropdown.style.display = profileDropdown.style.display === 'block' ? 'none' : 'block';
});

window.addEventListener('click', e => {
    if (!profileBtn.contains(e.target) && !profileDropdown.contains(e.target)) {
        profileDropdown.style.display = 'none';
    }
});



// ===== Line chart (all-time) =====
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
                    tension: 0.4
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
            plugins: { legend: { position: 'bottom' } },
            scales: { y: { beginAtZero: true } }
        }
    });
});


    

// ===== Get previous month correctly (1-12) =====
let today = new Date();
let prevMonth = today.getMonth(); // 0-11
let year = today.getFullYear();

if (prevMonth === 0) { // January
    prevMonth = 12;
    year -= 1;
} else {
    prevMonth = prevMonth; // 1-11
}
prevMonth += 1; // Convert to 1-12 for SQL


// ===== Expense Pie Chart =====
function drawExpensePie(data) {
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
}

fetch(`/expense_data?month=${prevMonth}&year=${year}`, { credentials: 'include' })
.then(res => res.json())
.then(data => {
    if (data.labels.length === 0) {
        // fallback to all-time data
        return fetch('/expense_data', { credentials: 'include' }).then(res => res.json());
    }
    return data;
})
.then(drawExpensePie);


// ===== Summary Bar Chart =====
function drawSummaryBar(data) {
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
}

fetch(`/summary_data?month=${prevMonth}&year=${year}`, { credentials: 'include' })
.then(res => res.json())
.then(data => {
    if (data.values.every(v => v === 0)) {
        // fallback to all-time summary
        return fetch('/summary_data', { credentials: 'include' }).then(res => res.json());
    }
    return data;
})
.then(drawSummaryBar);





// for delete the transactions 

const deleteButtons = document.querySelectorAll('.delete-btn');

deleteButtons.forEach(button => {
    button.addEventListener('click', function(event) {
        // Show confirmation dialog
        const confirmDelete = confirm("Are you sure you want to delete this transaction?");
        if (!confirmDelete) {
            // Prevent form submission if user clicks "Cancel"
            event.preventDefault();
        }
    });
});


// FOR DELETE THE REMINDER

const deletereminder=document.querySelectorAll(".btn-danger_small-btn")

deletereminder.forEach(button=>{  
 button.addEventListener('click',function(event){
    const confirmdeletereminders=confirm("Are you sure you want to delete this ?");
    if (!confirmdeletereminders)
        {
        event.preventDefault();
        }
    });
});