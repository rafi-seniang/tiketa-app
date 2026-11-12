// Generates TypeScript types from the OpenAPI schemas of the booking API and the chat agent.
// Run with both up: npm run api:types. The generated files are committed, so a build never needs a backend.
import { writeFileSync } from "node:fs";
import openapiTS, { astToString } from "openapi-typescript";

const services = [
  { name: "core", url: process.env.VITE_TIKETA_API_URL || "http://localhost:8070" },
  { name: "agent", url: process.env.VITE_TIKETA_AGENT_URL || "http://localhost:8060" },
];

for (const service of services) {
  const schemaUrl = new URL("/openapi.json", service.url);
  try {
    const types = astToString(await openapiTS(schemaUrl));
    const header =
      "/** Generated from the service's OpenAPI schema by scripts/generate-api-types.mjs. Do not edit. */\n";
    writeFileSync(new URL(`../src/api/generated/${service.name}.ts`, import.meta.url), header + types);
    console.log(`${service.name}: types written from ${schemaUrl}`);
  } catch (error) {
    console.error(`${service.name}: could not read ${schemaUrl} (${error.message}). Kept the committed types.`);
    process.exitCode = 1;
  }
}
