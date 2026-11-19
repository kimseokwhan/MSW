from datetime import date, datetime
from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, Field, StringConstraints, model_validator


Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
ContentId = Annotated[str, StringConstraints(pattern=r"^[0-9]+$")]
DataT = TypeVar("DataT")


class ToolError(BaseModel):
    code: str
    message: str


class ToolSuccess(BaseModel, Generic[DataT]):
    ok: Literal[True] = True
    data: DataT
    error: None = None


class ToolFailure(BaseModel):
    ok: Literal[False] = False
    data: None = None
    error: ToolError


class SearchInput(BaseModel):
    keyword: Text | None = None
    region_code: ContentId | None = None
    district_codes: list[ContentId] = Field(default_factory=list, max_length=5)
    excluded_districts: list[ContentId] = Field(default_factory=list, max_length=5)
    visit_date: date | None = None
    page: int = Field(default=1, ge=1)
    content_type_id: Literal["12", "14"] = "12"

    @model_validator(mode="after")
    def require_scope(self):
        if not self.region_code and (not self.keyword or self.district_codes or self.excluded_districts):
            raise ValueError("Provide a keyword or a region code; district filters require a region code")
        return self


class DetailInput(BaseModel):
    content_id: ContentId


class WeatherInput(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    date: date


class AirInput(BaseModel):
    province: Text


class Attraction(BaseModel):
    content_id: ContentId
    title: Text
    address: str | None
    latitude: float | None = Field(ge=-90, le=90)
    longitude: float | None = Field(ge=-180, le=180)
    content_type_id: str | None
    category_code: str | None


class SearchData(BaseModel):
    source: Literal["TourAPI"] = "TourAPI"
    requested_date: date
    checked_at: datetime
    basis: Literal["current_catalog"] = "current_catalog"
    page: int
    attractions: list[Attraction]


class DetailData(Attraction):
    source: Literal["TourAPI"] = "TourAPI"
    overview: str | None
    homepage: str | None


class WeatherData(BaseModel):
    source: Literal["Open-Meteo"] = "Open-Meteo"
    kind: Literal["forecast"] = "forecast"
    date: date
    timezone: Literal["Asia/Seoul"] = "Asia/Seoul"
    precipitation_probability_max: float | None = Field(ge=0, le=100)
    temperature_min_c: float | None
    temperature_max_c: float | None
    available_from: date
    available_to: date


class AirObservation(BaseModel):
    station_name: Text
    measured_at: datetime
    pm10_ug_m3: float | None = Field(ge=0)
    pm25_ug_m3: float | None = Field(ge=0)


class AirData(BaseModel):
    source: Literal["AirKorea"] = "AirKorea"
    kind: Literal["observation"] = "observation"
    province: str
    observations: list[AirObservation]
