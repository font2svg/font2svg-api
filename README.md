<p align="center">
  <img width="180px" src="https://github.com/font2svg/font2svg/assets/1836701/bf958bc8-e375-4c09-9cb9-d7462d217dbc" />
</p>

[![Release](https://img.shields.io/github/actions/workflow/status/font2svg/font2svg-api/release.yml)](https://github.com/font2svg/font2svg-api/actions/workflows/release.yml)
[![GitHub Release](https://img.shields.io/github/v/release/font2svg/font2svg-api)](https://github.com/font2svg/font2svg-api/releases/latest)
[![Docker Image Size](https://img.shields.io/docker/image-size/font2svg/font2svg-api)](https://hub.docker.com/r/font2svg/font2svg-api)
[![License](https://img.shields.io/github/license/font2svg/font2svg-api)](https://github.com/font2svg/font2svg-api/blob/main/LICENSE)

# Font2svg Api

Font2svg server-side project, written in Python. (ETA: 2024Q2)

## Getting started

### Docker run

This will start a stateless instance of Font2svg api listening on the default port of 8000.

Notice that all your fonts uploaded will be lost if container stopped running.

```bash
$ docker run -d --name font2svg-api font2svg/font2svg-api:latest
```

If all goes well, you'll be able to access your font2svg api on `http://localhost:8000` and `http://localhost:8000/docs` to access api docs.

#### Configuration

```bash
$ docker run -d --name font2svg-api \
        # Secret token for admin operations
        -e ADMIN_TOKEN=your_admin_token \
        # Enable or disable cache, default: true
        -e CACHE__ENABLED=true \
        # If true, svg file will be cached, default: true
        -e CACHE__PERSISTENT=true \
        # Maximum number of characters in memory cache
        -e CACHE__MEM_CHARS_LIMIT=10000 \
        -v /path/to/font2svg:/var/lib/font2svg/data \
        -v /path/to/font2svg/logs:/var/lib/font2svg/logs \
        -p 3001:8000 \
        font2svg/font2svg-api:latest
```

### Docker compose

```yaml
services:
  font2svg-api:
    container_name: font2svg-api
    image: font2svg/font2svg-api:latest
    restart: always
    ports:
      - 3001:8000
    environment:
      # Secret token for admin operations
      ADMIN_TOKEN: your_admin_token
      # Enable or disable cache, default: true
      CACHE__ENABLED: true
      # If true, svg file will be cached, default: true
      CACHE__PERSISTENT: true
      # Maximum number of characters in memory cache
      CACHE__MEM_CHARS_LIMIT: 10000
    volumes:
      - /path/to/font2svg:/var/lib/font2svg/data
      - /path/to/font2svg/logs:/var/lib/font2svg/logs
```

## Benchmark

Using `uvicorn[standard]` for better performance. See: [Run a Server Manually - Uvicorn](https://fastapi.tiangolo.com/deployment/manually/#install-the-server-program)

> By adding the `standard`, Uvicorn will install and use some recommended extra dependencies.
>
> That including `uvloop`, the high-performance drop-in replacement for `asyncio`, that provides the big concurrency performance boost.

### Running command:

```bash
$ uvicorn src.main:app --log-level critical
```

### Platform Info:

**Device**: Apple MacBook Pro(13-inch, M1, 2020)

**Chip**: Apple M1

**Memory**: 16GB

**System**: macOS Sonoma 14.3.1 (23D60)

### Results:

| RPS(QPS)         | concurrency=1 | concurrency=10 | concurrency=100 |
| ---------------- | ------------- | -------------- | --------------- |
| Cache off        | 198.95        | 145.44         | 139.51          |
| File cache hit   | 4043.38       | 5477.92        | 5555.66         |
| Memory cache hit | 4425.27       | 7573.39        | 7892.01         |
| Baseline         | 4646.00       | 8177.52        | 8528.67         |

### Details:

See [benchmarks](https://github.com/font2svg/font2svg-api/tree/main/benchmarks)

## License

[MIT](https://github.com/font2svg/font2svg-api/blob/main/LICENSE) License © 2022 [Bean Deng](https://github.com/HADB)
