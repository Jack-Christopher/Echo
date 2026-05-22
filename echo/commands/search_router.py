"""Resolve voice search queries to URLs via configurable routes."""

from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass
from typing import Any

from echo.commands.normalizer import normalize
from echo.config.schema import EchoConfig

VALID_MATCH = frozenset({"exact", "leading", "contains", "fallback"})
VALID_RESOLVE = frozenset({"template", "site"})


@dataclass(frozen=True)
class ResolvedSearch:
    query: str
    url: str
    route_id: str
    label: str


def _norm_term(term: str) -> str:
    return normalize(term)


def _format_template(template: str, query: str) -> str:
    encoded = urllib.parse.quote_plus(query)
    return template.replace("{query}", encoded).replace("{query_raw}", query)


def _rule_terms(rule: dict[str, Any]) -> list[str]:
    terms = rule.get("terms") or []
    return sorted((_norm_term(str(t)) for t in terms), key=len, reverse=True)


def _all_rules(config: EchoConfig) -> list[dict[str, Any]]:
    """custom_site_searches first in list, sorted by priority globally."""
    combined = list(config.custom_site_searches) + list(config.search_routes)
    return sorted(combined, key=lambda r: int(r.get("priority", 0)), reverse=True)


def _build_search_url(
    rule: dict[str, Any],
    payload: str,
    config: EchoConfig,
) -> str:
    """Build final URL: template mode or site:domain via search engine."""
    mode = str(rule.get("resolve_mode", "template")).lower()
    if mode == "site":
        domain = str(rule.get("site_domain", "")).strip()
        if domain.lower().startswith("site:"):
            domain = domain[5:].strip()
        if not domain:
            mode = "template"
        else:
            engine = str(rule.get("engine_template") or config.search_engine_template)
            site_q = f"{payload} site:{domain}".strip()
            return _format_template(engine, site_q)
    template = str(rule.get("template", "")).strip()
    if not template:
        template = config.search_engine_template
    return _format_template(template, payload)


def resolve_search(query: str, config: EchoConfig) -> ResolvedSearch:
    """Pick highest-priority matching route (custom sites + general routes)."""
    q = _norm_term(query)
    rules = _all_rules(config)
    fallback_template = config.search_engine_template

    for rule in rules:
        match_type = str(rule.get("match", "leading")).lower()
        if match_type not in VALID_MATCH:
            continue
        route_id = str(rule.get("id", "route"))
        label = str(rule.get("label", route_id))
        strip_terms = bool(rule.get("strip_terms", True))
        resolve_mode = str(rule.get("resolve_mode", "template")).lower()
        template = str(rule.get("template", "")).strip()

        if resolve_mode == "template" and not template and match_type != "fallback":
            continue
        if resolve_mode == "site" and not str(rule.get("site_domain", "")).strip():
            if match_type != "fallback":
                continue

        if match_type == "fallback":
            url = _format_template(fallback_template, q)
            return ResolvedSearch(q, url, route_id, label)

        terms = _rule_terms(rule)
        if not terms:
            continue

        if match_type == "exact":
            for term in terms:
                if q == term:
                    payload = q if not strip_terms else q
                    url = _build_search_url(rule, payload, config)
                    return ResolvedSearch(query.strip(), url, route_id, label)

        if match_type == "leading":
            for term in terms:
                if q == term or q.startswith(term + " "):
                    payload = q[len(term) :].strip() if strip_terms else q
                    if not payload:
                        payload = q
                    url = _build_search_url(rule, payload, config)
                    return ResolvedSearch(query.strip(), url, route_id, label)

        if match_type == "contains":
            for term in terms:
                if term in q:
                    payload = re.sub(rf"^{re.escape(term)}\s*", "", q).strip()
                    if not payload:
                        payload = q
                    if not strip_terms:
                        payload = q
                    url = _build_search_url(rule, payload, config)
                    return ResolvedSearch(query.strip(), url, route_id, label)

    url = _format_template(fallback_template, q)
    return ResolvedSearch(query.strip(), url, "default", "Busqueda general")
