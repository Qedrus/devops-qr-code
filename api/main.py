from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import qrcode
import boto3
import os
from io import BytesIO
from urllib.parse import quote_plus, urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Allowing CORS for local testing
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS S3 Configuration
aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRET_KEY")

# Check if AWS credentials are loaded properly
if not aws_access_key or not aws_secret_key:
    raise HTTPException(status_code=500, detail="AWS credentials are not set properly")

s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

bucket_name = "qrcode-storage-qedrus-1"
test_data = b'This is a test'  # Example binary data

try:
    s3.put_object(
        Bucket=bucket_name, 
        Key="test-upload/test.txt", 
        Body=test_data, 
        ContentType='text/plain', 
        ACL='public-read'
    )
    print(f"File uploaded successfully.")
except Exception as e:
    print(f"Error: {e}")

@app.post("/generate-qr/")
async def generate_qr(url: str):
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR Code to BytesIO object
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Generate sanitized file name for S3
    parsed_url = urlparse(url)
    file_name = f"qr_codes/{quote_plus(parsed_url.netloc + parsed_url.path)}.png"

    try:
        # Upload to S3
        s3.put_object(
            Bucket=bucket_name, 
            Key=file_name, 
            Body=img_byte_arr, 
            ContentType='image/png', 
            #ACL='public-read'
        )
        
         # Generate the S3 URL
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_name}"
        return {"qr_code_url": s3_url}
    except boto3.exceptions.S3UploadFailedError as e:
        print(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
