from dataclasses import dataclass, field


@dataclass(frozen=True)
class Source:
    source_id: str
    source_type: str
    distance_km: float
    source_name: str = ""
    area_id: str = ""


@dataclass(frozen=True)
class Rate:
    category: str
    credit_per_kg: float
    hazardous: bool


@dataclass(frozen=True)
class ItemLine:
    category: str
    count: int
    weight_kg: float


@dataclass(frozen=True)
class PickupRequest:
    request_id: str
    source_id: str
    items: tuple[ItemLine, ...]

    @property
    def total_weight_kg(self) -> float:
        return sum(item.weight_kg for item in self.items)


@dataclass
class VehicleDay:
    day_number: int
    requests: list[PickupRequest] = field(default_factory=list)
    total_weight_kg: float = 0.0
    hazardous_weight_kg: float = 0.0


@dataclass(frozen=True)
class Calculation:
    category_credit: float
    handling_deduction: float
    pickup_charge: float
    net_rupees: int


@dataclass(frozen=True)
class PickupResult:
    request: PickupRequest
    accepted: bool
    reason: str | None = None
    calculation: Calculation | None = None
    day_number: int | None = None
