"""
Quiz Royale — Content Banks & Domain Engines Unified Registry
"""

from typing import Dict, List, Any
from .python_bank import repository as python_repo
from .java_bank import repository as java_repo
from .cpp_bank import repository as cpp_repo
from .dsa_bank import repository as dsa_repo
from .dbms_bank import repository as dbms_repo
from .os_bank import repository as os_repo
from .networks_bank import repository as networks_repo
from .security_bank import repository as security_repo
from .math_bank import repository as math_repo
from .logic_bank import repository as logic_repo
from .gk_bank import repository as gk_repo
from .science_bank import repository as science_repo
from .sports_bank import repository as sports_repo
from .entertainment_bank import repository as entertainment_repo
from .cloud_devops_bank import repository as cloud_repo

from ..engine.generators_math import math_engine
from ..engine.generators_logic import logic_engine
from ..engine.ai_bots_engine import bot_engine
from ..engine.tournament_brackets import bracket_engine
from ..engine.analytics_irt import irt_engine
from ..engine.anti_cheat_heuristics import anti_cheat_engine

ALL_BANKS = {
    "python": python_repo,
    "java": java_repo,
    "cpp": cpp_repo,
    "dsa": dsa_repo,
    "dbms": dbms_repo,
    "os": os_repo,
    "networks": networks_repo,
    "security": security_repo,
    "math": math_repo,
    "logic": logic_repo,
    "gk": gk_repo,
    "science": science_repo,
    "sports": sports_repo,
    "entertainment": entertainment_repo,
    "cloud": cloud_repo,
}

def get_total_questions_count() -> int:
    return sum(repo.total_count for repo in ALL_BANKS.values())
