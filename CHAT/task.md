# Pharmacy Matcher Desktop App — Tasks

## Phase 1: Core Infrastructure
- [x] Create `desktop_app/` folder structure
- [x] Build `desktop_app/database.py` — SQLite history manager
- [x] Build `desktop_app/server_manager.py` — MSEMAX process manager
- [x] Build `desktop_app/backend.py` — Python API bridge (with file dialog, reviews, history)

## Phase 2: Frontend UI
- [x] Build `desktop_app/templates/index.html` — Full SPA (Home, New, Results, History, Settings)
- [x] Build `desktop_app/static/style.css` — RTL professional styling
- [x] Build `desktop_app/static/app.js` — Frontend logic + API calls

## Phase 3: App Entry & Launch
- [x] Build `desktop_app/app.py` — pywebview entry point
- [x] Create `setup.bat` — installs requirements + creates desktop shortcut
- [x] Create `run.bat` — launches app without Terminal
- [ ] Install `pywebview` dependency and test launch

## Phase 4: Testing & Polish
- [ ] End-to-end test: New → Submit → Review → Finalize
- [ ] Test History persistence
- [ ] Test MSEMAX server start/stop
