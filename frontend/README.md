# RAGaire — Frontend

A Next.js chat interface for the RAGaire Irish-language RAG assistant. Users can ask questions in English or Irish and receive answers sourced from a corpus of Irish-language documents, with expandable source snippets shown alongside each response.

## Stack

- **Next.js 14** (App Router)
- **Tailwind CSS** for styling
- **react-markdown** for rendering assistant responses
- Connects to the **FastAPI backend** via `NEXT_PUBLIC_API_URL`

## Getting Started

Copy the environment file and set the backend URL:

```bash
cp .env.local.example .env.local
```

Install dependencies and run the development server:

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser. The backend must be running at the URL configured in `.env.local` (default: `http://localhost:8000`).

## Environment Variables


| Variable              | Description                                         | Default                 |
| --------------------- | --------------------------------------------------- | ----------------------- |
| `NEXT_PUBLIC_API_URL` | Base URL of the FastAPI backend (no trailing slash) | `http://localhost:8000` |


## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx      # Root layout with fonts and metadata
│   ├── page.tsx        # Entry page, renders ChatWindow
│   └── globals.css     # Global styles
└── components/
    └── ChatWindow.tsx  # Main chat UI component
```

## Building for Production

```bash
npm run build
npm run start
```

