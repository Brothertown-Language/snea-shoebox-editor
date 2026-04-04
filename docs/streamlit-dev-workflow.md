# Streamlit Development Workflow

## Branch Strategy

| Environment | Branch | Purpose |
|-------------|--------|---------|
| **Production (Streamlit Cloud)** | `main` | Auto-deploys on push to main |
| **Local Development** | `dev` | Integration testing, stacked PRs |
| **Feature Development** | `feature/*` | Individual feature branches |

## Local Dev Streamlit

### Running from `dev` Branch

```bash
# Switch to dev branch
git checkout dev
git pull origin dev

# Start local Streamlit
./scripts/start_streamlit.sh

# Or manually:
uv run --extra local python -m streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
```

### Hot Reload Development

1. Edit code on feature branch
2. Run `git checkout dev && git merge feature/your-feature`
3. Local Streamlit auto-reloads with changes
4. Test stacked features before release

### Stopping Streamlit

```bash
./scripts/kill_streamlit.sh

# Or manually:
pkill -f "streamlit run streamlit_app.py"
```

## Integration Testing Workflow

### Testing Stacked PRs

When multiple PRs are merged to `dev`:

1. Pull latest `dev`:
   ```bash
   git checkout dev
   git pull origin dev
   ```

2. Start local Streamlit:
   ```bash
   ./scripts/start_streamlit.sh
   ```

3. Test integration of all merged features
4. Verify no conflicts between PRs
5. Report issues on respective PRs

### Before Release to Production

1. Verify all features on `dev` work together
2. Run local Streamlit from `dev` branch
3. Test critical user workflows
4. Confirm release PR is ready

## Production Deployment

### Streamlit Cloud (Production)

- **Branch**: `main`
- **Auto-deploy**: Yes (on push to `main`)
- **No changes needed**: Streamlit Cloud configuration stays the same

### Release Workflow

```bash
# Create release PR from dev to main
git checkout dev
git pull origin dev
git checkout -b release/v1.2.3

# Push and create PR targeting main
git push -u origin release/v1.2.3
gh pr create --base main --title "Release v1.2.3" --body "Release notes..."
```

After merge to `main`:
- Streamlit Cloud auto-deploys
- Production is updated

## Troubleshooting

### Issue: Streamlit won't start

**Check logs:**
```bash
cat tmp/streamlit.log
```

**Check for port conflicts:**
```bash
lsof -i :8501
```

### Issue: Changes not reflected

**Ensure you're on dev branch:**
```bash
git branch --show-current  # Should show 'dev'
git pull origin dev
```

**Restart Streamlit:**
```bash
./scripts/kill_streamlit.sh
./scripts/start_streamlit.sh
```

### Issue: Database conflicts

Local dev Streamlit uses the same database as production. If you need isolation:

```bash
# Use test database (if configured)
export DATABASE_URL="sqlite:///./tmp/test.db"
./scripts/start_streamlit.sh
```

## Best Practices

1. **Always test on `dev` before release** - Catch integration issues early
2. **Run local Streamlit from `dev`** - Test stacked PRs together
3. **Stop Streamlit when done** - Free up port 8501
4. **Check logs for errors** - `tmp/streamlit.log` contains output

## Related Documentation

- `scripts/start_streamlit.sh` - Start script
- `scripts/kill_streamlit.sh` - Stop script
- Git workflow: `docs/git-workflow-migration-guide.md`