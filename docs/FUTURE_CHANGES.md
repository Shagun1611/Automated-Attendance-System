# Future Changes & Roadmap — Automated Attendance System (Capstone)

This document lists recommended fixes, improvements, tests, and deployment steps to turn this repository into a fully functional, production-ready capstone project. Prioritize items marked "High" and aim to implement them before final demo.

---

## 1. Immediate fixes (High priority)

1.1. Fix backend dependency & environment setup
- Ensure `attendance_env` virtual environment has all `backend/requirements.txt` packages installed. Face recognition packages (dlib, face-recognition, opencv) are heavy; document OS-specific install steps (Windows vs Linux) and add `README` notes.
- Add a `requirements-dev.txt` with test-only packages (pytest, pytest-flask) to speed CI installs.

1.2. Consolidate route files and services
- Split `backend/app/routes/__init__.py` into multiple modules (auth, students, attendance, admin, face_recognition) to improve maintainability.
- Ensure imports are absolute and consistent (avoid circular imports by importing `db` and `app` once in a central module).

1.3. Improve CORS and security headers
- Set explicit CORS in `backend/app.py` to allow the frontend origin and Authorization header; do not use wildcard in production.
- Add rate-limiting on auth endpoints to reduce brute-force risk.

1.4. Run & fix tests
- Run `pytest` locally and iterate on failing tests. The repository currently includes an integration test for admin endpoints — ensure tests pass with in-memory SQLite.

---

## 2. Functional enhancements (High → Medium)

2.1. Teacher/Class relationship
- Current model: `Class.teacher_id` single teacher per class. Decide if teachers may manage multiple classes (current model supports multiple classes per teacher). If you need many-to-many, add `teacher_classes` association table.

2.2. Teacher onboarding UX
- Improve Admin Add Teacher page: full Create/Edit workflow with validation, invite email, and temporary password flows.
- Support teacher profile image upload during creation.

2.3. Audit & admin UI
- Add an `AuditLog` viewer endpoint and a secure admin page to view activity with filters (user, action, date range).
- Ensure all admin actions (create/update/delete users, class assignments, system settings) create AuditLog entries.

2.4. Import/export & data seeding
- Add scripts to seed demo data (students, classes, teachers) and an import tool for CSV/Excel.

---

## 3. Testing & Quality (High)

3.1. Expand automated tests
- Unit tests for business logic (attendance_service, face_recognition_service mocked), and integration tests for endpoints (Flask test client).
- Frontend tests with React Testing Library for AdminAddTeacher component (happy path + error states).
- Add CI pipeline to run linters and tests on PRs.

3.2. Linting & formatting
- Add `pre-commit` hooks to run `black` and `flake8` for Python and ESLint/Prettier for frontend.

3.3. Security scans
- Add dependency vulnerability checks (Safety for Python or GitHub Dependabot) and fix high/critical CVEs.

---

## 4. Performance & scaling (Medium)

4.1. Face recognition performance
- Move face recognition workloads to a background worker or separate service to avoid blocking API requests. Use Redis + RQ or Celery.
- Cache computed face encodings and use vector similarity indexing (FAISS or Annoy) for large datasets.

4.2. Database
- For production, use PostgreSQL. Tune indices (attendance_records(date, student_id), students(class_name, section) already exist) and add connection pooling.

4.3. Concurrency & deployment
- Use a WSGI server (Gunicorn) with multiple workers behind nginx or use containerized deployment to Azure/AWS/GCP.

---

## 5. Deployment & DevOps (High)

5.1. Containerize everything
- Create clean `Dockerfile` for backend and frontend. Backend should not include heavy CV deps unless you build a GPU-enabled image.
- Use `docker-compose.yml` to orchestrate backend, frontend, and PostgreSQL for local development.

5.2. CI/CD
- Configure GitHub Actions to run tests, linting, and build Docker images. Create a `deploy` workflow (manual trigger) for demo deploys.

5.3. Production checklist
- HTTPS + TLS
- Environment variable management / secret store
- Monitoring and logging (Prometheus/Grafana or cloud-native)
- Backups for PostgreSQL

---

## 6. Security & privacy (High)

6.1. Data protection
- Sensitive data: do not store raw face images in plain storage without proper access control. Consider encrypting profile images and encodings at rest.
- Add data retention policy and deletion workflows (GDPR-style deletion on request).

6.2. Authentication & Authorization
- Use role-based access control, and restrict admin-only endpoints robustly (backend checks). You already have JWT — consider short lived tokens + refresh tokens.

6.3. Secrets management
- Use `.env` for local dev, but store secrets in a secure vault for production.

---

## 7. Acceptance criteria for Capstone (deliverable-ready)

- Core functionality working end-to-end: register student, upload/capture face, recognize face, mark attendance automatically and manually.
- Admin flows: create teacher, assign classes, view and correct attendance, audit logs of all admin actions.
- Comprehensive test coverage: backend unit/integration tests, frontend unit tests, and passing CI checks.
- Deployment: a script or instruction to launch the full stack locally via `docker-compose` and a deployed demo (optional).
- Documentation: README with setup & usage, HOW_TO_USE.md (dev instructions), and this FUTURE_CHANGES.md included in `docs/`.

---

## 8. Suggested timeline (2–4 weeks depending on team size)

Week 1
- Stabilize backend routes and dependency install instructions.
- Fix failing tests and add CI pipeline skeleton.
- Add AuditLog viewer endpoint.

Week 2
- Finish frontend admin UX (Edit/Assign modal polish), add frontend tests.
- Add data seeding/import scripts.

Week 3
- Containerize and test docker-compose setup.
- Add monitoring/logging and finalize documentation.

Week 4
- Polish UI, run final end-to-end QA, fix edge-case bugs, and prepare final demo.

---

## 9. Quick checklist to hand to graders

- [ ] Does `python app.py` start without errors in a clean venv? (yes/no)
- [ ] Are tests passing (`pytest`)?
- [ ] Can admin create teacher and assign class from frontend?
- [ ] Can the system mark attendance via face recognition (demo-ready)?
- [ ] Is there audit logging for admin actions?
- [ ] Is there deployment documentation and `docker-compose` demo?

---

If you want, I can now:
- Add a `docs/DEPLOY.md` with exact docker-compose + production notes.
- Add the AuditLog viewer endpoint and a minimal frontend page to view logs.
- Create GitHub Actions workflows for tests + lint.

Tell me which of the above you'd like me to implement next and I will proceed.
