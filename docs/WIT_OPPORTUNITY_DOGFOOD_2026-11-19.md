# WIT Opportunity Discovery | first dogfood 2026-11-19

Status: observational desk test, NOT runtime/persistence test. Inputs: 10 publicly indexed Reddit discussion excerpts retrieved via web search. Some are months old; relevance is not current engagement opportunity. No direct Reddit API, login, scraping, messages or posting.

Rubric from experimental workflow. Community suitability awarded 0 because rules not independently verified; all cases gate NEEDS_REVIEW. Scores are provisional, not actionable rankings. No false-positive/negative accuracy estimate without labelled ground truth. This is a manual execution of the documented rubric, not proof that WIT runs it automatically.

## 1xsz7jz Cross-session context across tools
Source: https://www.reddit.com/r/AI_Agents/comments/1xsz7jz/
Scores relevance 35/35, request 25/25, verified fit 25/25, community 0/15; total 85/100. Gate NEEDS_REVIEW. Provisional category PRIORITY_REVIEW. Community promotion rules and live status unverified; no reply authorized.

## 1skur2q Long-running agent loses memory and subagent context
Source: https://www.reddit.com/r/AI_Agents/comments/1skur2q/
Scores relevance 35/35, request 18/25, verified fit 25/25, community 0/15; total 78/100. Gate NEEDS_REVIEW. Provisional category REVIEW_LATER. Community promotion rules and live status unverified; no reply authorized.

## 1r2puny Persistent agent memory
Source: https://www.reddit.com/r/AI_Agents/comments/1r2puny/
Scores relevance 35/35, request 25/25, verified fit 20/25, community 0/15; total 80/100. Gate NEEDS_REVIEW. Provisional category PRIORITY_REVIEW. Community promotion rules and live status unverified; no reply authorized.

## 1w0oknd Multi-user branchable agent memory
Source: https://www.reddit.com/r/AI_Agents/comments/1w0oknd/
Scores relevance 25/35, request 18/25, verified fit 12/25, community 0/15; total 55/100. Gate NEEDS_REVIEW. Provisional category ARCHIVE. Community promotion rules and live status unverified; no reply authorized.

## 1tnhhkt Agent memory junk drawer
Source: https://www.reddit.com/r/AI_Agents/comments/1tnhhkt/
Scores relevance 35/35, request 20/25, verified fit 25/25, community 0/15; total 80/100. Gate NEEDS_REVIEW. Provisional category PRIORITY_REVIEW. Community promotion rules and live status unverified; no reply authorized.

## 1ta69bp Replay and debug long-term memory
Source: https://www.reddit.com/r/AI_Agents/comments/1ta69bp/
Scores relevance 30/35, request 20/25, verified fit 20/25, community 0/15; total 70/100. Gate NEEDS_REVIEW. Provisional category REVIEW_LATER. Community promotion rules and live status unverified; no reply authorized.

## 1quz5ra Multi-agent cross-tool memory
Source: https://www.reddit.com/r/AI_Agents/comments/1quz5ra/
Scores relevance 35/35, request 25/25, verified fit 25/25, community 0/15; total 85/100. Gate NEEDS_REVIEW. Provisional category PRIORITY_REVIEW. Community promotion rules and live status unverified; no reply authorized.

## 1s3wv3s Instruction decay and task drift
Source: https://www.reddit.com/r/AI_Agents/comments/1s3wv3s/
Scores relevance 35/35, request 18/25, verified fit 25/25, community 0/15; total 78/100. Gate NEEDS_REVIEW. Provisional category REVIEW_LATER. Community promotion rules and live status unverified; no reply authorized.

## 1rrlbva Distributed agent state
Source: https://www.reddit.com/r/AI_Agents/comments/1rrlbva/
Scores relevance 25/35, request 18/25, verified fit 20/25, community 0/15; total 63/100. Gate NEEDS_REVIEW. Provisional category REVIEW_LATER. Community promotion rules and live status unverified; no reply authorized.

## 1sr3oou Repeated context reconstruction
Source: https://www.reddit.com/r/AI_Agents/comments/1sr3oou/
Scores relevance 35/35, request 25/25, verified fit 25/25, community 0/15; total 85/100. Gate NEEDS_REVIEW. Provisional category PRIORITY_REVIEW. Community promotion rules and live status unverified; no reply authorized.

## Findings
- All 10 sources were distinct by Reddit post ID; no duplicates in this small sample.
- 5 provisional priority, 4 review later, 1 archive. All 10 blocked from promotional outreach pending rules/status verification.
- Source evidence supports pain-point match, not actual adoption, permission to post, or WIT's runtime compatibility.
- Critical failure mode: rubric can over-score stale, promotional, or research-oriented posts; add freshness and buyer-intent gates before any lead action.
- Persistence/restart, accuracy, API access, and actual reply review remain UNTESTED.
- No extra scheduler, database, dependency, or stable change. No external communications.

## Next decision
Keep workflow experimental; improve gating with freshness, explicit help intent and community rules before promoting. No need to install OctoSift itself.
