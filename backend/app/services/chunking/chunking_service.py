from typing import List
import uuid
from app.state.processing_state import ChunkData

class ChunkingService:
    @staticmethod
    def chunk_elements(elements: List[any]) -> List[ChunkData]:
        chunks = []
        current_title = None
        list_item_buffer = []

        def flush_list_items(chunk_index):
            if not list_item_buffer:
                return None
            
            text = "\n".join([f"• {el.text}" for el in list_item_buffer if hasattr(el, 'text') and el.text])
            if current_title:
                text = f"Title: {current_title.text}\n\n{text}"
            
            c = ChunkData(
                chunk_id=str(uuid.uuid4()),
                chunk_text=text,
                chunk_index=chunk_index,
                element_ids=[el.element_id for el in list_item_buffer],
                element_types=["ListItem"] * len(list_item_buffer),
                page_numbers=list(set(el.page_number for el in list_item_buffer)),
                primary_page=list_item_buffer[0].page_number,
                chunk_type="text",
                coordinates=[el.coordinates for el in list_item_buffer if hasattr(el, 'coordinates')]
            )
            list_item_buffer.clear()
            return c

        chunk_idx = 0

        print("-------- Starting chunking process ---------- ", flush=True)

        for el in elements:
            el_type = getattr(el, 'element_type', None)
            el_text = getattr(el, 'text', "")
            
            if el_type == "Title":
                if list_item_buffer:
                    c = flush_list_items(chunk_idx)
                    if c:
                        chunks.append(c)
                        chunk_idx += 1
                current_title = el
                continue

            elif el_type == "ListItem":
                list_item_buffer.append(el)
                continue

            else:
                if list_item_buffer:
                    c = flush_list_items(chunk_idx)
                    if c:
                        chunks.append(c)
                        chunk_idx += 1

            if el_type == "NarrativeText":
                if current_title:
                    el_text = f"Title: {current_title.text}\n\n{el_text}"

                if len(el_text) < 512:
                    chunks.append(ChunkData(
                        chunk_id=str(uuid.uuid4()),
                        chunk_text=el_text,
                        chunk_index=chunk_idx,
                        element_ids=[el.element_id],
                        element_types=[el_type],
                        page_numbers=[el.page_number],
                        primary_page=el.page_number,
                        chunk_type="text",
                        coordinates=[el.coordinates] if getattr(el, 'coordinates', None) else None
                    ))
                    chunk_idx += 1
                else:
                    sentences = el_text.split(". ")
                    current_chunk_text = ""
                    for s in sentences:
                        if len(current_chunk_text) + len(s) < 512:
                            current_chunk_text += s + ". "
                        else:
                            chunks.append(ChunkData(
                                chunk_id=str(uuid.uuid4()),
                                chunk_text=current_chunk_text.strip(),
                                chunk_index=chunk_idx,
                                element_ids=[el.element_id],
                                element_types=[el_type],
                                page_numbers=[el.page_number],
                                primary_page=el.page_number,
                                chunk_type="text",
                                coordinates=[el.coordinates] if getattr(el, 'coordinates', None) else None
                            ))
                            chunk_idx += 1
                            current_chunk_text = s + ". "
                    
                    if current_chunk_text:
                        chunks.append(ChunkData(
                            chunk_id=str(uuid.uuid4()),
                            chunk_text=current_chunk_text.strip(),
                            chunk_index=chunk_idx,
                            element_ids=[el.element_id],
                            element_types=[el_type],
                            page_numbers=[el.page_number],
                            primary_page=el.page_number,
                            chunk_type="text",
                            coordinates=[el.coordinates] if getattr(el, 'coordinates', None) else None
                        ))
                        chunk_idx += 1

            elif el_type == "Table":
                meta = getattr(el, 'metadata', {})
                if meta is None: meta = {}
                table_html = meta.get('table_as_html', '')
                content = table_html if table_html else el_text
                
                chunks.append(ChunkData(
                    chunk_id=str(uuid.uuid4()),
                    chunk_text=f"Table Content:\n{content}",
                    chunk_index=chunk_idx,
                    element_ids=[el.element_id],
                    element_types=[el_type],
                    page_numbers=[el.page_number],
                    primary_page=el.page_number,
                    chunk_type="table",
                    coordinates=[el.coordinates] if getattr(el, 'coordinates', None) else None
                ))
                chunk_idx += 1

            elif el_type == "Image":
                meta = getattr(el, 'metadata', {})
                if meta is None: meta = {}
                img_path = meta.get('image_path')
                chunks.append(ChunkData(
                    chunk_id=str(uuid.uuid4()),
                    chunk_text="",
                    chunk_index=chunk_idx,
                    element_ids=[el.element_id],
                    element_types=[el_type],
                    page_numbers=[el.page_number],
                    primary_page=el.page_number,
                    chunk_type="image",
                    image_path=img_path,
                    coordinates=[el.coordinates] if getattr(el, 'coordinates', None) else None
                ))
                chunk_idx += 1
            
            else:
                if el_text:
                    chunks.append(ChunkData(
                        chunk_id=str(uuid.uuid4()),
                        chunk_text=el_text,
                        chunk_index=chunk_idx,
                        element_ids=[el.element_id],
                        element_types=[el_type],
                        page_numbers=[el.page_number],
                        primary_page=el.page_number,
                        chunk_type="text",
                        coordinates=[el.coordinates] if getattr(el, 'coordinates', None) else None
                    ))
                    chunk_idx += 1

        if list_item_buffer:
            c = flush_list_items(chunk_idx)
            if c:
                chunks.append(c)
                chunk_idx += 1
                
        print("-------- Finished chunking process ---------- ", flush=True)
        return chunks
