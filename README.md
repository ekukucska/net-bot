# NetBot - Network Diagnostics Chatbot 🤖

A rule-based network diagnostics chatbot with a beautiful web interface. Built with Python, FastAPI, and vanilla JavaScript.

## Features ✨

- **Natural Language Interface**: Chat with the bot using plain English
- **Network Diagnostics**:
  - Ping devices
  - Scan local network (LAN)
  - Check open ports
  - DNS lookups
  - Traceroute
  - Get local IP and gateway information
- **Beautiful UI**: Modern, responsive chat interface
- **Action Logging**: SQLite database logs all actions
- **Windows 11 Optimized**: Uses Windows-compatible networking tools

## Requirements 📋

- Python 3.13+
- Windows 11
- Poetry (for dependency management)

## Installation 🚀

1. **Clone the repository**

   ```powershell
   git clone https://github.com/yourusername/netbot.git
   cd netbot
   ```

2. **Install dependencies with Poetry**

   ```powershell
   poetry install
   ```

3. **Activate the virtual environment**
   ```powershell
   poetry shell
   ```

## Running the Application 🏃

1. **Start the server**

   ```powershell
   cd app
   poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open your browser**
   Navigate to: [http://localhost:8000](http://localhost:8000)

3. **Start chatting!**
   Try commands like:
   - "ping 192.168.1.1"
   - "scan network"
   - "what's my IP address?"
   - "check ports on 192.168.1.10"
   - "lookup google.com"
   - "help"

## Example Commands 💬

| Command                              | What it does                               |
| ------------------------------------ | ------------------------------------------ |
| `ping 192.168.1.1`                   | Ping a device to check if it's online      |
| `scan network`                       | Discover all devices on your local network |
| `check ports on 192.168.1.10`        | Check common ports (22, 80, 443)           |
| `check ports 192.168.1.10 8080,3000` | Check specific ports                       |
| `what's my IP?`                      | Get your local IP address                  |
| `what's my gateway?`                 | Get your default gateway                   |
| `traceroute google.com`              | Trace the route to a host                  |
| `lookup google.com`                  | Perform DNS lookup                         |
| `help`                               | Show all available commands                |

## Project Structure 📁

```
netbot/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── static/                 # Web UI files
│   │   ├── index.html         # Main HTML page
│   │   ├── styles.css         # Styling
│   │   └── script.js          # Frontend logic
│   └── netbot/
│       ├── api/               # API endpoints
│       │   ├── api.py        # Router aggregation
│       │   └── endpoints/
│       │       ├── ping.py   # Ping endpoint
│       │       └── chat.py   # Chat endpoint
│       ├── core/             # Business logic
│       │   ├── chatbot.py   # Rule-based intent parsing
│       │   └── networking.py # Network diagnostic functions
│       ├── db/               # Database
│       │   ├── models.py    # SQLAlchemy models
│       │   └── crud.py      # Database operations
│       └── schemas/          # Pydantic models
│           └── chat.py      # Request/Response schemas
├── pyproject.toml            # Poetry dependencies
└── README.md                 # This file
```

## API Documentation 📚

Once the server is running, access the interactive API docs:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## How It Works 🔧

1. **User Input**: You type a natural language command in the chat interface
2. **Intent Parsing**: The chatbot uses regex patterns to identify your intent
3. **Action Execution**: The appropriate networking function is called
4. **Response Formatting**: Results are converted to friendly, human-readable text
5. **Database Logging**: The action is logged to SQLite for history tracking

## Security Notes 🔒

- **Local Use Only**: This app is designed for home/LAN diagnostics
- **No Authentication**: Not intended for production or remote access
- **Admin Rights**: Some features (like network scanning) may require elevated privileges
- **Firewall**: Windows Firewall may prompt for network access

## Troubleshooting 🔧

### Port Already in Use

```powershell
# Use a different port
cd app
poetry run uvicorn main:app --reload --port 8001
```

### Network Scan Returns Empty

```powershell
# Run PowerShell as Administrator
# The ARP cache may need to be populated first
ping 192.168.1.1  # Ping your gateway first
```

### Database Issues

```powershell
# Delete the database file and restart
Remove-Item netbot.db
```

## Development 🛠️

### Run Tests

```powershell
poetry run pytest
```

### Install Dev Dependencies

```powershell
poetry install --with dev
```

### Format Code

```powershell
poetry run black app/
```

## License 📄

Educational project for network diagnostics learning.

---

**Note**: This tool is for educational and diagnostic purposes only. Only use on networks you own or have permission to test.
