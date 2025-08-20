FROM node:18-alpine AS builder

ARG VITE_API_URL
ARG VITE_COUNTRY
ARG VITE_LOCALE
ARG VITE_GDPR_MODE

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_COUNTRY=$VITE_COUNTRY
ENV VITE_LOCALE=$VITE_LOCALE
ENV VITE_GDPR_MODE=$VITE_GDPR_MODE

WORKDIR /app

COPY package*.json ./
RUN npm ci --legacy-peer-deps

COPY . .

RUN npm run build

FROM nginx:alpine AS production
COPY --from=builder /app/dist /usr/share/nginx/html
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]