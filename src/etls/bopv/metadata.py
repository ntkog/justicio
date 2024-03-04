import typing as tp
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator, Field
import re

from src.etls.common.metadata import MetadataDocument




class BOPVMetadataDocument(MetadataDocument):
    """Class for keeping metadata of a BOPV Document scrapped."""

    # Text
    filepath: str

    # Source
    source_name: str = "BOPV"
    source_type: str = "Boletin"

    # Metadatos

    departamento: Optional[str] = None 
    tipologia: str   

    # Links
    titulo: Optional[str] = None
    url_pdf: str  # pdf_link
    url_html: Optional[str] = None
    url_boletin: Optional[str] = None

    fecha_disposicion: str = ""
    anio: Optional[str] = None
    mes: Optional[str] = None
    dia: Optional[str] = None

    datetime_insert: str = datetime.utcnow().isoformat()

