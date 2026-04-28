.PHONY: service-run

service-run:
	@uvicorn main:app --reload & \
	BACKEND_PID=$$!; \
	cleanup() { \
		trap - INT TERM EXIT; \
		kill $$BACKEND_PID 2>/dev/null; \
		wait $$BACKEND_PID 2>/dev/null; \
	}; \
	trap cleanup INT TERM EXIT; \
	cd frontend && npm run dev || true