# ai-hackaton-w1-g2-pipeline-service
Service responsible for scheduling and running the data extraction pipeline.
Based one https://github.com/mu-semtech/mu-python-template
## How to extend in development
Add in `docker-compose.override.yml` of https://github.com/lblod/app-ai-hackathon-w1-g2
```
services:
  pipeline:
    image: lblod/ai-hackaton-w1-g2-pipeline-service:0.0.1-test
    build: /path/to/code
    environment:
      MODE: "development" # a quirk
    volumes:
      - /path/to/code:/app
```
