#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# A/B Test Entry Router — Shiny Express version

from shiny.express import input, render, ui
from shiny import reactive
import random

# Config
A_URL="https://howardcui.shinyapps.io/project3-app-a/"
B_URL="https://howardcui.shinyapps.io/project3-app-b/"

COOKIE_NAME="ab_group"
COOKIE_MAX_AGE=60 * 60 * 24 * 1/2  # 1/2 days

#Page setup
ui.page_opts(title="Data Studio", fillable=True)

#
ui.tags.head(
    ui.tags.script(f"""
        (function() {{
            var COOKIE = '{COOKIE_NAME}';
            var A_URL  = '{A_URL}';
            var B_URL  = '{B_URL}';
            var MAX_AGE = {COOKIE_MAX_AGE};

            function getCookie(name) {{
                var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
                return match ? match[2] : null;
            }}

            function setCookie(name, value, maxAge) {{
                document.cookie = name + '=' + value +
                    '; max-age=' + maxAge +
                    '; path=/; samesite=lax';
            }}

            // Check URL param for forced group (?group=A or ?group=B)
            var params = new URLSearchParams(window.location.search);
            var forced = params.get('group');
            if (forced === 'A' || forced === 'B') {{
                setCookie(COOKIE, forced, MAX_AGE);
            }}

            var group = getCookie(COOKIE);
            if (group !== 'A' && group !== 'B') {{
                group = Math.random() < 0.5 ? 'A' : 'B';
                setCookie(COOKIE, group, MAX_AGE);
            }}

            var target = group === 'A' ? A_URL : B_URL;
            window.location.replace(target);
        }})();
    """)
)

# UI
ui.tags.style("""
    body {
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        background: #f8fbfd;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .loading-wrap {
        text-align: center;
    }
    .spinner {
        width: 40px;
        height: 40px;
        border: 3px solid #d8e6ef;
        border-top-color: #89bdd8;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        margin: 0 auto 16px;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .loading-text {
        font-size: 15px;
        color: #475569;
    }
""")

ui.div(
    ui.div(class_="spinner"),
    ui.div("Loading Data Studio…", class_="loading-text"),
    class_="loading-wrap"
)