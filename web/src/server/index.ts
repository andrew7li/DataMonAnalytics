import { createServer } from "http";
import { createHTTPHandler } from "@trpc/server/adapters/standalone";
import { appRouter } from "./appRouter";

const corsOrigin = process.env.CLIENT_ORIGIN ?? "http://localhost:5173";

const corsHeaders = {
  "Access-Control-Allow-Origin": corsOrigin,
  "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
  "Access-Control-Allow-Headers": "content-type, x-trpc-source",
};

const handler = createHTTPHandler({
  router: appRouter,
  responseMeta() {
    return { headers: corsHeaders };
  },
});

const server = createServer((req, res) => {
  if (req.method === "OPTIONS") {
    res.writeHead(204, corsHeaders);
    res.end();
    return;
  }
  handler(req, res);
});

server.listen(Number(process.env.PORT) || 3000, "0.0.0.0");
