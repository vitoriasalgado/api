from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException


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

@router.get("/mentors/{id}", response_model=MentorRead)
async def get_mentor(id: int) -> MentorRead:
    if id not in mentors_db:
        raise HTTPException(status_code=404, detail="Mentor not found")
    return mentors_db[id]

@router.patch("/mentors/{id}", response_model=MentorRead)
async def update_mentor(id: int, payload: MentorUpdate) -> MentorRead:
    if id not in mentors_db:
        raise HTTPException(status_code=404, detail="Mentor not found")

    current = mentors_db[id]
    updates = payload.model_dump(exclude_unset=True)
    updated = current.model_copy(update=updates)
    mentors_db[id] = updated
    return updated

@router.delete("/mentors/{id}", status_code=204)
async def delete_mentor(id: int) -> None:
    if id not in mentors_db:
        raise HTTPException(status_code=404, detail="Mentor not found")
    del mentors_db[id]

