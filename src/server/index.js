import Fastify from 'fastify';
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';

const fastify = Fastify({ logger: true });

// Create MCP server
const createMCPServer = () => {
  const mcpServer = new McpServer({
    name: 'hello-world-mcp',
    version: '1.0.0',
  });

  // Register the HelloWorld widget as a resource
  mcpServer.registerResource(
    'widget-helloworld',
    'ui://widget/HelloWorld.html',
    {
      title: 'HelloWorld',
      description: 'ChatGPT widget for HelloWorld',
    },
    async () => {
      return {
        contents: [
          {
            uri: 'ui://widget/HelloWorld.html',
            mimeType: 'text/html+skybridge',
            text: `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {
      font-family: system-ui, -apple-system, sans-serif;
      padding: 20px;
      margin: 0;
    }
    h1 {
      color: #333;
    }
  </style>
</head>
<body>
  <div>
    <h1>Hello World JP Version</h1>
  </div>
</body>
</html>
            `,
          },
        ],
      };
    }
  );

  // Register the helloWorld tool
  mcpServer.registerTool(
    'helloWorld',
    {
      title: 'hello world',
      description: 'display a hello world message',
      annotations: { readOnlyHint: true },
      _meta: {
        'openai/outputTemplate': 'ui://widget/HelloWorld.html',
      },
    },
    async () => {
      return {
        structuredContent: {},
        content: [
          {
            type: 'text',
            text: 'Hello World JP Version',
          },
        ],
      };
    }
  );

  return mcpServer;
};

// MCP endpoint
fastify.all('/mcp', async (request, reply) => {
  const transport = new StreamableHTTPServerTransport({
    sessionIdGenerator: undefined,
    enableJsonResponse: true,
  });

  const server = createMCPServer();

  // Prevent Fastify from sending its own response
  reply.hijack();

  try {
    await server.connect(transport);
    await transport.handleRequest(request.raw, reply.raw, request.body);
  } catch (error) {
    console.error('Failed to start MCP session', error);
    if (!reply.raw.headersSent) {
      reply.raw.writeHead(500).end('Failed to establish MCP connection');
    }
  }
});

// Health check endpoint
fastify.get('/health', async () => {
  return { status: 'ok' };
});

// Start server
const start = async () => {
  try {
    await fastify.listen({ port: 3000, host: '0.0.0.0' });
    console.log('Server running at http://localhost:3000');
    console.log('MCP endpoint: http://localhost:3000/mcp');
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();
