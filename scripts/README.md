# 🛠️ Migration Scripts

Scripts trong thư mục này giúp migrate project sang cấu trúc mới có tổ chức.

## 📋 Migration Checklist

### ✅ Completed
- [x] Created PROJECT_ORGANIZATION_ANALYSIS.md
- [x] Updated copilot.instructions.md with organization rules
- [x] Created migration script

### ⏳ Pending
- [ ] Review migration mappings
- [ ] Run dry-run migration
- [ ] Execute actual migration
- [ ] Update view imports
- [ ] Run tests
- [ ] Commit changes

## 🚀 Quick Start

### 1. Preview Migration (Dry Run)

```bash
python scripts/migrate_organization.py
```

Xem những files nào sẽ được di chuyển mà không thực sự move.

### 2. Migrate Specific Category

```bash
# Chỉ migrate templates
python scripts/migrate_organization.py --templates

# Chỉ migrate docs
python scripts/migrate_organization.py --docs

# Chỉ migrate tests
python scripts/migrate_organization.py --tests

# Chỉ migrate management commands
python scripts/migrate_organization.py --commands

# Chỉ cleanup temp files
python scripts/migrate_organization.py --cleanup
```

### 3. Execute Full Migration

```bash
python scripts/migrate_organization.py --execute
```

⚠️ **Warning**: Lệnh này sẽ thực sự di chuyển files!

## 📊 Migration Summary

### Templates: 22 files
- **From**: `backend/templates/pages/` (flat structure)
- **To**: `backend/templates/{app}/{feature}/` (organized by app)

Example:
- `pages/pronunciation_lesson.html` → `curriculum/pronunciation/lesson_detail.html`
- `pages/phoneme_chart.html` → `curriculum/phoneme/chart.html`
- `pages/home.html` → `public/home.html`

### Documentation: 50+ files
- **From**: Root folder (chaos)
- **To**: `docs/{category}/` (organized by topic)

Categories:
- `curriculum/` - Pronunciation, phoneme, teacher features
- `curriculum/audio/` - TTS, audio generation
- `users/` - Auth, profile, settings
- `standards/` - Development standards, workflows
- `architecture/` - System design, sitemaps
- `requirements/` - Feature requirements
- `design/` - UI/UX design docs
- `implementation/` - Implementation docs
- `implementation/roadmap/` - Roadmaps
- `implementation/phases/` - Phase docs
- `testing/` - Test guides, reports
- `changelog/` - Daily completion summaries, bug fixes
- `project/` - Project-level docs
- `examples/` - Code examples

### Tests: 20+ files
- **From**: Root, backend/, backend/tests/ (scattered)
- **To**: `backend/tests/{app}/{type}/` (organized by app and type)

Types:
- `models/` - Model tests
- `api/` - API endpoint tests
- `services/` - Service layer tests
- `views/` - View/template rendering tests
- `integration/` - Integration tests

### Management Commands: 4 files
- **From**: Root folder
- **To**: `backend/apps/{app}/management/commands/`

Example:
- `generate_phoneme_tts.py` → `apps/curriculum/management/commands/generate_phoneme_audio.py`

### Temp Files: ~10 files
- Will be deleted: `temp_*.html`, `test_*.html` in root

## 🔍 After Migration

### 1. Update View Imports

Cần update view code để dùng đúng template paths mới:

```python
# OLD (Before)
return render(request, 'pages/pronunciation_lesson.html', context)

# NEW (After)
return render(request, 'curriculum/pronunciation/lesson_detail.html', context)
```

### 2. Find All Template Renders

```bash
# Search for old template paths
grep -r "pages/" backend/apps/
```

### 3. Update Template Extends/Includes

Trong templates, nếu có extends/includes:

```django
{# OLD #}
{% extends 'pages/base.html' %}

{# NEW #}
{% extends 'base.html' %}
```

### 4. Run Tests

```bash
# Run all tests
pytest backend/tests/ -v

# Run specific app tests
pytest backend/tests/curriculum/ -v
pytest backend/tests/users/ -v
```

## 📝 Manual Steps Required

### Step 1: Update View Imports

File list cần update (estimated ~30 views):
- `backend/apps/curriculum/views/pronunciation_views.py`
- `backend/apps/curriculum/views/phoneme_views.py`
- `backend/apps/curriculum/views/discrimination_views.py`
- `backend/apps/curriculum/views/production_views.py`
- `backend/apps/study/views.py`
- `backend/apps/users/views.py`

### Step 2: Update URL Namespaces (if needed)

Nếu có hardcoded URL patterns trong documentation hoặc comments, cần update.

### Step 3: Update CI/CD Pipelines (if any)

Nếu có GitHub Actions hoặc CI scripts chạy tests, cần update paths.

## ⏱️ Time Estimates

- **Dry run + review**: 10 minutes
- **Execute migration**: 2 minutes
- **Update view imports**: 30 minutes
- **Run tests + fix**: 20 minutes
- **Git commit**: 5 minutes

**Total**: ~1 hour

## 🆘 Rollback Plan

Nếu có vấn đề sau migration:

```bash
# Revert using git
git checkout HEAD -- .

# Or if already committed
git revert HEAD
```

## 🎯 Success Criteria

Migration thành công khi:

1. ✅ All files moved to correct locations
2. ✅ No broken imports
3. ✅ All tests passing
4. ✅ Templates render correctly
5. ✅ No 404 errors on pages
6. ✅ Documentation updated

## 🤝 Review Process

Trước khi execute:

1. Review migration mappings trong script
2. Run dry-run và check output
3. Backup current state (git commit)
4. Test một vài files manually trước
5. Execute full migration
6. Verify và fix issues
7. Final commit

## 📞 Questions?

Xem chi tiết trong: [docs/PROJECT_ORGANIZATION_ANALYSIS.md](../docs/PROJECT_ORGANIZATION_ANALYSIS.md)
