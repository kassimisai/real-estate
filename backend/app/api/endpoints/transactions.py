from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...core.auth import get_current_user
from ...models.transaction import Transaction, TransactionStatus
from ...schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from ...mcp.base import MCPController, AgentMessage
from ...mcp.agents.transaction_coordinator import TransactionCoordinatorAgent

router = APIRouter()

@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    mcp: MCPController = Depends(lambda: mcp_controller)
):
    # Create message for transaction coordinator agent
    message = AgentMessage(
        content="Create new transaction",
        metadata={
            "action": "create_transaction",
            "data": {
                **transaction.dict(),
                "user_id": current_user.id
            }
        },
        source_agent="api",
        target_agent="transaction_coordinator"
    )
    
    # Process message through MCP
    response = await mcp.process_message(message)
    
    if response.metadata["status"] == "error":
        raise HTTPException(status_code=400, detail=response.metadata["message"])
    
    return response.metadata["data"]

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    transactions = db.query(Transaction)\
        .filter(Transaction.user_id == current_user.id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return transactions

@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    transaction = db.query(Transaction)\
        .filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id)\
        .first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    mcp: MCPController = Depends(lambda: mcp_controller)
):
    # Check if transaction exists
    transaction = db.query(Transaction)\
        .filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id)\
        .first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Create message for transaction coordinator agent
    message = AgentMessage(
        content="Update transaction",
        metadata={
            "action": "update_transaction",
            "data": {
                "transaction_id": transaction_id,
                **transaction_update.dict(exclude_unset=True)
            }
        },
        source_agent="api",
        target_agent="transaction_coordinator"
    )
    
    # Process message through MCP
    response = await mcp.process_message(message)
    
    if response.metadata["status"] == "error":
        raise HTTPException(status_code=400, detail=response.metadata["message"])
    
    return response.metadata["data"]

@router.post("/{transaction_id}/documents")
async def upload_document(
    transaction_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    mcp: MCPController = Depends(lambda: mcp_controller)
):
    # Verify transaction exists and belongs to user
    transaction = db.query(Transaction)\
        .filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id)\
        .first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Read file content
    content = await file.read()
    
    # Create message for transaction coordinator agent
    message = AgentMessage(
        content="Upload document",
        metadata={
            "action": "upload_document",
            "data": {
                "transaction_id": transaction_id,
                "file_name": file.filename,
                "content": content
            }
        },
        source_agent="api",
        target_agent="transaction_coordinator"
    )
    
    # Process message through MCP
    response = await mcp.process_message(message)
    
    if response.metadata["status"] == "error":
        raise HTTPException(status_code=400, detail=response.metadata["message"])
    
    return response.metadata["data"]
