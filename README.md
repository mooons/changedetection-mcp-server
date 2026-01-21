# changedetection-mcp-server

> Production-ready MCP server for changedetection.io API - Monitor website changes through Model Context Protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A Model Context Protocol (MCP) server that provides seamless integration with [changedetection.io](https://changedetection.io/) for monitoring website changes. This server enables AI assistants and LLMs to interact with your changedetection.io instance to create, manage, and monitor website watches.

## 🌟 Features

- **Complete API Coverage**: Full support for changedetection.io API operations
- **Easy Setup**: Simple configuration with environment variables
- **Production Ready**: Built with error handling and logging
- **Type Safe**: Fully typed Python implementation
- **Async Operations**: Non-blocking async/await architecture
- **Vercel Compatible**: Ready for serverless deployment

## 🚀 Available Tools

| Tool | Description |
|------|-------------|
| `list_watches` | List all configured website watches |
| `get_watch` | Get detailed information about a specific watch |
| `create_watch` | Create a new watch to monitor a website |
| `delete_watch` | Delete a watch and stop monitoring |
| `trigger_check` | Manually trigger a change detection check |
| `get_history` | Get the history of detected changes |
| `system_info` | Get system information about the instance |

## 📋 Prerequisites

- Python 3.10 or higher
- A running [changedetection.io](https://changedetection.io/) instance
- API key from your changedetection.io instance

## 🔧 Installation

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/patrickcarmichael/changedetection-mcp-server.git
   cd changedetection-mcp-server
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your changedetection.io URL and API key
   ```

4. **Run the server**
   ```bash
   python server.py
   ```

### Using pip

```bash
pip install changedetection-mcp-server
```

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
CHANGEDETECTION_URL=http://localhost:5000
CHANGEDETECTION_API_KEY=your-api-key-here
```

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|--------|
| `CHANGEDETECTION_URL` | URL of your changedetection.io instance | Yes | `http://localhost:5000` |
| `CHANGEDETECTION_API_KEY` | API key for authentication | Yes | - |

### Getting Your API Key

1. Open your changedetection.io instance
2. Navigate to **Settings** → **API**
3. Generate or copy your API key
4. Add it to your `.env` file

## 🎯 Usage Examples

### With Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "changedetection": {
      "command": "python",
      "args": ["/path/to/changedetection-mcp-server/server.py"],
      "env": {
        "CHANGEDETECTION_URL": "http://localhost:5000",
        "CHANGEDETECTION_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### With uvx (run directly from GitHub)

You can also run this server via `uvx` without manually cloning the repo. Add to your
MCP client configuration:

```json
{
  "mcpServers": {
    "changedetection": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/mooons/changedetection-mcp-server@main",
        "changedetection-mcp-server"
      ],
      "env": {
        "CHANGEDETECTION_URL": "http://localhost:5000",
        "CHANGEDETECTION_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Example Interactions

**List all watches:**
```
Show me all my website watches
```

**Create a new watch:**
```
Monitor https://example.com for changes and tag it as "important"
```

**Check for changes:**
```
Trigger a check for watch ID abc-123
```

**View history:**
```
Show me the change history for watch abc-123
```

## 🚢 Deployment

### Vercel Deployment

This server is ready for deployment on Vercel:

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Deploy**
   ```bash
   vercel
   ```

3. **Set environment variables** in Vercel dashboard:
   - `CHANGEDETECTION_URL`
   - `CHANGEDETECTION_API_KEY`

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

CMD ["python", "server.py"]
```

Build and run:

```bash
docker build -t changedetection-mcp-server .
docker run -e CHANGEDETECTION_URL=http://localhost:5000 \
           -e CHANGEDETECTION_API_KEY=your-key \
           changedetection-mcp-server
```

## 🛠️ Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
ruff check .
```

### Project Structure

```
changedetection-mcp-server/
├── server.py              # Main MCP server implementation
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Package configuration
├── README.md             # This file
├── .env.example          # Environment template
├── .gitignore           # Git ignore rules
└── vercel.json          # Vercel configuration
```

## 📚 API Reference

### ChangeDetectionClient Methods

- `list_watches() -> dict`: Get all watches
- `get_watch(watch_id: str) -> dict`: Get specific watch details
- `create_watch(url: str, tag: Optional[str]) -> dict`: Create new watch
- `delete_watch(watch_id: str) -> dict`: Delete a watch
- `trigger_check(watch_id: str) -> dict`: Trigger manual check
- `get_history(watch_id: str) -> dict`: Get change history
- `system_info() -> dict`: Get system information

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [changedetection.io](https://changedetection.io/) - Official website
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP documentation
- [MCP Specification](https://spec.modelcontextprotocol.io/) - Protocol specification

## ⚠️ Troubleshooting

### Common Issues

**Connection Refused**
```
Error: Connection refused to http://localhost:5000
```
- Ensure changedetection.io is running
- Verify the URL in your `.env` file
- Check firewall settings

**Authentication Failed**
```
Error: 401 Unauthorized
```
- Verify your API key is correct
- Regenerate API key in changedetection.io settings

**Module Not Found**
```
ModuleNotFoundError: No module named 'mcp'
```
- Run `pip install -r requirements.txt`

## 📞 Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/patrickcarmichael/changedetection-mcp-server/issues)
- Check existing issues for solutions

## 🙏 Acknowledgments

- [changedetection.io](https://changedetection.io/) team for the excellent monitoring tool
- [Anthropic](https://www.anthropic.com/) for the Model Context Protocol
- All contributors to this project

---

Made with ❤️ by Patrick Carmichael
