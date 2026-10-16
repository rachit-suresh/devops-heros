FROM node:22-alpine AS build
WORKDIR /src
COPY package.json build.js ./
COPY public ./public
RUN npm run build

FROM nginxinc/nginx-unprivileged:stable-alpine
COPY --from=build /src/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
USER 101
EXPOSE 8080
