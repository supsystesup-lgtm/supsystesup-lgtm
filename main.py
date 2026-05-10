from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uuid
import os
from core.video_generator import VideoGenerator

app = FastAPI(title="CineStory AI API", version="1.0")

# تهيئة المولد
generator = VideoGenerator(
    mistral_api_key="9812edb1-e7b9-4f8d-bce1-62c23081b1aa"
)

# تخزين المهام (في الذاكرة حالياً)
jobs = {}

class GenerateRequest(BaseModel):
    story: str
    total_minutes: int = 8
    num_scenes: int = 12
    motion_style: str = "Cinematic Dramatic"
    motion_strength: float = 1.4


@app.post("/generate")
async def generate_video(request: GenerateRequest, background: BackgroundTasks):
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "status": "processing",
        "progress": 0,
        "story": request.story[:200] + "..."  # للعرض فقط
    }

    def run_generation():
        try:
            result = generator.generate_video(
                story=request.story,
                total_minutes=request.total_minutes,
                num_scenes=request.num_scenes,
                motion_style=request.motion_style,
                motion_strength=request.motion_strength,
                job_id=job_id
            )
            jobs[job_id] = {
                "status": "completed",
                "result": result,
                "progress": 100
            }
        except Exception as e:
            jobs[job_id] = {
                "status": "failed",
                "error": str(e),
                "progress": 0
            }

    background.add_task(run_generation)
    return {"job_id": job_id, "status": "processing"}


@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.get("/download/{job_id}")
async def download_video(job_id: str):
    job = jobs.get(job_id)
    if not job or job.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Video not ready yet")
    
    video_path = job["result"]["video_path"]
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"cine_story_{job_id[:8]}.mp4"
    )


# مستقبلاً: تجديد مشهد معين
@app.post("/regenerate-scene/{job_id}/{scene_index}")
async def regenerate_scene(job_id: str, scene_index: int):
    # هيتم تنفيذه لاحقاً
    raise HTTPException(501, "Feature under development")