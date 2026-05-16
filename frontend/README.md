# React Frontend - Document Intelligence System

A modern React application built with Vite and TailwindCSS for the AI-powered Document Intelligence System.

## Features

- 📄 **Document Upload** - Drag-and-drop interface with progress tracking
- 📋 **Summarization** - Generate concise or detailed summaries using AI
- 💡 **Insights Extraction** - Extract key themes, action items, and insights
- 💬 **RAG Chat** - Ask questions about documents using retrieval-augmented generation
- 📊 **System Status** - Monitor backend health and statistics
- 🎨 **Modern UI** - Built with React 18, Vite, and TailwindCSS

## Tech Stack

- **React 18.2.0** - UI library
- **Vite 5.0.8** - Build tool and dev server
- **TailwindCSS 3.4.1** - Utility-first CSS framework
- **React Router 6.20.0** - Client-side routing
- **Axios 1.6.0** - HTTP client

## Setup

### Prerequisites

- Node.js 18+ 
- npm 8+

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and update the API URL if needed
# VITE_API_URL=http://localhost:8000
```

### Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

The Vite dev server includes:
- **Hot Module Replacement (HMR)** - Auto-reload on file changes
- **API Proxy** - Requests to `/api/*` are forwarded to `http://localhost:8000`

### Build

Create a production build:
```bash
npm run build
```

The build output will be in the `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Common.jsx       # Button, Card, Badge, LoadingSpinner, Alert
│   │   ├── Chat.jsx         # ChatMessage, ChatInput components
│   │   ├── DocumentCard.jsx # DocumentCard, DocumentGrid
│   │   ├── FileUploader.jsx # Drag-drop file upload
│   │   ├── Header.jsx       # Navigation header and footer
│   │   └── index.js         # Component exports
│   │
│   ├── pages/               # Page components
│   │   ├── UploadPage.jsx   # Document upload interface
│   │   ├── DashboardPage.jsx# Summary and insights
│   │   ├── ChatPage.jsx     # RAG chat interface
│   │   ├── StatusPage.jsx   # System health and stats
│   │   └── index.js         # Page exports
│   │
│   ├── layouts/             # Layout components
│   │   └── MainLayout.jsx   # Default layout with header/footer
│   │
│   ├── hooks/               # Custom React hooks
│   │   ├── useAsync.js      # Async operation handler
│   │   ├── useDocumentManager.js  # Document state management
│   │   └── index.js         # Hook exports
│   │
│   ├── services/            # API clients
│   │   ├── apiClient.js     # Axios instance with interceptors
│   │   └── documentService.js # API endpoints
│   │
│   ├── App.jsx              # Root component with routing
│   ├── main.jsx             # Application entry point
│   └── index.css            # Global styles and Tailwind directives
│
├── public/                  # Static assets
├── index.html               # HTML entry point
├── vite.config.js           # Vite configuration
├── tailwind.config.js       # TailwindCSS theme
├── postcss.config.js        # PostCSS plugins
└── package.json             # Dependencies and scripts
```

## API Endpoints

The frontend communicates with the following backend endpoints:

- `POST /upload` - Upload a document
- `POST /summary` - Generate summary (params: doc_id, summary_type)
- `POST /insights` - Extract insights (params: doc_id)
- `POST /ask` - Ask a question (params: doc_id, question)
- `GET /health` - Check system health
- `GET /stats` - Get system statistics

## Configuration

### Environment Variables

- `VITE_API_URL` - Backend API URL (default: `http://localhost:8000`)

### TailwindCSS Theme

Custom color theme with sky blue as primary color:
- **Primary**: `primary-50` to `primary-900`
- **Secondary**: `gray-50` to `gray-900`

## Components

### Common Components

- **Button** - With variants (primary, secondary, outline), sizes (sm, md, lg), loading state
- **Card** - Container with shadow and rounded corners
- **Badge** - Colored labels (green, blue, yellow, red)
- **LoadingSpinner** - Animated loading indicator
- **Alert** - Notification boxes (info, success, warning, error)

### Specialized Components

- **FileUploader** - Drag-drop file upload with validation and progress
- **ChatMessage** - Message bubbles with source attribution
- **ChatInput** - Text input with send button and Enter hotkey
- **DocumentCard** - Document preview with metadata
- **Header/Footer** - Navigation and branding

## Hooks

- **useAsync** - Manage async operations (loading, error, data states)
- **useDocumentManager** - Manage document list and selection
- **useNotification** - Show temporary notifications

## Pages

- **UploadPage** - Upload documents and view features
- **DashboardPage** - View summaries and extracted insights
- **ChatPage** - Ask questions about documents (RAG)
- **StatusPage** - System health, statistics, and configuration

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Performance

- Code splitting with Vite
- CSS with TailwindCSS (optimized production build)
- Lazy loading of components
- Request caching in Axios interceptors

## Troubleshooting

### API Connection Issues
- Ensure the backend is running on `http://localhost:8000`
- Check `VITE_API_URL` environment variable
- Verify CORS is enabled on the backend

### Build Errors
- Delete `node_modules` and `package-lock.json`, then reinstall
- Clear Vite cache: `rm -rf .vite`

### Styling Issues
- Clear TailwindCSS cache: `rm -rf node_modules/.cache`
- Rebuild with: `npm run build`

## Contributing

When adding new components:
1. Place in `src/components/` directory
2. Export from `src/components/index.js`
3. Add PropTypes or TypeScript types
4. Include JSDoc comments

## License

Copyright © 2024 Mahindra AI-SDLC Project
