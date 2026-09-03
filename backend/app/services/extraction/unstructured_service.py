import json
from typing import List
from unstructured.partition.pdf import partition_pdf
from app.schemas.element import ExtractedElement, ElementCoordinates
import uuid
import os

class UnstructuredService:
    @staticmethod
    def extract_elements(file_path: str, document_id: str) -> List[ExtractedElement]:
        # Basic check to prevent unstructured from failing immediately if the file is missing during mock tests
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Try hi_res with OCR first; fall back to fast if OCR is unavailable
        strategies = ["hi_res", "fast"]
        raw_elements = None
        last_error = None

        for strategy in strategies:
            try:
                raw_elements = partition_pdf(
                    filename=file_path,
                    strategy=strategy,
                    infer_table_structure=True,
                    extract_images_in_pdf=True,
                    include_page_breaks=True
                )
                break  # Success, no need to try other strategies
            except Exception as e:
                last_error = e
                if strategy == "hi_res":
                    # Try next strategy
                    continue
                else:
                    # Last strategy failed, raise the error
                    raise RuntimeError(f"Extraction failed with all strategies. Last error: {str(e)}") from e
        if raw_elements is None:
            raise RuntimeError(f"Extraction failed: {str(last_error)}")

        extracted_elements = []
        for raw in raw_elements:
            element_type = type(raw).__name__
            
            # Map unstructured types to our types
            type_mapping = {
                "Title": "Title",
                "NarrativeText": "NarrativeText",
                "Image": "Image",
                "Table": "Table",
                "ListItem": "ListItem"
            }
            mapped_type = type_mapping.get(element_type, "Other")
            
            if element_type == "PageBreak":
                continue

            metadata = raw.metadata
            page_number = metadata.page_number if metadata and metadata.page_number else 1
            
            coords = None
            if metadata and metadata.coordinates:
                # unstructured coords typically have points and system
                points = metadata.coordinates.points if hasattr(metadata.coordinates, "points") else None
                system = metadata.coordinates.system if hasattr(metadata.coordinates, "system") else None
                
                if points and system:
                    coords = ElementCoordinates(
                        points=points,
                        page_width=system.width if hasattr(system, "width") else 0.0,
                        page_height=system.height if hasattr(system, "height") else 0.0
                    )

            extra_metadata = {}
            if metadata:
                if hasattr(metadata, "image_path") and metadata.image_path:
                    extra_metadata["image_path"] = metadata.image_path
                if hasattr(metadata, "is_continuation") and metadata.is_continuation:
                    extra_metadata["is_continuation"] = metadata.is_continuation

            text = str(raw) if str(raw) else None

            el = ExtractedElement(
                element_id=str(uuid.uuid4()),
                document_id=document_id,
                element_type=mapped_type,
                text=text,
                page_number=page_number,
                coordinates=coords,
                metadata=extra_metadata
            )
            extracted_elements.append(el)
        print(f"--------- {len(extracted_elements)} elements extracted -----")
        return extracted_elements
