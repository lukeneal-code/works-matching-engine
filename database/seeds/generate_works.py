#!/usr/bin/env python3
"""
Script to generate 10,000 works for the database.
Run this script to create a complete seed file for production use.
"""

import random
import json

# Base data for generation
FIRST_NAMES = [
    "John", "Paul", "George", "Ringo", "Mick", "Keith", "Bob", "James", "Michael", "David",
    "Robert", "Bruce", "Eric", "Tom", "Billy", "Chris", "Brian", "Steve", "Mark", "Peter",
    "Mary", "Diana", "Linda", "Stevie", "Aretha", "Dolly", "Whitney", "Madonna", "Adele", "Amy",
    "Taylor", "Beyonce", "Rihanna", "Lady", "Katy", "Britney", "Christina", "Jennifer", "Mariah", "Celine"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Davis", "Miller", "Wilson", "Moore", "Taylor",
    "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
    "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "King", "Wright",
    "Scott", "Green", "Baker", "Adams", "Nelson", "Hill", "Campbell", "Mitchell", "Roberts", "Carter"
]

TITLE_WORDS = [
    "Love", "Heart", "Dream", "Night", "Day", "Time", "Life", "World", "Soul", "Mind",
    "Fire", "Rain", "Sun", "Moon", "Star", "Sky", "Ocean", "River", "Mountain", "Road",
    "Dance", "Song", "Music", "Beat", "Rhythm", "Melody", "Harmony", "Blues", "Rock", "Jazz",
    "Sweet", "Bitter", "Wild", "Free", "Lost", "Found", "Broken", "Whole", "Dark", "Light",
    "Baby", "Honey", "Angel", "Devil", "Heaven", "Paradise", "Magic", "Wonder", "Beautiful", "Crazy"
]

TITLE_PATTERNS = [
    "{word1}",
    "The {word1}",
    "{word1} {word2}",
    "The {word1} of {word2}",
    "{word1} and {word2}",
    "My {word1}",
    "Your {word1}",
    "{word1} in the {word2}",
    "When {word1} Meets {word2}",
    "{word1} Tonight",
    "{word1} Forever",
    "Endless {word1}",
    "One More {word1}",
    "Last {word1}",
    "First {word1}"
]

PUBLISHERS = [
    "Sony/ATV", "Universal Music Publishing", "Warner Chappell", "BMG Rights Management",
    "Kobalt Music", "Downtown Music Publishing", "Concord Music", "Reservoir Media",
    "Spirit Music Group", "Round Hill Music", "Primary Wave", "Hipgnosis Songs",
    "peermusic", "ole", "Pulse Music Group", "Position Music"
]

GENRES = ["Rock", "Pop", "R&B", "Country", "Hip-Hop", "Electronic", "Jazz", "Folk", "Soul", "Blues"]


def generate_songwriter():
    """Generate a random songwriter name."""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{last}, {first}"


def generate_title():
    """Generate a random song title."""
    pattern = random.choice(TITLE_PATTERNS)
    word1 = random.choice(TITLE_WORDS)
    word2 = random.choice([w for w in TITLE_WORDS if w != word1])
    return pattern.format(word1=word1, word2=word2)


def generate_iswc(index):
    """Generate a plausible ISWC."""
    return f"T-{str(index).zfill(3)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(0, 9)}"


def generate_work(index):
    """Generate a single work entry."""
    num_writers = random.choices([1, 2, 3, 4], weights=[0.4, 0.35, 0.2, 0.05])[0]
    songwriters = [generate_songwriter() for _ in range(num_writers)]

    num_publishers = random.choices([1, 2], weights=[0.7, 0.3])[0]
    publishers = random.sample(PUBLISHERS, num_publishers)

    return {
        "work_code": f"WRK{str(index).zfill(6)}",
        "title": generate_title(),
        "songwriters": songwriters,
        "publishers": publishers,
        "release_year": random.randint(1950, 2024),
        "genre": random.choice(GENRES),
        "iswc": generate_iswc(index) if random.random() > 0.1 else None
    }


def generate_sql_insert(work):
    """Generate SQL INSERT statement for a work."""
    songwriters = "ARRAY[" + ", ".join(f"'{sw}'" for sw in work["songwriters"]) + "]"
    publishers = "ARRAY[" + ", ".join(f"'{pub}'" for pub in work["publishers"]) + "]"
    iswc = f"'{work['iswc']}'" if work["iswc"] else "NULL"

    return f"""('{work["work_code"]}', '{work["title"].replace("'", "''")}', {songwriters}, {publishers}, {work["release_year"]}, '{work["genre"]}', {iswc})"""


def main():
    print("-- Generated works data")
    print("-- This file contains 10,000 music works for testing")
    print()
    print("INSERT INTO works (work_code, title, songwriters, publishers, release_year, genre, iswc) VALUES")

    works = []
    for i in range(101, 10001):  # Start from 101 as seed_works.sql has 1-100
        work = generate_work(i)
        works.append(generate_sql_insert(work))

    print(",\n".join(works) + ";")


if __name__ == "__main__":
    main()
