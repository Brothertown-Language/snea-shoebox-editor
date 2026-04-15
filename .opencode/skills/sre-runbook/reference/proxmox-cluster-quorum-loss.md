---
name: proxmox-cluster-quorum-loss
description: Reference template for Proxmox cluster quorum loss runbook. Demonstrates prose-driven pattern with reasoning at every step. NOT a canonical project runbook.
type: reference
license: MIT
compatibility: opencode
---

# REFERENCE TEMPLATE — NOT A CANONICAL PROJECT RUNBOOK

> This file is a **reference template** demonstrating the prose-driven runbook pattern defined by the `sre-runbook` skill. It shows both prompt patterns (what a user would invoke) and output patterns (what the agent would generate). Adapt this template to your infrastructure — do not use it as-is without validating against your environment.

## Prompt Pattern (Invocation)

```
/skill sre-runbook --task generate
domain: Proxmox VE cluster
scenario_type: incident
severity: P1
```

Expected agent behavior: Generate a full runbook following the five-step protocol (symptoms → diagnosis → mitigation → verification → postmortem), with reasoning at every step.

---

## Symptom Catalog

Why this matters: Quorum loss is the most dangerous Proxmox failure mode because it doesn't just break one node — it freezes the entire cluster's ability to make consensus decisions. Virtual machines may continue running, but no management operations (start, stop, migrate, snapshot) can occur. The cluster effectively becomes read-only at the management layer while VMs run in an isolated state.

The symptoms below are ordered by diagnostic priority — the symptoms that most strongly indicate quorum loss appear first.

```yaml+symbolic
schema_version: "1.0"
symptoms:
  - description: "Cluster commands return 'cluster not ready - quorum?' or 'waiting for quorum'"
    severity: P1
    affected_components:
      - "pve-cluster"
      - "corosync"
    frequency: always
    observed_at: "Any pvecm or qm command during quorum loss"
    diagnostic_priority: 1
    reasoning: "This is the definitive symptom. The 'quorum?' message is Proxmox's explicit way of telling you the cluster consensus layer is broken. No other failure mode produces this specific message."

  - description: "pvecm status shows 'Node does not have quorum' or vote count below majority"
    severity: P1
    affected_components:
      - "corosync"
    frequency: always
    observed_at: "pvecm status command output"
    diagnostic_priority: 1
    reasoning: "Direct confirmation from the cluster manager. The vote count being below the majority threshold (e.g., 1 of 3 votes) is the objective measure of quorum loss. This symptom confirms what the error messages suggest."

  - description: "Web UI shows 'Connection error' or 'cluster filesystem not available'"
    severity: P1
    affected_components:
      - "pveproxy"
      - "pmxcfs"
    frequency: always
    observed_at: "Browser access to Proxmox web interface"
    diagnostic_priority: 2
    reasoning: "The web UI depends on the cluster filesystem (pmxcfs), which requires quorum to operate. When quorum is lost, pmxcfs becomes read-only, so the UI can display cached state but cannot execute changes. This is why the UI shows 'not available' rather than a complete failure."

  - description: "VMs continue running but cannot be managed (start/stop/migrate)"
    severity: P2
    affected_components:
      - "qemu-server"
      - "pve-ha-manager"
    frequency: always
    observed_at: "Attempted management operations"
    diagnostic_priority: 2
    reasoning: "This is the paradox of quorum loss that confuses new operators: VMs are still running because QEMU/KVM is a local process on each node, but you can't control them because management requires cluster consensus. The VMs are running in a 'frozen management' state, not a failed state."

  - description: "Corosync logs show 'quorum lost' or membership changes"
    severity: P1
    affected_components:
      - "corosync"
    frequency: always
    observed_at: "journalctl -u corosync or /var/log/corosync.log"
    diagnostic_priority: 3
    reasoning: "Corosync is the consensus layer. Its logs are the ground truth for quorum events. Checking these logs tells you WHEN quorum was lost and which nodes participated in the membership change, which is critical for root cause analysis."
```

### Quick-Reference: Symptom → Action Matrix

| Symptom | First Action | Why |
|---------|-------------|-----|
| "quorum?" error messages | `pvecm status` | Confirm quorum state before taking any other action |
| `pvecm` shows no quorum | Check which nodes are online | You need to know how many votes are available before deciding recovery path |
| Web UI "not available" | SSH to any remaining node | UI depends on quorum; SSH works locally without cluster consensus |
| VMs can't be managed | Verify VMs are still running locally | Don't assume VMs are down — check `qm list` on each node first |

### Detailed Procedural: Understanding Why Each Symptom Occurs

Proxmox uses a quorum-based consensus system built on Corosync. Every cluster state change — starting a VM, migrating storage, updating the cluster filesystem — requires a majority vote from configured nodes. When fewer than half the nodes are online, no majority exists, and the cluster enters a "frozen" state where:

1. **The cluster filesystem (pmxcfs) becomes read-only.** This is why the web UI shows errors — it can read cached configuration but cannot write any changes.

2. **HA manager stops fencing decisions.** Without quorum, the HA manager cannot safely determine which node should own a VM, so it suspends all fencing. This is actually protective — fencing without quorum could cause split-brain shutdowns.

3. **VMs continue running locally.** QEMU processes are independent of the cluster layer. A VM started on node A keeps running on node A regardless of cluster state. This is by design — a quorum failure should not automatically kill running workloads.

Understanding this architecture is critical because it determines your recovery strategy: you must restore quorum first, then address any VM state inconsistencies that occurred during the quorum loss period.

---

## Diagnosis Map

Why this matters: Quorum loss has three distinct root causes, each requiring a different recovery path. Misdiagnosis leads to wrong recovery actions — for example, trying to force quorum on a network-partitioned cluster makes the partition permanent.

```yaml+symbolic
schema_version: "1.0"
diagnosis:
  - root_cause: "Node failure — one or more cluster nodes are offline"
    confidence: high
    severity: P1
    evidence_chain:
      - symptom: "pvecm status shows fewer votes than expected"
        evidence: "pvecm status shows 1 of 3 votes; offline nodes show 'Node X: offline'"
        reasoning: "Node failure is the most common cause. When a node's corosync process stops, its vote is removed from the quorum calculation. If this drops the total below majority, quorum is lost. You confirm this by checking which nodes the cluster marks as offline."
      - symptom: "Cluster commands return quorum errors"
        evidence: "Commands fail immediately with 'cluster not ready'"
        reasoning: "If only one node's vote remains, the cluster cannot reach majority. Commands fail because the local node cannot commit any state change without cluster agreement."
    affected_components:
      - "pve-cluster"
      - "corosync"
    escalation_threshold: "30 minutes without quorum recovery"
    decision_tree:
      - condition: "Majority of nodes confirmed offline (e.g., 2 of 3)"
        action: "Proceed to forced quorum recovery (Task 2.1 in mitigation)"
        reasoning: "When a genuine majority of nodes is offline, forced quorum on the surviving node is the correct recovery path because the alternative (waiting for nodes to return) may leave the cluster unusable for an extended period."
      - condition: "Nodes are online but cannot reach each other"
        action: "Diagnose network issue first — do NOT force quorum"
        reasoning: "Forcing quorum during a network partition creates two independent clusters. This is called split-brain and is far worse than quorum loss because both sides believe they own the cluster state."

  - root_cause: "Network partition — nodes are online but cannot communicate"
    confidence: medium
    severity: P1
    evidence_chain:
      - symptom: "pvecm status shows nodes as 'online' but ping between nodes fails"
        evidence: "Node A shows Node B as online, but `ping <node-b-ip>` times out"
        reasoning: "A network partition means corosync heartbeats have stopped but the nodes themselves haven't crashed. The nodes are running but isolated. You differentiate this from node failure by checking whether the nodes respond to ICMP or SSH — if they do, it's a partition, not a failure."
      - symptom: "Corosync logs show repeated membership changes"
        evidence: "journalctl shows ' Membership change' entries with node join/leave cycles"
        reasoning: "Unstable membership (nodes repeatedly joining and leaving) is a hallmark of network partitions. The corosync ring becomes intermittent, causing the quorum calculation to fluctuate. This is different from a clean node failure which produces a single membership change."
    affected_components:
      - "corosync"
      - "network infrastructure"
    escalation_threshold: "15 minutes — network partitions degrade quickly"
    decision_tree:
      - condition: "Ping between all nodes fails"
        action: "Diagnose network layer (switch, VLAN, firewall)"
        reasoning: "If no inter-node connectivity exists, the network infrastructure is the blocker. Fixing the network resolves the quorum issue organically without risk of split-brain."
      - condition: "Partial connectivity — some nodes can reach each other"
        action: "Isolate the partition boundary and fix connectivity before any cluster actions"
        reasoning: "Partial connectivity is the most dangerous state because it can cause inconsistent cluster state. Never force quorum in a partially connected environment."

  - root_cause: "Corosync configuration error — nodes exist but cannot form consensus"
    confidence: low
    severity: P2
    evidence_chain:
      - symptom: "pvecm status shows all nodes but quorum is still missing"
        evidence: "All 3 nodes show as online with 0 expected votes"
        reasoning: "If corosync configuration is corrupted (wrong ring0 address, wrong expected votes), the cluster may have all nodes online but still fail to reach consensus. This is rare but occurs after manual configuration edits or failed cluster joins."
      - symptom: "Corosync logs show 'config error' or 'vote not counted'"
        evidence: "journalctl shows corosync configuration parse errors"
        reasoning: "Configuration errors prevent corosync from correctly calculating quorum. If corosync cannot parse the node list correctly, votes won't be counted even from online nodes."
    affected_components:
      - "corosync"
      - "pve-cluster"
    escalation_threshold: "Escalate immediately — this requires Corosync expertise"
    decision_tree:
      - condition: "Configuration file has obvious errors (wrong IPs, missing nodelist entries)"
        action: "Fix configuration and restart corosync"
        reasoning: "A clear config error is safe to fix because the cluster is already in a broken state. The fix cannot make things worse."
      - condition: "Configuration appears correct but consensus still fails"
        action: "Do NOT modify config — escalate to Corosync/Proxmox expertise"
        reasoning: "If the configuration looks correct but consensus fails, the issue is likely in the corosync protocol layer or cluster state database. These require deep expertise to diagnose safely."
```

### Quick-Reference: Diagnosis Decision Tree

```
Quorum lost?
├── pvecm status: Are nodes offline?
│   ├── YES → Node failure path
│   │   └── Majority offline? → Force quorum on survivor
│   └── NO → Network partition path
│       └── Can nodes ping each other?
│           ├── NO → Fix network first
│           └── PARTIAL → Isolate boundary, fix before cluster actions
│           └── YES → Corosync config path
│               └── Config looks wrong? → Fix and restart
│               └── Config looks correct? → ESCALATE
```

### Detailed Procedural: Diagnosis Reasoning

The key diagnostic principle for quorum loss is: **rule out network partitions before attempting any recovery action.** Forced quorum recovery on a network-partitioned cluster creates a permanent split-brain condition. Always verify network connectivity between all cluster nodes before deciding on a recovery path.

**Diagnostic sequence (why this order):**

1. **Run `pvecm status` first** — this tells you the objective quorum state (votes, online nodes, expected votes). All subsequent decisions depend on this information.

2. **Then check node reachability** — SSH or ping to each node shown as "offline" by pvecm. If you can reach an "offline" node, it's a network issue, not a node failure.

3. **Then check corosync logs** — these tell you the timeline and mechanism of quorum loss, which confirms the root cause category.

4. **Only then decide on recovery path** — with confirmed diagnosis, you can safely choose between forced quorum, network repair, or configuration fix.

---

## Mitigation Plan

Why this matters: Quorum recovery is destructive if done wrong. Force-quorum on the wrong node can corrupt cluster state. Recovery without verification can leave phantom quorum artifacts. Every mitigation step below includes rollback because the cost of a wrong step exceeds the cost of an extra verification.

```yaml+symbolic
schema_version: "1.0"
mitigation:
  - step: "Verify network connectivity between ALL cluster nodes"
    targets_root_cause: "Network partition (diagnosis 2)"
    risk_level: low
    rollback: "No rollback needed — this is a read-only diagnostic step"
    reasoning: "Before ANY recovery action, you must confirm network connectivity. This is the gate that prevents split-brain. If connectivity is broken, fix the network first — cluster recovery cannot succeed on a partitioned network."
    verification: "Ping all cluster node IPs from each node. Confirm zero packet loss."

  - step: "If network is intact and nodes are offline: force quorum on the surviving node"
    targets_root_cause: "Node failure (diagnosis 1)"
    risk_level: high
    rollback: "pvecm expected 3 (restore expected votes to original count) — ALWAYS restore original votes after recovery"
    reasoning: "Force quorum (`pvecm expected 1`) tells corosync that the current node's vote is sufficient for consensus. This is necessary when a genuine majority of nodes is offline, but it creates a single-node consensus which is fragile. You MUST restore expected votes to the original count once offline nodes return."
    verification: "pvecm status shows 'Has quorum: Yes' after force command"

  - step: "If network partition detected: fix network connectivity, do NOT force quorum"
    targets_root_cause: "Network partition (diagnosis 2)"
    risk_level: medium
    rollback: "Revert network changes if they don't restore connectivity within 5 minutes"
    reasoning: "Forcing quorum during a network partition creates two independent clusters that both believe they own the cluster state. This causes split-brain, which is far worse than the original quorum loss. The correct approach is to fix the network, which allows natural quorum to return."
    verification: "All nodes can ping all other nodes. pvecm status shows quorum restored."

  - step: "For each offline node: verify it's truly offline before excluding from recovery"
    targets_root_cause: "Node failure (diagnosis 1)"
    risk_level: low
    rollback: "No rollback needed — this is a diagnostic step"
    reasoning: "A node may appear offline in pvecm status due to corosync timeout but still be running. Check via ICMP ping, SSH, and iDRAC/IPMI before assuming it's failed. A node that's running but out-of-sync with the cluster requires a different recovery path (rejoin) than a truly offline node (rebuild)."
    verification: "Physical console, iDRAC/IPMI, or remote management confirms node state."

  - step: "Restore expected votes after nodes return"
    targets_root_cause: "Node failure (diagnosis 1) — cleanup after force quorum"
    risk_level: medium
    rollback: "If corosync becomes unstable after restoring votes, reduce expected votes back to the count of currently-online nodes and investigate"
    reasoning: "After force quorum recovery, expected votes is set to 1. Leaving it at 1 means any subsequent node failure causes immediate quorum loss again. Restoring to the original count (e.g., 3 for a 3-node cluster) re-enables proper majority consensus and fault tolerance."
    verification: "pvecm status shows 'Expected votes: 3' (or original count) and 'Has quorum: Yes'"

  - step: "Verify cluster sync after recovery"
    targets_root_cause: "All root causes — post-recovery validation"
    risk_level: low
    rollback: "Sync issues after recovery indicate state corruption — escalate, do NOT force sync"
    reasoning: "After quorum recovery, the cluster filesystem may have divergent state between nodes. Verifying sync confirms that the recovery didn't introduce state inconsistency, which could cause future failures."
    verification: "pvecm update runs without errors on all nodes. /etc/pve/ content is identical across all nodes."
```

### Quick-Reference: Mitigation Steps (Condensed)

| Step | Command | Risk | Rollback |
|------|---------|------|----------|
| Verify network | `ping <node-ip>` from each node | Low | N/A (diagnostic) |
| Force quorum (node failure only) | `pvecm expected 1` | **High** | `pvecm expected 3` |
| Fix network (partition only) | Network infrastructure repair | Medium | Revert changes after 5 min |
| Verify nodes offline | ICMP/SSH/iDRAC check | Low | N/A (diagnostic) |
| Restore expected votes | `pvecm expected 3` | Medium | `pvecm expected <online-count>` |
| Verify cluster sync | `pvecm update` on all nodes | Low | Escalate on failure |

### Detailed Procedural: Mitigation Reasoning

**Why force quorum is HIGH risk:** The `pvecm expected 1` command tells the cluster "trust this one node's decisions." If you run this on a node that's actually network-partitioned (not offline), you've just created a second cluster. Both clusters will try to manage the same VMs, storage, and network resources. This is split-brain — the single most destructive condition in clustered computing.

**Why expected votes restoration matters:** During force quorum, expected votes is 1. This means the cluster tolerates zero additional node failures. Restoring expected votes to 3 means the cluster regains its ability to survive one node failure — which is the whole point of having a 3-node cluster.

**Why cluster sync verification matters:** The cluster filesystem (pmxcfs) was in read-only mode during quorum loss. Any changes made on the quorum-holding node may not have propagated. After recovery, check that `/etc/pve/` content is consistent across all nodes. Divergence means state inconsistency that will cause future failures.

---

## Verification Criteria

Why this matters: Verification must confirm that quorum is restored AND that cluster state is consistent. Checking quorum alone is insufficient — a cluster can have quorum while still having divergent state between nodes.

```yaml+symbolic
schema_version: "1.0"
verification:
  - criterion: "Cluster has quorum"
    expected_result: "pvecm status shows 'Has quorum: Yes' and 'Expected votes: 3' (original count)"
    maps_to_symptom: "Cluster commands return 'cluster not ready - quorum?'"
    pass_condition: "pvecm status output shows quorum with original expected vote count"
    fail_action: "Return to diagnosis — quorum not restored. Check if forced quorum command was applied correctly and if nodes can communicate."

  - criterion: "All cluster nodes are online and synced"
    expected_result: "pvecm status shows all nodes as online. /etc/pve/ content matches across nodes."
    maps_to_symptom: "Web UI shows 'cluster filesystem not available'"
    pass_condition: "All node entries in pvecm show 'online' status AND diff of /etc/pve/ between nodes shows zero differences"
    fail_action: "If nodes are offline: investigate node failure. If /etc/pve/ differs: force cluster sync from the node with the most recent/correct state."

  - criterion: "VM management operations succeed"
    expected_result: "qm start, qm stop, and qm migrate commands complete without quorum errors"
    maps_to_symptom: "VMs cannot be managed (start/stop/migrate)"
    pass_condition: "At least one VM start, one VM stop, and (if applicable) one VM migration complete without errors"
    fail_action: "Check if pmxcfs is still in read-only mode. `pvecm update` may need to be run to force state synchronization."

  - criterion: "Corosync stable with no membership changes for 5 minutes"
    expected_result: "journalctl -u corosync --since '5 minutes ago' shows no membership change entries"
    maps_to_symptom: "Corosync logs show repeated membership changes"
    pass_condition: "Zero membership change entries in last 5 minutes"
    fail_action: "If membership changes continue: the underlying network or node health issue is not resolved. Return to diagnosis."
```

### Quick-Reference: Verification Checklist

```
[ ] pvecm status shows quorum with expected votes = original count
[ ] All nodes show 'online' in pvecm status
[ ] /etc/pve/ content is identical across nodes (diff check)
[ ] VM start/stop/migrate operations succeed without errors
[ ] Corosync stable for 5 minutes (no membership changes in logs)
```

### Detailed Procedural: Verification Reasoning

**Why check /etc/pve/ consistency, not just quorum:** Quorum confirms consensus capability, but the cluster filesystem may have diverged during the outage. A cluster with quorum but divergent state will appear healthy until it tries to make a decision that conflicts with the divergent state — then it will fail in ways that are very hard to diagnose. Checking `/etc/pve/` consistency after recovery prevents this.

**Why verify VM management, not just corosync:** Corosync quorum is necessary but not sufficient for VM management. The cluster filesystem must also be writable (pmxcfs must have transitioned from read-only to read-write). Testing actual VM operations confirms the full management stack is functional.

**Why 5 minutes of stability:** Corosync membership changes indicate the cluster is still converging. If the cluster loses and regains quorum repeatedly (flapping), the underlying issue (network instability or node health problems) isn't resolved. Five minutes of stable membership is a reasonable confidence threshold.

---

## Postmortem Template

```yaml+symbolic
schema_version: "1.0"
postmortem:
  incident_title: "Proxmox Cluster Quorum Loss — <date>"
  severity: P1
  duration: "<time from first symptom detection to quorum restoration>"
  root_cause_category: "configuration | dependency | capacity | code | security"
  contributing_factors:
    - factor: "<e.g., 'No redundant network paths between cluster nodes'>"
      reasoning: "<why this factor contributed to the incident>"
    - factor: "<e.g., 'No automated quorum monitoring or alerting'>"
      reasoning: "<why this lack of monitoring allowed the incident to persist>"
    - factor: "<e.g., 'Expected votes not documented in runbook'>"
      reasoning: "<why this documentation gap slowed recovery>"
  action_items:
    - action: "Implement quorum monitoring alert"
      owner: "<role or team>"
      reasoning: "Quorum loss is P1 but often not detected until operators try to manage VMs. An alert on quorum status enables faster response."
    - action: "Add redundant network paths for corosync ring"
      owner: "<role or team>"
      reasoning: "Single network path failure caused complete cluster isolation. Redundant paths (ring1/ring0) prevent network-induced quorum loss."
    - action: "Document expected votes and force quorum procedure"
      owner: "<role or team>"
      reasoning: "Operators need to know the correct expected votes value (3 for a 3-node cluster) and the exact commands. Without documentation, responders may make incorrect assumptions about cluster configuration."
```

### Postmortem Narrative Template

```markdown
## Incident Timeline

| Time | Event | Reasoning |
|------|-------|-----------|
| <T+0> | First symptom detected | <What triggered detection — alert, user report, automated check?> |
| <T+?> | Diagnosis confirmed | <How was root cause identified? What evidence confirmed it?> |
| <T+?> | Mitigation started | <Which recovery path was chosen and why?> |
| <T+?> | Quorum restored | <How was quorum confirmed? What verification was run?> |
| <T+?> | Cluster fully verified | <What confirmed full recovery beyond quorum restoration?> |

## Root Cause Analysis

<Explain the causal chain from root cause to symptoms. NOT just "node X went down" — explain WHY that caused quorum loss (e.g., "Node X's failure removed 1 of 3 votes, dropping quorum below majority threshold of 2").>

## Contributing Factors

1. **<Factor>**: <Why this contributed to the incident or slowed resolution>
2. **<Factor>**: <Why this contributed>
3. **<Factor>**: <Why this contributed>

## Action Items

| Action | Owner | Priority | Reasoning |
|--------|-------|----------|-----------|
| <Action> | <Owner> | P1/P2/P3 | <Why this prevents recurrence or speeds recovery> |

## Lessons Learned

<What was surprising? What assumptions were wrong? What would we do differently?>
```

---

## Escalation Paths

Why different escalation paths matter: Quorum loss can be caused by different root causes, and each requires different expertise. Routing to the wrong team wastes time during an incident.

```yaml+symbolic
schema_version: "1.0"
escalation:
  - condition: "Quorum not restored within 30 minutes of detection"
    escalate_to: "Senior infrastructure engineer with Proxmox cluster experience"
    reasoning: "Quorum loss that persists for 30+ minutes likely indicates a complex failure (multiple nodes, network partition, or corosync corruption) that requires experienced troubleshooting beyond standard runbook procedures."
    escalation_action: "Add 'escalation' label to tracking issue. Provide pvecm status, corosync logs, and network diagnostic output."

  - condition: "Network partition detected as root cause"
    escalate_to: "Network engineering team"
    reasoning: "Network partitions affecting cluster communication are infrastructure-level problems that require network diagnostic tools and authority that SRE/ops teams typically don't have."
    escalation_action: "Provide ping/traceroute results between cluster nodes, switch configuration review, and VLAN status."

  - condition: "Corosync configuration error detected"
    escalate_to: "Proxmox/corosync specialist"
    reasoning: "Corosync configuration errors can corrupt cluster state if fixed incorrectly. This requires expertise in corosync internals, quorum device configuration, and Proxmox cluster mesh protocols."
    escalation_action: "Provide /etc/corosync/corosync.conf from all nodes, corosync log output, and pvecm status."
```

---

## AI Agent Enforcement — State Machine

This section defines the state machine that governs AI agent behavior when executing this runbook. Each state transition requires confirmation of the condition before proceeding.

```yaml+symbolic
schema_version: "1.0"
state_machine:
  id: proxmox-quorum-loss-runbook
  initial_state: symptom_detection
  states:
    - name: symptom_detection
      description: "Catalog observed symptoms and confirm quorum loss"
      required_evidence:
        - "pvecm status output showing no quorum"
        - "At least one 'quorum?' error message"
      transitions:
        - to: diagnosis
          condition: "All symptoms catalogued with severity and affected components"
          action: "Proceed to diagnosis with evidence"

    - name: diagnosis
      description: "Trace symptoms to root cause through evidence chains"
      required_evidence:
        - "pvecm status showing vote counts"
        - "Network connectivity test results between all nodes"
        - "Corosync log entries showing quorum loss event"
      transitions:
        - to: mitigation_node_failure
          condition: "Confirmed: nodes offline, network intact"
          action: "Proceed to node failure mitigation path"
        - to: mitigation_network_partition
          condition: "Confirmed: network partition between nodes"
          action: "Proceed to network partition mitigation path"
        - to: mitigation_config_error
          condition: "Confirmed: corosync configuration error"
          action: "Proceed to config error mitigation path"
        - to: escalation
          condition: "Diagnosis cannot be confirmed (low confidence)"
          action: "HALT and escalate"

    - name: mitigation_node_failure
      description: "Force quorum on surviving node after confirming nodes offline"
      required_evidence:
        - "Verified network connectivity is intact"
        - "Confirmed offline nodes are truly offline (iDRAC/IPMI/physical)"
      transitions:
        - to: verification
          condition: "Quorum forced on surviving node. pvecm expected votes restored."
          action: "Proceed to verification"

    - name: mitigation_network_partition
      description: "Fix network connectivity without forcing quorum"
      required_evidence:
        - "Ping/traceroute results showing partition boundary"
        - "Switch/VLAN configuration review"
      transitions:
        - to: verification
          condition: "Network connectivity restored. pvecm shows quorum."
          action: "Proceed to verification"

    - name: mitigation_config_error
      description: "Fix corosync configuration"
      required_evidence:
        - "Configuration diff showing error"
        - "Corosync log showing configuration parse failure"
      transitions:
        - to: verification
          condition: "Configuration fixed. Corosync restarted. pvecm shows quorum."
          action: "Proceed to verification"

    - name: verification
      description: "Confirm quorum, cluster sync, VM management, and stability"
      required_evidence:
        - "pvecm status shows quorum with original expected votes"
        - "/etc/pve/ content matches across all nodes"
        - "VM start/stop/migrate operations succeed"
        - "Corosync stable for 5 minutes (no membership changes)"
      transitions:
        - to: postmortem
          condition: "All verification criteria pass"
          action: "Proceed to postmortem"
        - to: diagnosis
          condition: "Any verification criterion fails"
          action: "Return to diagnosis — do NOT proceed to postmortem"

    - name: postmortem
      description: "Document incident timeline, root cause, and action items"
      required_evidence:
        - "Complete timeline with timestamps"
        - "Root cause analysis with causal chain"
        - "Action items with owners and reasoning"
      transitions:
        - to: resolved
          condition: "Postmortem complete and tracking issue updated"
          action: "Close incident tracking issue"

    - name: escalation
      description: "HALT — escalation required"
      required_evidence:
        - "Reason for escalation documented"
        - "Diagnostic output collected for escalation target"
      transitions: []

    - name: resolved
      description: "Incident resolved and documented"
      transitions: []
```

### AI Agent Rules

```yaml+symbolic
rules:
  - id: quorum-loss-001
    title: "Network partition check before force quorum"
    conditions:
      all:
        - "diagnosis == 'node_failure'"
        - "network_connectivity_verified == false"
    actions:
      - HALT
      - REQUIRE: "Verify network connectivity before proceeding with force quorum"
    source: "proxmox-cluster-quorum-loss.md §Mitigation"

  - id: quorum-loss-002
    title: "Expected votes must be restored after force quorum"
    conditions:
      all:
        - "force_quorum_applied == true"
        - "expected_votes_restored == false"
    actions:
      - REQUIRE: "Restore expected votes to original count before proceeding to verification"
    source: "proxmox-cluster-quorum-loss.md §Mitigation"

  - id: quorum-loss-003
    title: "Cluster sync verification required"
    conditions:
      all:
        - "quorum_restored == true"
        - "cluster_sync_verified == false"
    actions:
      - HALT
      - REQUIRE: "Verify /etc/pve/ consistency before proceeding"
    source: "proxmox-cluster-quorum-loss.md §Verification"

  - id: quorum-loss-004
    title: "Do NOT force quorum during network partition"
    conditions:
      all:
        - "network_partition_detected == true"
        - "proposed_action == 'force_quorum'"
    actions:
      - BLOCK
      - REASON: "Force quorum during network partition creates split-brain"
    source: "proxmox-cluster-quorum-loss.md §Mitigation"
```