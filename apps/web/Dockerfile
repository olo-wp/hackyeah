# syntax=docker/dockerfile:1
FROM node:22-alpine AS build

WORKDIR /app
COPY package.json ./
COPY apps/web/package.json ./apps/web/
RUN --mount=type=secret,id=routeable_ca,required=false \
	if [ -s /run/secrets/routeable_ca ]; then export NODE_EXTRA_CA_CERTS=/run/secrets/routeable_ca; fi; \
	npm install

COPY apps/web ./apps/web
RUN --mount=type=secret,id=routeable_ca,required=false \
	if [ -s /run/secrets/routeable_ca ]; then export NODE_EXTRA_CA_CERTS=/run/secrets/routeable_ca; fi; \
	npm run build --workspace @routeable/web

FROM node:22-alpine AS runtime

WORKDIR /app
ENV NODE_ENV=production

COPY --from=build /app/apps/web/.next/standalone ./
COPY --from=build /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=build /app/apps/web/public ./apps/web/public

USER node
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
