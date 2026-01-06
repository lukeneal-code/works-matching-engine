# Works Matching Engine

AI-powered music usage matching service for publishing collection societies. This system matches uploaded usage data against a local works database using vector similarity search and local LLM reasoning.

## Features

- **Drag-and-drop file upload** - Support for TXT and CSV files with pipe delimiters
- **Real-time progress tracking** - Live updates showing match counts and processing status
- **AI-powered matching** - Uses Ollama with local LLMs for intelligent fuzzy matching
- **Vector similarity search** - PostgreSQL with pgvector for semantic matching
- **Manual review interface** - Review and confirm/reject flagged matches
- **Export functionality** - Export unmatched and flagged entries as CSV

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React     │────▶│   FastAPI   │────▶│ PostgreSQL  │
│  Frontend   │     │   Backend   │     │  + pgvector │
└─────────────┘     └──────┬──────┘     └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │   Ollama    │
                   │  (LLM/EMB)  │
                   └─────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- At least 8GB RAM (for Ollama models)
- Approximately 10GB disk space

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd works-matching-engine
```

2. Start all services:
```bash
docker-compose up -d
```

3. Pull the required Ollama models (first time only):
```bash
docker exec works-ollama ollama pull nomic-embed-text
docker exec works-ollama ollama pull llama3.2:3b
```

4. Seed the database with sample works:
```bash
docker exec -i works-postgres psql -U works_user -d works_matching < database/seeds/seed_works.sql
```

5. Generate embeddings for the works:
```bash
curl -X POST http://localhost:8000/api/works/generate-embeddings
```

6. Access the application:
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

## Usage

### Uploading Usage Files

1. Navigate to the Upload page
2. Drag and drop a pipe-delimited file or click to select
3. Review the preview and click "Start Processing"
4. Monitor real-time progress as records are matched

### File Format

Files should be pipe-delimited (|) with the following columns:

```
Recording Title|Recording Artist|Work Title|Songwriter
Yesterday|The Beatles|Yesterday|McCartney, Paul
```

### Reviewing Matches

1. Go to the Batches page
2. Click on a completed batch
3. Use the tabs to view:
   - **Matched**: High-confidence matches
   - **Flagged**: Medium/low-confidence matches requiring review
   - **Unmatched**: Records with no matches found
4. Confirm or reject flagged matches
5. Export unmatched records for manual processing

## API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/upload | Upload usage file (SSE stream) |
| POST | /api/upload/validate | Validate file without processing |
| GET | /api/batches | List processing batches |
| GET | /api/batches/{id} | Get batch details |
| DELETE | /api/batches/{id} | Delete a batch |
| GET | /api/matches/batch/{id} | List matches for a batch |
| GET | /api/matches/unmatched/{id} | List unmatched records |
| POST | /api/matches/{id}/review | Confirm/reject a match |
| GET | /api/matches/export/{id}/unmatched | Export unmatched as CSV |
| GET | /api/matches/export/{id}/flagged | Export flagged as CSV |
| GET | /api/works | List works in database |
| POST | /api/works | Add a new work |
| POST | /api/works/generate-embeddings | Generate embeddings for works |
| GET | /api/health | Health check |

### Example API Calls

```bash
# Check system health
curl http://localhost:8000/api/health/detailed

# List batches
curl http://localhost:8000/api/batches

# Get matches for a batch
curl http://localhost:8000/api/matches/batch/{batch_id}

# Review a match
curl -X POST http://localhost:8000/api/matches/{match_id}/review \
  -H "Content-Type: application/json" \
  -d '{"action": "confirm"}'
```

## Matching Algorithm

The matching engine uses a multi-stage approach:

1. **Text Normalization**: Lowercase, remove punctuation, collapse whitespace
2. **Trigram Similarity**: Fast candidate selection using PostgreSQL pg_trgm
3. **Vector Similarity**: Semantic matching using embeddings from nomic-embed-text
4. **Fuzzy Matching**: RapidFuzz algorithms (ratio, partial_ratio, token_sort, token_set)
5. **AI Reasoning**: Ollama LLM for ambiguous cases

### Confidence Thresholds

| Confidence | Match Type | Action |
|------------|------------|--------|
| >= 95% | Exact | Auto-match |
| >= 85% | High Confidence | Auto-match |
| >= 70% | Medium Confidence | Flag for review |
| >= 50% | Low Confidence | Flag for review |
| < 50% | No Match | Unmatched |

## Configuration

Environment variables (in docker-compose.yml):

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | postgresql://... | PostgreSQL connection string |
| OLLAMA_HOST | http://ollama:11434 | Ollama API URL |
| OLLAMA_MODEL | llama3.2:3b | LLM model for reasoning |
| EMBEDDING_MODEL | nomic-embed-text | Model for embeddings |

## Development

### Running Locally

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm start
```

### Project Structure

```
works-matching-engine/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Config, database
│   │   ├── models/        # SQLAlchemy models
│   │   └── services/      # Business logic
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API client
│   │   └── types/         # TypeScript types
│   └── package.json
├── database/
│   ├── migrations/        # SQL schema
│   └── seeds/             # Sample data
├── sample-data/           # Test files
└── docker-compose.yml
```

## Scaling Considerations

For production with 10,000+ works and concurrent users:

1. **Database**: Add connection pooling (PgBouncer)
2. **Embeddings**: Pre-compute and index embeddings
3. **Processing**: Use Celery/Redis for background jobs
4. **Caching**: Add Redis for frequently accessed data
5. **Load Balancing**: Multiple backend instances behind nginx

## Troubleshooting

### Common Issues

**Ollama models not found:**
```bash
docker exec works-ollama ollama pull nomic-embed-text
docker exec works-ollama ollama pull llama3.2:3b
```

**Database connection failed:**
```bash
docker-compose restart postgres
docker-compose logs postgres
```

**Slow embedding generation:**
- Embeddings are generated on first use
- Pre-generate with `/api/works/generate-embeddings`

**Memory issues:**
- Ollama requires 4GB+ RAM
- Consider using smaller models

## License

MIT License
# works-matching-engine
