FROM python:3.11

RUN apt-get update \
  && apt-get install -y --no-install-recommends curl \
  && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
  && apt-get install -y --no-install-recommends nodejs \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy everything (build context may be repo root OR MiroFish/)
COPY . .

# Normalize: if we were copied from repo root, MiroFish/ subdir exists — move into it
RUN if [ -d "/app/MiroFish/frontend" ]; then \
      echo "Repo-root context detected, flattening MiroFish/"; \
      mv /app/MiroFish/* /app/MiroFish/.[!.]* /app/ 2>/dev/null || true; \
      rm -rf /app/MiroFish /app/PRD /app/.git; \
    fi

# Install frontend deps and build static files
RUN cd frontend && npm ci && npm run build && ls -la dist/index.html

# Install backend deps
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# Verify build
RUN test -f /app/frontend/dist/index.html && echo "Frontend build OK"

ENV PORT=5001
EXPOSE 5001

WORKDIR /app/backend
CMD ["python", "run.py"]
