FROM python:3.11

# Install Node.js 18
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl \
  && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
  && apt-get install -y --no-install-recommends nodejs \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy everything from MiroFish
COPY MiroFish/ .

# Install frontend deps and build
RUN cd frontend && npm ci && npm run build && ls -la dist/

# Install backend deps
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# Verify frontend dist exists
RUN ls -la /app/frontend/dist/index.html

ENV PORT=5001
EXPOSE 5001

WORKDIR /app/backend
CMD ["python", "run.py"]
