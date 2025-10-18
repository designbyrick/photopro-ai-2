"""
Batch photo processing functionality for PhotoPro AI.
Allows users to process multiple photos at once with different styles.
"""

from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import asyncio
import replicate
from datetime import datetime
import uuid

from models import User, GeneratedPhoto, CreditTransaction
from schemas import PhotoGenerate, PhotoResponse
from config import settings

class BatchProcessor:
    """Handles batch photo processing operations"""
    
    def __init__(self):
        self.replicate_client = replicate.Client(api_token=settings.REPLICATE_API_TOKEN)
    
    async def process_batch(
        self, 
        user: User, 
        photos: List[PhotoGenerate], 
        db: Session,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """
        Process multiple photos in batch
        
        Args:
            user: Current user
            photos: List of photo generation requests
            db: Database session
            background_tasks: FastAPI background tasks
            
        Returns:
            Dict with batch processing results
        """
        
        # Validate user has enough credits
        total_credits_needed = len(photos)
        if user.credits < total_credits_needed:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient credits. Need {total_credits_needed}, have {user.credits}"
            )
        
        # Create batch processing record
        batch_id = str(uuid.uuid4())
        batch_photos = []
        
        try:
            # Create photo records for each request
            for photo_request in photos:
                photo = GeneratedPhoto(
                    user_id=user.id,
                    original_url=photo_request.original_url,
                    style=photo_request.style,
                    prompt=photo_request.prompt or "",
                    status="queued",
                    batch_id=batch_id
                )
                db.add(photo)
                batch_photos.append(photo)
            
            db.commit()
            
            # Deduct credits
            user.credits -= total_credits_needed
            db.commit()
            
            # Create credit transaction
            credit_transaction = CreditTransaction(
                user_id=user.id,
                amount=-total_credits_needed,
                transaction_type="batch_photo_generation",
                description=f"Batch processing - {len(photos)} photos"
            )
            db.add(credit_transaction)
            db.commit()
            
            # Start background processing
            background_tasks.add_task(
                self._process_batch_background,
                batch_id,
                batch_photos,
                user.id
            )
            
            return {
                "batch_id": batch_id,
                "total_photos": len(photos),
                "credits_used": total_credits_needed,
                "status": "processing",
                "message": f"Batch processing started for {len(photos)} photos"
            }
            
        except Exception as e:
            # Rollback on error
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")
    
    async def _process_batch_background(
        self, 
        batch_id: str, 
        photos: List[GeneratedPhoto],
        user_id: int
    ):
        """Background task to process batch photos"""
        
        # Process photos with rate limiting
        for i, photo in enumerate(photos):
            try:
                # Update status to processing
                photo.status = "processing"
                # Note: In real implementation, you'd update the database here
                
                # Process with Replicate API
                await self._process_single_photo(photo)
                
                # Add delay between requests to respect rate limits
                if i < len(photos) - 1:
                    await asyncio.sleep(2)
                    
            except Exception as e:
                photo.status = "failed"
                print(f"Failed to process photo {photo.id}: {e}")
    
    async def _process_single_photo(self, photo: GeneratedPhoto):
        """Process a single photo with Replicate API"""
        
        try:
            # Style-specific parameters
            model_params = {
                "corporate": {"style_strength": 25, "steps": 50},
                "creative": {"style_strength": 30, "steps": 60},
                "formal": {"style_strength": 20, "steps": 50},
                "casual": {"style_strength": 35, "steps": 55}
            }
            
            params = model_params.get(photo.style, model_params["corporate"])
            
            # Process with Replicate API
            output = self.replicate_client.run(
                "tencentarc/photomaker:ddfc2b08d209f9fa8c1eca692712918bd449f695dabb4a958da31802a9570fe4",
                input={
                    "input_image": photo.original_url,
                    "style": photo.style,
                    "num_outputs": 1,
                    "style_strength_ratio": params["style_strength"],
                    "num_inference_steps": params["steps"]
                }
            )
            
            # Update photo with result
            if output and len(output) > 0:
                photo.processed_url = output[0]
                photo.status = "completed"
            else:
                photo.status = "failed"
                
        except Exception as e:
            photo.status = "failed"
            print(f"Replicate API error for photo {photo.id}: {e}")
    
    async def get_batch_status(self, batch_id: str, db: Session) -> Dict[str, Any]:
        """Get status of batch processing"""
        
        # Query photos in this batch
        batch_photos = db.query(GeneratedPhoto).filter(
            GeneratedPhoto.batch_id == batch_id
        ).all()
        
        if not batch_photos:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        # Calculate status counts
        status_counts = {}
        for photo in batch_photos:
            status_counts[photo.status] = status_counts.get(photo.status, 0) + 1
        
        total_photos = len(batch_photos)
        completed_photos = status_counts.get("completed", 0)
        failed_photos = status_counts.get("failed", 0)
        processing_photos = status_counts.get("processing", 0)
        
        # Determine overall batch status
        if completed_photos == total_photos:
            overall_status = "completed"
        elif failed_photos > 0 and completed_photos + failed_photos == total_photos:
            overall_status = "completed_with_errors"
        elif processing_photos > 0 or status_counts.get("queued", 0) > 0:
            overall_status = "processing"
        else:
            overall_status = "failed"
        
        return {
            "batch_id": batch_id,
            "total_photos": total_photos,
            "completed": completed_photos,
            "failed": failed_photos,
            "processing": processing_photos,
            "overall_status": overall_status,
            "photos": [
                {
                    "id": photo.id,
                    "style": photo.style,
                    "status": photo.status,
                    "processed_url": photo.processed_url,
                    "created_at": photo.created_at
                }
                for photo in batch_photos
            ]
        }

# Global batch processor instance
batch_processor = BatchProcessor()
