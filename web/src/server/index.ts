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

server.server.on("request", (req, res) => {
  if (req.method === "OPTIONS") {
    res.writeHead(204, corsHeaders);
    res.end();
  }
});

server.listen(Number(process.env.PORT) || 3000, "0.0.0.0");
