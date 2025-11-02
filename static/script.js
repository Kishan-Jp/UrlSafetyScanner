const scanBtn = document.getElementById("scanBtn");
const statusEl = document.getElementById("status");
const reasonEl = document.getElementById("reason");
const scoreEl = document.getElementById("score");
const progressBar = document.getElementById("progressBar");

scanBtn.addEventListener("click", async () => {
  const url = document.getElementById("urlInput").value.trim();

  if (!url) {
    alert("Please enter a URL.");
    return;
  }

  // Reset UI
  statusEl.textContent = "Scanning...";
  statusEl.className = "";
  reasonEl.textContent = "Please wait...";
  scoreEl.textContent = "--";
  progressBar.style.width = "0%";

  // Animate progress bar
  setTimeout(() => progressBar.style.width = "100%", 50);

  try {
    const response = await fetch(`/check-url?url=${encodeURIComponent(url)}`);
    const data = await response.json();

    statusEl.textContent = data.status;
    reasonEl.textContent = data.reason;
    scoreEl.textContent = `${data.score}/100`;

    statusEl.className = data.status.toLowerCase(); // safe, risky, unsafe
    scoreEl.className = data.status.toLowerCase();

  } catch (error) {
    statusEl.textContent = "Error contacting server";
    reasonEl.textContent = error.message;
    progressBar.style.width = "0%";
  }
});
