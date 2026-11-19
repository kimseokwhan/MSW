import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Destination:
    label: str
    region_code: str
    air_province: str | None
    districts: tuple[str, ...] = ()
    excluded_districts: tuple[str, ...] = ()


CATALOG = json.loads(Path(__file__).with_name("regions.json").read_text(encoding="utf-8"))
PROVINCE_ALIASES = {
    "11": ("서울", "서울시"), "26": ("부산", "부산시"), "27": ("대구", "대구시"),
    "28": ("인천", "인천시"), "30": ("대전", "대전시"), "31": ("울산", "울산시"),
    "41": ("경기",), "43": ("충북",), "44": ("충남",), "47": ("경북",),
    "48": ("경남",), "50": ("제주", "제주도"), "51": ("강원", "강원도"),
    "52": ("전북", "전라북도"), "36110": ("세종", "세종시"),
}
GWANGJU_DISTRICTS = ("210", "240", "270", "300", "330")


def key(name):
    return re.sub(r"\s+", "", name)


def district_aliases(name):
    words = name.split()
    short = [word[:-1] if len(word) > 2 and word[-1] in "시군구" else word for word in words]
    return {key(name), key("".join(short)), key("".join(short[:-1]) + words[-1]),
            key("".join(words[:-1]) + short[-1])}


def build_index():
    provinces, districts, qualified = {}, {}, {}
    for area in CATALOG:
        code = area["code"]
        if code == "12":
            entries = [
                (Destination("광주", code, "광주", GWANGJU_DISTRICTS), ("광주", "광주광역시", "광주광역")),
                (Destination("전남", code, "전남", excluded_districts=GWANGJU_DISTRICTS),
                 ("전남", "전라남도")),
                (Destination(area["name"], code, None), (area["name"], "전남광주")),
            ]
        else:
            aliases = PROVINCE_ALIASES[code]
            entries = [(Destination(aliases[0], code, aliases[0]), (*aliases, area["name"]))]
        for destination, aliases in entries:
            for alias in aliases:
                provinces[key(alias)] = destination
        if code == "36110":
            continue
        names = area["districts"]
        for district_code, name in names:
            if code == "12":
                index = 0 if district_code in GWANGJU_DISTRICTS else 1
                parent, aliases = entries[index]
                aliases = (*aliases, *entries[2][1])
            else:
                parent, aliases = entries[0]
            children = tuple(item_code for item_code, item_name in names if item_name.startswith(name + " "))
            destination = Destination(f"{parent.label} {name}", code, parent.air_province,
                                      children or (district_code,))
            for alias in district_aliases(name):
                districts.setdefault(alias, set()).add(destination)
                for province in aliases:
                    qualified.setdefault(key(province) + alias, set()).add(destination)
            # A named subdistrict can also be addressed as, for example, 경기도 분당구.
            if " " in name:
                for alias in district_aliases(name.split()[-1]):
                    districts.setdefault(alias, set()).add(destination)
                    for province in aliases:
                        qualified.setdefault(key(province) + alias, set()).add(destination)
    return provinces, districts, qualified


PROVINCES, DISTRICTS, QUALIFIED = build_index()


def resolve_destination(name):
    token = key(name)
    if token in QUALIFIED:
        return sorted(QUALIFIED[token], key=lambda item: item.label)
    matches = set(DISTRICTS.get(token, ()))
    if token in PROVINCES:
        province = PROVINCES[token]
        if token not in {"광주"}:
            return [province]
        matches.add(province)
    return sorted(matches, key=lambda item: item.label)
