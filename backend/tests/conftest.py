import sys
from unittest.mock import MagicMock

# Mock unstructured modules that require heavy ML dependencies
# This prevents collection errors when these dependencies are not installed
sys.modules['unstructured'] = MagicMock()
sys.modules['unstructured.partition'] = MagicMock()
sys.modules['unstructured.partition.pdf'] = MagicMock()
sys.modules['unstructured.partition.pdf_image'] = MagicMock()
sys.modules['unstructured.partition.pdf_image.pdfminer_processing'] = MagicMock()
sys.modules['unstructured.partition.pdf_image.pdfminer_utils'] = MagicMock()
sys.modules['unstructured_inference'] = MagicMock()
sys.modules['unstructured_inference.inference'] = MagicMock()
sys.modules['unstructured_inference.inference.layout'] = MagicMock()
