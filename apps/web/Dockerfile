# syntax=docker/dockerfile:1
FROM node:22-alpine AS build

WORKDIR /app
COPY package.json ./
COPY apps/web/package.json ./apps/web/
ARG CACHE_BUSTER=none
RUN --mount=type=secret,id=routeable_ca,target=/tmp/routeable-ca.crt,required=false \
		if [ -s /tmp/routeable-ca.crt ]; then \
			NODE_EXTRA_CA_CERTS=/tmp/routeable-ca.crt npm install; \
		else \
			npm install; \
		fi

COPY apps/web ./apps/web
ARG ROUTEABLE_API_URL=http://api:3001
ARG NEXT_PUBLIC_MAPTILER_KEY
RUN --mount=type=secret,id=routeable_ca,target=/tmp/routeable-ca.crt,required=false \
		if [ -s /tmp/routeable-ca.crt ]; then \
			NODE_EXTRA_CA_CERTS=/tmp/routeable-ca.crt npm run build --workspace @routeable/web; \
		else \
			npm run build --workspace @routeable/web; \
		fi

FROM node:22-alpine AS runtime

WORKDIR /app
ENV NODE_ENV=production

COPY --from=build /app/apps/web/.next/standalone ./
COPY --from=build /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=build /app/apps/web/public ./apps/web/public

USER node
EXPOSE 3000
CMD ["node", "apps/web/server.js"]
