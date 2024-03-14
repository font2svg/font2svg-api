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

### Docker

```
$ docker run -d --name font2svg-api \
        -v /path/to/font2svg:/var/lib/font2svg/data \
        -v /path/to/font2svg/logs:/var/lib/font2svg/logs \
        -p 3001:8000 \
        font2svg/font2svg-api:latest
```

### Deploy compose

```
services:

  font2svg-api:
    container_name: font2svg-api
    image: font2svg/font2svg-api:latest
    restart: always
    ports:
      - 3001:8000
    volumes:
      - /path/to/font2svg:/var/lib/font2svg/data
      - /path/to/font2svg/logs:/var/lib/font2svg/logs
```

If all goes well, you'll be able to access your font2svg api on `http://localhost:3001` and `http://localhost:3001/docs` to access api docs.

## License

[MIT](https://github.com/font2svg/font2svg-api/blob/main/LICENSE) License © 2022 [Bean Deng](https://github.com/HADB)
