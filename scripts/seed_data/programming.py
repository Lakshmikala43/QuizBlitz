"""
Quiz Royale — Seed Questions Dataset for Programming Languages:
- Python
- Java
- C and C++
"""

PROGRAMMING_CATEGORIES = [
    {
        "slug": "python",
        "name": "Python",
        "description": "Python programming language, syntax, OOP, standard library, and runtime semantics.",
        "icon": "code",
        "color_hex": "#38bdf8",
        "sort_order": 1,
    },
    {
        "slug": "java",
        "name": "Java",
        "description": "Core Java, JVM internals, multithreading, collections, and object-oriented design.",
        "icon": "coffee",
        "color_hex": "#f97316",
        "sort_order": 2,
    },
    {
        "slug": "c-cpp",
        "name": "C and C++",
        "description": "Pointers, memory management, templates, standard template library (STL), and low-level computing.",
        "icon": "cpu",
        "color_hex": "#6366f1",
        "sort_order": 3,
    },
]

PROGRAMMING_QUESTIONS = [
    # Python - Easy
    {
        "category_slug": "python",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "What is the output of bool([]) in Python?",
        "options": [
            {"text": "False", "is_correct": True},
            {"text": "True", "is_correct": False},
            {"text": "None", "is_correct": False},
            {"text": "TypeError", "is_correct": False},
        ],
        "explanation": "Empty collections (lists, tuples, dicts, sets, strings) evaluate to False in a boolean context.",
    },
    {
        "category_slug": "python",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "Which built-in function returns the length of a sequence in Python?",
        "options": [
            {"text": "len()", "is_correct": True},
            {"text": "size()", "is_correct": False},
            {"text": "length()", "is_correct": False},
            {"text": "count()", "is_correct": False},
        ],
        "explanation": "len() is Python's built-in function to query the length of a container or collection.",
    },
    {
        "category_slug": "python",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "Which data type in Python is immutable?",
        "options": [
            {"text": "Tuple", "is_correct": True},
            {"text": "List", "is_correct": False},
            {"text": "Dictionary", "is_correct": False},
            {"text": "Set", "is_correct": False},
        ],
        "explanation": "Tuples are immutable; once instantiated, their elements cannot be modified, added, or removed.",
    },
    # Python - Medium
    {
        "category_slug": "python",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "What is the Global Interpreter Lock (GIL) in CPython?",
        "options": [
            {"text": "A mutex that prevents multiple native threads from executing Python bytecodes simultaneously", "is_correct": True},
            {"text": "A compiler flag that turns off memory allocation checks", "is_correct": False},
            {"text": "A security feature disabling socket networking on untrusted scripts", "is_correct": False},
            {"text": "An encryption cipher protecting bytecode files (.pyc)", "is_correct": False},
        ],
        "explanation": "The GIL is a mechanism in CPython ensuring thread safety for internal memory management by allowing only one thread to execute Python bytecode at a time.",
    },
    {
        "category_slug": "python",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "What is the difference between `is` and `==` in Python?",
        "options": [
            {"text": "`is` tests object identity in memory while `==` tests equality of values", "is_correct": True},
            {"text": "`is` tests value equality while `==` tests object type", "is_correct": False},
            {"text": "Both are strictly identical in all scenarios", "is_correct": False},
            {"text": "`is` is only valid for strings and integers", "is_correct": False},
        ],
        "explanation": "`==` invokes `__eq__` to verify whether values match, whereas `is` checks whether two variables point to the exact same memory address (`id(a) == id(b)`).",
    },
    {
        "category_slug": "python",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "What does a generator function use instead of `return` to yield values lazily?",
        "options": [
            {"text": "yield", "is_correct": True},
            {"text": "emit", "is_correct": False},
            {"text": "send", "is_correct": False},
            {"text": "produce", "is_correct": False},
        ],
        "explanation": "The `yield` keyword pauses execution, preserving stack state, and returns an iterator value to the caller.",
    },
    # Python - Hard
    {
        "category_slug": "python",
        "difficulty": "hard",
        "points": 300,
        "time_limit_sec": 20,
        "question_text": "In Python metaclasses, which method is called first to allocate memory before class initialization?",
        "options": [
            {"text": "__new__", "is_correct": True},
            {"text": "__init__", "is_correct": False},
            {"text": "__prepare__", "is_correct": False},
            {"text": "__call__", "is_correct": False},
        ],
        "explanation": "__new__ is the static allocator that constructs the instance, whereas __init__ initializes already allocated instance attributes.",
    },
    {
        "category_slug": "python",
        "difficulty": "hard",
        "points": 300,
        "time_limit_sec": 20,
        "question_text": "What is the method resolution order (MRO) algorithm utilized by modern Python 3?",
        "options": [
            {"text": "C3 Linearization", "is_correct": True},
            {"text": "Depth-First Search (DFS)", "is_correct": False},
            {"text": "Breadth-First Search (BFS)", "is_correct": False},
            {"text": "Dijkstra DAG Topological Order", "is_correct": False},
        ],
        "explanation": "Python 2.3+ and Python 3 implement C3 linearization for deterministic multiple inheritance resolution.",
    },

    # Java - Easy
    {
        "category_slug": "java",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "Which keyword in Java prevents a class from being subclassed?",
        "options": [
            {"text": "final", "is_correct": True},
            {"text": "static", "is_correct": False},
            {"text": "sealed", "is_correct": False},
            {"text": "const", "is_correct": False},
        ],
        "explanation": "Marking a class as `final` prevents other classes from extending or subclassing it.",
    },
    {
        "category_slug": "java",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "What is the default value of a boolean primitive in Java?",
        "options": [
            {"text": "false", "is_correct": True},
            {"text": "true", "is_correct": False},
            {"text": "0", "is_correct": False},
            {"text": "null", "is_correct": False},
        ],
        "explanation": "In Java, primitive boolean instance variables default to `false`.",
    },
    # Java - Medium
    {
        "category_slug": "java",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "What is the primary difference between `HashMap` and `ConcurrentHashMap` in Java?",
        "options": [
            {"text": "ConcurrentHashMap is thread-safe using lock-striping/CAS without locking the whole table", "is_correct": True},
            {"text": "HashMap does not allow null keys while ConcurrentHashMap requires null keys", "is_correct": False},
            {"text": "ConcurrentHashMap is stored off-heap in native memory", "is_correct": False},
            {"text": "HashMap is synchronized by default", "is_correct": False},
        ],
        "explanation": "ConcurrentHashMap enables high concurrent throughput by avoiding global locking through CAS operations and synchronized bucket nodes.",
    },
    {
        "category_slug": "java",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "Which garbage collection generation in HotSpot JVM stores objects that survive multiple GC cycles?",
        "options": [
            {"text": "Tenured (Old) Generation", "is_correct": True},
            {"text": "Eden Space", "is_correct": False},
            {"text": "Survivor Space S0", "is_correct": False},
            {"text": "Metaspace", "is_correct": False},
        ],
        "explanation": "Objects surviving tenure thresholds in the Young Generation (Eden/Survivor) are promoted to Tenured (Old) Generation.",
    },
    # Java - Hard
    {
        "category_slug": "java",
        "difficulty": "hard",
        "points": 300,
        "time_limit_sec": 20,
        "question_text": "What memory barrier effect does writing to a `volatile` variable establish in the Java Memory Model?",
        "options": [
            {"text": "A happens-before relationship ensuring subsequent reads observe the write", "is_correct": True},
            {"text": "It forces immediate Young Generation garbage collection", "is_correct": False},
            {"text": "It places the object in the CPU L1 cache exclusively", "is_correct": False},
            {"text": "It prohibits class reloading by custom ClassLoaders", "is_correct": False},
        ],
        "explanation": "A write to a volatile field happens-before every subsequent read of that same field across threads according to JMM JSR-133.",
    },

    # C / C++ - Easy
    {
        "category_slug": "c-cpp",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "Which operator is used to obtain the memory address of a variable in C?",
        "options": [
            {"text": "&", "is_correct": True},
            {"text": "*", "is_correct": False},
            {"text": "->", "is_correct": False},
            {"text": "::", "is_correct": False},
        ],
        "explanation": "The address-of operator `&` yields a pointer to the memory location of its operand.",
    },
    {
        "category_slug": "c-cpp",
        "difficulty": "easy",
        "points": 100,
        "time_limit_sec": 15,
        "question_text": "Which standard library header file is required for `malloc()` and `free()` in C?",
        "options": [
            {"text": "<stdlib.h>", "is_correct": True},
            {"text": "<stdio.h>", "is_correct": False},
            {"text": "<string.h>", "is_correct": False},
            {"text": "<memory.h>", "is_correct": False},
        ],
        "explanation": "stdlib.h declares dynamic memory allocation routines including malloc, calloc, realloc, and free.",
    },
    # C / C++ - Medium
    {
        "category_slug": "c-cpp",
        "difficulty": "medium",
        "points": 200,
        "time_limit_sec": 15,
        "question_text": "In C++, what does the `std::unique_ptr` smart pointer enforce regarding ownership?",
        "options": [
            {"text": "Exclusive ownership; it cannot be copied, only moved", "is_correct": True},
            {"text": "Shared ownership tracked via reference counting", "is_correct": False},
            {"text": "Weak non-owning observer semantics", "is_correct": False},
            {"text": "Automatic garbage collection via marks and sweeps", "is_correct": False},
        ],
        "explanation": "`std::unique_ptr` manages a resource exclusively through move semantics (`std::move`), releasing it upon destruction.",
    },
    # C / C++ - Hard
    {
        "category_slug": "c-cpp",
        "difficulty": "hard",
        "points": 300,
        "time_limit_sec": 20,
        "question_text": "In C++, what is RAII (Resource Acquisition Is Initialization)?",
        "options": [
            {"text": "Binding resource lifecycle to object lifetime so destructors automatically release resources", "is_correct": True},
            {"text": "Initializing all pointer variables to NULL at program startup", "is_correct": False},
            {"text": "A compiler optimization turning recursion into loops", "is_correct": False},
            {"text": "Dynamic runtime memory defragmentation", "is_correct": False},
        ],
        "explanation": "RAII guarantees that resources (memory, file handles, mutex locks) are acquired during construction and deterministically released during destruction (stack unwinding).",
    },
]
