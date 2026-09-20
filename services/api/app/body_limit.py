"""Bound request bytes before multipart parsing can spill unbounded data to disk."""
from starlette.responses import JSONResponse


class BodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['method'] not in ('POST', 'PUT', 'PATCH'):
            return await self.app(scope, receive, send)
        maximum = 5 * 1024 * 1024 + 128 * 1024 if scope['path'] == '/api/documents' else 64 * 1024
        chunks, size = [], 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            chunk = message.get('body', b'')
            size += len(chunk)
            if size > maximum:
                response = JSONResponse({'detail': {'code': 'request_too_large',
                    'message': 'Request too large. Upload a file no larger than 5 MB or shorten the task.'}}, status_code=413)
                return await response(scope, receive, send)
            chunks.append(chunk)
            if not message.get('more_body', False):
                break
        body = b''.join(chunks)
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {'type': 'http.request', 'body': body, 'more_body': False}
            return await receive()

        return await self.app(scope, replay, send)
