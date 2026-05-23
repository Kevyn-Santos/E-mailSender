from fastapi import APIRouter

router = APIRouter()

@router.get('/health')
def health_Check():
    return{
        "Status": 200,
        "Description": "OK"
    }