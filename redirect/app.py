#!/usr/bin/env python 3.12
# -*- coding: utf-8 -*-
# time: 2026/04/10
import random
from starlette.applications import Starlette
from starlette.responses import RedirectResponse, PlainTextResponse
from starlette.routing import Route

COOKIE_NAME = "ab_group"
COOKIE_MAX_AGE = 60 * 60 * 24 * 0.5 # 1/2 days

A_URL = "https://howardcui.shinyapps.io/project3-app-a1/"
B_URL = "https://howardcui.shinyapps.io/project3-app-b/"


async def entry_router(request):
    group = request.cookies.get(COOKIE_NAME)

    if group not in ("A", "B"):
        group = random.choice(["A", "B"])

    target = A_URL if group == "A" else B_URL
    response = RedirectResponse(url=target)

    response.set_cookie(
        key=COOKIE_NAME,
        value=group,
        max_age=COOKIE_MAX_AGE,
        httponly=False,
        samesite="lax",
    )
    return response


async def force_a(request):
    response = RedirectResponse(url=A_URL)
    response.set_cookie(
        key=COOKIE_NAME,
        value="A",
        max_age=COOKIE_MAX_AGE,
        httponly=False,
        samesite="lax",
    )
    return response


async def force_b(request):
    response = RedirectResponse(url=B_URL)
    response.set_cookie(
        key=COOKIE_NAME,
        value="B",
        max_age=COOKIE_MAX_AGE,
        httponly=False,
        samesite="lax",
    )
    return response


async def debug_group(request):
    group = request.cookies.get(COOKIE_NAME, "not_set")
    return PlainTextResponse(f"Current ab_group cookie: {group}")


app = Starlette(
    routes=[
        Route("/", entry_router),
        Route("/goA", force_a),
        Route("/goB", force_b),
        Route("/debug-group", debug_group),
    ]
)

