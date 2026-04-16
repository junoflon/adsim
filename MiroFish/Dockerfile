FROM python:3.11

RUN apt-get update \
  && apt-get install -y --no-install-recommends curl \
  && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
  && apt-get install -y --no-install-recommends nodejs \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy everything
COPY . .

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
