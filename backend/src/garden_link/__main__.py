from . import (
    landscape_recognition,
    plan_customizing,
    satisfaction_survey,
    utils,
    config,
)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
from typing import Generator, List
import sys
from pydantic import BaseModel


app = FastAPI(title="HAGCC API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok"}


@app.post("/api/landscape-recognition")
async def analyze_landscape():
    try:
        base64 = utils.image_to_base64(utils.take_photo(config.CAMERA_INDEX))
        def generate() -> Generator[str, None, None]:
            for chunk in landscape_recognition._analyze_image(base64):
                if chunk != utils.NULL_TEXT:
                    yield chunk
        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PlanCustomizingRequest(BaseModel):
    prior_knowledge: str
    duration: str
    preferences: List[str] = []


@app.post("/api/plan-customizing")
async def customize_plan(
    req: PlanCustomizingRequest,
):
    try:
        def generate() -> Generator[str, None, None]:
            for chunk in plan_customizing._generate_plan(
                req.prior_knowledge, req.duration, req.preferences
            ):
                yield chunk

        return StreamingResponse(generate(), media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/satisfaction-survey")
async def analyze_satisfaction():
    try:
        base64 = utils.image_to_base64(utils.take_photo(config.CAMERA_INDEX))
        res = satisfaction_survey._analyze_image(base64)

        if res == utils.NULL_TEXT:
            return {"scores": [], "total": 0, "message": "未识别到人脸"}

        scores = []
        for r in res.strip().split(","):
            s = r.strip()
            if s.isdigit():
                x = int(s)
                if 1 <= x <= 5:
                    scores.append(x)
                else:
                    raise HTTPException(status_code=500, detail=f"无效的分数：{x}")
            else:
                raise HTTPException(status_code=500, detail=f"无法解析响应：{res}")

        return {
            "scores": scores,
            "total": sum(scores),
            "average": sum(scores) / len(scores) if scores else 0,
            "count": len(scores),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def cli():
    """命令行模式"""
    try:
        while True:
            op = input("请输入操作：", duration=3)
            match op:
                case "":
                    break
                case "lr":
                    landscape_recognition.capture()
                case "ss":
                    satisfaction_survey.capture_expressions()
                case "pc":
                    plan_customizing.ask()
                case _:
                    print("无效操作")
            print()
    except KeyboardInterrupt:
        print(flush=True)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        cli()
    else:
        uvicorn.run(app, host="0.0.0.0", port=8908, log_level="info")


if __name__ == "__main__":
    main()
