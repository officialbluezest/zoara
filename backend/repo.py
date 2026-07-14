import json
from database import get_conn, now, new_id, row_to_dict

# ---------- Brands ----------

def create_brand(name):
    conn = get_conn()
    bid = new_id()
    ts = now()
    conn.execute(
        "INSERT INTO brands (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (bid, name, ts, ts),
    )
    conn.commit()
    conn.close()
    return get_brand(bid)


def list_brands():
    conn = get_conn()
    rows = conn.execute("SELECT id, name, created_at, updated_at FROM brands ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


JSON_FIELDS = ["strategy_answers", "formats", "platforms", "goals", "build_specs", "creative_angles"]


def get_brand(brand_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM brands WHERE id = ?", (brand_id,)).fetchone()
    conn.close()
    return row_to_dict(row, JSON_FIELDS)


def update_brand(brand_id, fields: dict):
    allowed = {"name", "strategy_answers", "strategy_doc_text", "strategy_doc_filename",
               "formats", "platforms", "goals", "build_specs", "creative_angles"}
    sets, values = [], []
    for k, v in fields.items():
        if k not in allowed:
            continue
        if k in JSON_FIELDS:
            v = json.dumps(v)
        sets.append(f"{k} = ?")
        values.append(v)
    if not sets:
        return get_brand(brand_id)
    sets.append("updated_at = ?")
    values.append(now())
    values.append(brand_id)
    conn = get_conn()
    conn.execute(f"UPDATE brands SET {', '.join(sets)} WHERE id = ?", values)
    conn.commit()
    conn.close()
    return get_brand(brand_id)


def delete_brand(brand_id):
    conn = get_conn()
    conn.execute("DELETE FROM brands WHERE id = ?", (brand_id,))
    conn.commit()
    conn.close()


# ---------- Competitors ----------

def add_competitor(brand_id, url, label=""):
    conn = get_conn()
    cid = new_id()
    conn.execute(
        "INSERT INTO competitors (id, brand_id, url, label, created_at) VALUES (?, ?, ?, ?, ?)",
        (cid, brand_id, url, label, now()),
    )
    conn.commit()
    conn.close()
    return get_competitor(cid)


def get_competitor(cid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM competitors WHERE id = ?", (cid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_competitor(cid, extracted_summary, status="analyzed"):
    conn = get_conn()
    conn.execute(
        "UPDATE competitors SET extracted_summary = ?, status = ? WHERE id = ?",
        (extracted_summary, status, cid),
    )
    conn.commit()
    conn.close()
    return get_competitor(cid)


def list_competitors(brand_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM competitors WHERE brand_id = ? ORDER BY created_at DESC", (brand_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- Inspo links ----------

def add_inspo(brand_id, room, url, user_note):
    conn = get_conn()
    iid = new_id()
    conn.execute(
        "INSERT INTO inspo_links (id, brand_id, room, url, user_note, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (iid, brand_id, room, url, user_note, now()),
    )
    conn.commit()
    conn.close()
    return get_inspo(iid)


def get_inspo(iid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM inspo_links WHERE id = ?", (iid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_inspo(iid, extracted_summary, extracted_pattern, status="analyzed"):
    conn = get_conn()
    conn.execute(
        "UPDATE inspo_links SET extracted_summary = ?, extracted_pattern = ?, status = ? WHERE id = ?",
        (extracted_summary, extracted_pattern, status, iid),
    )
    conn.commit()
    conn.close()
    return get_inspo(iid)


def list_inspo(brand_id, room=None):
    conn = get_conn()
    if room:
        rows = conn.execute("SELECT * FROM inspo_links WHERE brand_id = ? AND room = ? ORDER BY created_at DESC", (brand_id, room)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM inspo_links WHERE brand_id = ? ORDER BY created_at DESC", (brand_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------- Research ----------

def create_research_job(brand_id, requested_count=30):
    conn = get_conn()
    jid = new_id()
    conn.execute(
        "INSERT INTO research_jobs (id, brand_id, status, requested_count, created_at) VALUES (?, ?, 'running', ?, ?)",
        (jid, brand_id, requested_count, now()),
    )
    conn.commit()
    conn.close()
    return jid


def complete_research_job(job_id, error=""):
    conn = get_conn()
    status = "failed" if error else "complete"
    conn.execute(
        "UPDATE research_jobs SET status = ?, error = ?, completed_at = ? WHERE id = ?",
        (status, error, now(), job_id),
    )
    conn.commit()
    conn.close()


def get_research_job(job_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM research_jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def add_research_ideas(brand_id, job_id, ideas: list):
    conn = get_conn()
    for idea in ideas:
        conn.execute(
            "INSERT INTO research_ideas (id, brand_id, job_id, topic, source_pattern, suggested_angle, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (new_id(), brand_id, job_id, idea.get("topic", ""), idea.get("source_pattern", ""), idea.get("suggested_angle", ""), now()),
        )
    conn.commit()
    conn.close()


def list_research_ideas(brand_id, status=None):
    conn = get_conn()
    if status:
        rows = conn.execute("SELECT * FROM research_ideas WHERE brand_id = ? AND status = ? ORDER BY created_at DESC", (brand_id, status)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM research_ideas WHERE brand_id = ? ORDER BY created_at DESC", (brand_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_research_idea(idea_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM research_ideas WHERE id = ?", (idea_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_research_idea_status(idea_id, status, tweak_comment=""):
    conn = get_conn()
    conn.execute(
        "UPDATE research_ideas SET status = ?, tweak_comment = ? WHERE id = ?",
        (status, tweak_comment, idea_id),
    )
    conn.commit()
    conn.close()
    return get_research_idea(idea_id)


# ---------- Content ----------

def create_content(brand_id, format_id, platform_id, research_idea_id, content_json, raw_text, parent_id=None, title=""):
    conn = get_conn()
    cid = new_id()
    ts = now()
    conn.execute(
        """INSERT INTO content_items
        (id, brand_id, format, platform, research_idea_id, parent_id, title, content_json, raw_text, status, version, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft', 1, ?, ?)""",
        (cid, brand_id, format_id, platform_id, research_idea_id, parent_id, title, json.dumps(content_json), raw_text, ts, ts),
    )
    conn.commit()
    conn.close()
    return get_content(cid)


def get_content(cid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM content_items WHERE id = ?", (cid,)).fetchone()
    conn.close()
    return row_to_dict(row, ["content_json"])


def update_content(cid, raw_text, content_json=None, status=None):
    conn = get_conn()
    sets, values = ["raw_text = ?", "updated_at = ?", "version = version + 1"], [raw_text, now()]
    if content_json is not None:
        sets.append("content_json = ?")
        values.append(json.dumps(content_json))
    if status:
        sets.append("status = ?")
        values.append(status)
    values.append(cid)
    conn.execute(f"UPDATE content_items SET {', '.join(sets)} WHERE id = ?", values)
    conn.commit()
    conn.close()
    return get_content(cid)


def list_content(brand_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM content_items WHERE brand_id = ? ORDER BY created_at DESC", (brand_id,)).fetchall()
    conn.close()
    return [row_to_dict(r, ["content_json"]) for r in rows]


# ---------- Critiques ----------

def add_critique(content_item_id, result: dict):
    conn = get_conn()
    crid = new_id()
    conn.execute(
        """INSERT INTO critiques
        (id, content_item_id, strategist_score, customer_score, overall_score,
         strategist_feedback, customer_feedback, improvement_notes, passed_cutoff, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (crid, content_item_id, result.get("strategist_score"), result.get("customer_score"),
         result.get("overall_score"), result.get("strategist_feedback", ""),
         result.get("customer_feedback", ""), result.get("improvement_notes", ""),
         1 if result.get("passed_cutoff") else 0, now()),
    )
    conn.commit()
    conn.close()
    return get_critique(crid)


def get_critique(crid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM critiques WHERE id = ?", (crid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_critiques(content_item_id):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM critiques WHERE content_item_id = ? ORDER BY created_at DESC", (content_item_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_critique_comment(crid, comment):
    conn = get_conn()
    conn.execute("UPDATE critiques SET user_comment = ? WHERE id = ?", (comment, crid))
    conn.commit()
    conn.close()
    return get_critique(crid)
