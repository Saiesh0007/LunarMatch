import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Pin the workspace root so a stray lockfile in a parent directory isn't picked up
  turbopack: {
    root: path.resolve(__dirname),
  },
};

export default nextConfig;
