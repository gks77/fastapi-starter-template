import os
import uuid
import shutil
from typing import Optional
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import io

from app.core.config import settings


class FileUploadService:
    """Service for handling file uploads, particularly profile images."""
    
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.profile_images_dir = self.upload_dir / "profile_images"
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        self.image_size = (300, 300)  # Standard profile image size
        
        # Create directories if they don't exist
        self.profile_images_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_image_file(self, file: UploadFile) -> None:
        """Validate the uploaded image file."""
        # Check file size
        if hasattr(file, 'size') and file.size > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {self.max_file_size // (1024*1024)}MB"
            )
        
        # Check file extension
        file_extension = Path(file.filename or "").suffix.lower()
        if file_extension not in self.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Supported formats: {', '.join(self.allowed_extensions)}"
            )
        
        # Check if it's actually an image
        try:
            file.file.seek(0)
            image = Image.open(file.file)
            image.verify()
            file.file.seek(0)  # Reset file pointer
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )
    
    def resize_image(self, image_data: bytes) -> bytes:
        """Resize image to standard profile size."""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary (for RGBA images)
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize image while maintaining aspect ratio
            image.thumbnail(self.image_size, Image.Resampling.LANCZOS)
            
            # Create a new image with the exact size and center the resized image
            new_image = Image.new('RGB', self.image_size, (255, 255, 255))
            
            # Calculate position to center the image
            x = (self.image_size[0] - image.width) // 2
            y = (self.image_size[1] - image.height) // 2
            
            new_image.paste(image, (x, y))
            
            # Save to bytes
            output = io.BytesIO()
            new_image.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing image: {str(e)}"
            )
    
    def save_profile_image(self, file: UploadFile, user_id: uuid.UUID) -> str:
        """Save uploaded profile image and return the file path."""
        self.validate_image_file(file)
        
        try:
            # Read file content
            file_content = file.file.read()
            
            # Resize image
            resized_image = self.resize_image(file_content)
            
            # Generate unique filename
            file_extension = Path(file.filename or "").suffix.lower() or ".jpg"
            filename = f"{user_id}_{uuid.uuid4().hex[:8]}.jpg"  # Always save as JPEG
            file_path = self.profile_images_dir / filename
            
            # Save file
            with open(file_path, "wb") as buffer:
                buffer.write(resized_image)
            
            # Return relative path for storing in database
            return f"uploads/profile_images/{filename}"
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving file: {str(e)}"
            )
    
    def delete_profile_image(self, image_path: str) -> bool:
        """Delete profile image file."""
        try:
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
                return True
            return False
        except Exception:
            return False
    
    def get_image_url(self, image_path: Optional[str]) -> Optional[str]:
        """Get the full URL for an image path."""
        if not image_path:
            return None
        
        # In production, you'd use your domain
        # For now, return the relative path that can be served by FastAPI
        return f"/static/{image_path}"


file_upload_service = FileUploadService()
