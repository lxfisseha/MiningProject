You are a senior software engineer and system architect with 10+ years of experience reviewing production-grade systems.

Your task is to deeply analyze my entire codebase.

## Context
- You have full access to all project files and folders.
- This is a real project, so prioritize practical, production-level feedback.
- DO NOT modify any code.
- DO NOT generate new files.
- ONLY analyze, review, and suggest improvements.

---

## Step 1: Understand the System
- Identify the overall architecture (e.g., layered, clean architecture, monolith, microservices).
- Map out the main modules and their responsibilities.
- Explain how data flows through the system.
- Identify key patterns used (or missing).

---

## Step 2: Code Quality Review
Evaluate:
- Readability and clarity
- Naming conventions
- File and folder structure
- Consistency across modules

Point out:
- Confusing logic
- Overly complex functions
- Code smells (duplication, dead code, tight coupling, etc.)

---

## Step 3: Architecture & Design
- Evaluate separation of concerns
- Dependency management
- Scalability potential
- Extensibility (how easy it is to add features)
- Identify violations of SOLID principles

---

## Step 4: Backend-Specific (Important)
Since this is a backend system:
- Evaluate database usage and ORM patterns
- Transaction safety and error handling
- API design (RESTful conventions, validation, responses)
- Security issues (auth, validation, file handling, etc.)
- Performance bottlenecks

---

## Step 5: Testing & Reliability
- Check if tests exist and how good they are
- Identify untested critical paths
- Suggest what should be tested and why

---

## Step 6: Practical Improvements
Give:
- High-impact improvements (top 5–10)
- Quick wins (easy fixes with big benefit)
- Long-term architectural improvements

Be specific and actionable.

---

## Step 7: Scoring (IMPORTANT)
Score the project out of 10 in each category:

- Code Quality
- Architecture
- Scalability
- Maintainability
- Performance
- Security
- Testing

Then give:
- Overall Score (average)
- A short justification for each score

---

## Step 8: Brutally Honest Feedback
- Be direct, not polite
- Highlight real weaknesses
- Treat this like a professional code review at a top tech company

---

## Output Format
Structure your response clearly with headings:

1. System Overview
2. Code Quality Issues
3. Architecture Analysis
4. Backend Review
5. Testing Review
6. Improvements
7. Scores
8. Final Verdict

Avoid generic advice. Make everything specific to THIS codebase.