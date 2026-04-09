"""
AdSim SQLite 데이터베이스 관리
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..config import Config


def _generate_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _now() -> str:
    return datetime.utcnow().isoformat()


class AdSimDB:
    DB_PATH = os.path.join(Config.UPLOAD_FOLDER, 'adsim.db')
    SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'adsim_schema.sql')

    @classmethod
    def init_db(cls):
        os.makedirs(os.path.dirname(cls.DB_PATH), exist_ok=True)
        with sqlite3.connect(cls.DB_PATH) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            with open(cls.SCHEMA_PATH) as f:
                conn.executescript(f.read())

    @classmethod
    def _conn(cls) -> sqlite3.Connection:
        if not os.path.exists(cls.DB_PATH):
            cls.init_db()
        conn = sqlite3.connect(cls.DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ── Projects ──

    @classmethod
    def create_project(cls, name: str, project_type: str, description: str = "") -> Dict[str, Any]:
        project_id = _generate_id("proj")
        now = _now()
        with cls._conn() as conn:
            conn.execute(
                "INSERT INTO adsim_projects (project_id, name, type, description, created_at, updated_at) VALUES (?,?,?,?,?,?)",
                (project_id, name, project_type, description, now, now)
            )
        return {"project_id": project_id, "name": name, "type": project_type, "description": description, "created_at": now, "updated_at": now}

    @classmethod
    def list_projects(cls) -> List[Dict[str, Any]]:
        with cls._conn() as conn:
            rows = conn.execute("SELECT * FROM adsim_projects ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

    @classmethod
    def get_project(cls, project_id: str) -> Optional[Dict[str, Any]]:
        with cls._conn() as conn:
            row = conn.execute("SELECT * FROM adsim_projects WHERE project_id = ?", (project_id,)).fetchone()
        return dict(row) if row else None

    @classmethod
    def delete_project(cls, project_id: str) -> bool:
        with cls._conn() as conn:
            cur = conn.execute("DELETE FROM adsim_projects WHERE project_id = ?", (project_id,))
        return cur.rowcount > 0

    # ── Seed Materials ──

    @classmethod
    def create_seed(cls, project_id: str, seed_type: str, content: str = "", file_path: str = "", file_size: int = 0) -> Dict[str, Any]:
        seed_id = _generate_id("seed")
        now = _now()
        with cls._conn() as conn:
            conn.execute(
                "INSERT INTO adsim_seed_materials (seed_id, project_id, type, content, file_path, file_size, created_at) VALUES (?,?,?,?,?,?,?)",
                (seed_id, project_id, seed_type, content, file_path, file_size, now)
            )
        return {"seed_id": seed_id, "project_id": project_id, "type": seed_type, "content": content, "created_at": now}

    @classmethod
    def list_seeds(cls, project_id: str) -> List[Dict[str, Any]]:
        with cls._conn() as conn:
            rows = conn.execute("SELECT * FROM adsim_seed_materials WHERE project_id = ? ORDER BY created_at DESC", (project_id,)).fetchall()
        return [dict(r) for r in rows]

    @classmethod
    def get_seed(cls, seed_id: str) -> Optional[Dict[str, Any]]:
        with cls._conn() as conn:
            row = conn.execute("SELECT * FROM adsim_seed_materials WHERE seed_id = ?", (seed_id,)).fetchone()
        return dict(row) if row else None

    @classmethod
    def delete_seed(cls, seed_id: str) -> bool:
        with cls._conn() as conn:
            cur = conn.execute("DELETE FROM adsim_seed_materials WHERE seed_id = ?", (seed_id,))
        return cur.rowcount > 0

    # ── Persona Configs ──

    @classmethod
    def create_persona(cls, project_id: str, name: str, age_range: str, gender: str = "",
                       interests: List[str] = None, consumption_habits: str = "",
                       agent_count: int = 30, is_preset: bool = False) -> Dict[str, Any]:
        persona_id = _generate_id("persona")
        now = _now()
        interests_json = json.dumps(interests or [], ensure_ascii=False)
        with cls._conn() as conn:
            conn.execute(
                "INSERT INTO adsim_persona_configs (persona_id, project_id, name, age_range, gender, interests, consumption_habits, agent_count, is_preset, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (persona_id, project_id, name, age_range, gender, interests_json, consumption_habits, agent_count, int(is_preset), now)
            )
        return {"persona_id": persona_id, "project_id": project_id, "name": name, "age_range": age_range,
                "gender": gender, "interests": interests or [], "consumption_habits": consumption_habits,
                "agent_count": agent_count, "is_preset": is_preset, "created_at": now}

    @classmethod
    def list_personas(cls, project_id: str) -> List[Dict[str, Any]]:
        with cls._conn() as conn:
            rows = conn.execute("SELECT * FROM adsim_persona_configs WHERE project_id = ? ORDER BY created_at DESC", (project_id,)).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["interests"] = json.loads(d["interests"]) if d["interests"] else []
            d["is_preset"] = bool(d["is_preset"])
            result.append(d)
        return result

    @classmethod
    def delete_persona(cls, persona_id: str) -> bool:
        with cls._conn() as conn:
            cur = conn.execute("DELETE FROM adsim_persona_configs WHERE persona_id = ?", (persona_id,))
        return cur.rowcount > 0

    # ── Simulations ──

    @classmethod
    def create_simulation(cls, project_id: str, persona_config_id: str, seed_id: str, total_rounds: int = 30) -> Dict[str, Any]:
        simulation_id = _generate_id("sim")
        now = _now()
        with cls._conn() as conn:
            conn.execute(
                "INSERT INTO adsim_simulations (simulation_id, project_id, persona_config_id, seed_id, status, total_rounds, current_round, created_at) VALUES (?,?,?,?,?,?,?,?)",
                (simulation_id, project_id, persona_config_id, seed_id, "pending", total_rounds, 0, now)
            )
        return {"simulation_id": simulation_id, "project_id": project_id, "status": "pending",
                "total_rounds": total_rounds, "current_round": 0, "created_at": now}

    @classmethod
    def get_simulation(cls, simulation_id: str) -> Optional[Dict[str, Any]]:
        with cls._conn() as conn:
            row = conn.execute("SELECT * FROM adsim_simulations WHERE simulation_id = ?", (simulation_id,)).fetchone()
        return dict(row) if row else None

    @classmethod
    def list_simulations(cls, project_id: str) -> List[Dict[str, Any]]:
        with cls._conn() as conn:
            rows = conn.execute("SELECT * FROM adsim_simulations WHERE project_id = ? ORDER BY created_at DESC", (project_id,)).fetchall()
        return [dict(r) for r in rows]

    @classmethod
    def update_simulation_status(cls, simulation_id: str, status: str, current_round: int = None):
        fields = ["status = ?"]
        values = [status]
        if current_round is not None:
            fields.append("current_round = ?")
            values.append(current_round)
        if status == "running" :
            fields.append("started_at = ?")
            values.append(_now())
        if status in ("completed", "failed"):
            fields.append("completed_at = ?")
            values.append(_now())
        values.append(simulation_id)
        with cls._conn() as conn:
            conn.execute(f"UPDATE adsim_simulations SET {', '.join(fields)} WHERE simulation_id = ?", values)

    # ── Agent Responses ──

    @classmethod
    def save_agent_response(cls, simulation_id: str, agent_id: int, agent_name: str,
                            agent_persona: Dict, sentiment: str, sentiment_score: float,
                            key_reactions: List[str], conversation_log: List[Dict]) -> Dict[str, Any]:
        response_id = _generate_id("resp")
        now = _now()
        with cls._conn() as conn:
            conn.execute(
                "INSERT INTO adsim_agent_responses (response_id, simulation_id, agent_id, agent_name, agent_persona, sentiment, sentiment_score, key_reactions, conversation_log, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (response_id, simulation_id, agent_id, agent_name,
                 json.dumps(agent_persona, ensure_ascii=False), sentiment, sentiment_score,
                 json.dumps(key_reactions, ensure_ascii=False), json.dumps(conversation_log, ensure_ascii=False), now)
            )
        return {"response_id": response_id, "simulation_id": simulation_id, "agent_name": agent_name, "sentiment": sentiment}

    @classmethod
    def list_responses(cls, simulation_id: str) -> List[Dict[str, Any]]:
        with cls._conn() as conn:
            rows = conn.execute("SELECT * FROM adsim_agent_responses WHERE simulation_id = ? ORDER BY agent_id", (simulation_id,)).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["agent_persona"] = json.loads(d["agent_persona"])
            d["key_reactions"] = json.loads(d["key_reactions"])
            d["conversation_log"] = json.loads(d["conversation_log"])
            result.append(d)
        return result

    @classmethod
    def get_response(cls, response_id: str) -> Optional[Dict[str, Any]]:
        with cls._conn() as conn:
            row = conn.execute("SELECT * FROM adsim_agent_responses WHERE response_id = ?", (response_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["agent_persona"] = json.loads(d["agent_persona"])
        d["key_reactions"] = json.loads(d["key_reactions"])
        d["conversation_log"] = json.loads(d["conversation_log"])
        return d

    # ── Simulation Rounds ──

    @classmethod
    def save_round(cls, simulation_id: str, round_number: int, summary: str, sentiment_snapshot: Dict) -> Dict[str, Any]:
        round_id = _generate_id("round")
        now = _now()
        with cls._conn() as conn:
            conn.execute(
                "INSERT INTO adsim_simulation_rounds (round_id, simulation_id, round_number, summary, sentiment_snapshot, created_at) VALUES (?,?,?,?,?,?)",
                (round_id, simulation_id, round_number, summary, json.dumps(sentiment_snapshot, ensure_ascii=False), now)
            )
        return {"round_id": round_id, "round_number": round_number, "summary": summary}

    @classmethod
    def list_rounds(cls, simulation_id: str) -> List[Dict[str, Any]]:
        with cls._conn() as conn:
            rows = conn.execute("SELECT * FROM adsim_simulation_rounds WHERE simulation_id = ? ORDER BY round_number", (simulation_id,)).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["sentiment_snapshot"] = json.loads(d["sentiment_snapshot"])
            result.append(d)
        return result

    # ── Reports ──

    @classmethod
    def save_report(cls, simulation_id: str, overall_sentiment: Dict, key_insights: List[str],
                    concerns: List[str], recommendations: List[str], full_report_text: str) -> Dict[str, Any]:
        report_id = _generate_id("rpt")
        now = _now()
        with cls._conn() as conn:
            conn.execute(
                "INSERT INTO adsim_reports (report_id, simulation_id, overall_sentiment, key_insights, concerns, recommendations, full_report_text, created_at) VALUES (?,?,?,?,?,?,?,?)",
                (report_id, simulation_id, json.dumps(overall_sentiment, ensure_ascii=False),
                 json.dumps(key_insights, ensure_ascii=False), json.dumps(concerns, ensure_ascii=False),
                 json.dumps(recommendations, ensure_ascii=False), full_report_text, now)
            )
        return {"report_id": report_id, "simulation_id": simulation_id, "overall_sentiment": overall_sentiment, "created_at": now}

    @classmethod
    def get_report(cls, simulation_id: str) -> Optional[Dict[str, Any]]:
        with cls._conn() as conn:
            row = conn.execute("SELECT * FROM adsim_reports WHERE simulation_id = ?", (simulation_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["overall_sentiment"] = json.loads(d["overall_sentiment"])
        d["key_insights"] = json.loads(d["key_insights"])
        d["concerns"] = json.loads(d["concerns"])
        d["recommendations"] = json.loads(d["recommendations"])
        return d
