# app/state_assignments.py
from collections import defaultdict
from typing import Dict

# pending_assignments[hpid][bed_type] = 현재 그 병원 bed_type으로 보내기로 한 환자 수
pending_assignments: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
