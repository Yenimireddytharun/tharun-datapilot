FROM node:18-alpine
WORKDIR /app
COPY datapilot-ui/package*.json ./
RUN npm install
COPY datapilot-ui/ .

# FIXED: Use the API URL during build time
ARG NEXT_PUBLIC_API_URL=https://tharun-datapilot-api.onrender.com
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]