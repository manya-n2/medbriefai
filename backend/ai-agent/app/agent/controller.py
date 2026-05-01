
from app.agent import memory, planner, executor
from app.schema.response_schema import AgentResponse
from app.utils.logger import get_logger

logger = get_logger("controller")

def run_agent(clinical_note: str, goal: str) -> AgentResponse:
    session_id = memory.create_session()
    logger.info(f"New session started: {session_id} | Goal: {goal}")

    try:
        logger.info("Generating plan...")
        plan = planner.generate_plan(clinical_note, goal)
        logger.info(f"Plan generated: {[s['tool'] for s in plan]}")

        logger.info("Executing plan...")
        executed_steps = executor.execute_plan(session_id, plan, clinical_note)
        logger.info(f"Steps executed: {executed_steps}")

        mem = memory.get_session_memory(session_id)

        extracted = mem.get("extract_entities")
        summary = mem.get("summarize")
        interactions = mem.get("check_interactions")
        risks = mem.get("detect_risks")

        logger.debug(f"Extracted entities keys: {list(extracted.keys()) if extracted else 'None'}")
        logger.debug(f"Summary length: {len(summary) if summary else 0} chars")
        logger.debug(f"Interactions found: {interactions.get('interactions_found') if interactions else 'None'}")
        logger.debug(f"Risk level: {risks.get('risk_level') if risks else 'None'}")

        response_data = {
            "success": True,
            "session_id": session_id,
            "goal": goal,
            "steps_executed": executed_steps,
            "extracted_entities": extracted,
            "summary": summary,
            "drug_interactions": interactions,
            "risk_assessment": risks,
        }

        memory.persist_result(session_id, clinical_note, goal, response_data)
        logger.info(f"Session {session_id} completed successfully")
        return AgentResponse(**response_data)

    except Exception as e:
        logger.error(f"Agent failed for session {session_id}: {e}", exc_info=True)
        return AgentResponse(
            success=False,
            session_id=session_id,
            goal=goal,
            steps_executed=[],
            error=str(e),
        )
