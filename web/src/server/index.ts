import { createHTTPServer } from "@trpc/server/adapters/standalone";
import { appRouter } from "./appRouter";

const corsOrigin = process.env.CLIENT_ORIGIN ?? "http://localhost:5173";

const corsHeaders = {
  "Access-Control-Allow-Origin": corsOrigin,
  "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
  "Access-Control-Allow-Headers": "content-type, x-trpc-source",
};

const server = createHTTPServer({
  router: appRouter,
  responseMeta() {
    return { headers: corsHeaders };
  },
});

// Handle OPTIONS preflight before tRPC processes the request
const [trpcHandler] = server.listeners("request");
server.removeAllListeners("request");
server.on("request", (req, res) => {
  if (req.method === "OPTIONS") {
    res.writeHead(204, corsHeaders);
    res.end();
  } else {
    trpcHandler(req, res);
  }
});

const port = Number(process.env.PORT) || 3000;

server.on("error", (err) => {
  console.error("Server failed to start:", err);
});

server.listen(port, "0.0.0.0", () => {
  console.log(`Server listening on 0.0.0.0:${port}`);
});
