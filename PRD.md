MatSearch AI
Product Requirements Document (PRD)

Project Type: BS Materials Engineering Final Year Project
Product: MatSearch AI — Autonomous Materials Discovery & Engineering Platform
Document Type: Product Requirements Document
Version: 1.0
Status: Active Development

1. Team
Team Member	Responsibility
Hardik Sonu	Backend Development & AI/ML
Samreen Rehman	Frontend Development
Laiba Naeem	Documentation & Presentation
Javeria Munawar	Documentation & Presentation
2. Executive Summary

MatSearch AI is an autonomous AI-powered materials discovery and engineering platform designed to assist Materials and Metallurgical Engineers in finding, evaluating, comparing, and validating candidate materials for engineering requirements.

Instead of requiring an engineer to manually search scientific databases, inspect individual materials, compare properties, and prepare a technical conclusion, MatSearch AI accepts an engineering requirement written in natural language and executes a structured research workflow.

Example:

"Find stable lightweight semiconductor materials with density below 5 g/cm³ and band gap between 1 and 2 eV."

The system interprets the requirement, creates a research plan, searches real materials-science data, evaluates candidate materials against explicit constraints, identifies ambiguities, validates the results, and generates an engineering-oriented report.

The platform is designed around an important scientific principle:

AI should assist the engineer's research and reasoning, but it must not fabricate scientific data or replace engineering judgment.

Numerical material properties are obtained from authoritative scientific data sources or deterministic calculations. AI is used for natural-language interpretation, planning, explanation, and report generation.

3. Product Vision

The vision of MatSearch AI is to create an intelligent materials engineering research assistant capable of transforming natural-language engineering requirements into evidence-based materials discovery workflows.

The long-term goal is to provide engineers with a system that can:

Understand engineering requirements.
Identify measurable constraints.
Search scientific materials databases.
Retrieve real material properties.
Evaluate candidate materials deterministically.
Identify missing or ambiguous requirements.
Compare candidate materials.
Validate the reasoning process.
Explain how conclusions were reached.
Generate engineering reports.
Allow engineers to challenge and refine recommendations.
4. Problem Statement

Materials engineers often need to investigate large numbers of possible materials before selecting candidates for a particular application.

This process can involve:

Scientific databases
Research papers
Materials-property databases
Manual filtering
Property comparison
Thermodynamic analysis
Literature review
Data validation
Report preparation

The process can become time-consuming when multiple material properties and constraints must be considered simultaneously.

Traditional search systems also generally require users to know exactly which database fields and filters to use.

MatSearch AI addresses this problem by providing a natural-language engineering interface combined with an agentic research workflow.

5. Product Objectives

The primary objectives are:

Objective 1 — Natural-Language Materials Search

Allow engineers to describe material requirements naturally instead of requiring complex database queries.

Objective 2 — Automated Research Workflow

Automatically perform the major stages of materials discovery.

Objective 3 — Scientific Data Retrieval

Retrieve real material properties from scientific databases.

Objective 4 — Deterministic Evaluation

Evaluate explicit numerical requirements using deterministic software rather than relying on an LLM to perform scientific filtering.

Objective 5 — Explainability

Show why materials passed, failed, or remained ambiguous.

Objective 6 — Validation

Use a critic/validation stage to identify missing information, ambiguous requirements, and limitations.

Objective 7 — Engineering Reporting

Generate a structured report summarizing the search, candidates, evidence, limitations, and validation status.

6. Target Users

Primary users include:

Materials Engineers
Metallurgical Engineers
Materials Science Researchers
Engineering Students
University Researchers
R&D Engineers
Computational Materials Scientists
Academic Supervisors

Potential future users include:

Aerospace engineers
Semiconductor researchers
Energy researchers
Additive manufacturing engineers
Battery researchers
Corrosion engineers
Automotive materials engineers
7. Core User Problem

A user should be able to enter:

"Find lightweight semiconductor materials with a band gap between 1 and 2 eV and high thermodynamic stability."

without needing to manually construct database queries.

The system should then:

Engineering Requirement
        ↓
Requirement Understanding
        ↓
Research Planning
        ↓
Scientific Database Search
        ↓
Candidate Retrieval
        ↓
Deterministic Evaluation
        ↓
Validation / Critic
        ↓
Engineering Report
8. Core User Journey
Step 1 — Enter Requirement

The user enters a natural-language engineering requirement.

Step 2 — Requirement Interpretation

The system extracts:

Material properties
Numerical constraints
Units
Comparison operators
Qualitative requirements
Application context
Ambiguous terminology
Step 3 — Research Planning

The planning agent creates a research strategy.

Step 4 — Scientific Search

The system queries the Materials Project database.

Step 5 — Candidate Evaluation

Retrieved materials are evaluated against explicit constraints.

Step 6 — Validation

The critic checks:

Missing properties
Ambiguous requirements
Constraint satisfaction
Data provenance
Limitations
Step 7 — Report Generation

The system generates an engineering-oriented report.

Step 8 — Engineer Review

The engineer reviews the evidence and makes the final engineering decision.

9. Product Principles

MatSearch AI must follow these principles:

9.1 No Fabricated Scientific Data

The system must never invent material properties.

9.2 Evidence First

Scientific values should originate from identifiable data sources or deterministic calculations.

9.3 AI Is Not the Numerical Source of Truth

LLMs should not be trusted as the source of numerical material properties.

9.4 Deterministic Evaluation

Explicit numerical requirements should be evaluated programmatically.

9.5 Transparency

The system should explain where values came from.

9.6 Human Engineering Judgment

The final material-selection decision remains with the engineer.

9.7 Uncertainty Must Be Visible

If a requirement cannot be evaluated reliably, the system should identify it as ambiguous or unavailable instead of making assumptions.

10. System Architecture

The system follows an agentic architecture.

                    USER
                      |
                      v
             Requirement Agent
                      |
                      v
              Planning Agent
                      |
                      v
         Materials Project Agent
                      |
             +--------+--------+
             |                 |
             v                 v
      Scientific Data     Calculation Tools
             |                 |
             +--------+--------+
                      |
                      v
             Evaluation Agent
                      |
                      v
                Critic Agent
                      |
             +--------+--------+
             |                 |
          Revision          Validated
             |                 |
             v                 v
          Planner          Report Agent
                               |
                               v
                       Engineering Report
11. Agent Architecture
11.1 Requirement Agent

Responsibilities:

Interpret natural-language requirements.
Identify properties.
Extract numerical ranges.
Extract units.
Identify operators.
Identify qualitative requirements.
Identify ambiguous terminology.

Example:

Density below 5 g/cm³
→ property: density
→ operator: <
→ value: 5
→ unit: g/cm³
12. Planning Agent

The Planning Agent creates a research strategy based on the parsed requirements.

Responsibilities:

Determine searchable properties.
Identify required database fields.
Determine evaluation requirements.
Identify ambiguities.
Define the research workflow.

The planning agent must not invent scientific thresholds.

13. Materials Project Agent

The Materials Project Agent retrieves scientific material information.

Primary data source:

Materials Project

The agent retrieves available properties such as:

Material ID
Formula
Density
Band gap
Formation energy
Energy above hull
Stability information
Crystal system
Structure-related information

The frontend must never directly communicate with Materials Project.

All Materials Project access must occur through the backend.

14. Evaluation Agent

The Evaluation Agent performs deterministic evaluation.

Example:

Requirement:

Density < 5 g/cm³

Candidate:

Density = 4.58 g/cm³

Result:

PASS

Another example:

Band gap = 1.23 eV
Required = 1–2 eV
Result = PASS

The evaluator must not use an LLM to decide numerical pass/fail conditions.

15. Evaluation Statuses

The system should support:

PASS

The candidate satisfies the requirement.

FAIL

The candidate does not satisfy the requirement.

AMBIGUOUS

The requirement cannot be evaluated without additional definition or clarification.

UNAVAILABLE

The required property is not available.

INCOMPLETE

The candidate cannot receive a complete overall evaluation because one or more requirements remain unresolved.

16. Qualitative Requirements

The system must distinguish between quantitative and qualitative requirements.

For example:

Lightweight

does not automatically mean:

Density < 5 g/cm³

unless the user explicitly defines it that way.

Similarly:

Stable

does not automatically define a specific thermodynamic threshold.

Therefore the system may report:

Thermodynamic Stability
Status: AMBIGUOUS

Reason:
No numerical stability criterion was provided.

The system may identify potentially relevant scientific indicators such as:

Energy above hull
Stability flag

but must clearly distinguish these from the user's original requirement.

17. Scientific Data Provenance

Every important scientific value should have provenance.

Supported provenance categories:

SOURCE_VALUE

Directly retrieved from a scientific database.

DERIVED_VALUE

Produced by a deterministic calculation.

AI_INTERPRETATION

Interpretation generated by the AI.

UNAVAILABLE

Required information is not available.

Example:

Band Gap
Value: 1.2258 eV
Provenance: SOURCE_VALUE
Source: Materials Project
18. Candidate Materials

Candidate results should contain information such as:

Material ID
Formula
Density
Band gap
Formation energy
Energy above hull
Stability
Crystal system
Requirement evaluation
Provenance

The candidate list must be based on real retrieved data.

19. Requirement Matching

Each candidate should show a clear requirement match.

Example:

Density

Required:
< 5 g/cm³

Actual:
4.5871 g/cm³

Status:
PASS

Example:

Band Gap

Required:
1–2 eV

Actual:
1.2258 eV

Status:
PASS

If a candidate fails:

Status:
FAIL

Reason:
Band gap is outside the requested range.
20. Material Detail Page

Each material should have a dedicated detail view.

Information may include:

Formula
Materials Project ID
Density
Band gap
Formation energy
Energy above hull
Stability
Crystal system
Space group
Lattice parameters
Unit-cell information
Available structure data
Provenance
21. Crystal Structure Visualization

The frontend should provide interactive crystal structure visualization.

Technology:

3Dmol.js

The visualization should allow users to inspect the retrieved structure where structure data is available.

The visualization must represent real structure data rather than fabricated geometry.

22. Material Comparison

Users should be able to select multiple candidate materials and compare them.

Comparison properties may include:

Density
Band gap
Formation energy
Energy above hull
Stability
Crystal system
Other available properties

The comparison interface should support:

Tables
Charts
Property differences
Requirement status
23. Validation / Critic Agent

The Critic Agent validates the research workflow.

It should check:

Were requirements correctly interpreted?
Were numerical constraints evaluated?
Were required properties available?
Were data sources identified?
Are any requirements ambiguous?
Are any important limitations present?
Is further research required?

The critic must not fabricate evidence.

24. Challenge Recommendation

The platform should support:

Challenge This Recommendation

The user can ask the system to:

Reconsider candidates.
Change priorities.
Search for alternatives.
Modify constraints.
Investigate another property.
Re-run the research workflow.

The challenge workflow should preserve the original search context.

25. Engineering Report

The report should summarize:

Original engineering requirement.
Parsed requirements.
Research plan.
Scientific data sources.
Search process.
Candidate materials.
Requirement evaluation.
Ambiguous requirements.
Validation results.
Important limitations.
Candidate comparison.
Evidence/provenance.
Engineering interpretation.

The report must clearly distinguish:

Scientific Data
vs.
Deterministic Evaluation
vs.
AI Interpretation
26. Human Decision Requirement

MatSearch AI is a decision-support system.

The final engineering decision must remain with the engineer.

The platform should not claim that a material is universally "the best" material without defining the engineering criteria and supporting evidence.

The system should instead provide:

Evidence
Property values
Constraint results
Comparisons
Limitations
Validation status

so that the engineer can make the final decision.

27. Real-Time Agent Workflow

The frontend should display actual workflow progress.

Example:

✓ Understanding engineering requirement

✓ Creating research plan

✓ Querying Materials Project

✓ Evaluating candidates

✓ Validating results

● Generating engineering report

Supported states:

pending
running
completed
failed
28. Server-Sent Events

The backend should provide real-time workflow events through SSE.

Endpoint:

GET /api/search/{search_id}/events

The frontend should use these events to update the agent timeline.

The frontend should not simulate agent progress independently.

29. Backend API

Primary endpoints:

POST /api/search/

GET /api/search/{search_id}

GET /api/search/{search_id}/events

GET /api/material/{material_id}

POST /api/compare/

GET /api/reports/{search_id}

POST /api/reports/{search_id}/generate

GET /health

GET /api/status
30. Backend Technology

The backend will use:

Python
FastAPI
Pydantic
SQLAlchemy
PostgreSQL
SQLite for local development
Materials Project API
pymatgen
NumPy
Pandas
LangGraph / LangChain
Gemini
SSE
pytest
httpx
31. Frontend Technology

The frontend will use:

Next.js
React
TypeScript
Tailwind CSS
Lucide React
Recharts
3Dmol.js
TanStack Query
Zod
32. Frontend Routes

Required routes:

/
 /search
 /search/[id]
 /materials/[materialId]
 /compare
 /history
 /saved
 /reports
 /settings
33. Main Frontend Components

The frontend should include:

LandingPage
SearchInput
RequirementPanel
ConstraintEditor
AgentTimeline
AgentStep
SearchSummary
CandidateTable
CandidateCard
RequirementMatch
MaterialDetails
CrystalViewer
PropertyTable
PropertyCharts
ComparisonTable
AgentExplanation
ValidationPanel
ChallengePanel
SearchHistory
SavedMaterials
ReportViewer
34. User Interface Requirements

The application should look like a professional engineering research workstation.

Design priorities:

Strong typography
Clean hierarchy
Professional tables
Technical visualizations
Clear status indicators
Consistent spacing
Responsive layout
Minimal unnecessary decoration

The application should avoid:

Generic chatbot appearance
Excessive gradients
Cartoon AI graphics
Excessive animation
Unnecessary glassmorphism
Decorative elements that reduce information density
35. Application Experience

The user should feel that they have assigned an engineering research problem to an autonomous materials engineer.

The interface should communicate:

UNDERSTAND
    ↓
PLAN
    ↓
SEARCH
    ↓
EVALUATE
    ↓
VALIDATE
    ↓
REPORT

rather than simply displaying a chatbot conversation.

36. Search History

The platform should maintain search history.

Each search should contain information such as:

Search ID
Original query
Date/time
Status
Number of candidates
Validation status
Report availability

Users should be able to reopen previous searches.

37. Saved Materials

Users should be able to save materials for later review.

Saved materials should include:

Material ID
Formula
Key properties
Original search context
Saved timestamp
38. Database Architecture

Production database:

PostgreSQL / Supabase

Local development:

SQLite

The database should store:

Search jobs
Search requirements
Agent state
Candidate results
Evaluation results
Validation information
Report information
39. Security Requirements

The system must:

Keep API keys on the backend.
Never expose Materials Project credentials to the frontend.
Never expose Gemini API keys to the frontend.
Store secrets in environment variables.
Validate API requests.
Validate user input.
Avoid storing unnecessary sensitive information.
40. API Separation

The frontend must communicate only with the MatSearch AI backend.

Architecture:

Frontend
   |
   v
MatSearch AI Backend
   |
   +---- Materials Project
   |
   +---- Gemini
   |
   +---- PostgreSQL

The frontend must not directly call Materials Project.

41. Error Handling

The platform must provide clear error states for:

Backend unavailable
Materials Project unavailable
LLM unavailable
Database failure
Invalid requirement
No candidates found
Missing scientific properties
Search timeout
Report generation failure
SSE connection failure

Errors should be understandable to the user.

42. No-Result State

If no materials satisfy the explicit constraints, the system must not fabricate results.

Instead it should explain:

Number of candidates searched
Constraints applied
Why candidates failed
Whether constraints could be relaxed
Whether additional research is recommended
43. Scientific Limitations

Materials Project data represents computational materials information and should not automatically be interpreted as experimental validation.

The system must clearly communicate that:

Computational predictions may differ from experimental behavior.
Database completeness is limited.
Material availability may not be guaranteed.
Synthesis feasibility is not automatically established.
Processing conditions may affect real-world properties.
Application-specific performance requires further validation.
44. AI Limitations

The AI system may:

Misinterpret ambiguous natural language.
Require clarification.
Produce an incomplete interpretation.
Provide an interpretation that requires human verification.

Therefore, AI-generated conclusions must remain distinguishable from source scientific data.

45. Performance Requirements

The system should:

Respond quickly to normal API requests.
Provide real-time progress during long searches.
Avoid unnecessary database requests.
Cache appropriate information where useful.
Handle multiple candidate materials efficiently.

Long-running agent workflows should not require the user to keep refreshing the page.

46. Reliability Requirements

The platform should:

Preserve workflow state.
Recover gracefully from failures where possible.
Record search status.
Avoid losing completed search results.
Maintain provenance.
Prevent partial results from being presented as fully validated results.
47. Accessibility

The frontend should provide:

Readable typography
Sufficient contrast
Keyboard accessibility where practical
Clear status indicators
Accessible form controls
Responsive layout
Meaningful labels
48. Responsive Design

The application should support:

Desktop
Laptop
Tablet

The primary experience is desktop-first because materials engineering research requires tables, comparisons, and technical visualizations.

49. MVP Scope

The MVP must include:

Search
Natural-language search
Requirement parsing
Numerical constraints
Qualitative requirement detection
Agent Workflow
Requirement Agent
Planning Agent
Materials Project Agent
Evaluation Agent
Critic Agent
Report Agent
Results
Candidate materials
Material properties
Requirement matching
Pass/fail/ambiguous states
Provenance
Material Details
Material properties
Crystal structure
3D visualization
Comparison
Multi-material comparison
Property tables
Charts where appropriate
Validation
Critic results
Missing information
Ambiguity
Limitations
Reports
Engineering report
Evidence
Evaluation
Validation
Limitations
Application
Search history
Saved materials
Loading states
Error states
Responsive interface
50. Future Scope

Potential future capabilities include:

Literature search
Scientific paper retrieval
Experimental dataset integration
Additional materials databases
Materials synthesis feasibility analysis
Cost analysis
Environmental impact analysis
Manufacturing constraints
Process-property prediction
Materials optimization
Multi-objective optimization
Autonomous literature review
Experimental recommendation planning
Additional computational materials databases
Advanced structure-property analysis
51. Out of Scope for Current MVP

The following are not required for the initial version:

Direct experimental laboratory control
Automatic material synthesis
Autonomous physical experiments
Guaranteed experimental validation
Fabricated scientific values
Unverified engineering claims
Direct frontend access to Materials Project
AI-generated replacement for scientific databases
52. Acceptance Criteria

The MVP will be considered functionally complete when:

AC-01

A user can submit a natural-language materials engineering requirement.

AC-02

The system can identify numerical constraints.

AC-03

The system can identify qualitative or ambiguous requirements.

AC-04

The system can create a research plan.

AC-05

The backend can retrieve real materials from Materials Project.

AC-06

The system can evaluate explicit numerical constraints deterministically.

AC-07

The system can identify ambiguous requirements.

AC-08

The system displays material provenance.

AC-09

The system displays candidate materials.

AC-10

Users can inspect material details.

AC-11

Users can compare multiple materials.

AC-12

Users can see agent workflow progress.

AC-13

The system provides validation information.

AC-14

The system can generate an engineering report.

AC-15

The system does not fabricate scientific properties.

AC-16

The frontend does not directly communicate with Materials Project.

AC-17

The system preserves search state.

AC-18

The application provides meaningful error states.

53. Testing Requirements

Testing should include:

Backend Tests
API tests
Requirement parsing tests
Evaluation tests
Materials Project integration tests
Database tests
Report generation tests
SSE tests
AI Tests
Requirement interpretation
Ambiguous terminology
Planning
Critic behavior
Report generation
Frontend Tests
Search interface
Candidate table
Material details
Comparison
SSE updates
Loading states
Error states
Responsive layout
End-to-End Testing

A complete test should verify:

User Query
   ↓
Requirement Parsing
   ↓
Planning
   ↓
Materials Project
   ↓
Evaluation
   ↓
Critic
   ↓
Report
   ↓
Frontend Display
54. Production Verification Example

A production search was successfully tested using the query:

Find stable lightweight semiconductor materials with density below 5 g/cm3 and band gap between 1 and 2 eV.

The workflow successfully completed with:

Status: completed

Candidates: 10

Evaluations: 10

Critic: PASS_WITH_AMBIGUITY

Report: AVAILABLE

The system correctly identified that:

Density was quantitatively defined.
Band gap was quantitatively defined.
Stability was qualitative and therefore remained ambiguous.
Lightweight was not treated as an independent invented threshold.

This demonstrates the intended scientific behavior of the system.

55. Example Candidate

Example candidate retrieved from Materials Project:

Material ID:
mp-560328

Formula:
Ag15P4S16Cl3

Density:
4.5871 g/cm³

Band Gap:
1.2258 eV

Energy Above Hull:
0 eV/atom

Is Stable:
True

Evaluation:

Density < 5 g/cm³
PASS

Band Gap 1–2 eV
PASS

Thermodynamic Stability
AMBIGUOUS

Overall Evaluation
INCOMPLETE

The incomplete status is appropriate because the original qualitative stability requirement was not converted into an arbitrary numerical threshold.

56. Product Success Metrics

The project should measure:

Successful search completion rate
Requirement parsing accuracy
Numerical evaluation correctness
Scientific provenance coverage
Candidate retrieval success
Validation coverage
Report generation success
API reliability
Frontend usability
Search response time

Scientific correctness should take priority over simply maximizing the number of generated results.

57. Non-Functional Requirements

The system should be:

Reliable

Workflow state should be preserved.

Explainable

The user should understand how results were produced.

Maintainable

Backend, frontend, and documentation should remain modular.

Extensible

Additional databases and material properties should be possible to integrate later.

Secure

API credentials must remain server-side.

Scientifically Responsible

The platform must clearly distinguish data, calculations, and AI interpretation.

58. Maintainability

The codebase should maintain separation between:

API Layer
    ↓
Agent Layer
    ↓
Scientific Data Layer
    ↓
Evaluation Layer
    ↓
Database Layer

Frontend should maintain separation between:

Pages
Components
API Client
Types
State Management
Visualization
59. Extensibility

The architecture should allow future integration of additional data sources such as:

Other computational materials databases
Experimental datasets
Scientific literature databases
Open materials datasets
Domain-specific databases

New data sources should not require rewriting the entire application.

60. Data Integrity

Scientific values should be stored with:

Property name
Value
Unit
Source
Provenance
Material ID
Retrieval context where applicable

The system should avoid silently modifying source values.

61. Engineering Ethics

MatSearch AI is an engineering decision-support system.

The system should not present AI-generated interpretations as experimental facts.

Reports should clearly communicate:

Evidence
Assumptions
Uncertainty
Missing data
Limitations

Users must be able to distinguish between:

What the database says

and

What the AI interprets

and

What the engineer decides
62. Team Responsibilities
Hardik Sonu
Backend Development & AI/ML

Responsibilities:

Backend architecture
FastAPI development
Database integration
Materials Project integration
AI/ML integration
Agent architecture
Requirement processing
Evaluation system
Critic system
Report generation
API development
SSE implementation
Backend testing
Deployment and backend maintenance
Samreen Rehman
Frontend Development

Responsibilities:

Next.js application
React components
UI/UX implementation
Search interface
Agent timeline
Candidate results
Material detail pages
Material comparison
Crystal visualization
Charts
Validation interface
Reports interface
API integration
SSE frontend integration
Responsive design
Frontend testing
Laiba Naeem
Documentation & Presentation

Responsibilities:

Project documentation
Technical documentation support
Project report preparation
User documentation
Presentation preparation
Diagrams and workflow documentation
Research documentation
Final project presentation material
Javeria Munawar
Documentation & Presentation

Responsibilities:

Project documentation
Technical writing support
Project report preparation
Presentation preparation
System workflow documentation
Research documentation
Demonstration material
Final project presentation support
63. Team Collaboration Workflow

The team will work using clearly separated responsibilities while maintaining continuous integration between modules.

                MATSEARCH AI
                     |
       +-------------+-------------+
       |             |             |
       v             v             v
   Backend &      Frontend     Documentation
    AI/ML                      & Presentation
       |             |             |
       |             |             |
       +-------------+-------------+
                     |
                     v
              Final Integration
                     |
                     v
              Final Demonstration

Backend and frontend development must follow the agreed API contract.

Documentation should be updated alongside major project milestones rather than only at the end of development.

64. Official Technical Resources

Production Backend:

https://mat-search-ai-backend.vercel.app

API Documentation:

https://mat-search-ai-backend.vercel.app/docs

OpenAPI Specification:

https://mat-search-ai-backend.vercel.app/openapi.json

ReDoc:

https://mat-search-ai-backend.vercel.app/redoc

GitHub Repository:

https://github.com/hardik-sonu/MatSearch-AI-Backend
65. Documentation Structure

The project repository should contain:

MatSearch-AI-Backend/
│
├── PRD.md
├── README.md
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API-INTEGRATION.md
│   ├── SCIENTIFIC-METHODOLOGY.md
│   └── DEVELOPMENT.md
│
├── app/
├── api/
├── requirements.txt
├── vercel.json
└── .env.example

The PRD should serve as the main product-level reference for the entire team.

66. Document Relationship

The project documentation should follow this structure:

PRD
"What are we building and why?"

        ↓

ARCHITECTURE
"How is the system structured?"

        ↓

API INTEGRATION
"How do frontend and backend communicate?"

        ↓

SCIENTIFIC METHODOLOGY
"How are materials scientifically evaluated?"

        ↓

DEVELOPMENT
"How do developers run and maintain the project?"
67. Final Product Definition

MatSearch AI is an autonomous materials discovery and engineering platform that transforms natural-language engineering requirements into structured, evidence-based materials research workflows.

The completed system should allow an engineer to:

Describe an Engineering Problem
            ↓
Understand the Requirement
            ↓
Plan the Research
            ↓
Search Real Materials Data
            ↓
Evaluate Candidate Materials
            ↓
Identify Ambiguities
            ↓
Validate the Results
            ↓
Compare Candidates
            ↓
Generate an Engineering Report
            ↓
Make the Final Engineering Decision

The platform must prioritize scientific integrity, traceability, explainability, and engineering usefulness.

68. Final Principle

MatSearch AI does not replace the Materials Engineer. It reduces the time required to discover, evaluate, compare, and understand candidate materials while keeping scientific evidence, uncertainty, and engineering judgment visible throughout the process.

Document Status

Project: MatSearch AI
Version: 1.0
Status: Active Development
Project Type: BS Materials Engineering Final Year Project

Backend Development & AI/ML: Hardik Sonu
Frontend Development: Samreen Rehman
Documentation & Presentation: Laiba Naeem & Javeria Munawar