from dataclasses import dataclass ,field
from .enums import MediaRefType

@dataclass
class MediaRef:
    ref_type:MediaRefType
    ref :str

@dataclass
class NodeCollection:
    collected_text:list = field(default_factory=list)
    links:list[tuple[str,str]] =  field(default_factory=list)
    media_ref:list[MediaRef] = field(default_factory=list)