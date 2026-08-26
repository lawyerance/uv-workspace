from fastapi import APIRouter

r1 = APIRouter(prefix='/api/v1')

@r1.get('/health')
def health():
    return {'status': 'ok',"message": "api"}
