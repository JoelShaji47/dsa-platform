import type { NextConfig } from "next";

// A placeholder or empty value (e.g. the `https://<your-render-service>...`
// template that ships in .env.local) must never become the proxy target —
// that turns every API call into a multi-second network timeout. Fall back to
// the local backend instead.
const rawBackend = process.env.BACKEND_API_URL?.trim();
const BACKEND_URL =
  !rawBackend || rawBackend.includes("<")
    ? "http://localhost:8000"
    : rawBackend.replace(/\/+$/, "");

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_URL}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
