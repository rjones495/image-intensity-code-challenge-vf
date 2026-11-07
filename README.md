# Average Image Intensity Microservice
A REST API microservice that accepts PNG images and calculates their average grayscale pixel intensity.

## Tech Stack

- Python 3.15
- uv
- FastAPI
- Pillow
- Uvicorn
- Pytest
- Docker

## Features

- Accepts a PNG image file upload.
- Converts an image to grayscale.
- Calculates average pixel intensity (0–255).
- Returns image metadata and intensity as JSON.
- Handles invalid and empty image uploads.
- Provides a health-check endpoint.

## Prerequisites

- Python 3.15
- uv >=0.13.7 (if running locally)
- Docker (optional) 

## Installation

### Install the project dependencies locally
    $ uv sync --all-groups

### Run the app using a virtual enironment
    $ uv run uvicorn rob_jones_code_assessment.microservice.main:app --reload

### Run Tests
    $ uv run pytest

### Build docker image
    $ docker build -t image-intensity-service .

### Run docker container
    $ docker run -d -p 8000:8000 --name image-intensity-container image-intensity-service

## API

http://localhost:8000

Swagger docs:

http://localhost:8000/docs

## API Endpoints

### Health Check

GET `/health`

Response:

```json
{
    "status": "healthy"
}
```
### Calculate Average Intensity

POST `/api/v1/intensity`

Request:
- Content-Type: multipart/form-data
- Parameter: file
- Supported format: PNG

```bash
curl -X POST \
  http://localhost:8000/api/v1/intensity \
  -F "file=@sample.png"
```

Example response:

```json
{
    "filename": "sample.png",
    "average_intensity": 127.5,
    "min_intensity": 0,
    "max_intensity": 255,
    "format": "PNG",
    "width": 100,
    "height": 100
}
```