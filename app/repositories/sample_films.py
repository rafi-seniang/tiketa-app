"""The films on the programme (Tiketa v1's list), one studio each."""

from typing import Any

TMDB = "https://image.tmdb.org/t/p/original"

SAMPLE_MOVIES: list[dict[str, Any]] = [
    {
        "title": "Spirited Away",
        "synopsis": (
            "Ten-year-old Chihiro wanders into a hidden town of spirits, where her parents are turned into pigs. "
            "To free them she takes a job in a bathhouse for the gods, gives up her name to the witch who runs "
            "it, and has to remember who she is before the way home disappears."
        ),
        "release_year": 2001,
        "genres": ["Animation", "Fantasy", "Family"],
        "studio_number": 1,
        "poster_url": "https://images.weserv.nl/?url=theposterdb.com/api/assets/111928/view",
        "backdrop_url": f"{TMDB}/m4TUa2ciEWSlk37rOsjiSIvZDXE.jpg",
        "trailer_youtube_id": "GAp2_0JJskk",
    },
    {
        "title": "Your Name",
        "synopsis": (
            "Mitsuha, bored in a mountain town, and Taki, a Tokyo schoolboy, start waking up in each other's "
            "bodies a few days a week. They leave notes to keep their lives straight, until the swaps stop and "
            "Taki sets out to find a girl he has never met, before a comet changes everything."
        ),
        "release_year": 2016,
        "genres": ["Animation", "Drama", "Romance"],
        "studio_number": 2,
        "poster_url": "https://images.weserv.nl/?url=theposterdb.com/api/assets/90914/view",
        "backdrop_url": f"{TMDB}/mMtUybQ6hL24FXo0F3Z4j2KG7kZ.jpg",
        "trailer_youtube_id": "k4xGqY5IDBE",
    },
    {
        "title": "Akira",
        "synopsis": (
            "In Neo-Tokyo, rebuilt after a war, biker gang leader Kaneda watches his friend Tetsuo taken by the "
            "army after a crash. Experiments wake a power in Tetsuo that he cannot control, and it leads him to "
            "the secret the government buried under the city."
        ),
        "release_year": 1988,
        "genres": ["Animation", "Action", "Science Fiction"],
        "studio_number": 3,
        "poster_url": f"{TMDB}/6pG3nVF7uWvFPCrNRBGwZqFhoQT.jpg",
        "backdrop_url": f"{TMDB}/fK40VGYIm7hmKrLJ26fgPQU0qRG.jpg",
        "trailer_youtube_id": "nA8KmHC2Z-g",
    },
    {
        "title": "Ghost in the Shell",
        "synopsis": (
            "In 2029 Major Motoko Kusanagi, a cyborg with an almost fully artificial body, leads Section 9 "
            "against a hacker who rewrites people's memories. The chase brings her face to face with a being that "
            "asks what makes her human at all."
        ),
        "release_year": 1995,
        "genres": ["Animation", "Science Fiction", "Thriller"],
        "studio_number": 4,
        "poster_url": "https://images.weserv.nl/?url=theposterdb.com/api/assets/98465/view",
        "backdrop_url": f"{TMDB}/jIpagj2Dud9g3ZVJFvaWikEWsYz.jpg",
        "trailer_youtube_id": "rU6Matng9MU",
    },
    {
        "title": "Attack on Titan: The Last Attack",
        "synopsis": (
            "Eren has set the Rumbling in motion: countless Titans march to flatten the world beyond the island. "
            "His oldest friends and their former enemies join forces for one last fight to stop him, the story's "
            "two final episodes told as one film for the big screen."
        ),
        "release_year": 2024,
        "genres": ["Animation", "Action", "Drama"],
        "studio_number": 5,
        "poster_url": f"{TMDB}/wgwldDDlTDDMrluOMkpSA8lyKjv.jpg",
        "backdrop_url": f"{TMDB}/yPJyXYfDrlD7bEjAtTAQ8nqmRIf.jpg",
        "trailer_youtube_id": None,
    },
    {
        "title": "Mobile Suit Gundam SEED Freedom",
        "synopsis": (
            "In the uneasy peace after the war, Kira Yamato and Lacus Clyne lead COMPASS, a force that steps in "
            "wherever fighting breaks out. A new nation, Foundation, offers a joint operation, and Kira is pulled "
            "into a conflict that tests everything he fought for."
        ),
        "release_year": 2024,
        "genres": ["Animation", "Action", "Science Fiction"],
        "studio_number": 6,
        "poster_url": f"{TMDB}/1EBnttleJaKnWWyyEqfiSn76ZjT.jpg",
        "backdrop_url": f"{TMDB}/fU3oaBud5SZadw6k1ycftYedmXJ.jpg",
        "trailer_youtube_id": "Gsj6ToFTGgc",
    },
    {
        "title": "Interstellar",
        "synopsis": (
            "With crops failing and dust storms covering the Earth, former pilot Cooper leaves his children to "
            "fly through a wormhole near Saturn. His crew searches for a planet humanity can move to, while time "
            "runs differently for them than for the family waiting at home."
        ),
        "release_year": 2014,
        "genres": ["Adventure", "Drama", "Science Fiction"],
        "studio_number": 7,
        "poster_url": f"{TMDB}/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "backdrop_url": f"{TMDB}/8sNiAPPYU14PUepFNeSNGUTiHW.jpg",
        "trailer_youtube_id": "zSWdZVtXT7E",
    },
    {
        "title": "Blade Runner 2049",
        "synopsis": (
            "Thirty years after the first film, K, a replicant who hunts older replicants for the police, finds "
            "the remains of a woman who gave birth. The discovery could break the order between humans and "
            "machines, and it leads him to Rick Deckard, missing for decades."
        ),
        "release_year": 2017,
        "genres": ["Drama", "Science Fiction", "Thriller"],
        "studio_number": 8,
        "poster_url": f"{TMDB}/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg",
        "backdrop_url": f"{TMDB}/gNdLJU9TxrpGx4dkZidjys3fyy0.jpg",
        "trailer_youtube_id": "gCcx85zbxz4",
    },
    {
        "title": "Dune: Part Two",
        "synopsis": (
            "Paul Atreides joins Chani and the Fremen in the deserts of Arrakis and wages war on the house that "
            "destroyed his family. As the Fremen begin to see him as their messiah, he must choose between the "
            "woman he loves and a future he has seen in visions."
        ),
        "release_year": 2024,
        "genres": ["Adventure", "Drama", "Science Fiction"],
        "studio_number": 9,
        "poster_url": f"{TMDB}/6izwz7rsy95ARzTR3poZ8H6c5pp.jpg",
        "backdrop_url": f"{TMDB}/eZ239CUp1d6OryZEBPnO2n87gMG.jpg",
        "trailer_youtube_id": "U2Qp5pL3ovA",
    },
    {
        "title": "The Matrix",
        "synopsis": (
            "Thomas Anderson, a programmer who hacks at night as Neo, learns from the rebel Morpheus that the "
            "world he knows is a simulation built by machines to keep people asleep. Freed from it, he trains to "
            "fight back from inside the code."
        ),
        "release_year": 1999,
        "genres": ["Action", "Science Fiction"],
        "studio_number": 10,
        "poster_url": f"{TMDB}/p96dm7sCMn4VYAStA6siNz30G1r.jpg",
        "backdrop_url": f"{TMDB}/tlm8UkiQsitc8rSuIAscQDCnP8d.jpg",
        "trailer_youtube_id": "vKQi3bBA1y8",
    },
    {
        "title": "Star Wars: A New Hope",
        "synopsis": (
            "Farm boy Luke Skywalker finds a message from Princess Leia hidden in a droid and joins the old Jedi "
            "Obi-Wan Kenobi, the smuggler Han Solo and Chewbacca to rescue her. Together they carry the plans "
            "that could destroy the Empire's Death Star."
        ),
        "release_year": 1977,
        "genres": ["Adventure", "Action", "Science Fiction"],
        "studio_number": 11,
        "poster_url": f"{TMDB}/2Cm0oygiJpk7tzboSvX8F86v8PW.jpg",
        "backdrop_url": f"{TMDB}/4qCqAdHcNKeAHcK8tJ8wNJZa9cx.jpg",
        "trailer_youtube_id": "vZ734NWnAHA",
    },
    {
        "title": "Mad Max: Fury Road",
        "synopsis": (
            "In a desert wasteland, Imperator Furiosa drives off with the five wives of the warlord Immortan Joe, "
            "and the drifter Max ends up on her side. What follows is one long chase across the sand, with the "
            "warlord's whole army behind them."
        ),
        "release_year": 2015,
        "genres": ["Action", "Adventure", "Science Fiction"],
        "studio_number": 12,
        "poster_url": f"{TMDB}/hA2ple9q4qnwxp3hKVNhroipsir.jpg",
        "backdrop_url": f"{TMDB}/gqrnQA6Xppdl8vIb2eJc58VC1tW.jpg",
        "trailer_youtube_id": "hEJnMQG9ev8",
    },
    {
        "title": "Everything Everywhere All at Once",
        "synopsis": (
            "Evelyn Wang, buried in her laundromat's tax audit and a strained family, learns that she can borrow "
            "the skills of her selves in other universes. Only she can stop a power that threatens every one of "
            "them, and it wears her daughter's face."
        ),
        "release_year": 2022,
        "genres": ["Action", "Comedy", "Science Fiction"],
        "studio_number": 13,
        "poster_url": f"{TMDB}/u68AjlvlutfEIcpmbYpKcdi09ut.jpg",
        "backdrop_url": f"{TMDB}/fIwiFha3WPu5nHkBeMQ4GzEk0Hv.jpg",
        "trailer_youtube_id": "wxN1T1uxQ2g",
    },
    {
        "title": "Black Panther",
        "synopsis": (
            "After his father's death, T'Challa returns home to Wakanda, a hidden and advanced African nation, to "
            "take the throne as its king and the Black Panther. A challenger with a claim of his own forces him "
            "to decide what Wakanda owes the rest of the world."
        ),
        "release_year": 2018,
        "genres": ["Action", "Adventure", "Science Fiction"],
        "studio_number": 14,
        "poster_url": f"{TMDB}/uxzzxijgPIY7slzFvMotPv8wjKA.jpg",
        "backdrop_url": f"{TMDB}/b6ZJZHUdMEFECvGiDpJjlfUWela.jpg",
        "trailer_youtube_id": "xjDjIWPwcPU",
    },
    {
        "title": "The Dark Knight",
        "synopsis": (
            "Batman, Lieutenant Gordon and the new district attorney Harvey Dent are winning their war on "
            "Gotham's mob. Then the Joker arrives, a criminal who wants nothing but chaos, and pushes each of "
            "them to the limit of what they believe."
        ),
        "release_year": 2008,
        "genres": ["Action", "Crime", "Drama"],
        "studio_number": 15,
        "poster_url": f"{TMDB}/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "backdrop_url": f"{TMDB}/cfT29Im5VDvjE0RpyKOSdCKZal7.jpg",
        "trailer_youtube_id": "EXeTwQWrcwY",
    },
    {
        "title": "Inception",
        "synopsis": (
            "Dom Cobb steals secrets from inside people's dreams. Offered a way home to his children, he takes on "
            "the reverse: planting an idea in a businessman's mind, through a dream inside a dream inside a "
            "dream, while his own past follows him down."
        ),
        "release_year": 2010,
        "genres": ["Action", "Science Fiction", "Thriller"],
        "studio_number": 16,
        "poster_url": f"{TMDB}/ljsZTbVsrQSqZgWeep2B1QiDKuh.jpg",
        "backdrop_url": f"{TMDB}/8ZTVqvKDQ8emSGUEMjsS4yHAwrp.jpg",
        "trailer_youtube_id": "YoHD9XEInc0",
    },
    {
        "title": "Pulp Fiction",
        "synopsis": (
            "Two hitmen, a boxer who will not throw a fight, a gangster's wife and a pair of diner robbers cross "
            "paths in Los Angeles. Their stories are told out of order and meet in ways none of them sees coming."
        ),
        "release_year": 1994,
        "genres": ["Crime", "Thriller"],
        "studio_number": 17,
        "poster_url": f"{TMDB}/vQWk5YBFWF4bZaofAbv0tShwBvQ.jpg",
        "backdrop_url": f"{TMDB}/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg",
        "trailer_youtube_id": "s7EdQ4FqbhY",
    },
    {
        "title": "Parasite",
        "synopsis": (
            "The Kims, out of work in a semi-basement flat, talk their way one by one into jobs with the wealthy "
            "Park family. The plan works perfectly until a visitor on a rainy night reveals what the Parks' house "
            "has been hiding."
        ),
        "release_year": 2019,
        "genres": ["Comedy", "Drama", "Thriller"],
        "studio_number": 18,
        "poster_url": f"{TMDB}/nMF2GX9SriEMbixRvI23KZwCs0U.jpg",
        "backdrop_url": f"{TMDB}/TU9NIjwzjoKPwQHoHshkFcQUCG.jpg",
        "trailer_youtube_id": "SEUXfv87Wpk",
    },
    {
        "title": "The Lord of the Rings: The Fellowship of the Ring",
        "synopsis": (
            "The hobbit Frodo inherits a ring that holds the power of the Dark Lord Sauron. With eight companions "
            "he sets out from the Shire to destroy it in the fires of Mount Doom, the one place where it can be "
            "unmade."
        ),
        "release_year": 2001,
        "genres": ["Adventure", "Fantasy", "Action"],
        "studio_number": 19,
        "poster_url": f"{TMDB}/6oom5QYQ2yQTMJIbnvbkBL9cHo6.jpg",
        "backdrop_url": f"{TMDB}/oiwc338EoBgS4sEI2ixAny4KQKg.jpg",
        "trailer_youtube_id": "V75dMMIW2B4",
    },
    {
        "title": "Coco",
        "synopsis": (
            "Miguel dreams of music in a family that has banned it for generations. On the Day of the Dead he "
            "crosses into the Land of the Dead, where he has until sunrise to find his musician "
            "great-great-grandfather and get home."
        ),
        "release_year": 2017,
        "genres": ["Animation", "Adventure", "Family"],
        "studio_number": 20,
        "poster_url": f"{TMDB}/6Ryitt95xrO8KXuqRGm1fUuNwqF.jpg",
        "backdrop_url": f"{TMDB}/g7CHF8gTLGooTbP4GznIGwaqAGL.jpg",
        "trailer_youtube_id": "Rvr68u6k5sI",
    },
    {
        "title": "La La Land",
        "synopsis": (
            "In Los Angeles, Sebastian, a jazz pianist who wants his own club, and Mia, an actress between "
            "auditions, fall in love over a year of seasons. Their dreams start to pull them apart as each one "
            "comes within reach."
        ),
        "release_year": 2016,
        "genres": ["Comedy", "Drama", "Romance"],
        "studio_number": 21,
        "poster_url": f"{TMDB}/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg",
        "backdrop_url": f"{TMDB}/nlPCdZlHtRNcF6C9hzUH4ebmV1w.jpg",
        "trailer_youtube_id": "0pdqf4P9MB8",
    },
]
