from io import BytesIO

from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

app = FastAPI(
    title="Image Intensity Service",
    description="REST API for calculating the average intensity of an image.",
    version="1.0.0",
)

@app.get("/health")
async def health_check():
    """Check whether the service is running."""
    return {"status": "healthy"}


def calculate_average_intensity(image: Image.Image) -> float:
    """
    Calculate the average grayscale intensity of an image.

    Pixel intensity ranges from:
        0   = Black
        255 = White

    RGB images are converted to grayscale before calculation.
    """
    grayscale_image = image.convert("L")

    # Create a histogram 
    histogram = grayscale_image.histogram()

    total_pixels = sum(histogram)

    # Protect against dividing by 0 for the average when the image contains no pixels
    if total_pixels == 0:
        raise ValueError("Image contains no pixels.")

    weighted_sum = sum(
        intensity * count
        for intensity, count in enumerate(histogram)
    )

    average_intensity = weighted_sum / total_pixels

    return round(average_intensity, 2)


@app.post("/api/v1/intensity")
async def get_image_intensity(file: UploadFile = File(...)):
    """
    Consume an image of the type PNG.
    Create a histogram of all of the intensities with a count of each intensity.
    Calculate the average of the intensities and returns the metrics in the response.
    """

    # Throw error when not filename sent
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    #  Throw error if the file type is not a png
    if file.content_type != "image/png":
        raise HTTPException(
            status_code=415,
            detail="Unsupported image format. Please upload a PNG image."
        )

    image_data = await file.read()

    #  Throw error if nothing in the image file
    if not image_data:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty."
        )

    try:
        image = Image.open(BytesIO(image_data))

        # Validate the actual image format before processing.
        if image.format != "PNG":
            raise HTTPException(
                status_code=415,
                detail="Unsupported image format. Please upload a PNG image.",
            )

        image.load()

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
            detail="Invalid or corrupted image."
        )

    finally:
        await file.close()