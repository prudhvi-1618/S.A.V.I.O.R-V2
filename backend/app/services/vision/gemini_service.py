import google.generativeai as genai
import json
from dataclasses import dataclass
from typing import List
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

@dataclass
class ImageDescription:
    image_type: str
    summary: str
    description: str
    visible_text: List[str]
    components: List[str]
    relationships: List[str]

    def to_retrieval_text(self) -> str:
        parts = [
            f"Image Type: {self.image_type}",
            f"Summary: {self.summary}",
            f"Description: {self.description}",
        ]
        if self.visible_text:
            parts.append(f"Visible Text: {', '.join(self.visible_text)}")
        if self.components:
            parts.append(f"Components: {', '.join(self.components)}")
        if self.relationships:
            parts.append(f"Relationships: {', '.join(self.relationships)}")
        return "\n".join(parts)

class GeminiService:
    @staticmethod
    def describe_image(image_path: str) -> ImageDescription:
        try:
            model = genai.GenerativeModel(settings.VISION_MODEL)
            sample_file = genai.upload_file(path=image_path)

            prompt = """
Analyze this image extracted from a PDF document and provide:

1. A concise summary (1-2 sentences)
2. A detailed description of all visual content
3. List all text visible in the image
4. List all components, objects, or entities shown
5. Describe relationships between components if applicable
6. Note the type of image (diagram, chart, photo, screenshot, etc.)

Respond in this exact JSON format:
{
  "image_type": "diagram | chart | photo | screenshot | table | other",
  "summary": "...",
  "description": "...",
  "visible_text": ["...", "..."],
  "components": ["...", "..."],
  "relationships": ["...", "..."]
}
"""
            response = model.generate_content([sample_file, prompt])
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            
            data = json.loads(clean_text)
            return ImageDescription(
                image_type=data.get("image_type", "other"),
                summary=data.get("summary", ""),
                description=data.get("description", ""),
                visible_text=data.get("visible_text", []),
                components=data.get("components", []),
                relationships=data.get("relationships", [])
            )
        except Exception as e:
            print(f"Error describing image: {e}")
            return ImageDescription(
                image_type="other",
                summary="Image content unavailable",
                description=f"Error generating description: {str(e)}",
                visible_text=[],
                components=[],
                relationships=[]
            )

    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        try:
            result = genai.embed_content(
                model=settings.EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_document"
            )
            return result["embedding"]
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.0] * settings.EMBEDDING_DIMENSION

    @staticmethod
    def generate_query_embedding(text: str) -> List[float]:
        try:
            result = genai.embed_content(
                model=settings.EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_query"
            )
            return result["embedding"]
        except Exception as e:
            print(f"Error generating query embedding: {e}")
            return [0.0] * settings.EMBEDDING_DIMENSION

    @staticmethod
    def stream_chat_response(
        question: str,
        context: str,
        conversation_history: list[dict] | None = None,
    ):
        model = genai.GenerativeModel(settings.CHAT_MODEL)
        
        system_prompt = f"""You are S.A.V.I.O.R, an AI assistant that answers questions about an uploaded PDF document.

Your answers must be grounded only in the document context provided below.

RULES:
1. Use only the provided document context to answer.
2. Do not use outside knowledge.
3. Do not invent information.
4. If the answer cannot be determined from the provided context, clearly say:
   "I could not find that information in the uploaded document."
5. Be concise but provide sufficient explanation.
6. When information comes from multiple sources, combine them clearly.
7. Do not mention internal vector embeddings or retrieval implementation unless the user asks.
8. Do not fabricate page numbers or sources.

DOCUMENT CONTEXT:
{context}"""

        # Convert conversation_history to Gemini format if provided
        gemini_history = []
        if conversation_history:
            for msg in conversation_history:
                # Gemini expects role to be 'user' or 'model'
                role = "model" if msg["role"] == "assistant" else "user"
                gemini_history.append({"role": role, "parts": [msg["content"]]})
                
        # To strictly enforce the system prompt across the chat, 
        # it is often best to include it as a developer instruction or the first message.
        # Here we just prepend it to the current question to be absolutely sure context is grounded.
        # A more elegant way in genai API is passing system_instruction to GenerativeModel,
        # but let's keep it simple and prepend to the query if not using system_instruction.
        
        full_question = f"{system_prompt}\n\nUSER QUESTION:\n{question}"

        try:
            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(full_question, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            print(f"Error in chat stream: {e}")
            yield f"Error generating answer: {str(e)}"

