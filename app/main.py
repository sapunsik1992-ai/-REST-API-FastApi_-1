from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel, Field

app = FastAPI(title="Advertisement Service")


class AdvertisementCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    author: str = Field(..., min_length=1)


class AdvertisementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    author: Optional[str] = None


class Advertisement(AdvertisementCreate):
    id: int
    created_at: datetime


advertisements: dict[int, Advertisement] = {}
_next_advertisement_id = 1


def _get_now() -> datetime:
    return datetime.now(timezone.utc)


@app.post("/advertisement", response_model=Advertisement, status_code=201)
def create_advertisement(advertisement: AdvertisementCreate) -> Advertisement:
    global _next_advertisement_id

    new_advertisement = Advertisement(
        id=_next_advertisement_id,
        created_at=_get_now(),
        **advertisement.model_dump(),
    )
    advertisements[new_advertisement.id] = new_advertisement
    _next_advertisement_id += 1
    return new_advertisement


@app.get("/advertisement/{advertisement_id}", response_model=Advertisement)
def get_advertisement(advertisement_id: int) -> Advertisement:
    advertisement = advertisements.get(advertisement_id)
    if advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return advertisement


@app.patch("/advertisement/{advertisement_id}", response_model=Advertisement)
def update_advertisement(advertisement_id: int, update: AdvertisementUpdate) -> Advertisement:
    advertisement = advertisements.get(advertisement_id)
    if advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    data = update.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(advertisement, field, value)

    advertisements[advertisement_id] = advertisement
    return advertisement


@app.delete("/advertisement/{advertisement_id}", status_code=204)
def delete_advertisement(advertisement_id: int) -> Response:
    if advertisement_id not in advertisements:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    del advertisements[advertisement_id]
    return Response(status_code=204)


@app.get("/advertisement", response_model=list[Advertisement])
def search_advertisements(
    title: Optional[str] = Query(default=None),
    description: Optional[str] = Query(default=None),
    price: Optional[float] = Query(default=None),
    author: Optional[str] = Query(default=None),
    created_at: Optional[str] = Query(default=None),
) -> list[Advertisement]:
    results = list(advertisements.values())

    if title is not None:
        results = [ad for ad in results if title.lower() in ad.title.lower()]
    if description is not None:
        results = [ad for ad in results if description.lower() in ad.description.lower()]
    if price is not None:
        results = [ad for ad in results if ad.price == price]
    if author is not None:
        results = [ad for ad in results if author.lower() in ad.author.lower()]
    if created_at is not None:
        results = [
            ad for ad in results if created_at in ad.created_at.isoformat() or created_at == ad.created_at.date().isoformat()
        ]

    return results


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
