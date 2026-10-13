"""
Quiz Royale — Seed Questions Dataset for General Knowledge, STEM, and Culture:
- Mathematics (mathematics)
- Logical Reasoning (logic)
- Science (science)
- General Knowledge (gk)
- Sports (sports)
- Movies and Entertainment (movies)
"""

GENERAL_CATEGORIES = [
    {
        "slug": "mathematics",
        "name": "Mathematics",
        "description": "Calculus, linear algebra, probability, discrete math, and arithmetic puzzles.",
        "icon": "percent",
        "color_hex": "#8b5cf6",
        "sort_order": 9,
    },
    {
        "slug": "logic",
        "name": "Logical Reasoning",
        "description": "Puzzles, deductions, syllogisms, pattern recognition, and analytical aptitude.",
        "icon": "zap",
        "color_hex": "#a855f7",
        "sort_order": 10,
    },
    {
        "slug": "science",
        "name": "Science",
        "description": "Physics, chemistry, astronomy, biology, and scientific breakthroughs.",
        "icon": "activity",
        "color_hex": "#14b8a6",
        "sort_order": 11,
    },
    {
        "slug": "gk",
        "name": "General Knowledge",
        "description": "World geography, history, geopolitics, landmarks, and global trivia.",
        "icon": "compass",
        "color_hex": "#f59e0b",
        "sort_order": 12,
    },
    {
        "slug": "sports",
        "name": "Sports",
        "description": "Football, cricket, basketball, olympics, champions, and athletic records.",
        "icon": "award",
        "color_hex": "#10b981",
        "sort_order": 13,
    },
    {
        "slug": "movies",
        "name": "Movies & Entertainment",
        "description": "Cinema history, directors, Oscars, soundtrack scores, and pop culture.",
        "icon": "film",
        "color_hex": "#f43f5e",
        "sort_order": 14,
    },
]

GENERAL_QUESTIONS = [
    # Mathematics - Easy
    {
        "category_slug": "mathematics",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "What is the derivative of f(x) = x^3 with respect to x?",
        "options": [
            {"text": "3x^2", "is_correct": True},
            {"text": "x^2", "is_correct": False},
            {"text": "3x", "is_correct": False},
            {"text": "6x", "is_correct": False},
        ],
        "explanation": "Applying the power rule d/dx [x^n] = n*x^(n-1) gives 3*x^2.",
    },
    {
        "category_slug": "mathematics",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "What is the sum of interior angles in a hexagon?",
        "options": [
            {"text": "720 degrees", "is_correct": True},
            {"text": "540 degrees", "is_correct": False},
            {"text": "360 degrees", "is_correct": False},
            {"text": "1080 degrees", "is_correct": False},
        ],
        "explanation": "The formula for sum of interior angles is (n - 2) * 180. For a hexagon (n=6), (6-2)*180 = 720 degrees.",
    },
    # Mathematics - Medium
    {
        "category_slug": "mathematics",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 20,
        "question_text": "If a fair 6-sided die is rolled twice, what is the probability that the sum of outcomes is 7?",
        "options": [
            {"text": "1/6", "is_correct": True},
            {"text": "1/12", "is_correct": False},
            {"text": "7/36", "is_correct": False},
            {"text": "5/36", "is_correct": False},
        ],
        "explanation": "There are 6 winning pairs out of 36 outcomes: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1). 6/36 = 1/6.",
    },
    # Mathematics - Hard
    {
        "category_slug": "mathematics",
        "difficulty": "hard",
        "points": 300,
        "time_limit_sec": 20,
        "question_text": "What is Euler's identity relating e, i, pi, 1, and 0?",
        "options": [
            {"text": "e^(i*pi) + 1 = 0", "is_correct": True},
            {"text": "e^(2*pi) - 1 = 0", "is_correct": False},
            {"text": "e^pi + i = 0", "is_correct": False},
            {"text": "i^2 * pi + e = 0", "is_correct": False},
        ],
        "explanation": "Euler's identity e^(i*pi) + 1 = 0 is considered one of the most beautiful equations in mathematics.",
    },

    # Logical Reasoning - Easy
    {
        "category_slug": "logic",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "Find the missing number in the sequence: 2, 4, 8, 16, ___",
        "options": [
            {"text": "32", "is_correct": True},
            {"text": "24", "is_correct": False},
            {"text": "30", "is_correct": False},
            {"text": "64", "is_correct": False},
        ],
        "explanation": "Each number is multiplied by 2 (powers of 2). 16 * 2 = 32.",
    },
    # Logical Reasoning - Medium
    {
        "category_slug": "logic",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 20,
        "question_text": "All squares are rectangles. Some rectangles are red. Therefore:",
        "options": [
            {"text": "Some rectangles may or may not be squares", "is_correct": True},
            {"text": "All red shapes are squares", "is_correct": False},
            {"text": "No square is red", "is_correct": False},
            {"text": "All squares are red", "is_correct": False},
        ],
        "explanation": "A square is a special case of a rectangle, but the premises do not guarantee that any square is red.",
    },

    # Science - Easy
    {
        "category_slug": "science",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "What is the chemical symbol for Gold?",
        "options": [
            {"text": "Au", "is_correct": True},
            {"text": "Ag", "is_correct": False},
            {"text": "Fe", "is_correct": False},
            {"text": "Pb", "is_correct": False},
        ],
        "explanation": "The symbol Au comes from the Latin word 'Aurum', meaning shining dawn or gold.",
    },
    # Science - Medium
    {
        "category_slug": "science",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "What subatomic particle was discovered by J.J. Thomson via cathode ray tube experiments?",
        "options": [
            {"text": "Electron", "is_correct": True},
            {"text": "Proton", "is_correct": False},
            {"text": "Neutron", "is_correct": False},
            {"text": "Positron", "is_correct": False},
        ],
        "explanation": "In 1897, J.J. Thomson demonstrated that cathode rays were composed of negatively charged particles named electrons.",
    },

    # General Knowledge - Easy
    {
        "category_slug": "gk",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "Which is the largest ocean on Earth by surface area?",
        "options": [
            {"text": "Pacific Ocean", "is_correct": True},
            {"text": "Atlantic Ocean", "is_correct": False},
            {"text": "Indian Ocean", "is_correct": False},
            {"text": "Arctic Ocean", "is_correct": False},
        ],
        "explanation": "The Pacific Ocean covers more than 30% of the Earth's surface.",
    },
    # General Knowledge - Medium
    {
        "category_slug": "gk",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "In which city is the headquarters of the International Court of Justice located?",
        "options": [
            {"text": "The Hague, Netherlands", "is_correct": True},
            {"text": "Geneva, Switzerland", "is_correct": False},
            {"text": "Brussels, Belgium", "is_correct": False},
            {"text": "New York, USA", "is_correct": False},
        ],
        "explanation": "The ICJ sits at the Peace Palace in The Hague, Netherlands.",
    },

    # Sports - Easy
    {
        "category_slug": "sports",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "How many players are on the field for one team in a standard association football (soccer) match?",
        "options": [
            {"text": "11", "is_correct": True},
            {"text": "9", "is_correct": False},
            {"text": "10", "is_correct": False},
            {"text": "12", "is_correct": False},
        ],
        "explanation": "A standard soccer team fields 11 players including the goalkeeper.",
    },
    # Sports - Medium
    {
        "category_slug": "sports",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "Which tennis player holds the record for winning 14 French Open (Roland Garros) men's singles titles?",
        "options": [
            {"text": "Rafael Nadal", "is_correct": True},
            {"text": "Roger Federer", "is_correct": False},
            {"text": "Novak Djokovic", "is_correct": False},
            {"text": "Bjorn Borg", "is_correct": False},
        ],
        "explanation": "Rafael Nadal, the 'King of Clay', achieved an unprecedented 14 Roland Garros crowns.",
    },

    # Movies - Easy
    {
        "category_slug": "movies",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "Who directed the 2010 sci-fi mind-heist film 'Inception'?",
        "options": [
            {"text": "Christopher Nolan", "is_correct": True},
            {"text": "Denis Villeneuve", "is_correct": False},
            {"text": "Steven Spielberg", "is_correct": False},
            {"text": "James Cameron", "is_correct": False},
        ],
        "explanation": "Christopher Nolan wrote and directed Inception starring Leonardo DiCaprio.",
    },
    # Movies - Medium
    {
        "category_slug": "movies",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "Which movie was the first non-English language film to win the Academy Award for Best Picture?",
        "options": [
            {"text": "Parasite (2019)", "is_correct": True},
            {"text": "Life Is Beautiful (1997)", "is_correct": False},
            {"text": "Roma (2018)", "is_correct": False},
            {"text": "Crouching Tiger, Hidden Dragon (2000)", "is_correct": False},
        ],
        "explanation": "Bong Joon-ho's South Korean film 'Parasite' won Best Picture at the 92nd Academy Awards in 2020.",
    },
]
