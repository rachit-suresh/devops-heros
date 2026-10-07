FROM node:22-alpine AS build
WORKDIR /src
COPY package.json build.js ./
COPY public ./public
RUN npm run build

FROM nginx:1.27-alpine
RUN addgroup -S app && adduser -S app -G app
COPY --from=build /src/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN chown -R app:app /usr/share/nginx/html /var/cache/nginx /var/run && chmod -R u+rwX /var/cache/nginx
USER app
EXPOSE 80
