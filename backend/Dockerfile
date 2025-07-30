FROM node:18-alpine
LABEL authors="kevin"

RUN addgroup -g 1001 -S nodejs
RUN adduser -S backend -u 1001

WORKDIR /app

COPY . .

RUN npm ci --only=production && npm cache clean --force

RUN chown -R backend:nodejs /app
USER backend

EXPOSE 4000

ENV NODE_ENV=production

CMD ["npm", "start"]