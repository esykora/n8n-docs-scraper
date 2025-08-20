# n8n API Toolkit for MCP Server & AI Agents

## Overview

This toolkit provides a complete set of HTTP Request nodes configured to interact with the n8n API. These nodes can be used as tool actions for:
- **MCP Server Integration**: Connect to Model Context Protocol servers
- **n8n AI Agents**: Provide agents with workflow management capabilities
- **Automation**: Build meta-workflows that manage other workflows

## 🚀 Quick Start

### 1. Import the Workflow

1. Copy the content from `n8n-api-toolkit-workflow.json`
2. In n8n, go to **Workflows** → **Import from File**
3. Paste the JSON and import

### 2. Set Up Environment Variables

Add these to your n8n instance:
```bash
N8N_API_URL=https://your-n8n-instance.com/api/v1
N8N_API_KEY=your-api-key-here
```

### 3. Get Your API Key

1. Go to n8n **Settings** → **API**
2. Click **Create API Key**
3. Copy the key (you won't see it again!)
4. Add it as an environment variable

## 📊 Available API Operations

### Workflow Management

| Action | HTTP Method | Endpoint | Description |
|--------|------------|----------|-------------|
| `list` | GET | `/workflows` | List all workflows |
| `search` | GET | `/workflows?search=` | Search workflows by name |
| `read` | GET | `/workflows/{id}` | Get specific workflow |
| `create` | POST | `/workflows` | Create new workflow |
| `update` | PATCH | `/workflows/{id}` | Update existing workflow |
| `delete` | DELETE | `/workflows/{id}` | Delete workflow |

### Workflow Execution

| Action | HTTP Method | Endpoint | Description |
|--------|------------|----------|-------------|
| `execute` | POST | `/workflows/{id}/execute` | Run a workflow |
| `activate` | PATCH | `/workflows/{id}/activate` | Activate workflow |
| `deactivate` | PATCH | `/workflows/{id}/deactivate` | Deactivate workflow |

### Execution History

| Action | HTTP Method | Endpoint | Description |
|--------|------------|----------|-------------|
| `list-executions` | GET | `/executions` | List executions |
| `get-execution` | GET | `/executions/{id}` | Get execution details |

## 💡 Usage Examples

### Example 1: List All Active Workflows
```json
{
  "action": "list",
  "active": true,
  "limit": 50
}
```

### Example 2: Search for Workflows
```json
{
  "action": "search",
  "searchQuery": "email automation",
  "limit": 10
}
```

### Example 3: Create a New Workflow
```json
{
  "action": "create",
  "workflowData": {
    "name": "My Automated Workflow",
    "nodes": [
      {
        "id": "node1",
        "name": "Start",
        "type": "n8n-nodes-base.start",
        "typeVersion": 1,
        "position": [250, 300]
      }
    ],
    "connections": {},
    "active": false,
    "settings": {
      "executionOrder": "v1"
    }
  }
}
```

### Example 4: Execute a Workflow with Data
```json
{
  "action": "execute",
  "workflowId": "workflow_123",
  "executionData": {
    "email": "user@example.com",
    "message": "Hello from API"
  }
}
```

### Example 5: Update Workflow Settings
```json
{
  "action": "update",
  "workflowId": "workflow_123",
  "workflowData": {
    "name": "Updated Workflow Name",
    "active": true,
    "settings": {
      "timezone": "America/New_York"
    }
  }
}
```

## 🤖 Integration with MCP Server

### Setup Steps:

1. **Replace the Manual Trigger** with an MCP Server Trigger node
2. **Configure MCP Server Connection**:
   ```json
   {
     "serverUrl": "http://localhost:3000",
     "apiKey": "mcp-server-key"
   }
   ```
3. **Map MCP Tool Calls** to the action router

### MCP Tool Definition:
```json
{
  "name": "n8n_workflow_manager",
  "description": "Manage n8n workflows via API",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["list", "search", "read", "create", "update", "delete", "execute", "activate", "deactivate"]
      },
      "workflowId": {
        "type": "string",
        "description": "ID of the workflow"
      },
      "searchQuery": {
        "type": "string",
        "description": "Search term for workflows"
      },
      "workflowData": {
        "type": "object",
        "description": "Workflow configuration"
      }
    },
    "required": ["action"]
  }
}
```

## 🧠 Integration with n8n AI Agents

### Setup for AI Agent:

1. **Add an Agent Node** instead of Manual Trigger
2. **Configure Agent Tools**:
   - Each HTTP Request node becomes a tool
   - The agent can call them based on user intent
3. **Add System Prompt**:
   ```
   You are an n8n workflow manager. You can:
   - List and search workflows
   - Create and update workflows
   - Execute workflows on demand
   - Manage workflow activation status
   ```

### Agent Tool Configuration:
```javascript
{
  tools: [
    {
      name: "List Workflows",
      description: "Get a list of all workflows",
      action: "list"
    },
    {
      name: "Execute Workflow",
      description: "Run a specific workflow",
      action: "execute",
      parameters: ["workflowId", "executionData"]
    }
    // ... more tools
  ]
}
```

## 🔧 Advanced Configuration

### Custom Headers
Add authentication or custom headers:
```javascript
{
  "X-Custom-Header": "value",
  "Authorization": "Bearer {{ $env.CUSTOM_TOKEN }}"
}
```

### Error Handling
Add an Error Trigger node to catch API errors:
```javascript
{
  "node": "Error Handler",
  "type": "n8n-nodes-base.errorTrigger",
  "handleErrors": ["list-workflows-node", "create-workflow-node"]
}
```

### Rate Limiting
Add delays between API calls:
```javascript
{
  "node": "Wait",
  "type": "n8n-nodes-base.wait",
  "waitTime": 1,
  "unit": "seconds"
}
```

## 📝 Response Format

All operations return a standardized response:

```json
{
  "action": "create",
  "success": true,
  "timestamp": "2024-01-01T12:00:00Z",
  "workflowId": "workflow_123",
  "message": "Workflow created successfully",
  "workflow": {
    // Full workflow object
  }
}
```

## 🔒 Security Best Practices

1. **API Key Storage**:
   - Never hardcode API keys
   - Use environment variables
   - Rotate keys regularly

2. **Access Control**:
   - Create separate API keys for different uses
   - Limit permissions per key
   - Monitor API usage

3. **Input Validation**:
   - Validate all input parameters
   - Sanitize workflow data
   - Check for injection attempts

## 🐛 Troubleshooting

### Common Issues:

1. **401 Unauthorized**:
   - Check API key is correct
   - Verify key has necessary permissions

2. **404 Not Found**:
   - Check workflow ID exists
   - Verify API URL is correct

3. **500 Server Error**:
   - Check workflow data format
   - Verify all required fields are present

### Debug Mode:
Enable verbose logging in HTTP Request nodes:
```json
{
  "options": {
    "timeout": 30000,
    "fullResponse": true,
    "ignoreResponseErrors": true
  }
}
```

## 📚 Additional Resources

- [n8n API Documentation](https://docs.n8n.io/api/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [n8n AI Agents Guide](https://docs.n8n.io/advanced-ai/)
- [HTTP Request Node Documentation](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)

## 💻 Example Use Cases

### 1. Workflow Backup System
Create automated backups of all workflows:
- List all workflows
- Export each as JSON
- Store in version control

### 2. Workflow Template System
Build a library of workflow templates:
- Create base workflows
- Clone and customize via API
- Deploy to different environments

### 3. Workflow Analytics
Track workflow performance:
- List executions
- Analyze success/failure rates
- Generate reports

### 4. Multi-Instance Management
Manage workflows across multiple n8n instances:
- Sync workflows between dev/prod
- Deploy updates programmatically
- Monitor all instances from one place

## 🚦 Rate Limits

Default n8n API rate limits:
- **Requests per minute**: 60
- **Requests per hour**: 600
- **Concurrent executions**: 10

Consider implementing:
- Request queuing
- Exponential backoff
- Caching for read operations

---

*This toolkit is part of the n8n Documentation Scraper project. For more information, visit the [GitHub repository](https://github.com/esykora/n8n-docs-scraper).*
