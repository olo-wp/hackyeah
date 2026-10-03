/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: "standalone",
  webpack(config) {
    config.module.rules.push({
      test: /maplibre-gl-(worker|shared)\.mjs$/,
      resourceQuery: /maplibre-worker-asset/,
      type: "asset/resource",
      generator: { filename: "static/media/[name][ext]" }
    });
    return config;
  },
  async rewrites() {
    return [{
      source: "/route-api/:path*",
      destination: `${(process.env.ROUTEABLE_API_URL ?? "http://localhost:3001").replace(/\/$/, "")}/api/routes/:path*`
    }];
  }
};

export default nextConfig;
