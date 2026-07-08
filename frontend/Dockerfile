FROM node:20-alpine

WORKDIR /app

# Install deps first for layer caching.
COPY package.json ./
RUN npm install

# App source.
COPY . .

EXPOSE 5173

# Dev server, bound to 0.0.0.0 so it's reachable from the host.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
