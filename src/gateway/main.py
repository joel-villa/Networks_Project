"""Runnable main"""
import asyncio
import os

from dotenv import load_dotenv
load_dotenv()
path = os.getenv("MESH_PATH")
