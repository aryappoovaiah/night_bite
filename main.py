from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["night_mess"]
orders_collection = db["orders"]

# Fetch all orders and feedback
@app.get("/orders")
def get_orders():
    orders = list(orders_collection.find())
    for order in orders:
        order["_id"] = str(order["_id"])  # Convert ObjectId to string
    return {"orders": orders}

# Update order status
@app.put("/orders/{order_id}")
def update_order_status(order_id: str, status: str):
    if status not in ["pending", "preparing", "completed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    result = orders_collection.update_one({"_id": ObjectId(order_id)}, {"$set": {"status": status}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order status updated successfully"}

# Verify payment
@app.put("/orders/{order_id}/verify-payment")
def verify_payment(order_id: str):
    result = orders_collection.update_one({"_id": ObjectId(order_id)}, {"$set": {"payment_verified": True}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Payment verified successfully"}

# Run the server (only needed for local testing)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
