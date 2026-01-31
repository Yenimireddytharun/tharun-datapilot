FROM node:20

WORKDIR /app

# Copy package files
COPY datapilot-ui/package*.json ./

# Fresh install to ensure Linux binaries match
RUN npm install

# Copy frontend code
COPY datapilot-ui/ .

# FIXED: Correct spacing to avoid 'command not found'
RUN rm -rf .next

EXPOSE 3000

CMD ["npm", "run", "dev"]