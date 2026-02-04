# Setup Guide

## Google Calendar Integration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` to this directory
6. Run the agent - it will open browser for OAuth flow
7. Credentials saved to `token.pickle` for future use

## Email Configuration

Set environment variables:
```bash
export SMTP_SERVER=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
```

For Gmail, use [App Passwords](https://support.google.com/accounts/answer/185833).

## Zoom Integration (Optional)

Set environment variables:
```bash
export ZOOM_API_KEY=your_api_key
export ZOOM_API_SECRET=your_api_secret
```

Get credentials from [Zoom Marketplace](https://marketplace.zoom.us/).

## Quick Test

```bash
# Set API key
export ANTHROPIC_API_KEY=your_key

# Set email (minimum required)
export SMTP_USER=your-email@gmail.com
export SMTP_PASSWORD=your-app-password

# Run
python agent.py
```

The agent will use real integrations when configured, gracefully degrade otherwise.
