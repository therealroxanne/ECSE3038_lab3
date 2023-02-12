import array
from fastapi import FastAPI,Request, HTTPException,status
from fastapi.responses import Response, JSONResponse
from datetime import datetime, time
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio
import pydantic

app= FastAPI()

origins=[
    "http://localhost:8000",
    "https://ecse3038-lab3-tester.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client=motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://Enginebot:XxGxwdO7zDzBH8hU@cluster1.h0ath04.mongodb.net/?retryWrites=true&w=majority")
db= client.water_tank

pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

@app.get("/profile")
async def get_all_profiles():
    profiles= await db["profile"].find().to_list(999)
    if len(profiles) < 1:
        return {}
    return profiles[0]

@app.post("/profile",status_code=201)
async def create_new_profile(request:Request):
    profile_object= await request.json()
    profile_object["last_updated"]=datetime.now()

    new_profile= await db["profile"].insert_one(profile_object)
    created_profile= await db["profile"].find_one({"_id":new_profile.inserted_id})

    return created_profile

@app.get("/data",status_code=201)
async def get_all_tank_by_data():
    tank_route_object= await db["tank_data"].find().to_list(999)
    #if len(tank_route_object) < 1:
        #return {}
   # return tank_route_object[0]
    return tank_route_object

@app.post("/data",status_code=201)
async def create_new_tank_route(request:Request):
    tank_objects= await request.json()

    new_tank_route= await db["tank_data"].insert_one(tank_objects)
    created_route= await db["tank_data"].find_one({"_id":new_tank_route.inserted_id})

    return created_route

"""@app.patch("/data/{id}")
async def update_data_by_id(id:str, request:Request):
    data_update= await request.json()
    for tank_objects in db:
        if id==tank_objects["id"]:
            index=db.index(tank_objects)
            db[index]["location"]=data_update["location"]
            return db[index]"""
@app.patch("/data/{id}")
async def update_tank(id: str, request: Request):
    data_update = await request.json()
    updatetank = await db["tank_data"].update_one({"_id": ObjectId(id)},{'$set': data_update})
    tank_status = await db["tank_data"].find_one({"_id": ObjectId(id)})
    if updatetank.modified_count==1:
        if tank_status is not None:
            return tank_status
    else:
        raise HTTPException(status_code=304,detail="Item not modified")
@app.delete("/data/{id}")
async def delete_data_by_id(id:str):
    data_delete= await db["tank_data"].delete_one({"_id":ObjectId(id)})
    if data_delete.deleted_count == 1:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail="Item not found")


    

        
