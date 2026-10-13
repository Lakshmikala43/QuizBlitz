"""
Quiz Royale — Seed Questions Dataset for Core Computer Science:
- Data Structures and Algorithms (dsa)
- DBMS and SQL (dbms-sql)
- Operating Systems (os)
- Computer Networks (networks)
- Cybersecurity (cybersecurity)
"""

CS_CATEGORIES = [
    {
        "slug": "dsa",
        "name": "Data Structures & Algorithms",
        "description": "Trees, graphs, dynamic programming, sorting, complexity analysis, and algorithms.",
        "icon": "git-merge",
        "color_hex": "#10b981",
        "sort_order": 4,
    },
    {
        "slug": "dbms-sql",
        "name": "DBMS & SQL",
        "description": "Relational algebra, SQL queries, indexing, ACID transactions, and database normalization.",
        "icon": "database",
        "color_hex": "#06b6d4",
        "sort_order": 5,
    },
    {
        "slug": "os",
        "name": "Operating Systems",
        "description": "Process scheduling, synchronization, virtual memory, paging, and deadlocks.",
        "icon": "layers",
        "color_hex": "#eab308",
        "sort_order": 6,
    },
    {
        "slug": "networks",
        "name": "Computer Networks",
        "description": "TCP/IP, OSI model, HTTP/3, routing protocols, DNS, and socket programming.",
        "icon": "globe",
        "color_hex": "#ec4899",
        "sort_order": 7,
    },
    {
        "slug": "cybersecurity",
        "name": "Cybersecurity",
        "description": "Cryptography, network defense, penetration testing, authentication, and secure protocols.",
        "icon": "shield",
        "color_hex": "#ef4444",
        "sort_order": 8,
    },
]

CS_QUESTIONS = [
    # DSA - Easy
    {
        "category_slug": "dsa",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "What is the worst-case time complexity of binary search on a sorted array of size N?",
        "options": [
            {"text": "O(log N)", "is_correct": True},
            {"text": "O(N)", "is_correct": False},
            {"text": "O(N log N)", "is_correct": False},
            {"text": "O(1)", "is_correct": False},
        ],
        "explanation": "Binary search divides the search space in half with every comparison, yielding O(log N) time.",
    },
    {
        "category_slug": "dsa",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "Which data structure operates on a Last-In, First-Out (LIFO) principle?",
        "options": [
            {"text": "Stack", "is_correct": True},
            {"text": "Queue", "is_correct": False},
            {"text": "Array", "is_correct": False},
            {"text": "Hash Map", "is_correct": False},
        ],
        "explanation": "Stacks push and pop elements from the top, obeying the LIFO order.",
    },
    # DSA - Medium
    {
        "category_slug": "dsa",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "What is the balance factor of a node in an AVL tree?",
        "options": [
            {"text": "Height of Left Subtree minus Height of Right Subtree", "is_correct": True},
            {"text": "Total nodes in Left Subtree minus Total in Right", "is_correct": False},
            {"text": "Depth of the node from root", "is_correct": False},
            {"text": "Degree of node multiplied by height", "is_correct": False},
        ],
        "explanation": "In an AVL tree, the balance factor is defined as height(left) - height(right) and must stay within {-1, 0, 1}.",
    },
    {
        "category_slug": "dsa",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "Which algorithm finds the shortest path from a single source in a weighted graph with non-negative edge weights?",
        "options": [
            {"text": "Dijkstra's Algorithm", "is_correct": True},
            {"text": "Kruskal's Algorithm", "is_correct": False},
            {"text": "Prim's Algorithm", "is_correct": False},
            {"text": "Tarjan's SCC Algorithm", "is_correct": False},
        ],
        "explanation": "Dijkstra's algorithm greedily extracts vertices with minimal known distance using a priority queue.",
    },
    # DSA - Hard
    {
        "category_slug": "dsa",
        "difficulty": "hard",
        "points": 300,
        "time_limit_sec": 20,
        "question_text": "What is the amortized time complexity of the decrease-key operation in a Fibonacci Heap?",
        "options": [
            {"text": "O(1)", "is_correct": True},
            {"text": "O(log N)", "is_correct": False},
            {"text": "O(N)", "is_correct": False},
            {"text": "O(N log N)", "is_correct": False},
        ],
        "explanation": "Fibonacci heaps achieve O(1) amortized time for insert, find-min, and decrease-key operations.",
    },

    # DBMS & SQL - Easy
    {
        "category_slug": "dbms-sql",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "Which SQL clause is used to filter aggregated group results?",
        "options": [
            {"text": "HAVING", "is_correct": True},
            {"text": "WHERE", "is_correct": False},
            {"text": "FILTER", "is_correct": False},
            {"text": "GROUP BY", "is_correct": False},
        ],
        "explanation": "`WHERE` filters rows before grouping, while `HAVING` filters group summaries produced by `GROUP BY`.",
    },
    {
        "category_slug": "dbms-sql",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "What does the 'A' represent in the ACID transaction acronym?",
        "options": [
            {"text": "Atomicity", "is_correct": True},
            {"text": "Availability", "is_correct": False},
            {"text": "Authorization", "is_correct": False},
            {"text": "Asynchrony", "is_correct": False},
        ],
        "explanation": "ACID stands for Atomicity, Consistency, Isolation, and Durability.",
    },
    # DBMS & SQL - Medium
    {
        "category_slug": "dbms-sql",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "What anomaly does the 'Repeatable Read' transaction isolation level prevent?",
        "options": [
            {"text": "Non-repeatable reads", "is_correct": True},
            {"text": "Phantom reads in all standard SQL implementations", "is_correct": False},
            {"text": "Dirty writes only", "is_correct": False},
            {"text": "Deadlock occurrence", "is_correct": False},
        ],
        "explanation": "Repeatable Read guarantees that any data read during a transaction will not change when re-read in that same transaction.",
    },
    # DBMS & SQL - Hard
    {
        "category_slug": "dbms-sql",
        "difficulty": "hard",
        "points": 300,
        "time_limit_sec": 20,
        "question_text": "Which normal form requires every determinant in a relation to be a candidate key?",
        "options": [
            {"text": "Boyce-Codd Normal Form (BCNF)", "is_correct": True},
            {"text": "Third Normal Form (3NF)", "is_correct": False},
            {"text": "Second Normal Form (2NF)", "is_correct": False},
            {"text": "Fourth Normal Form (4NF)", "is_correct": False},
        ],
        "explanation": "BCNF is a stricter version of 3NF where for every functional dependency X -> Y, X must be a superkey.",
    },

    # Operating Systems - Easy
    {
        "category_slug": "os",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "What state does a process enter when waiting for an I/O operation to finish?",
        "options": [
            {"text": "Blocked / Waiting", "is_correct": True},
            {"text": "Ready", "is_correct": False},
            {"text": "Running", "is_correct": False},
            {"text": "Terminated", "is_correct": False},
        ],
        "explanation": "A process waiting for an external event (like disk or network I/O) moves from Running to Waiting/Blocked.",
    },
    # Operating Systems - Medium
    {
        "category_slug": "os",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "Which algorithm is used by operating systems to detect or avoid deadlocks dynamically?",
        "options": [
            {"text": "Banker's Algorithm", "is_correct": True},
            {"text": "Round Robin", "is_correct": False},
            {"text": "K-Means Clustering", "is_correct": False},
            {"text": "Shortest Job Next", "is_correct": False},
        ],
        "explanation": "Dijkstra's Banker's Algorithm simulates resource allocation to verify that a safe state can be maintained before granting resources.",
    },
    # Operating Systems - Hard
    {
        "category_slug": "os",
        "difficulty": "hard",
        "points": 300,
        "time_limit_sec": 20,
        "question_text": "What phenomenon occurs when increasing the number of page frames causes more page faults in FIFO replacement?",
        "options": [
            {"text": "Belady's Anomaly", "is_correct": True},
            {"text": "Thrashing Effect", "is_correct": False},
            {"text": "Amdahl's Paradox", "is_correct": False},
            {"text": "False Sharing", "is_correct": False},
        ],
        "explanation": "Belady's Anomaly demonstrates that certain page references with FIFO replacement trigger more page faults despite allocating more physical frames.",
    },

    # Networks - Easy
    {
        "category_slug": "networks",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "Which protocol operates at the Transport layer and provides reliable, ordered data stream delivery?",
        "options": [
            {"text": "TCP", "is_correct": True},
            {"text": "UDP", "is_correct": False},
            {"text": "IP", "is_correct": False},
            {"text": "ICMP", "is_correct": False},
        ],
        "explanation": "TCP (Transmission Control Protocol) is connection-oriented and provides reliable, sequence-verified transmissions.",
    },
    # Networks - Medium
    {
        "category_slug": "networks",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "What underlying transport protocol does HTTP/3 utilize instead of TCP?",
        "options": [
            {"text": "QUIC (UDP-based)", "is_correct": True},
            {"text": "SCTP", "is_correct": False},
            {"text": "Raw IP", "is_correct": False},
            {"text": "TLS Over WebSocket", "is_correct": False},
        ],
        "explanation": "HTTP/3 uses QUIC over UDP to eliminate head-of-line blocking and accelerate handshake connection times.",
    },

    # Cybersecurity - Easy
    {
        "category_slug": "cybersecurity",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "Which security vulnerability allows an attacker to inject client-side scripts into web pages viewed by other users?",
        "options": [
            {"text": "Cross-Site Scripting (XSS)", "is_correct": True},
            {"text": "SQL Injection (SQLi)", "is_correct": False},
            {"text": "Cross-Site Request Forgery (CSRF)", "is_correct": False},
            {"text": "Denial of Service (DoS)", "is_correct": False},
        ],
        "explanation": "XSS occurs when malicious scripts are embedded into benign and trusted websites without output sanitization.",
    },
    # Cybersecurity - Medium
    {
        "category_slug": "cybersecurity",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "What is the purpose of adding a cryptographic 'salt' before hashing a password?",
        "options": [
            {"text": "To defend against precomputed rainbow table attacks", "is_correct": True},
            {"text": "To compress the password string to 32 bits", "is_correct": False},
            {"text": "To make password hashing reversible by administrators", "is_correct": False},
            {"text": "To encrypt the password using symmetric AES keys", "is_correct": False},
        ],
        "explanation": "A unique cryptographic salt ensures two identical passwords result in different hashes, mitigating rainbow tables and dictionary attacks.",
    },
    # Cybersecurity - Hard
    {
        "category_slug": "cybersecurity",
        "difficulty": "hard",
        "points": 300,
        "time_limit_sec": 20,
        "question_text": "In asymmetric cryptography, which hard computational problem forms the basis for RSA encryption?",
        "options": [
            {"text": "Integer factorization of large semiprime numbers", "is_correct": True},
            {"text": "Discrete logarithm problem on elliptic curves", "is_correct": False},
            {"text": "Solving systems of linear diophantine equations", "is_correct": False},
            {"text": "Subset sum NP-complete decision problem", "is_correct": False},
        ],
        "explanation": "RSA relies on the mathematical difficulty of factoring the product of two large prime numbers.",
    },
]
