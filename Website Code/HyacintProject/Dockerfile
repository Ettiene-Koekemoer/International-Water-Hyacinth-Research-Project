FROM node:lts-alpine AS build

WORKDIR /app
COPY . .

RUN npm install && npm run build


FROM nginx:alpine AS production

WORKDIR /app
COPY --from=build /app/dist /app
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 3000