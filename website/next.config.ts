import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  output: 'standalone',
  outputFileTracingRoot: path.join(__dirname, './'),
  skipTrailingSlashRedirect: true,  // Don't auto-redirect trailing slashes - let middleware handle it
  eslint: {
    // Only run ESLint on these directories during production builds
    dirs: ['app'],
    // Ignore ESLint errors during production builds
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
