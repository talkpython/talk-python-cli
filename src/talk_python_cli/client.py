"""MCP HTTP client — thin JSON-RPC 2.0 wrapper over httpx."""

from __future__ import annotations

import httpx

from talk_python_cli import __version__

DEFAULT_URL = 'https://talkpython.fm/api/mcp'
_PROTOCOL_VERSION = '2025-03-26'
_CLIENT_INFO = {'name': 'talk-python-cli', 'version': __version__}


class MCPError(Exception):
    """Raised when the MCP server returns a JSON-RPC error."""

    def __init__(self, code: int, message: str, data: object = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f'MCP error {code}: {message}')


class MCPClient:
    """Synchronous client for the Talk Python MCP server (Streamable HTTP)."""

    def __init__(self, base_url: str = DEFAULT_URL, output_format: str = 'text'):
        self.base_url = base_url.rstrip('/')
        self.output_format = output_format
        self._msg_id = 0
        self._session_id: str | None = None
        self._initialized = False
        self._http = httpx.Client(
            timeout=30.0,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream',
                'User-Agent': f'talk-python-cli/{__version__}',
            },
        )

    # -- internal helpers -----------------------------------------------------

    def _next_id(self) -> int:
        self._msg_id += 1
        return self._msg_id

    def _url(self) -> str:
        if self.output_format == 'json':
            return f'{self.base_url}?format=json'
        return self.base_url

    def _post(self, payload: dict) -> httpx.Response:
        """Send a JSON-RPC request, attaching session header if available."""
        headers: dict[str, str] = {}
        if self._session_id:
            headers['Mcp-Session-Id'] = self._session_id
        resp = self._http.post(self._url(), json=payload, headers=headers)
        # Capture session id from response
        if 'mcp-session-id' in resp.headers:
            self._session_id = resp.headers['mcp-session-id']
        resp.raise_for_status()
        return resp

    def _send_request(self, method: str, params: dict | None = None) -> dict:
        """Send a JSON-RPC *request* (expects a response with an id)."""
        payload: dict = {
            'jsonrpc': '2.0',
            'id': self._next_id(),
            'method': method,
        }
        if params is not None:
            payload['params'] = params

        resp = self._post(payload)
        body = resp.json()

        if 'error' in body:
            err = body['error']
            raise MCPError(err.get('code', -1), err.get('message', 'Unknown error'), err.get('data'))

        return body.get('result', {})

    def _send_notification(self, method: str, params: dict | None = None) -> None:
        """Send a JSON-RPC *notification* (no id, no response expected)."""
        payload: dict = {
            'jsonrpc': '2.0',
            'method': method,
        }
        if params is not None:
            payload['params'] = params
        self._post(payload)

    # -- MCP lifecycle --------------------------------------------------------

    def _initialize(self) -> None:
        """Perform the MCP initialize handshake."""
        self._send_request(
            'initialize',
            {
                'protocolVersion': _PROTOCOL_VERSION,
                'capabilities': {},
                'clientInfo': _CLIENT_INFO,
            },
        )
        self._send_notification('notifications/initialized')
        self._initialized = True

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            self._initialize()

    # -- public API -----------------------------------------------------------

    def call_tool(self, tool_name: str, arguments: dict | None = None) -> str:
        """Call an MCP tool and return the text content from the first result.

        Returns the raw text string from the server (Markdown or JSON depending
        on the ``output_format`` passed at construction time).
        """
        self._ensure_initialized()

        result = self._send_request(
            'tools/call',
            {
                'name': tool_name,
                'arguments': arguments or {},
            },
        )

        # MCP tools/call result: {"content": [{"type": "text", "text": "..."}]}
        content_list = result.get('content', [])
        texts = [item['text'] for item in content_list if item.get('type') == 'text']
        return '\n'.join(texts)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._http.close()

    def __enter__(self) -> MCPClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
