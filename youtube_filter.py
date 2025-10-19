#!/usr/bin/env python3
"""
youtube_filter.py
Filters existing YouTube comments dataset using a keyword scoring system.

Input:  youtube_comments_simple.csv  (from youtube_extract.py)
Output: youtube_comments_filtered.csv

Requires: pandas
pip install pandas
"""

import pandas as pd
import re

# === Keyword Scoring System ===
keyword_points = {
    # Predatory/Sexual terms
    "meetup": 8, "private": 5, "dm": 8, "old": 5, "soyjak": 100,
    "whatsapp": 8, "loli": 30, "child": 5, "teen": 5, "cutie": 9,
    "young": 5, "discord": 10, "snapchat": 8, "telegram": 10, "snap": 8,
    "instagram": 5, "tiktok": 5, "onlyfans": 10, "email": 5, "phone": 5,
    "blacked": 8, "blowjob": 8, "bdsm": 8, "fetish": 8, "camgirl": 10,
    "camslut": 15, "camwhore": 15, "rape": 15, "incest": 20, "shota": 20,
    "furry": 3, "futa": 10, "futanari": 10, "guro": 15, "vore": 10,
    "yiff": 10, "hentai": 8, "anime": 3, "BBC": 10, "MILF": 10,
    "Pawg": 10, "thicc": 5, "thot": 8, "gilf": 10, "childporn": 5,
    # Explicit/offensive terms
    "sex": 8, "sexy": 8, "nude": 10, "naked": 10, "cum": 8, "nigger": 15,
    "faggot": 15, "chink": 15, "cracker": 15, "spic": 15, "gook": 15,
    "pajeet" : 15, "shitskin": 15, "mutt": 15, "amerimutt": 15, "euromutt": 15,
    "meximutt": 15, "jap": 15, "troon": 10, "tranny": 15, "kike": 15,
    "cock": 10, "pussy": 10, "dick": 10, "fuck": 8, "shit": 5,
    "bitch": 8, "slut": 8, "whore": 8, "porn": 10, "xxx": 10, "asshole": 8,
    "clanker": 8, "KYS": 15, "retard": 5, "autist": 5, "autistic": 5,
    "cripple": 5, "crippled": 5, "kys": 15,
    # Drug/violence terms
    "drugs": 5, "alcohol": 5, "weed": 5, "coke": 8, "meth": 8,
    "heroin": 8, "kill": 5, "murder": 8,  "abuse": 8, "harm": 5,
    "die": 5, "suicide": 8, "bash": 5, "gun": 5, "pistol": 5, "rifle": 5,
    "knife": 5, "bomb": 10,
    # Context-dependent terms
    "love": 1, "want": 1, "please": 1, "alone": 3, "baby": 3,
    "kitten": 3, "daddy": 4, "daddy's": 8, "girl": 3, "boy": 3,
    "cute": 3, "hookup": 8, "date": 5, "yourself": 2, "touch": 5, "touching": 5,
    "body": 2,
}

def calculate_status_level(comment: str, keyword_points: dict):
    """
    Assigns a risk score, status level, and triggered keywords based on detected keywords.
    Returns (score, status, triggered_keywords).
    """
    if not isinstance(comment, str):
        return 0, "Safe", []

    score = 0
    text = comment.lower()
    triggered_keywords = []

    for word, points in keyword_points.items():
        if re.search(r'\b' + re.escape(word.lower()) + r'\b', text):
            score += points
            triggered_keywords.append(word)

    if score >= 10:
        status = "Dangerous"
    elif score >= 5:
        status = "Suspicious"
    else:
        status = "Safe"

    return score, status, triggered_keywords

def filter_comments(input_csv="youtube_comments_simple.csv",
                    output_csv="youtube_comments_filtered.csv"):
    """
    Reads a CSV of comments, applies keyword filtering, and outputs a new CSV.
    """
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"[ERROR] Input file '{input_csv}' not found.")
        return
    except pd.errors.EmptyDataError:
        print(f"[ERROR] Input file '{input_csv}' is empty.")
        return

    if "Comment" not in df.columns:
        print("[ERROR] The CSV must contain a 'Comment' column.")
        return

    print(f"[INFO] Processing {len(df)} comments...")

    # Apply scoring
    df["Score"], df["Status Level"], df["Triggered Keywords"] = zip(
        *df["Comment"].apply(lambda c: calculate_status_level(c, keyword_points))
    )

    # Convert triggered keywords to string for CSV output
    df["Triggered Keywords"] = df["Triggered Keywords"].apply(lambda x: ", ".join(x))

    # Save output
    try:
        df.to_csv(output_csv, index=False, encoding="utf-8-sig")
        print(f"[DONE] Saved filtered data to '{output_csv}' with {len(df)} entries.")
    except Exception as e:
        print(f"[ERROR] Failed to save output file: {e}")

if __name__ == "__main__":
    filter_comments()