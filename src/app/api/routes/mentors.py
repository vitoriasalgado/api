from pydantic import BaseModel, Field


class MentorCreate(BaseModel):
    name: str = Field(min_length=1)
    expertise: str = Field(min_length=1)
    bio: str | None = None


class MentorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    expertise: str | None = Field(default=None, min_length=1)
    bio: str | None = None


class MentorRead(BaseModel):
    id: int
    name: str
    expertise: str
    bio: str | None

from fastapi import APIRouter

router = APIRouter(tags=["mentors"])

mentors_db: dict[int, MentorRead] = {}
next_id: int = 1


@router.post("/mentors", status_code=201, response_model=MentorRead)
async def create_mentor(payload: MentorCreate) -> MentorRead:
    global next_id
    mentor = MentorRead(
        id=next_id,
        name=payload.name,
        expertise=payload.expertise,
        bio=payload.bio,
    )
    mentors_db[next_id] = mentor
    next_id += 1
    return mentor
@router.get("/mentors", response_model=list[MentorRead])
async def list_mentors() -> list[MentorRead]:
    return list(mentors_db.values())
