from pydantic import BaseModel


class ModelServiceResponse(BaseModel):
    probability: float
    prediction: int
    class_name: str
    inference_time: float
