# n8n Cloud Authentication Guide for API Tools

## Overview
n8n Cloud handles authentication differently than self-hosted instances. This guide shows you how to properly authenticate the API tool nodes in your n8n Cloud instance.

## 🔐 Authentication Methods

### Method 1: API Key Authentication (Recommended for Cloud)

#### Step 1: Generate Your API Key

1. **Log into your n8n Cloud instance**
   - Go to: `https://[your-instance].app.n8n.cloud`

2. **Navigate to Settings**
   - Click your profile icon (bottom-left)
   - Select **Settings**

3. **Generate API Key**
   - Go to **API** section
   - Click **Create API Key**
   - Give it a descriptive name (e.g., "Workflow Management Tools")
   - **IMPORTANT**: Copy the key immediately - you won't see it again!

#### Step 2: Store the API Key Securely

**Option A: Environment Variables (Best Practice)**

In your n8n Cloud instance:
1. Go to **Settings** → **Variables**
2. Click **Add Variable**
3. Create these variables:
   ```
   Name: N8N_API_KEY
   Value: [your-api-key]
   Type: String
   
   Name: N8N_API_URL
   Value: https://[your-instance].app.n8n.cloud/api/v1
   Type: String
   ```

**Option B: Credentials (Alternative Method)**

1. Go to **Credentials** → **Add Credential**
2. Search for **Header Auth**
3. Configure:
   ```
   Name: n8n API Authentication
   Header Name: X-N8N-API-KEY
   Header Value: [your-api-key]
   ```

#### Step 3: Configure the Tool Nodes

Each tool node needs to be configured with authentication. Here's how:

**Using Environment Variables:**
```json
{
  "headerParameters": {
    "parameters": [
      {
        "name": "X-N8N-API-KEY",
        "value": "={{ $vars.N8N_API_KEY }}"
      }
    ]
  },
  "url": "={{ $vars.N8N_API_URL }}/workflows"
}
```

**Using Credentials:**
1. In each tool node, find the **Authentication** section
2. Select **Predefined Credential Type**
3. Choose **Header Auth**
4. Select your saved "n8n API Authentication" credential

### Method 2: OAuth2 Authentication (For Advanced Use Cases)

If your organization uses SSO or OAuth2:

1. **Set up OAuth2 Application**
   - Contact n8n support for OAuth2 client setup
   - You'll receive Client ID and Client Secret

2. **Create OAuth2 Credential**
   ```
   Type: OAuth2
   Grant Type: Client Credentials
   Access Token URL: https://[your-instance].app.n8n.cloud/oauth/token
   Client ID: [provided-by-n8n]
   Client Secret: [provided-by-n8n]
   Scope: workflows:read workflows:write executions:read
   ```

## 🛠️ Implementation in Tool Nodes

### Update Each Tool Node

Here's the corrected configuration for n8n Cloud:

```javascript
// For the List Workflows tool
{
  "parameters": {
    "name": "list_workflows",
    "description": "List all workflows in n8n",
    "method": "GET",
    "url": "={{ $vars.N8N_API_URL }}/workflows",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "X-N8N-API-KEY",
          "value": "={{ $vars.N8N_API_KEY }}"
        }
      ]
    }
  }
}
```

## 📋 Complete Setup Checklist

- [ ] Generate API key from n8n Cloud Settings
- [ ] Store API key in Variables or Credentials
- [ ] Store API URL in Variables
- [ ] Update all tool nodes with authentication
- [ ] Test with a simple list operation
- [ ] Verify error handling for invalid keys

## 🔍 Finding Your Cloud Instance Details

### Your API URL Format:
```
https://[your-instance-id].app.n8n.cloud/api/v1
```

### To find your instance ID:
1. Look at your n8n URL when logged in
2. The instance ID is the first part: `https://[THIS-PART].app.n8n.cloud`

### Example:
- Dashboard URL: `https://acme-corp.app.n8n.cloud`
- API URL: `https://acme-corp.app.n8n.cloud/api/v1`

## 🚨 Common Issues & Solutions

### Issue 1: 401 Unauthorized
**Cause**: Invalid or missing API key
**Solution**: 
- Verify the API key is correct
- Check it hasn't been revoked
- Ensure the X-N8N-API-KEY header is being sent

### Issue 2: 403 Forbidden
**Cause**: API key lacks necessary permissions
**Solution**: 
- Generate a new key with full permissions
- Check your n8n Cloud plan includes API access

### Issue 3: 404 Not Found
**Cause**: Incorrect API URL
**Solution**: 
- Verify your instance ID
- Ensure `/api/v1` is included in the URL
- Check the specific endpoint path

### Issue 4: CORS Errors
**Cause**: Making requests from browser/frontend
**Solution**: 
- API calls must be made from n8n workflows
- Cannot be called directly from browser JavaScript

## 🔒 Security Best Practices

1. **Never expose API keys in:**
   - Workflow descriptions
   - Public workflows
   - Git repositories
   - Client-side code

2. **Use Variables instead of hardcoding:**
   ```javascript
   // Good ✅
   "value": "={{ $vars.N8N_API_KEY }}"
   
   // Bad ❌
   "value": "n8n_api_key_abc123xyz"
   ```

3. **Rotate keys regularly:**
   - Set calendar reminder for monthly rotation
   - Delete old keys after creating new ones

4. **Use separate keys for different purposes:**
   - Development workflows
   - Production workflows
   - Testing and debugging

## 📝 Quick Test Workflow

After setting up authentication, test with this simple workflow:

```json
{
  "nodes": [
    {
      "parameters": {},
      "id": "trigger",
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "={{ $vars.N8N_API_URL }}/workflows",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "X-N8N-API-KEY",
              "value": "={{ $vars.N8N_API_KEY }}"
            }
          ]
        },
        "options": {
          "response": {
            "response": {
              "responseFormat": "json"
            }
          }
        }
      },
      "id": "test-api",
      "name": "Test API Access",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300]
    }
  ],
  "connections": {
    "Manual Trigger": {
      "main": [[{"node": "Test API Access", "type": "main", "index": 0}]]
    }
  }
}
```

## 🎯 Specific Configuration for AI Tools

When using with AI Agent nodes in n8n Cloud:

1. **Store credentials at the workflow level**
   - Each workflow can have its own API key
   - Useful for permission segregation

2. **Configure Agent System Prompt:**
   ```
   You have access to n8n API tools. 
   The authentication is already configured.
   You can list, create, update, and execute workflows.
   Always verify workflow IDs before operations.
   ```

3. **Environment Variables for Agents:**
   ```javascript
   // In the Agent node configuration
   {
     "systemMessage": "API URL: {{ $vars.N8N_API_URL }}",
     "options": {
       "temperature": 0.3,  // Lower for more consistent API calls
       "maxIterations": 10
     }
   }
   ```

## 📚 Additional Resources

- [n8n Cloud Documentation](https://docs.n8n.io/manage-cloud/)
- [API Authentication Docs](https://docs.n8n.io/api/authentication/)
- [n8n Cloud Variables](https://docs.n8n.io/code/variables/)
- [Security Best Practices](https://docs.n8n.io/hosting/security/)

## 💡 Pro Tips

1. **Use Variables for easy updates:**
   - Change API key in one place
   - All workflows automatically use new key

2. **Test in Dev first:**
   - Create a separate dev instance
   - Test API operations there first

3. **Monitor API usage:**
   - Check Settings → API for usage stats
   - Set up alerts for unusual activity

4. **Backup your workflows:**
   - Use the API tools to export workflows
   - Store backups in version control

---

*Part of the n8n API Tools project. For more info: https://github.com/esykora/n8n-docs-scraper*
