# GitBucket Repository Operations

## Overview

Repository management operations using GitBucket Python API client.

**Primary Tool: Python client from `.opencode/skills/gitbucket-api/tools/gitbucket_api.py`**

**CRITICAL: The `gitbucket_*` MCP tools have been REMOVED. The Python client is the ONLY option. Use `from skills.gitbucket_api.tools import GitBucketAPI` for all operations.**

## Basic Operations

### Get Repository

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()
repo = api.get_repository(owner="org", repo="project")
# Returns: Repository object (dict)
print(f"Repo: {repo['full_name']}")
print(f"Stars: {repo['stargazers_count']}")
print(f"Forks: {repo['forks_count']}")
```

### List User's Repositories

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()
repos = api.list_own_repositories()
# Returns: array of Repository objects (list[dict])
for repo in repos:
    print(f"{repo['full_name']}: {repo.get('description', 'No description')}")
```

### List Branches

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()
branches = api.list_branches(owner="org", repo="project")
# Returns: array of Branch objects (list[dict])
for branch in branches:
    print(f"{branch['name']}: {branch['commit']['sha'][:8]}")
```

### List Pull Requests

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()
prs = api.list_pull_requests(owner="org", repo="project", state="open")
# Returns: array of PullRequest objects (list[dict])
for pr in prs:
    print(f"PR #{pr['number']}: {pr['title']} ({pr['state']})")
```

### Get Pull Request

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()
pr = api.get_pull_request(owner="org", repo="project", pull_number=42)
# Returns: PullRequest object (dict)
print(f"PR #{pr['number']}: {pr['title']}")
print(f"Head: {pr['head']['ref']}")
print(f"Base: {pr['base']['ref']}")
print(f"State: {pr['state']}")
print(f"Mergeable: {pr.get('mergeable', 'unknown')}")
```

## Chained Operations

### Workflow 1: Check Branch Status Before Creating PR

**Scenario:** Verify branch exists, check for open PRs, create PR if none exists.

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

branch_name = "feature/oauth2"
base_branch = "dev"

# Step 1: Check if branch exists
branches = api.list_branches(owner="org", repo="project")
branch_exists = any(b['name'] == branch_name for b in branches)

if not branch_exists:
    print(f"Branch '{branch_name}' does not exist")
    exit(1)

print(f"✓ Branch '{branch_name}' exists")

# Step 2: Check for existing PRs for this branch
prs = api.list_pull_requests(owner="org", repo="project", state="open")
existing_pr = None
for pr in prs:
    if pr['head']['ref'] == branch_name:
        existing_pr = pr
        break

if existing_pr:
    print(f"✓ PR already exists: #{existing_pr['number']}")
    print(f"  Title: {existing_pr['title']}")
    print(f"  State: {existing_pr['state']}")
    exit(0)

# Step 3: Create new PR
pr = api.create_pull_request(
    owner="org",
    repo="project",
    title=f"Feature: {branch_name}",
    head=branch_name,
    base=base_branch,
    body="## Description\n\nImplements OAuth2 authentication.\n\n## Changes\n\n- Added OAuth2 client\n- Implemented token management\n- Added session handling"
)

print(f"✓ Created PR #{pr['number']}")
print(f"  URL: {pr['html_url']}")
```

### Workflow 2: Find Stale Branches

**Scenario:** Find branches that haven't been updated recently.

```python
from skills.gitbucket_api.tools import GitBucketAPI
from datetime import datetime, timedelta

api = GitBucketAPI()

# Step 1: List all branches
branches = api.list_branches(owner="org", repo="project")

# Step 2: Check for stale branches (no activity in 30 days)
stale_days = 30
stale_threshold = datetime.now() - timedelta(days=stale_days)
stale_branches = []

for branch in branches:
    # Get branch commit date (if available)
    # GitBucket API may not include commit date in branch list
    # You may need to call get_ref() or parse commit info separately
    
    # For now, filter out protected branches
    if branch['name'] in ['main', 'master', 'dev']:
        continue
    
    # Add to stale list (simplified - real logic needs commit date)
    stale_branches.append(branch['name'])

print(f"Found {len(stale_branches)} candidate stale branches:")
for name in stale_branches:
    print(f"  - {name}")
```

### Workflow 3: Repository Health Check

**Scenario:** Check repository for CI compliance, labels, milestones.

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

def check_repo_health(owner: str, repo: str):
    """Check repository health."""
    issues = []
    
    # Step 1: Check for required labels
    labels = api.list_labels(owner=owner, repo=repo)
    label_names = [l['name'] for l in labels]
    
    required_labels = ['bug', 'enhancement', 'documentation']
    missing_labels = [l for l in required_labels if l not in label_names]
    
    if missing_labels:
        issues.append(f"Missing labels: {', '.join(missing_labels)}")
    else:
        print("✓ All required labels present")
    
    # Step 2: Check for open PRs
    prs = api.list_pull_requests(owner=owner, repo=repo, state="open")
    if len(prs) > 10:
        issues.append(f"Many open PRs ({len(prs)}) - consider reviewing")
    else:
        print(f"✓ Open PRs: {len(prs)}")
    
    # Step 3: Check for milestones
    from skills.gitbucket_api.tools import GitBucketAPI
    milestones = api.list_milestones(owner=owner, repo=repo)
    if not milestones:
        issues.append("No milestones defined")
    else:
        print(f"✓ Milestones: {len(milestones)}")
    
    # Step 4: Check branches
    branches = api.list_branches(owner=owner, repo=repo)
    protected = ['main', 'master', 'dev']
    missing_protected = [b for b in protected if b not in [br['name'] for br in branches]]
    
    if missing_protected:
        issues.append(f"Missing protected branches: {', '.join(missing_protected)}")
    else:
        print(f"✓ Protected branches present")
    
    # Report
    if issues:
        print("\n⚠️ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("\n✓ Repository health check passed")
        return True

# Run health check
check_repo_health(owner="<GIT_OWNER>", repo="<GIT_REPO>")
```

### Workflow 4: Sync Fork with Upstream

**Scenario:** Check if fork is behind upstream and needs sync.

```python
from skills.gitbucket_api.tools import GitBucketAPI
import subprocess

api = GitBucketAPI()

# Step 1: Get repository info
repo = api.get_repository(owner="org", repo="fork-repo")
print(f"Repo: {repo['full_name']}")
print(f"Default branch: {repo.get('default_branch', 'master')}")

# Step 2: Check if this is a fork
if not repo.get('fork'):
    print("Not a fork - nothing to sync")
    exit(0)

# Step 3: Get upstream info
parent = repo.get('parent')
if parent:
    print(f"Fork of: {parent['full_name']}")
    print("To sync with upstream, use git commands:")
    print("  git remote add upstream <upstream-url>")
    print("  git fetch upstream")
    print("  git merge upstream/main")
```

### Workflow 5: Create Release from Milestone

**Scenario:** Create release when milestone is completed.

```python
from skills.gitbucket_api.tools import GitBucketAPI

api = GitBucketAPI()

# Step 1: Find milestone
milestones = api.list_milestones(owner="org", repo="project")
milestone_title = "v2.0.0"

milestone = None
for m in milestones:
    if m['title'] == milestone_title:
        milestone = m
        break

if not milestone:
    print(f"Milestone '{milestone_title}' not found")
    exit(1)

print(f"Found milestone: {milestone['title']} (ID: {milestone['number']})")

# Step 2: List issues in milestone (via search)
issues = api.list_issues(owner="org", repo="project", state="all", milestone=str(milestone['number']))
print(f"Issues in milestone: {len(issues)}")

# Step 3: Create release
release = api.create_release(
    owner="org",
    repo="project",
    tag_name=milestone_title,
    name=f"Release {milestone_title}",
    body=f"## Release {milestone_title}\n\n{milestone.get('description', '')}\n\n## Issues Resolved\n\n" + 
         "\n".join([f"- #{i['number']}: {i['title']}" for i in issues if i['state'] == 'closed']),
    draft=False,
    prerelease=False
)

print(f"✓ Created release: {release['html_url']}")
```

## Complete API Reference

| Operation | Method | Returns |
|-----------|--------|---------|
| Get repository | `get_repository()` | `dict` |
| List own repos | `list_own_repositories()` | `list[dict]` |
| List user repos | `list_user_repositories()` | `list[dict]` |
| List branches | `list_branches()` | `list[dict]` |
| List PRs | `list_pull_requests()` | `list[dict]` |
| Get PR | `get_pull_request()` | `dict` |
| Create PR | `create_pull_request()` | `dict` |
| List releases | `list_releases()` | `list[dict]` |
| Create release | `create_release()` | `dict` |
| List milestones | `list_milestones()` | `list[dict]` |
| Create milestone | `create_milestone()` | `dict` |
| List labels | `list_labels()` | `list[dict]` |
| Create label | `create_label()` | `dict` |
| Get ref | `get_ref()` | `dict` |
| Create status | `create_status()` | `dict` |

## Source Code

- `tools/gitbucket_api.py` - All repository methods
- `tools/exceptions.py` - Exception classes