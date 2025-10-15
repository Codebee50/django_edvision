import json
import re
from diagram.models import Diagram
from anthropic import Anthropic
from django.conf import settings

from diagram.serializers import AiExportDiagramSerializer

def remove_code_fences(text: str) -> str:
    """
    Remove markdown code fence markers (```language and ```) from text.
    Handles various language identifiers like ```python, ```sql, ```go, etc.
    """
    # Pattern matches:
    # - ``` followed by optional language identifier at the start
    # - ``` at the end
    # Uses re.DOTALL to match across multiple lines
    pattern = r'^```[\w]*\n?(.*?)\n?```$'
    
    match = re.match(pattern, text.strip(), re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # If no code fences found, return original text
    return text.strip()


def export_diagram_using_claude(diagram_id:str, format_name:str):
    try:
        diagram = Diagram.objects.get(id=diagram_id)
    except Diagram.DoesNotExist:
        raise ValueError("Diagram not found")
    
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    diagram_json = AiExportDiagramSerializer(diagram).data
    
    system_prompt = f"""You are an expert database designer and software engineer, proficient in {format_name}.

        Task: Convert the provided {diagram.database_type} database entity relationship diagram (in JSON format) into DDL code for {format_name}.

        Requirements:
        - Generate production-ready, syntactically correct DDL statements
        - Include appropriate indexes for foreign keys and frequently queried columns
        - Use proper data types and constraints (PRIMARY KEY, FOREIGN KEY, NOT NULL, UNIQUE, CHECK)
        - Follow {format_name} naming conventions and best practices
        - Maintain referential integrity between tables

        Output format:
        - Return ONLY the DDL code
        - No explanations, comments, or markdown formatting
        - No introductory or closing text
    """
    
    try:
    
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens = 10000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": json.dumps(diagram_json, default=str)
                }
            ]

        )
        response_text = response.content[0].text
        response_text = remove_code_fences(response_text)
        
        return True, response_text
    except Exception as e:
        return False, str(e)
    
    
    
