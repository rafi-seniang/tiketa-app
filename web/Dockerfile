# syntax=docker/dockerfile:1.7
FROM node:25-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
# Service addresses are baked into the bundle at build time (public, never a secret).
# Leave one empty to use its local port: the API on 8070, the chat agent on 8060.
ARG VITE_TIKETA_API_URL=
ARG VITE_TIKETA_AGENT_URL=
# The path the site is served under, with both slashes, such as /tiketa/. Empty serves it at the root.
ARG VITE_BASE_PATH=
ENV VITE_TIKETA_API_URL=${VITE_TIKETA_API_URL} VITE_TIKETA_AGENT_URL=${VITE_TIKETA_AGENT_URL}
ENV VITE_BASE_PATH=${VITE_BASE_PATH}
RUN npm run build

# Static files only: no Node at runtime, nginx runs as a non-root user on 8080.
FROM nginxinc/nginx-unprivileged:stable-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1
