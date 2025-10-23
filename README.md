# ChatGPT MCP App - Minimal Standalone Version

This is a minimal standalone version extracted from your Gadget.dev ChatGPT app, containing only the custom business logic.

## What's Included

- **MCP Server**: Basic Model Context Protocol server for ChatGPT integration
- **HelloWorld Widget**: Your custom "Hello World JP Version" widget
- **Tool Registration**: `helloWorld` tool that ChatGPT can invoke

## What's NOT Included (from original Gadget app)

This minimal version does NOT include:
- OAuth 2.1 authentication system
- User management and sessions
- Database models (User, OAuth Client, OAuth Code, Session)
- Email verification system
- Password reset functionality
- Access control and permissions
- All UI components (shadcn/ui, Radix UI)
- React Router routes and layouts
- Vite build configuration
- Gadget platform integration

## Project Structure

```
chatgpt-mcp-app/
├── src/
│   ├── server/
│   │   └── index.js          # MCP server with Fastify
│   └── widgets/
│       └── HelloWorld.jsx    # Your custom widget component
├── package.json
├── .env.example
├── .gitignore
└── README.md
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd chatgpt-mcp-app
npm install
```

### 2. Start the Server

```bash
npm run dev
```

The server will start at `http://localhost:3000`

### 3. Test the MCP Endpoint

```bash
curl http://localhost:3000/health
```

### 4. Connect to ChatGPT

To connect this to ChatGPT:

1. **Enable Developer Mode** in ChatGPT
2. **Create a new connection** in ChatGPT
3. **Enter your MCP endpoint**: `http://localhost:3000/mcp`
4. **Test the tool**: Ask ChatGPT "Use my app to say hello!"

**Note**: For ChatGPT to access your local server, you'll need to:
- Use a tunneling service like [ngrok](https://ngrok.com/) or [localtunnel](https://localtunnel.github.io/www/)
- Or deploy to a public server

## Using ngrok for Local Development

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Start your server
npm run dev

# In another terminal, create a tunnel
ngrok http 3000

# Use the ngrok URL in ChatGPT
# Example: https://abc123.ngrok.io/mcp
```

## Customization

### Adding New Tools

Edit `src/server/index.js` and add more tools:

```javascript
mcpServer.registerTool(
  'myCustomTool',
  {
    title: 'My Custom Tool',
    description: 'Does something custom',
  },
  async () => {
    return {
      content: [
        {
          type: 'text',
          text: 'Custom response',
        },
      ],
    };
  }
);
```

### Adding New Widgets

1. Create a new widget in `src/widgets/`
2. Register it as a resource in `src/server/index.js`
3. Reference it in your tool's `_meta.openai/outputTemplate`

## What You'll Need to Add for Production

If you want to recreate the full Gadget app functionality:

1. **Authentication System**
   - OAuth 2.1 server implementation
   - User registration/login
   - Session management
   - JWT token handling

2. **Database**
   - PostgreSQL or similar
   - User model
   - OAuth models (Client, Code, Token)
   - Session model

3. **Email Service**
   - Email verification
   - Password reset emails
   - SMTP configuration

4. **Frontend Framework**
   - React Router or Remix
   - UI component library
   - State management

5. **Build System**
   - Vite configuration
   - Asset bundling
   - Environment variable management

6. **Deployment**
   - Production server setup
   - SSL certificates
   - Domain configuration
   - Environment management

## Resources

- [OpenAI Apps SDK](https://developers.openai.com/apps-sdk)
- [MCP Documentation](https://modelcontextprotocol.io/docs/getting-started/intro)
- [Fastify Documentation](https://fastify.dev/)

## License

This is a minimal extraction for development purposes. Original code from Gadget.dev template.
