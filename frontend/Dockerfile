
FROM node:24-alpine

WORKDIR /app

# Copy dependencies
COPY package*.json ./

# Install React dependencies
RUN npm ci

# Copy frontend files
COPY . .

EXPOSE 5173

# Start React development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

