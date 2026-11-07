from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image

from rob_jones_code_assessment.microservice.main import (
    app,
    calculate_average_intensity,
)

client = TestClient(app)


def create_test_image(color, image_format="PNG"):
    """Create an in-memory test image."""
    image = Image.new("RGB", (2, 2), color=color)

    image_bytes = BytesIO()
    image.save(image_bytes, format=image_format)
    image_bytes.seek(0)

    return image_bytes


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_average_intensity_calculation():
    image = Image.new("L", (2, 2))
    image.putdata([0, 50, 100, 150])

    result = calculate_average_intensity(image)

    assert result == 75.0


def test_black_image():
    image = Image.new("RGB", (2, 2), color=(0, 0, 0))

    assert calculate_average_intensity(image) == 0.0


def test_white_image():
    image = Image.new("RGB", (2, 2), color=(255, 255, 255))

    assert calculate_average_intensity(image) == 255.0


def test_upload_valid_png():
    image_bytes = create_test_image((255, 255, 255))

    response = client.post(
        "/api/v1/intensity",
        files={
            "file": ("white.png", image_bytes, "image/png")
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "white.png"
    assert data["average_intensity"] == 255.0
    assert data["format"] == "PNG"
    assert data["width"] == 2
    assert data["height"] == 2


def test_upload_black_png():
    image_bytes = create_test_image((0, 0, 0))

    response = client.post(
        "/api/v1/intensity",
        files={
            "file": ("black.png", image_bytes, "image/png")
        },
    )

    assert response.status_code == 200
    assert response.json()["average_intensity"] == 0.0


def test_upload_invalid_image():
    response = client.post(
        "/api/v1/intensity",
        files={
            "file": (
                "invalid.png",
                b"this is not an image",
                "image/png",
            )
        },
    )

    assert response.status_code == 400


def test_upload_empty_image():
    response = client.post(
        "/api/v1/intensity",
        files={
            "file": ("empty.png", b"", "image/png")
        },
    )

    assert response.status_code == 400


def test_unsupported_image_format():
    image_bytes = create_test_image(
        (255, 255, 255),
        image_format="JPEG",
    )

    response = client.post(
        "/api/v1/intensity",
        files={
            "file": ("image.jpg", image_bytes, "image/jpeg")
        },
    )

    assert response.status_code == 415


def test_png_content_type_with_jpeg_content():
    image_bytes = create_test_image(
        (255, 255, 255),
        image_format="JPEG",
    )

    response = client.post(
        "/api/v1/intensity",
        files={
            "file": ("image.png", image_bytes, "image/png")
        },
    )

    assert response.status_code == 415