# Spinning Wheel Slot Selector

A web application featuring a spinning wheel that randomly selects from a list of slots, each with an image.

## Features

- Interactive spinning wheel with a centered spin button
- Random slot selection after spinning animation
- Placeholder images for each slot (replace with your own images)

## Getting Started

1. Install dependencies: `npm install`
2. Start the development server: `npm run dev`
3. Open http://localhost:5173 in your browser

## Building

Run `npm run build` to build the project for production.

## Customizing Slots

Edit the `slots` array in `src/App.jsx` to add your own slots with names and image URLs.

## Deployment: serving images from a self-hosted NUC

Slot images are bundled under `public/images` and served at `/images/...` by default. Point the app at a self-hosted image server by setting `VITE_IMAGE_BASE_URL` at build time.

On the NUC:

1. Point DNS at the NUC: create a CNAME `images.markbakker.work.gd`.
2. Forward inbound port 443 (and 80 for the ACME HTTP challenge) from the internet to the NUC.
3. Place the images folder at `/home/mark/srv/slotselector-images` on the NUC (mounted into the container at `/srv/slotselector-images`).
4. Start Caddy:

   ```sh
   docker compose -f deploy/docker-compose.yml up -d
   ```

Then build the app pointing at the image host:

```sh
VITE_IMAGE_BASE_URL=https://images.markbakker.work.gd npm run build
```

Without `VITE_IMAGE_BASE_URL` the app falls back to `/images`, so it keeps working fully locally.
