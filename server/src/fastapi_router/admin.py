from fastapi import APIRouter

from app.session import query

admin = APIRouter()

@admin.get('/health')
def health():
    q = query()

    return {'status': 'ok', 'message': 'admin','data': q}
