from io import BytesIO

from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

app = FastAPI(
    title="Image Intensity Service",
    description="REST API for calculating average image intensity.",
    version="1.0.0",
)


@app.get("/health")
async def health_check():
    """Check whether the service is running."""
    return {"status": "healthy"}


def calculate_average_intensity(image: Image.Image) -> float:
    """
    Calculate average grayscale intensity.

    0   = Black
    255 = White
    """
    grayscale_image = image.convert("L")
    histogram = grayscale_image.histogram()

    total_pixels = sum(histogram)

    if total_pixels == 0:
        raise ValueError("Image contains no pixels.")

    weighted_sum = sum(
        intensity * count
        for intensity, count in enumerate(histogram)
    )

    return round(weighted_sum / total_pixels, 2)


@app.post("/api/v1/intensity")
async def get_image_intensity(file: UploadFile = File(...)):
    """Accept a PNG image and return its average intensity."""

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    if file.content_type != "image/png":
        raise HTTPException(
            status_code=415,
            detail="Unsupported image format. Please upload a PNG image.",
        )

    image_data = await file.read()

    if not image_data:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty.",
        )

    try:
        image = Image.open(BytesIO(image_data))
        image.load()

        if image.format != "PNG":
            raise HTTPException(
                status_code=415,
                detail="Unsupported image format. Please upload a PNG image.",
            )

        average_intensity = calculate_average_intensity(image)

        return {
            "filename": file.filename,
            "average_intensity": average_intensity,
            "min_intensity": 0,
            "max_intensity": 255,
            "format": image.format,
            "width": image.width,
            "height": image.height,
        }

    except HTTPException:
        raise

    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted image.",
        )

    finally:
        await file.close()