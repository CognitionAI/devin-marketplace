---
name: setup-metabase-instance
description: Set up and run a local Metabase instance. Downloads the JAR (if Java 21+ is available) or runs via Docker. Also handles stopping running instances.
---

# Set Up a Local Metabase Instance

This skill helps users run a local Metabase instance for development, testing, or exploration.

## Important: Network Access Required

This skill requires network access. All `curl`, `java`, and `docker` commands must be run outside the Cursor sandbox. Request full network access or run outside the sandbox before attempting these commands. Do not run them inside the sandbox as they will fail.

## Prerequisites Check

Run these checks in order. Stop at the first successful path.

### 1. Check for Java 21+

Expand PATH first to avoid the macOS stub at `/usr/bin/java`:

```bash
export PATH=”/opt/homebrew/opt/openjdk/bin:/opt/homebrew/opt/openjdk@21/bin:/opt/homebrew/bin:/usr/local/opt/openjdk/bin:/usr/local/opt/openjdk@21/bin:/usr/local/bin:$PATH”
java -version 2>&1 | head -1
```

If the output shows Java 21 or higher → use Section A (JAR). Keep this `PATH` export for all subsequent commands.
If not found or version < 21 → check Docker (step 2).

### 2. Check for Docker

```bash
docker --version 2>&1
```

**If Docker is available**: Use the Docker method (Section B).

**If neither Java 21+ nor Docker is available**: Direct the user to install Docker:

- macOS/Windows: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Linux: [Docker Engine](https://docs.docker.com/engine/install/)

Tell them to re-run this skill after installing Docker.

---

## Section A: JAR Method (Java 21+)

### A1. Check for existing Metabase directory

```bash
ls -la ./metabase 2>/dev/null
```

If `./metabase` exists and contains files, ask the user:

- "A `./metabase` directory already exists. Should I use it (preserving existing data) or remove it and start fresh?"

If the user wants to start fresh:

```bash
rm -rf ./metabase
```

### A2. Create directory and download JAR

```bash
mkdir -p ./metabase
```

Get the latest OSS release URL and download:

```bash
curl -sL -o ./metabase/metabase.jar https://downloads.metabase.com/latest/metabase.jar
```

Tell the user this may take a minute (the JAR is ~400MB).

### A3. Check if port 3000 is in use

```bash
lsof -i :3000 2>/dev/null | grep LISTEN
```

If the port is in use, ask the user:

- "Port 3000 is already in use. Would you like to use a different port?"
- Suggest port 3001, 3002, etc.

Store the chosen port as `$PORT` (default: 3000).

### A4. Start Metabase in the background

Use the same `PATH` as in the Java prerequisite step when the agent uses a fresh shell (prepend the macOS Homebrew line again if unsure). Optionally set `JAVA_CMD=$(command -v java)` after that export so you invoke the same binary you version-checked.

```bash
export PATH="/opt/homebrew/opt/openjdk/bin:/opt/homebrew/opt/openjdk@21/bin:/opt/homebrew/bin:/usr/local/opt/openjdk/bin:/usr/local/opt/openjdk@21/bin:/usr/local/bin:$PATH"
cd ./metabase && \
  MB_DB_FILE=./metabase.db \
  MB_JETTY_PORT=$PORT \
  nohup java -jar metabase.jar > metabase.log 2>&1 &
echo $! > metabase.pid
```

Tell the user: "Metabase is starting in the background. I'll check when it's ready..."

Also mention:

- "View logs: `tail -f ./metabase/metabase.log`"
- "The process ID is saved in `./metabase/metabase.pid`"

### A5. Wait for Metabase to be ready

Poll the health endpoint every 5 seconds until it returns `{"status":"ok"}`:

```bash
curl -s http://localhost:$PORT/api/health
```

Keep polling until the response is `{"status":"ok"}`. Metabase usually starts within 30-60 seconds.

If the health check keeps failing after 2 minutes, check if the process is still running:

```bash
ps -p $(cat ./metabase/metabase.pid 2>/dev/null) > /dev/null 2>&1 && echo "Running" || echo "Not running"
tail -50 ./metabase/metabase.log
```

Once healthy, tell the user: "Metabase is ready at `http://localhost:$PORT`"

---

## Section B: Docker Method

### B1. Check for existing Metabase directory

```bash
ls -la ./metabase 2>/dev/null
```

If `./metabase` exists and contains files, ask the user:

- "A `./metabase` directory already exists. Should I use it (preserving existing data) or remove it and start fresh?"

If the user wants to start fresh:

```bash
rm -rf ./metabase
```

### B2. Create directory for data persistence

```bash
mkdir -p ./metabase
```

### B3. Check if port 3000 is in use

```bash
lsof -i :3000 2>/dev/null | grep LISTEN
```

If the port is in use, ask the user for an alternative port. Store as `$PORT` (default: 3000).

### B4. Check for existing Metabase container

```bash
docker ps -a --filter "name=metabase-local" --format "{{.Names}} {{.Status}}"
```

If a container named `metabase-local` exists:

- If running: Ask if they want to stop it and start fresh, or keep using it
- If stopped: Ask if they want to remove it and start fresh, or restart it

To remove an existing container:

```bash
docker rm -f metabase-local 2>/dev/null
```

### B5. Get the latest Metabase version

The `latest` tag on Docker Hub is often outdated. Get the actual latest version from GitHub:

```bash
curl -s https://api.github.com/repos/metabase/metabase/releases/latest | grep '"tag_name"' | head -1
```

This returns something like `"tag_name": "v0.52.5"`. Extract the version (e.g., `v0.52.5`).

Verify the Docker image exists:

```bash
docker manifest inspect metabase/metabase:$VERSION 2>&1 | head -5
```

If it doesn't exist, fall back to `latest`.

### B6. Start Metabase container

```bash
docker run -d \
  --name metabase-local \
  -p $PORT:3000 \
  -v "$(pwd)/metabase:/metabase.db" \
  -e MB_DB_FILE=/metabase.db/metabase.db \
  -e MB_JETTY_HOST=0.0.0.0 \
  -e MB_ENABLE_EMBEDDING_SDK=true \
  -e MB_ENABLE_EMBEDDING_SIMPLE=true \
  metabase/metabase:$VERSION
```

Tell the user: "Metabase is starting via Docker. I'll check when it's ready..."

### B7. Wait for Metabase to be ready

Poll the health endpoint every 5 seconds until it returns `{"status":"ok"}`:

```bash
curl -s http://localhost:$PORT/api/health
```

Keep polling until the response is `{"status":"ok"}`. Metabase usually starts within 30-60 seconds.

If the health check keeps failing after 2 minutes, check the container status and logs:

```bash
docker ps --filter "name=metabase-local" --format "{{.Status}}"
docker logs metabase-local 2>&1 | tail -50
```

Once healthy, tell the user:

- "Metabase is ready at `http://localhost:$PORT`"
- "View logs: `docker logs -f metabase-local`"

---

## Next Steps: MCP Setup

Once the health check passes and Metabase is ready, ask the user:

"Would you like to set up the Metabase MCP so you can query your data directly from the IDE?"

- If they agree, invoke the `setup-metabase-mcp` skill. The MCP setup will:
  - Configure the MCP server with the local instance URL (`http://localhost:$PORT`)
  - Guide them through authentication
  - Enable querying tables, metrics, and dashboards from the IDE

- If they decline, let them know they can set up the MCP later by asking for "Metabase MCP setup".

---

## Stopping Metabase

When the user asks to stop Metabase, determine which method was used.

### Stop JAR-based Metabase

```bash
if [ -f ./metabase/metabase.pid ]; then
  kill $(cat ./metabase/metabase.pid) 2>/dev/null && rm ./metabase/metabase.pid && echo "Metabase stopped"
else
  # Fallback: find by process
  pkill -f "metabase.jar" && echo "Metabase stopped"
fi
```

### Stop Docker-based Metabase

```bash
docker stop metabase-local && echo "Metabase stopped"
```

To also remove the container (but keep data):

```bash
docker rm metabase-local
```

---

## Checking Metabase Status

### Check JAR status

```bash
if [ -f ./metabase/metabase.pid ] && ps -p $(cat ./metabase/metabase.pid) > /dev/null 2>&1; then
  echo "Metabase (JAR) is running with PID $(cat ./metabase/metabase.pid)"
else
  echo "Metabase (JAR) is not running"
fi
```

### Check Docker status

```bash
docker ps --filter "name=metabase-local" --format "{{.Names}}: {{.Status}}"
```

---

## Environment Variables Reference

These can be customized when starting Metabase:

| Variable        | Default         | Description                                  |
| --------------- | --------------- | -------------------------------------------- |
| `MB_DB_FILE`    | `./metabase.db` | H2 database file location                    |
| `MB_JETTY_PORT` | `3000`          | Port Metabase listens on                     |
| `MB_JETTY_HOST` | `localhost`     | Network interface (use `0.0.0.0` for Docker) |

For all options, see the [Metabase Environment Variables documentation](https://www.metabase.com/docs/latest/configuring-metabase/environment-variables).

---

## Troubleshooting

### "Address already in use"

Another process is using the port. Either stop that process or choose a different port.

### "Java version too old"

Install Java 21+ or use the Docker method instead.

### "Unable to locate a Java Runtime" on macOS

You are likely hitting `/usr/bin/java` (stub). Prepend Homebrew OpenJDK to `PATH` as in **Check for Java 21+**, or call the real binary explicitly, e.g. `/opt/homebrew/bin/java -version`.

### Metabase starts but is slow

First startup takes longer as it initializes the database. Subsequent starts are faster.

### "Cannot connect to Docker daemon"

Make sure Docker Desktop is running (macOS/Windows) or the Docker service is started (Linux).
