
import os
import sys
import uuid

from dotenv import load_dotenv

from app.db.database import get_db, Base, engine
from app.models.search import SearchJob

load_dotenv()


# ---------------------------------------------------------
# VALID SUCCESS STATES
# ---------------------------------------------------------

VALID_CRITIC_SUCCESS_STATES = {
    "PASS",
    "PASS_WITH_AMBIGUITY",
    "PASS_WITH_INCOMPLETE_DATA",
}


# ---------------------------------------------------------
# ENVIRONMENT
# ---------------------------------------------------------

def test_environment():
    """
    Verify required configuration without making external API calls.
    """

    print("\n[1/4] Checking environment configuration...")

    required = {
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER"),
        "LLM_MODEL": os.getenv("LLM_MODEL"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "MP_API_KEY": os.getenv("MP_API_KEY"),
    }

    success = True

    for key, value in required.items():

        if key in {"GEMINI_API_KEY", "MP_API_KEY"}:
            status = "CONFIGURED" if value else "MISSING"
        else:
            status = value if value else "MISSING"

        print(f"{key}: {status}")

        if not value:
            success = False

    if success:
        print("Environment Check: PASS")
    else:
        print("Environment Check: FAIL")

    return success


# ---------------------------------------------------------
# MATERIALS PROJECT
# ---------------------------------------------------------

def test_materials_project():
    """
    Test the real Materials Project API.

    This does NOT consume Gemini quota.
    """

    print("\n[2/4] Testing Materials Project...")

    try:
        from mp_api.client import MPRester

        api_key = os.getenv("MP_API_KEY")

        if not api_key:
            print(
                "MP Error: MP_API_KEY is not configured."
            )
            return False

        with MPRester(api_key) as mpr:

            docs = mpr.materials.summary.search(
                band_gap=(1, 2),
                num_chunks=1,
                chunk_size=2,
            )

            success = len(docs) > 0

            print("MP Check:", success)
            print(
                "MP Records Retrieved:",
                len(docs),
            )

            if docs:

                for doc in docs:

                    print(
                        "  -",
                        getattr(
                            doc,
                            "material_id",
                            "unknown",
                        ),
                        getattr(
                            doc,
                            "formula_pretty",
                            "unknown",
                        ),
                    )

            return success

    except Exception as exc:

        print(
            "MP Error:",
            str(exc),
        )

        return False


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

def test_database():
    """
    Verify SQLite/database infrastructure.
    """

    print("\n[3/4] Testing database...")

    try:

        Base.metadata.create_all(
            bind=engine
        )

        db = next(get_db())

        try:

            test_job_id = (
                f"database_test_{uuid.uuid4().hex}"
            )

            job = SearchJob(
                id=test_job_id,
                query="database verification",
                status="test",
            )

            db.add(job)
            db.commit()

            stored = (
                db.query(SearchJob)
                .filter(
                    SearchJob.id == test_job_id
                )
                .first()
            )

            success = stored is not None

            print(
                "Database Check:",
                success,
            )

            if stored:

                db.delete(stored)
                db.commit()

            return success

        finally:

            db.close()

    except Exception as exc:

        print(
            "Database Error:",
            str(exc),
        )

        return False


# ---------------------------------------------------------
# GEMINI
# ---------------------------------------------------------

def test_gemini_live():
    """
    Perform one REAL Gemini API request.

    WARNING:
    This consumes Gemini quota.

    Only run this when --live-llm is explicitly supplied.
    """

    print("\n[LIVE] Testing Gemini API...")

    try:

        from app.services.llm import get_llm

        llm = get_llm()

        response = llm.invoke(
            "Answer exactly with the word OK."
        )

        content = getattr(
            response,
            "content",
            "",
        )

        if isinstance(content, str):

            text = content

        elif isinstance(content, list):

            text = " ".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
            )

        else:

            text = str(content)

        success = (
            "OK" in text.upper()
        )

        print(
            "Gemini Check:",
            success,
        )

        print(
            "Gemini Response:",
            text,
        )

        return success

    except Exception as exc:

        error_text = str(exc)

        print(
            "Gemini Error:",
            error_text,
        )

        if (
            "429" in error_text
            or "RESOURCE_EXHAUSTED"
            in error_text
        ):

            print(
                "Gemini Status: "
                "QUOTA EXHAUSTED"
            )

            return "QUOTA_EXHAUSTED"

        if (
            "503" in error_text
            or "UNAVAILABLE"
            in error_text
        ):

            print(
                "Gemini Status: "
                "TEMPORARILY UNAVAILABLE"
            )

            return "TEMPORARILY_UNAVAILABLE"

        return False


# ---------------------------------------------------------
# COMPLETE AGENTIC WORKFLOW
# ---------------------------------------------------------

def test_full_workflow():
    """
    Execute the complete real agentic workflow.

    WARNING:
    This consumes multiple Gemini requests.

    Only run this with --live-llm.
    """

    print(
        "\n[LIVE] Testing complete agentic workflow..."
    )

    from app.orchestration.workflow import (
        run_workflow
    )

    Base.metadata.create_all(
        bind=engine
    )

    db = next(get_db())

    job_id = (
        f"test_job_{uuid.uuid4().hex}"
    )

    query = (
        "Find semiconductor materials with a band gap "
        "between 1 and 2 eV and good thermodynamic stability."
    )

    try:

        job = SearchJob(
            id=job_id,
            query=query,
            status="running",
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        print(
            "Workflow Job ID:",
            job_id,
        )

        run_workflow(
            job_id,
            query,
            db,
        )

        db.expire_all()

        job = (
            db.query(SearchJob)
            .filter(
                SearchJob.id == job_id
            )
            .first()
        )

        if job is None:

            print(
                "Workflow Error: "
                "Job not found."
            )

            return False

        state = job.state or {}

        status = job.status

        candidates = state.get(
            "candidates",
            [],
        )

        evaluations = state.get(
            "evaluations",
            [],
        )

        critic = state.get(
            "critic_result",
            "",
        )

        report = state.get(
            "report",
            "",
        )

        errors = state.get(
            "errors",
            [],
        )

        print(
            "\nWorkflow Results"
        )

        print(
            "----------------"
        )

        print(
            "Status:",
            status,
        )

        print(
            "Candidates:",
            len(candidates),
        )

        print(
            "Evaluations:",
            len(evaluations),
        )

        print(
            "Critic:",
            critic or "N/A",
        )

        print(
            "Report:",
            "AVAILABLE"
            if report
            else "UNAVAILABLE",
        )

        if errors:

            print("Errors:")

            for error in errors:

                print(
                    " -",
                    error,
                )

        # -------------------------------------------------
        # VALIDATE THE COMPLETE PIPELINE
        # -------------------------------------------------

        search_pipeline_success = (
            status == "completed"
            and len(candidates) > 0
            and len(evaluations) > 0
            and critic
            in VALID_CRITIC_SUCCESS_STATES
        )

        if search_pipeline_success:

            print(
                "\nAgentic Search Pipeline: PASS"
            )

            if critic == "PASS":

                print(
                    "Critic Validation: PASS"
                )

            elif critic == "PASS_WITH_AMBIGUITY":

                print(
                    "Critic Validation: "
                    "PASS_WITH_AMBIGUITY"
                )

                print(
                    "Note: The workflow "
                    "completed successfully "
                    "while preserving an "
                    "ambiguous qualitative "
                    "requirement."
                )

            elif (
                critic
                == "PASS_WITH_INCOMPLETE_DATA"
            ):

                print(
                    "Critic Validation: "
                    "PASS_WITH_INCOMPLETE_DATA"
                )

                print(
                    "Note: The workflow "
                    "completed successfully "
                    "while explicitly "
                    "preserving unavailable "
                    "scientific data."
                )

            if report:

                print(
                    "Final Report Generation: PASS"
                )

            else:

                print(
                    "Final Report Generation: "
                    "UNAVAILABLE"
                )

            return True

        # -------------------------------------------------
        # INVALID WORKFLOW RESULT
        # -------------------------------------------------

        print(
            "\nAgentic Search Pipeline: FAIL"
        )

        print(
            "Reason:"
        )

        if status != "completed":

            print(
                " - Workflow status was:",
                status,
            )

        if len(candidates) == 0:

            print(
                " - No candidates were returned."
            )

        if len(evaluations) == 0:

            print(
                " - No evaluations were produced."
            )

        if critic not in VALID_CRITIC_SUCCESS_STATES:

            print(
                " - Critic result was:",
                critic or "N/A",
            )

        return False

    except Exception as exc:

        print(
            "Workflow Error:",
            str(exc),
        )

        return False

    finally:

        db.close()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    live_llm = (
        "--live-llm"
        in sys.argv
    )

    print("=" * 60)

    print(
        "MatSearch AI - Backend Verification"
    )

    print("=" * 60)

    print(
        "\nMode:",
        "LIVE GEMINI"
        if live_llm
        else "QUOTA-SAFE",
    )

    environment_ok = (
        test_environment()
    )

    materials_project_ok = (
        test_materials_project()
    )

    database_ok = (
        test_database()
    )

    # -------------------------------------------------
    # QUOTA-SAFE MODE
    # -------------------------------------------------

    if not live_llm:

        print(
            "\n" + "=" * 60
        )

        print(
            "VERIFICATION SUMMARY"
        )

        print(
            "=" * 60
        )

        print(
            "Environment:",
            "PASS"
            if environment_ok
            else "FAIL",
        )

        print(
            "Materials Project:",
            "PASS"
            if materials_project_ok
            else "FAIL",
        )

        print(
            "Database:",
            "PASS"
            if database_ok
            else "FAIL",
        )

        print(
            "\nGemini Live API: "
            "NOT TESTED"
        )

        print(
            "Reason: quota-safe mode."
        )

        print(
            "\nTo perform the real "
            "Gemini test later:"
        )

        print(
            "python e2e_test.py --live-llm"
        )

        if (
            environment_ok
            and materials_project_ok
            and database_ok
        ):

            print(
                "\nFINAL RESULT: "
                "PASS "
                "(QUOTA-SAFE VERIFICATION)"
            )

            return 0

        print(
            "\nFINAL RESULT: FAIL"
        )

        return 1

    # -------------------------------------------------
    # LIVE GEMINI MODE
    # -------------------------------------------------

    gemini_result = (
        test_gemini_live()
    )

    if (
        gemini_result
        == "QUOTA_EXHAUSTED"
    ):

        print(
            "\n" + "=" * 60
        )

        print(
            "VERIFICATION SUMMARY"
        )

        print(
            "=" * 60
        )

        print(
            "Environment:",
            "PASS"
            if environment_ok
            else "FAIL",
        )

        print(
            "Materials Project:",
            "PASS"
            if materials_project_ok
            else "FAIL",
        )

        print(
            "Database:",
            "PASS"
            if database_ok
            else "FAIL",
        )

        print(
            "Gemini:",
            "QUOTA EXHAUSTED",
        )

        print(
            "\nFULL WORKFLOW: "
            "NOT RUN"
        )

        print(
            "Reason: Gemini quota "
            "is exhausted."
        )

        return 2

    if (
        gemini_result
        == "TEMPORARILY_UNAVAILABLE"
    ):

        print(
            "\nGemini is temporarily "
            "unavailable."
        )

        return 1

    if gemini_result is not True:

        print(
            "\nGemini live test "
            "did not pass."
        )

        return 1

    # -------------------------------------------------
    # FULL AGENTIC WORKFLOW
    # -------------------------------------------------

    workflow_ok = (
        test_full_workflow()
    )

    # -------------------------------------------------
    # FINAL SUMMARY
    # -------------------------------------------------

    print(
        "\n" + "=" * 60
    )

    print(
        "LIVE VERIFICATION SUMMARY"
    )

    print(
        "=" * 60
    )

    print(
        "Environment:",
        "PASS"
        if environment_ok
        else "FAIL",
    )

    print(
        "Materials Project:",
        "PASS"
        if materials_project_ok
        else "FAIL",
    )

    print(
        "Database:",
        "PASS"
        if database_ok
        else "FAIL",
    )

    print(
        "Gemini:",
        "PASS"
        if gemini_result is True
        else "FAIL",
    )

    print(
        "Agentic Workflow:",
        "PASS"
        if workflow_ok
        else "FAIL",
    )

    # -------------------------------------------------
    # FINAL VERDICT
    # -------------------------------------------------

    if (
        environment_ok
        and materials_project_ok
        and database_ok
        and gemini_result is True
        and workflow_ok
    ):

        print(
            "\nFINAL RESULT: PASS"
        )

        return 0

    print(
        "\nFINAL RESULT: FAIL"
    )

    return 1


if __name__ == "__main__":
    sys.exit(main())
