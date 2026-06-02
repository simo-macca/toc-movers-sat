# OptiMove | SAT Logistics Frontend

A modern, interactive Vue 3 web application built to visualize and configure the "Movers" SAT problem. It connects to the FastAPI backend to generate optimal logistics plans using the `Glucose3` SAT solver.

## Features

- **Dynamic Configuration:** Configure Task 1 (movement) and Task 2 (movement and items) problems.
- **Advanced SAT Settings:** Exposes engine options like specific Goal Floors, Custom Mover Names, and Iterative Deepening timeouts vs. Fixed Time Horizons (T).
- **Building Visualizer:** A custom-built, interactive elevator-shaft visualizer that animates the output plan step-by-step.
- **Playback Controls:** Fully controllable simulation timeline with `1x`, `2x`, and `4x` playback speeds.
- **SAT Data Export:** 1-click downloads for raw `DIMACS CNF` constraints and `Variable Mapping` JSON for academic review.

## Architecture

This project uses a modern "Smart Parent / Dumb Child" component architecture to ensure code remains lightweight and maintainable:

- `App.vue` (Smart): Manages global state, handles API communication, and coordinates components.
- `ProblemSetup.vue` (Child): Handles the complex reactive form and payload building.
- `ResultsPanel.vue` (Child): Orchestrates the timeline, timer logic, and download handlers.
- `BuildingVisualizer.vue` (Child): Pure UI component responsible *only* for rendering the visual state of floors, movers, and items.
- `ActionLog.vue` (Child): Renders textual log outputs for the current simulation step.

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v16 or higher recommended)
- [npm](https://www.npmjs.com/)

### 1. Installation

Navigate into the frontend directory and install the required dependencies:

```bash
npm install
```

### 2. Environment Configuration

Create a `.env` file in the root of the `frontend/` directory to point to your FastAPI backend:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```

*(Note: If you omit this file, the app will safely default to localhost:8000).*

### 3. Running the Development Server

Start the Vite development server:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

### 4. Production Build

To compile and minify for production:

```bash
npm run build
```

This will generate a `dist/` directory containing static files ready to be served by any static hosting provider (Nginx, Vercel, Netlify, etc.).

## Tech Stack

- **Framework:** Vue 3 (Composition API, `<script setup>`)
- **Styling:** Tailwind CSS
- **Build Tool:** Vite
- **Icons/Visuals:** Custom SVG & Native DOM Elements (No heavy 3D/Canvas libraries required)
