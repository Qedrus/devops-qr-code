# Use the official Node.js 18 image based on Alpine Linux as the base image
FROM node:18-alpine AS base

# Set the working directory inside the container
WORKDIR /app

# Copy package manager files to the working directory
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./

# Install dependencies based on the detected lock file type
RUN \
    if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
    elif [ -f package-lock.json ]; then npm ci; \
    elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm i --frozen-lockfile; \
    else echo "lockfile not found." && exit 1; \
    fi

# Copy the rest of the application code to the working directory
COPY . .

# Build the application (assuming 'npm run build' is the build script)
RUN npm run build

# Expose port 3000 to the outside world
EXPOSE 3000

# Command to run the applications
CMD ["npm", "start"]
