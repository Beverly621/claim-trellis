from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from claim_trellis import __version__
from claim_trellis.audit import run_audit
from claim_trellis.config import Settings, get_settings
from claim_trellis.ingestion import IngestionError, parse_document_bytes
from claim_trellis.models import (
    AuditEvent,
    AuditRequest,
    ClaimAudit,
    EvidenceSearchRequest,
    HumanReviewRequest,
    ParsedDocument,
    ProposalVersion,
    RetrievedCandidate,
    RevisionRequest,
    RevisionRun,
)
from claim_trellis.retrieval import retrieve
from claim_trellis.revisions import revise
from claim_trellis.storage import AuditStore, LifecycleConflict


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    resolved_settings.ensure_local_paths()
    store = AuditStore(resolved_settings.resolved_database_path)
    app = FastAPI(
        title="ClaimTrellis API",
        version=__version__,
        description="Auditable claim-to-source verification with human final judgment.",
    )
    app.state.settings = resolved_settings
    app.state.store = store
    app.state.judgment_provider = None

    @app.exception_handler(LifecycleConflict)
    async def lifecycle_conflict(request: Request, exc: LifecycleConflict) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.get("/healthz")
    def health() -> dict[str, object]:
        active = app.state.settings
        return {
            "status": "ok",
            "version": __version__,
            "judgment_provider": active.judgment_provider,
            "provider_configured": bool(active.jev_api_key),
            "jev_model": active.jev_model,
            "auto_accept_enabled": False,
        }

    @app.post("/api/v1/documents/parse", response_model=ParsedDocument)
    async def parse_document(
        document: Annotated[UploadFile, File(...)],
    ) -> ParsedDocument:
        active: Settings = app.state.settings
        data = await document.read(active.max_upload_bytes + 1)
        try:
            return parse_document_bytes(
                document.filename or "upload.txt",
                data,
                document.content_type or "application/octet-stream",
                max_bytes=active.max_upload_bytes,
                max_chars=active.max_source_chars,
            )
        except IngestionError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post("/api/v1/evidence/search", response_model=list[RetrievedCandidate])
    def evidence_search(request: EvidenceSearchRequest) -> list[RetrievedCandidate]:
        return retrieve(request.claim, request.source_text, top_k=request.top_k)

    @app.post("/api/v1/audits", response_model=ClaimAudit, status_code=201)
    async def create_audit(
        request: AuditRequest,
    ) -> ClaimAudit:
        active: Settings = app.state.settings
        database: AuditStore = app.state.store
        if len(request.source_text) > active.max_source_chars:
            raise HTTPException(status_code=413, detail="Source text exceeds the configured limit.")
        audit = await run_audit(request, active, judgment_provider=app.state.judgment_provider)
        return database.save(audit)

    @app.get("/api/v1/audits", response_model=list[ClaimAudit])
    def list_audits(limit: int = 50) -> list[ClaimAudit]:
        database: AuditStore = app.state.store
        return database.list_audits(limit=min(max(limit, 1), 200))

    @app.get("/api/v1/audits/{audit_id}", response_model=ClaimAudit)
    def get_audit(audit_id: str) -> ClaimAudit:
        database: AuditStore = app.state.store
        audit = database.get(audit_id)
        if audit is None:
            raise HTTPException(status_code=404, detail="Audit not found.")
        return audit

    @app.post("/api/v1/audits/{audit_id}/reviews", response_model=ClaimAudit)
    def review_audit(
        audit_id: str,
        request: HumanReviewRequest,
    ) -> ClaimAudit:
        database: AuditStore = app.state.store
        if database.get(audit_id) is None:
            raise HTTPException(status_code=404, detail="Audit not found.")
        return database.review(audit_id, request)

    @app.get("/api/v1/audits/{audit_id}/proposals", response_model=list[ProposalVersion])
    def proposal_history(audit_id: str) -> list[ProposalVersion]:
        get_audit(audit_id)
        return store.proposals(audit_id)

    @app.get("/api/v1/audits/{audit_id}/proposals/current", response_model=ProposalVersion)
    def current_proposal(audit_id: str) -> ProposalVersion:
        return proposal_history(audit_id)[-1]

    @app.get("/api/v1/audits/{audit_id}/revisions", response_model=list[RevisionRun])
    def revision_history(audit_id: str) -> list[RevisionRun]:
        get_audit(audit_id)
        return store.revisions(audit_id)

    @app.post("/api/v1/audits/{audit_id}/revisions", response_model=RevisionRun)
    async def request_revision(audit_id: str, request: RevisionRequest) -> RevisionRun:
        get_audit(audit_id)
        return await revise(
            store, audit_id, request, resolved_settings, app.state.judgment_provider
        )

    @app.get("/api/v1/audits/{audit_id}/events", response_model=list[AuditEvent])
    def audit_events(audit_id: str) -> list[AuditEvent]:
        database: AuditStore = app.state.store
        if database.get(audit_id) is None:
            raise HTTPException(status_code=404, detail="Audit not found.")
        return database.events(audit_id)

    packaged_web_dir = Path(__file__).resolve().parent / "web"
    source_web_dir = Path(__file__).resolve().parents[2] / "web"
    web_dir = packaged_web_dir if packaged_web_dir.exists() else source_web_dir
    if web_dir.exists():
        app.mount("/assets", StaticFiles(directory=web_dir), name="assets")

        @app.get("/", include_in_schema=False)
        def index() -> FileResponse:
            return FileResponse(web_dir / "index.html")

    return app


app: FastAPI = create_app()
