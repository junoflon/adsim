FROM python:3.11

RUN apt-get update \
  && apt-get install -y --no-install-recommends nodejs npm \
  && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

WORKDIR /app

# Copy everything
COPY MiroFish/ .

# Install deps
RUN npm ci \
  && npm ci --prefix frontend \
  && cd backend && pip install -r requirements.txt

EXPOSE 3000 5001

CMD ["npm", "run", "dev"]
