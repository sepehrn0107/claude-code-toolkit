# Stitch MCP Setup

Connect IDEs and CLIs to [Google Stitch](https://stitch.withgoogle.com) using the Model Context Protocol.

Stitch is a **Remote MCP server** (lives in the cloud, not local). It requires authentication before an AI agent can modify your designs.

---

## Authentication Methods

### API Key (recommended for most cases)

1. Go to Stitch Settings → API Keys → **Create API Key**
2. Copy and store securely (never commit to a repo)

**Claude Code:**
```bash
claude mcp add stitch --transport http https://stitch.googleapis.com/mcp --header "X-Goog-Api-Key: YOUR-API-KEY" -s user
```

**VSCode** (`~/.vscode/mcp.json` or workspace `.vscode/mcp.json`):
```json
{
  "servers": {
    "stitch": {
      "url": "https://stitch.googleapis.com/mcp",
      "type": "http",
      "headers": {
        "Accept": "application/json",
        "X-Goog-Api-Key": "YOUR-API-KEY"
      }
    }
  }
}
```

---

### OAuth (for zero-trust / ephemeral environments)

Access tokens expire every ~1 hour. Refresh by re-running step 4.

**1. Install Google Cloud SDK**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**2. Authenticate (twice)**
```bash
gcloud auth login
gcloud auth application-default login
```

**3. Configure project & enable Stitch API**
```bash
PROJECT_ID="YOUR_PROJECT_ID"
gcloud config set project "$PROJECT_ID"
gcloud beta services mcp enable stitch.googleapis.com --project="$PROJECT_ID"

USER_EMAIL=$(gcloud config get-value account)
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="user:$USER_EMAIL" \
    --role="roles/serviceusage.serviceUsageConsumer" \
    --condition=None
```

**4. Generate access token**
```bash
TOKEN=$(gcloud auth application-default print-access-token)
echo "GOOGLE_CLOUD_PROJECT=$PROJECT_ID" > .env
echo "STITCH_ACCESS_TOKEN=$TOKEN" >> .env
```

**5. Add to Claude Code**
```bash
claude mcp add stitch \
  --transport http https://stitch.googleapis.com/mcp \
  --header "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  --header "X-Goog-User-Project: YOUR_PROJECT_ID" \
  -s user
# -s user  → saves to $HOME/.claude.json
# -s project → saves to ./.mcp.json
```

---

## Available MCP Tools

### Project Management
| Tool | Description |
|------|-------------|
| `list_projects` | List all active designs (`filter`: owned/shared) |
| `get_project` | Get details for a single project (`name`) |
| `create_project` | Create a new project (`title`) |

### Screen Management
| Tool | Description |
|------|-------------|
| `list_screens` | List all screens in a project (`projectId`) |
| `get_screen` | Get details for a single screen (`name`) |

### AI Generation
| Tool | Description |
|------|-------------|
| `generate_screen_from_text` | Create design from text prompt (`projectId`, `prompt`, `modelId`: GEMINI_3_FLASH or GEMINI_3_1_PRO) |
| `edit_screens` | Edit screens with a prompt (`projectId`, `selectedScreenIds[]`, `prompt`) |
| `generate_variants` | Generate design variants (`projectId`, `selectedScreenIds[]`, `prompt`, `variantOptions`) |

### Design Systems
| Tool | Description |
|------|-------------|
| `create_design_system` | Create design system with tokens (`designSystem`, optional `projectId`) |
| `update_design_system` | Update existing design system (`name`, `projectId`, `designSystem`) |
| `list_design_systems` | List design systems for a project (`projectId`) |
| `apply_design_system` | Apply design system to screens (`projectId`, `selectedScreenInstances[]`, `assetId`) |

---

## When to Use API Key vs OAuth

| | API Key | OAuth |
|---|---|---|
| Setup speed | Faster | Slower (~5 min) |
| Token expiry | Never (until revoked) | ~1 hour |
| Best for | Local dev machines | Zero-trust / CI / shared envs |
| Revocation | Manual (delete from Settings) | Instant via Settings |
