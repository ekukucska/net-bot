// API configuration
const API_BASE_URL = "/v1";

// DOM elements
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const chatMessages = document.getElementById("chatMessages");
const statusElement = document.getElementById("status");
const connectionStatus = document.getElementById("connectionStatus");
const helpBtn = document.getElementById("helpBtn");
const themeToggle = document.getElementById("themeToggle");
const quickActionBtns = document.querySelectorAll(".quick-action-btn");

// Theme management
function initTheme() {
  const savedTheme = localStorage.getItem("netbot-theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme");
  const newTheme = currentTheme === "light" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("netbot-theme", newTheme);
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  // Initialize theme
  initTheme();

  // Focus input on load
  messageInput.focus();

  // Add event listeners
  chatForm.addEventListener("submit", handleSubmit);
  helpBtn.addEventListener("click", showHelp);
  themeToggle.addEventListener("click", toggleTheme);

  // Quick action buttons
  quickActionBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const command = btn.getAttribute("data-command");
      if (command) {
        messageInput.value = command;
        messageInput.focus();
        handleSubmit(new Event("submit"));
      }
    });
  });

  // Handle Enter key
  messageInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  });

  // Check connection
  checkConnection();
});

// Check API connection
async function checkConnection() {
  try {
    const response = await fetch("/health");
    if (response.ok) {
      connectionStatus.textContent = "Connected";
      connectionStatus.style.color = "var(--success-color)";
    } else {
      throw new Error("API not responding");
    }
  } catch (error) {
    connectionStatus.textContent = "Offline";
    connectionStatus.style.color = "var(--error-color)";
  }
}

// Handle form submission
async function handleSubmit(e) {
  e.preventDefault();

  const message = messageInput.value.trim();
  if (!message) return;

  // Add user message to chat
  addMessage(message, "user");

  // Clear input
  messageInput.value = "";

  // Disable input while processing
  setLoading(true);

  // Show typing indicator
  const typingId = addTypingIndicator();

  try {
    // Send message to API
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Remove typing indicator
    removeTypingIndicator(typingId);

    // Add bot response with enhanced formatting
    addBotMessage(data.message, data.status, data.data);

    // Update status
    updateStatus("Ready", "ready");
  } catch (error) {
    console.error("Error:", error);

    // Remove typing indicator
    removeTypingIndicator(typingId);

    // Show error message
    addMessage(
      "⚠️ Sorry, I encountered an error. Please make sure the server is running and try again.",
      "bot",
      "error"
    );

    updateStatus("Error connecting to server", "error");
    connectionStatus.textContent = "Connection Failed";
    connectionStatus.style.color = "var(--error-color)";
  } finally {
    setLoading(false);
    messageInput.focus();
  }
}

// Add simple message to chat
function addMessage(text, sender, status = "success") {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${sender}-message`;

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";

  if (sender === "user") {
    avatar.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
            </svg>
        `;
  } else {
    avatar.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 9.9-1"/>
            </svg>
        `;
  }

  const contentDiv = document.createElement("div");
  contentDiv.className = "message-content";

  const textDiv = document.createElement("div");
  textDiv.className = "message-text";

  // Convert markdown-style formatting
  const formattedText = formatMessage(text);
  textDiv.innerHTML = formattedText;

  const timeDiv = document.createElement("div");
  timeDiv.className = "message-time";
  timeDiv.textContent = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  contentDiv.appendChild(textDiv);
  contentDiv.appendChild(timeDiv);

  messageDiv.appendChild(avatar);
  messageDiv.appendChild(contentDiv);

  chatMessages.appendChild(messageDiv);
  scrollToBottom();
}

// Add enhanced bot message with data formatting
function addBotMessage(text, status, data) {
  const messageDiv = document.createElement("div");
  messageDiv.className = "message bot-message";

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 9.9-1"/>
        </svg>
    `;

  const contentDiv = document.createElement("div");
  contentDiv.className = "message-content";

  const textDiv = document.createElement("div");
  textDiv.className = "message-text";

  // Format the main message
  textDiv.innerHTML = formatMessage(text);

  // Add data visualization if available
  if (data && Object.keys(data).length > 0) {
    const dataDiv = formatData(data);
    if (dataDiv) {
      textDiv.appendChild(dataDiv);
    }
  }

  const timeDiv = document.createElement("div");
  timeDiv.className = "message-time";
  timeDiv.textContent = new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  contentDiv.appendChild(textDiv);
  contentDiv.appendChild(timeDiv);

  messageDiv.appendChild(avatar);
  messageDiv.appendChild(contentDiv);

  chatMessages.appendChild(messageDiv);
  scrollToBottom();
}

// Format message with markdown-like syntax
function formatMessage(text) {
  // Convert **bold** to <strong>
  text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // Convert line breaks
  text = text.replace(/\n/g, "<br>");

  // Highlight IP addresses
  text = text.replace(
    /\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b/g,
    "<code>$1</code>"
  );

  // Highlight ports
  text = text.replace(/\bport (\d+)\b/gi, "port <code>$1</code>");

  // Keep lists intact
  text = text.replace(/<br>• /g, "<br>• ");
  text = text.replace(/<br>🔹 /g, "<br>🔹 ");

  return text;
}

// Format technical data into visual components
function formatData(data) {
  if (!data || typeof data !== "object") return null;

  const container = document.createElement("div");
  container.style.marginTop = "12px";

  // If data has devices array (network scan)
  if (data.devices && Array.isArray(data.devices)) {
    const table = document.createElement("table");
    table.className = "data-table";

    const thead = document.createElement("thead");
    thead.innerHTML = `
            <tr>
                <th>IP Address</th>
                <th>MAC Address</th>
                <th>Status</th>
            </tr>
        `;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    data.devices.slice(0, 10).forEach((device) => {
      const row = document.createElement("tr");
      row.innerHTML = `
                <td><code>${device.ip || "N/A"}</code></td>
                <td><code>${device.mac || "N/A"}</code></td>
                <td><span class="status-badge ${device.status || "online"}">${
        device.status || "online"
      }</span></td>
            `;
      tbody.appendChild(row);
    });
    table.appendChild(tbody);

    container.appendChild(table);

    if (data.devices.length > 10) {
      const note = document.createElement("p");
      note.style.fontSize = "12px";
      note.style.color = "var(--text-secondary)";
      note.style.marginTop = "8px";
      note.textContent = `... and ${data.devices.length - 10} more devices`;
      container.appendChild(note);
    }
  }
  // If data has ports array
  else if (data.results && Array.isArray(data.results)) {
    const table = document.createElement("table");
    table.className = "data-table";

    const thead = document.createElement("thead");
    thead.innerHTML = `
            <tr>
                <th>Port</th>
                <th>Service</th>
                <th>Status</th>
            </tr>
        `;
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    data.results.forEach((port) => {
      const row = document.createElement("tr");
      const statusClass = port.open ? "online" : "offline";
      const statusText = port.open ? "Open" : "Closed";
      row.innerHTML = `
                <td><code>${port.port}</code></td>
                <td>${port.service || "Unknown"}</td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            `;
      tbody.appendChild(row);
    });
    table.appendChild(tbody);

    container.appendChild(table);
  }

  return container.children.length > 0 ? container : null;
}

// Add typing indicator
function addTypingIndicator() {
  const typingDiv = document.createElement("div");
  typingDiv.className = "message bot-message";
  typingDiv.id = "typing-indicator";

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 9.9-1"/>
        </svg>
    `;

  const contentDiv = document.createElement("div");
  contentDiv.className = "message-content";

  const indicatorDiv = document.createElement("div");
  indicatorDiv.className = "message-text";
  indicatorDiv.innerHTML = `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

  contentDiv.appendChild(indicatorDiv);
  typingDiv.appendChild(avatar);
  typingDiv.appendChild(contentDiv);

  chatMessages.appendChild(typingDiv);
  scrollToBottom();

  return "typing-indicator";
}

// Remove typing indicator
function removeTypingIndicator(id) {
  const indicator = document.getElementById(id);
  if (indicator) {
    indicator.remove();
  }
}

// Show help
async function showHelp() {
  setLoading(true);
  const typingId = addTypingIndicator();

  try {
    const response = await fetch(`${API_BASE_URL}/chat/help`);
    const data = await response.json();

    removeTypingIndicator(typingId);
    addMessage(data.message, "bot");
  } catch (error) {
    console.error("Error:", error);
    removeTypingIndicator(typingId);
    addMessage("Error loading help. Please try again.", "bot", "error");
  } finally {
    setLoading(false);
  }
}

// Set loading state
function setLoading(isLoading) {
  sendBtn.disabled = isLoading;
  messageInput.disabled = isLoading;

  const statusIndicator = document.querySelector(".status-indicator");
  if (isLoading) {
    updateStatus("Processing...", "loading");
    statusIndicator.classList.add("loading");
  } else {
    statusIndicator.classList.remove("loading");
  }
}

// Update status
function updateStatus(text, state = "ready") {
  statusElement.textContent = text;
  statusElement.className = state;
}

// Scroll to bottom
function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Auto-reconnect on page visibility change
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) {
    checkConnection();
    updateStatus("Ready", "ready");
  }
});

// Keyboard shortcuts
document.addEventListener("keydown", (e) => {
  // Ctrl/Cmd + K to focus input
  if ((e.ctrlKey || e.metaKey) && e.key === "k") {
    e.preventDefault();
    messageInput.focus();
  }

  // Ctrl/Cmd + D to toggle dark mode
  if ((e.ctrlKey || e.metaKey) && e.key === "d") {
    e.preventDefault();
    toggleTheme();
  }
});
