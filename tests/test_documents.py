import base64
import json
from io import BytesIO
from unittest.mock import AsyncMock, patch

import pytest
from mcp.types import CallToolResult, EmbeddedResource
from pypdf import PdfWriter

from dolibarr_mcp.dolibarr_mcp_server import handle_call_tool, is_write_tool


def _pdf_bytes(attachment: bytes | None = None) -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    if attachment is not None:
        writer.add_attachment("factur-x.xml", attachment)
    buf = BytesIO()
    writer.write(buf)
    return buf.getvalue()


def _mock_client(MockClient):
    instance = MockClient.return_value
    instance.__aenter__.return_value = instance
    return instance


def _download_payload(data: bytes, mime: str = "application/pdf", filename: str = "FA1.pdf") -> dict:
    return {
        "filename": filename,
        "content-type": mime,
        "filesize": len(data),
        "content": base64.b64encode(data).decode(),
        "encoding": "base64",
    }


def test_document_tools_are_read_only():
    assert not is_write_tool("get_documents")
    assert not is_write_tool("download_document")


@pytest.mark.asyncio
async def test_get_documents_summarizes_entries():
    with patch("dolibarr_mcp.dolibarr_mcp_server.DolibarrClient") as MockClient:
        client = _mock_client(MockClient)
        client.get_documents = AsyncMock(return_value=[
            {"name": "FA1.pdf", "level1name": "FA1", "size": 123, "date": 1792220493,
             "type": "file", "fullname": "/srv/documents/facture/FA1/FA1.pdf"},
        ])

        result = await handle_call_tool("get_documents", {"modulepart": "invoice", "ref": "FA1"})

        client.get_documents.assert_awaited_once_with("invoice", ref="FA1", id=None)
        docs = json.loads(result[0].text)
        assert docs == [{
            "name": "FA1.pdf",
            "original_file": "FA1/FA1.pdf",
            "size": 123,
            "date": "2026-10-17T07:01:33Z",
            "type": "file",
        }]


@pytest.mark.asyncio
async def test_get_documents_requires_ref_or_id():
    with patch("dolibarr_mcp.dolibarr_mcp_server.DolibarrClient") as MockClient:
        client = _mock_client(MockClient)
        client.get_documents = AsyncMock()

        result = await handle_call_tool("get_documents", {"modulepart": "invoice"})

        assert isinstance(result, CallToolResult) and result.isError
        client.get_documents.assert_not_called()


@pytest.mark.asyncio
async def test_download_facturx_extracts_embedded_xml():
    xml = b'<?xml version="1.0"?><rsm:CrossIndustryInvoice/>'
    with patch("dolibarr_mcp.dolibarr_mcp_server.DolibarrClient") as MockClient:
        client = _mock_client(MockClient)
        client.download_document = AsyncMock(return_value=_download_payload(_pdf_bytes(xml)))

        result = await handle_call_tool(
            "download_document", {"modulepart": "invoice", "original_file": "FA1/FA1_facturx.pdf"}
        )

        meta = json.loads(result[0].text)
        assert meta["embedded_files"] == [{"name": "factur-x.xml", "size": len(xml)}]
        assert "CrossIndustryInvoice" in result[1].text
        assert isinstance(result[2], EmbeddedResource)
        assert result[2].resource.mimeType == "application/pdf"


@pytest.mark.asyncio
async def test_download_without_file_returns_only_metadata():
    with patch("dolibarr_mcp.dolibarr_mcp_server.DolibarrClient") as MockClient:
        client = _mock_client(MockClient)
        client.download_document = AsyncMock(return_value=_download_payload(_pdf_bytes()))

        result = await handle_call_tool(
            "download_document",
            {"modulepart": "invoice", "original_file": "FA1/FA1.pdf", "include_file": False},
        )

        assert len(result) == 1
        assert json.loads(result[0].text)["embedded_files"] == []


@pytest.mark.asyncio
async def test_download_text_file_returned_as_text():
    with patch("dolibarr_mcp.dolibarr_mcp_server.DolibarrClient") as MockClient:
        client = _mock_client(MockClient)
        client.download_document = AsyncMock(
            return_value=_download_payload(b"hello", mime="text/plain", filename="note.txt")
        )

        result = await handle_call_tool(
            "download_document", {"modulepart": "invoice", "original_file": "FA1/note.txt"}
        )

        assert result[-1].text == "hello"


@pytest.mark.asyncio
async def test_download_rejects_oversized_file():
    with patch("dolibarr_mcp.dolibarr_mcp_server.DolibarrClient") as MockClient, \
         patch("dolibarr_mcp.dolibarr_mcp_server.MAX_DOCUMENT_BYTES", 10):
        client = _mock_client(MockClient)
        client.download_document = AsyncMock(return_value=_download_payload(b"x" * 11))

        result = await handle_call_tool(
            "download_document", {"modulepart": "invoice", "original_file": "FA1/big.pdf"}
        )

        assert isinstance(result, CallToolResult) and result.isError
