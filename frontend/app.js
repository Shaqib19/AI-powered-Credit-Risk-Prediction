const API_URL = "https://credit-risk-api-fzpk.onrender.com";

// ================= TOKEN =================
function saveToken(token) {
  localStorage.setItem("token", token);
}
function getToken() {
  return localStorage.getItem("token");
}
function logout() {
  localStorage.removeItem("token");
  window.location.href = "index.html";
}
function protect() {
  if (!getToken()) window.location.href = "index.html";
}

// ================= LOGIN =================
function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  fetch(API_URL + "/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  })
    .then(res => res.json())
    .then(data => {
      if (!data.token) {
        alert("Invalid login");
        return;
      }
      saveToken(data.token);
      window.location.href = "dashboard.html";
    })
    .catch(() => alert("Login failed"));
}

// ================= REGISTER =================
function register() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  fetch(API_URL + "/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  })
    .then(() => {
      alert("Registered successfully!");
      window.location.href = "index.html";
    })
    .catch(() => alert("Registration failed"));
}

// ================= PREDICT =================
function predict() {
  const income = Number(document.getElementById("income").value);
  const loan = Number(document.getElementById("loan").value);
  const tenure = Number(document.getElementById("tenure").value);
  const score = Number(document.getElementById("score").value);

  if (
    isNaN(income) || income <= 0 ||
    isNaN(loan) || loan <= 0 ||
    isNaN(tenure) || tenure <= 0 ||
    isNaN(score) || score < 300
  ) {
    alert("Please enter valid numeric values");
    return;
  }

  fetch(API_URL + "/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": getToken()
    },
    body: JSON.stringify({
      income: income,
      credit_score: score,
      employment_type: "Salaried",
      loan_amount: loan,
      loan_tenure: tenure,
      past_default_history: 0
    })
  })
    .then(res => res.json())
    .then(data => {
      console.log("API RESPONSE:", data);

      // ✅ correct validation
      if (data.default_probability === undefined) {
        document.getElementById("risk").innerText = "API Error";
        document.getElementById("prob").innerText = "";
        return;
      }

      document.getElementById("risk").innerText = data.risk_category;
      document.getElementById("prob").innerText =
        (data.default_probability * 100).toFixed(2) + "% probability of default";
    })
    .catch(err => {
      console.error(err);
      document.getElementById("risk").innerText = "Network Error";
      document.getElementById("prob").innerText = "";
    });
}
