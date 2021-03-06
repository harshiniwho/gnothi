# FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_sqlalchemy import DBSessionMiddleware  # middleware helper

# Database
from common.database import init_db, shutdown_db, fa_users_db, engine
from common.utils import vars, SECRET, utcnow
import common.models as M

# Jobs
import pytz
from app.ml import run_influencers
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app import habitica
from common.cloud_updown import cloud_up_maybe

app = FastAPI()
# app.secret_key = SECRET
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(DBSessionMiddleware, db_url=vars.DB_FULL)
# 9131155e: attempted log-filtering

@app.on_event("startup")
async def startup():
    await fa_users_db.connect()
    init_db()

    scheduler = AsyncIOScheduler(timezone=pytz.timezone('America/Los_Angeles'))
    scheduler.start()
    scheduler.add_job(habitica.cron, "cron", hour="*")
    scheduler.add_job(run_influencers, "cron", hour="*")
    scheduler.add_job(cloud_up_maybe, "cron", second="*/5")
    scheduler.add_job(M.Machine.prune, "cron", minute="*")
    scheduler.add_job(M.Job.prune, "cron", minute="*")


@app.on_event("shutdown")
async def shutdown_session():
    await fa_users_db.disconnect()
    shutdown_db()

