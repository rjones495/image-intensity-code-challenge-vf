# Run the app using virtual enironment
    $ uv run uvicorn rob_jones_code_assessment.microservice.main:app --reload

# To install the project
    $ uv sync --all-groups

# Run Test
    $ uv run pytest


# Build docker image
    $ docker build -t image-intensity-service .

# Run docker container
    $ docker run -d -p 8000:8000 --name image-intensity-container image-intensity-service

