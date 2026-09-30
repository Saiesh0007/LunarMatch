# LunarMatch Frontend Setup Guide

This guide helps you spin up the new React Workstation frontend correctly.

## 1. Prerequisites
- Node.js (v18, v20, or v22 recommended)
- `npm` or `pnpm`

## 2. Installation
Navigating into the frontend directory:
```bash
cd frontend
npm install
```

## 3. Running the Development Server
```bash
npm run dev
```
By default, the Vite server will boot up and provide a URL (usually `http://localhost:3000` or `3001`). **Click the URL in your terminal to view the interactive application.**

*Note: Do not render the static HTML prototypes from the `stitch_lunarmatch_frontend_application` folder, as they DO NOT have any interactive UI, image uploading, or React Router capabilities wired up.*

## 4. Production Build
To create a minified artifact for deployment:
```bash
npm run build
```

The output will be found in the `/dist` directory.

## 5. API Connection
Currently, the UI pulls from the placeholder mock data providers inside `src/services/`. You will eventually switch out these Axios wrappers to hit the FastAPI backend located natively at `http://10.0.2.2:8000`. Set the `VITE_API_URL` environment variable properly in a `.env` file when executing the integration.
