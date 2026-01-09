# Multi-stage build for Focus Agent Frontend
FROM node:20-alpine as base

WORKDIR /app

# Copy package files
COPY package*.json ./

# Development stage
FROM base as development

# Install all dependencies (including dev)
RUN npm install

# Copy source code
COPY . .

EXPOSE 3000

# Development server with hot reload
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Build stage
FROM base as build

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build for production
ARG VITE_API_URL=http://192.168.0.18:30085
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Production stage
FROM nginx:alpine as production

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
