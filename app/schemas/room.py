from pydantic import BaseModel, ConfigDict, Field

class RoomBase(BaseModel):
    name: str = Field(..., example="A1 스터디룸")
    floor: int = Field(..., example="4")
    capacity: int = Field(..., gt=0, example=4)
    description: str | None = None
    image_url: str | None = None
    has_whiteboard: bool = False 
    has_projector: bool = False  

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    name: str | None = None
    floor: int | None = None
    capacity: int | None = Field(None, gt=0)
    description: str | None = None
    is_active: bool | None = None

class RoomResponse(RoomBase):
    id: int
    is_active: bool
    availability_status: str = "AVAILABLE"

    model_config = ConfigDict(from_attributes=True)