FROM node:18-alpine

WORKDIR /app

# Fix: Path must match your local structure
COPY datapilot-ui/package.json datapilot-ui/package-lock.json* ./
RUN npm install

COPY datapilot-ui/ .

# CRITICAL: This "bakes" the URL into the code during build
ARG NEXT_PUBLIC_API_URL=https://tharun-datapilot.onrender.com
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]