---
name: proxmox-node-failure-recovery
description: Reference template for Proxmox full node failure recovery. Demonstrates prose-driven pattern with different escalation paths from the quorum loss template. NOT a canonical project runbook.
type: reference
license: MIT
compatibility: opencode
---

# REFERENCE TEMPLATE — NOT A CANONICAL PROJECT RUNBOOK

> This file is a **reference template** demonstrating the prose-driven runbook pattern. It shows both prompt patterns (what a user would invoke) and output patterns (what the agent would generate). Adapt this template to your infrastructure — do not use it as-is without validating against your environment.

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

Node failure is distinct from quorum loss: a single node is completely unreachable, but the rest of the cluster retains quorum and continues operating. The critical question is whether VMs on the failed node need immediate recovery or can wait for the node to return.

```yaml+symbolic
schema_version: "1.0"
symptoms:
  - description: "Node completely unreachable via SSH, ping, and web UI"
    severity: P1
    affected_components: ["pve-node", "qemu-server", "network"]
    frequency: always
    reasoning: "Total unreachability across all protocols indicates the node is down at the OS or hardware level, not just a service failure."

  - description: "pvecm status shows node as 'offline' while cluster retains quorum"
    severity: P1
    affected_components: ["corosync", "pve-cluster"]
    frequency: always
    reasoning: "Unlike quorum loss, the remaining nodes still have a majority. The cluster continues to function for VMs on surviving nodes. The offline node's VMs are the primary concern."

  - description: "VMs on the failed node show as 'unknown' status in cluster view"
    severity: P2
    affected_components: ["qemu-server", "pve-ha-manager"]
    frequency: always
    reasoning: "The cluster knows the VMs existed but cannot determine their state because the hosting node is unreachable. They may still be running on the dead node if it has power but no network, or they may have been killed by the hardware failure."

  - description: "HA manager attempts fencing of the failed node"
    severity: P1
    affected_components: ["pve-ha-manager"]
    frequency: sometimes
    reasoning: "If HA is configured, the manager will attempt to recover HA-managed VMs by fencing the failed node and restarting VMs on surviving nodes. This is expected behavior but needs monitoring — fencing failures indicate deeper problems."

  - description: "iDRAC/IPMI shows powered off or hardware error state"
    severity: P1
    affected_components: ["hardware", "bmc"]
    frequency: sometimes
    reasoning: "Remote management interfaces (iDRAC, IPMI, iLO) operate independently of the OS. If they also show failure, the problem is hardware-level. If they show the node as powered off, someone or something shut it down."
```

### Quick-Reference: Symptom → Action

| Symptom | First Action | Why |
|---------|-------------|-----|
| Node unreachable | Check iDRAC/IPMI | Hardware vs OS failure determines recovery path |
| Cluster retains quorum | Focus on VM recovery, not cluster | Remaining cluster is healthy — prioritize workload recovery |
| VMs show 'unknown' | Check if VMs are actually running | Don't assume VMs are down — verify via iDRAC console |
| HA fencing triggering | Verify HA manager progress | HA should auto-recover managed VMs; intervene only if fencing stalls |

---

## Diagnosis Map

The three root causes for node failure, eachrequiring a different recovery approach.

```yaml+symbolic
schema_version: "1.0"
diagnosis:
  - root_cause: "Hardware failure — power supply, disk, motherboard, or RAM"
    confidence: high
    severity: P1
    evidence_chain:
      - symptom: "iDRAC/IPMI shows hardware error or powered off state"
        reasoning: "Hardware management controllers report directly from the BMC layer. If they show errors, the OS may not have had time to log anything before the node went down."
      - symptom: "Node does not respond to power-on via remote management"
        reasoning: "If remote power-on fails, the hardware is physically damaged. No amount of software recovery will help."
    decision_tree:
      - condition: "iDRAC shows specific hardware error (PSU, disk, ECC memory)"
        action: "Order replacement part, begin VM evacuation from other nodes"
        reasoning: "Hardware replacement takes time. VMs should not wait — evacuate them to surviving nodes now."
      - condition: "iDRAC shows powered off but no error"
        action: "Attempt remote power-on; if successful, investigate OS-level cause"
        reasoning: "A clean power-off may indicate an OS panic or administrator action rather than hardware failure."

  - root_cause: "OS or kernel panic — software crash"
    confidence: medium
    severity: P1
    evidence_chain:
      - symptom: "iDRAC shows node powered on but SSH fails"
        reasoning: "Hardware is up but OS is not responding. This could be a kernel panic, filesystem corruption, or hung init."
      - symptom: "Console shows kernel panic or stack trace"
        reasoning: "Definitive evidence of OS-level failure. The panic message tells you which subsystem crashed."
    decision_tree:
      - condition: "Kernel panic visible on console"
        action: "Attempt reboot; if panic recurs, investigate driver/hardware incompatibility"
        reasoning: "One-time panics can be transient. Recurring panics indicate a systemic problem that needs root cause analysis before the node returns to production."
      - condition: "Console unresponsive (no login prompt)"
        action: "Force reboot via iDRAC; monitor boot sequence for errors"
        reasoning: "An unresponsive console may indicate a hung init or filesystem corruption. A clean reboot often resolves transient hangs."

  - root_cause: "Storage failure — ZFS pool degraded or disk failure"
    confidence: medium
    severity: P1
    evidence_chain:
      - symptom: "Node is online but VMs are frozen or I/O errors in logs"
        reasoning: "Storage failure doesn't always crash the node — it may leave the OS running while making VMs unusable. ZFS pools enter a degraded state before going offline."
      - symptom: "ZFS pool status shows DEGRADED or FAULTED"
        reasoning: "ZFS provides explicit pool state. DEGRADED means resilience is reduced but data is available. FAULTED means data is at risk."
    decision_tree:
      - condition: "Pool DEGRADED with available spares"
        action: "Replace failed disk, run zpool scrub, continue operations"
        reasoning: "DEGRADED with spares means ZFS is already rebuilding. The node can continue serving data, but performance may be reduced during rebuild."
      - condition: "Pool FAULTED with no redundancy"
        action: "HALT — escalate to storage specialist; data recovery may be needed"
        reasoning: "A FAULTED pool with no redundancy means data loss has occurred or is imminent. Do not attempt normal recovery — this requires specialized data recovery procedures."
```

### Quick-Reference: Diagnosis Decision Tree

```
Node unreachable?
├── iDRAC/IPMI reachable?
│   ├── YES → Check hardware status
│   │   ├── Hardware error → Hardware failure path
│   │   ├── Powered off → Try remote power-on
│   │   └── Powered on, no OS → OS/kernel panic path
│   └── NO → Network failure (check switch port, cable)
└── Node online but VMs frozen?
    └── Check ZFS pool status
        ├── DEGRADED → Replace disk, scrub
        └── FAULTED → ESCALATE — data recovery needed
```

---

## Mitigation Plan

```yaml+symbolic
schema_version: "1.0"
mitigation:
  - step: "Assess node state via iDRAC/IPMI"
    targets_root_cause: "All root causes — initial triage"
    risk_level: low
    rollback: "No rollback needed — diagnostic step"
    reasoning: "Remote management gives you hardware state without requiring OS access. This determines the entire recovery path."
    verification: "iDRAC/IPMI responds with power state and hardware status"

  - step: "Evacuate VMs from failed node (if HA not configured)"
    targets_root_cause: "All root causes — workload recovery"
    risk_level: medium
    rollback: "VMs can be migrated back once node recovers"
    reasoning: "HA-managed VMs auto-recover. Non-HA VMs need manual evacuation. Prioritize production workloads over development VMs."
    verification: "All critical VMs running on surviving nodes"

  - step: "Attempt node reboot via iDRAC (for OS/kernel panic)"
    targets_root_cause: "OS or kernel panic"
    risk_level: low
    rollback: "If reboot doesn't resolve, proceed to hardware investigation"
    reasoning: "A reboot resolves most transient kernel panics. Monitor the boot sequence via iDRAC console to catch recurring panics."
    verification: "Node boots, SSH accessible, pvecm status shows node online"

  - step: "Replace failed hardware component (for hardware failure)"
    targets_root_cause: "Hardware failure"
    risk_level: medium
    rollback: "If replacement doesn't resolve, escalate to vendor support"
    reasoning: "Hardware replacement is straightforward but requires physical access and parts. Run hardware diagnostics on the replacement before returning node to production."
    verification: "Node passes hardware diagnostics, boots cleanly, rejoins cluster"

  - step: "Replace failed disk and resilver ZFS pool (for storage failure)"
    targets_root_cause: "Storage failure"
    risk_level: medium
    rollback: "Remove replacement disk if resilver fails; pool remains in pre-replacement state"
    reasoning: "ZFS resilvering rebuilds data from redundancy. Monitor resilver progress — do not add load during resilver."
    verification: "zpool status shows pool ONLINE with no errors; scrub completes without errors"

  - step: "Verify node rejoins cluster cleanly"
    targets_root_cause: "All root causes — post-recovery validation"
    risk_level: low
    rollback: "If node cannot rejoin, remove from cluster and re-add"
    reasoning: "A node that was offline may have stale cluster state. Verify pvecm status, corosync connectivity, and /etc/pve/ sync before declaring recovery complete."
    verification: "pvecm status shows all nodes online with quorum; /etc/pve/ content matches across nodes"
```

### Quick-Reference: Mitigation Steps

| Step | Action | Risk | Rollback |
|------|--------|------|----------|
| Assess via iDRAC | Check power/hardware state | Low | N/A |
| Evacuate VMs | Migrate to surviving nodes | Medium | Migrate back |
| Reboot node | iDRAC power cycle | Low | Hardware investigation |
| Replace hardware | Physical component swap | Medium | Escalate to vendor |
| Replace disk + resilver | zpool replace + scrub | Medium | Remove replacement disk |
| Verify cluster rejoin | pvecm status, sync check | Low | Remove and re-add node |

---

## Verification Criteria

```yaml+symbolic
schema_version: "1.0"
verification:
  - criterion: "Failed node is online and rejoined to cluster"
    expected_result: "pvecm status shows all nodes online; node responds to SSH"
    pass_condition: "Node appears online in pvecm status AND SSH access works"
    fail_action: "If node won't rejoin: remove from cluster (pvecm delnode) and re-add"

  - criterion: "All evacuated VMs running on surviving or recovered nodes"
    expected_result: "qm list shows expected VMs running on appropriate nodes"
    pass_condition: "All production VMs are in 'running' state"
    fail_action: "Check VM migration logs; re-migrate any failed VMs"

  - criterion: "ZFS pool healthy (if storage failure occurred)"
    expected_result: "zpool status shows ONLINE with no errors"
    pass_condition: "Pool state is ONLINE AND scrub completes without errors"
    fail_action: "If resilver hasn't completed, wait. If errors persist, escalate to storage specialist."

  - criterion: "Cluster filesystem synchronized across all nodes"
    expected_result: "/etc/pve/ content matches on all nodes"
    pass_condition: "Diff of /etc/pve/ between all nodes shows no differences"
    fail_action: "Run pvecm update to force sync; if differences persist, investigate cluster state corruption"
```

---

## Postmortem Template

```yaml+symbolic
schema_version: "1.0"
postmortem:
  incident_title: "Proxmox Node Failure — <node-name> — <date>"
  severity: P1
  duration: "<time from detection to full recovery>"
  root_cause_category: "hardware | software | storage | unknown"
  contributing_factors:
    - factor: "<e.g., 'No VM HA configured for production workloads'>"
      reasoning: "<why this made recovery harder or slower>"
    - factor: "<e.g., 'No spare hardware available for replacement'>"
      reasoning: "<why this extended downtime>"
  action_items:
    - action: "<e.g., 'Configure HA for all production VMs'>"
      owner: "<role>"
      reasoning: "HA provides automatic VM recovery without manual intervention"
    - action: "<e.g., 'Maintain spare hardware for cluster nodes'>"
      owner: "<role>"
      reasoning: "Hardware replacement took hours because parts were not on-site"
```

### Postmortem Narrative Template

```markdown
## Incident Timeline

| Time | Event | Reasoning |
|------|-------|-----------|
| <T+0> | Node failure detected | <How detected — monitoring, user report, HA alert?> |
| <T+?> | Diagnosis confirmed | <Hardware failure, OS panic, or storage failure?> |
| <T+?> | VM evacuation started | <Which VMs were prioritized and why?> |
| <T+?> | Node recovery attempted | <Reboot, hardware replacement, or disk replacement?> |
| <T+?> | Node rejoined cluster | <How was clean rejoin verified?> |

## Root Cause Analysis

<Explain the causal chain from root cause to symptoms. Why did the node fail? What made it worse?>

## Action Items

| Action | Owner | Priority | Reasoning |
|--------|-------|----------|-----------|
| <Action> | <Owner> | P1/P2/P3 | <Why this prevents recurrence> |
```

---

## Escalation Paths

Different from the quorum loss template — node failure escalates to hardware/vendor support and data recovery teams, not network engineering.

```yaml+symbolic
schema_version: "1.0"
escalation:
  - condition: "Hardware diagnostics show component failure (PSU, motherboard, RAM)"
    escalate_to: "Hardware vendor support"
    reasoning: "Hardware component replacement requires vendor RMA or on-site support that SRE teams cannot provide independently."
    escalation_action: "Provide iDRAC hardware log, serial numbers, and failure details to vendor."

  - condition: "ZFS pool FAULTED with data loss risk"
    escalate_to: "Storage and backup recovery team"
    reasoning: "Data loss risk requires specialized recovery tools (ZFS send/recv from backup, or commercial recovery). SRE should not attempt data recovery without backup team involvement."
    escalation_action: "Provide zpool status, zpool history, and backup inventory to recovery team."

  - condition: "HA-managed VMs not recovering after 15 minutes"
    escalate_to: "Service owners of affected VMs"
    reasoning: "HA should auto-recover, but if fencing is stuck or recovery stalls, service owners need to know their workloads are impacted and may need to activate DR plans."
    escalation_action: "Notify service owners with current VM status and estimated recovery time."

  - condition: "Node cannot rejoin cluster after recovery"
    escalate_to: "Proxmox cluster specialist"
    reasoning: "Cluster rejoin failures involve corosync configuration, cluster state database, and quorum interactions that require deep Proxmox expertise."
    escalation_action: "Provide pvecm status, corosync config, and /etc/pve/ state from all nodes."
```

---

## AI Agent Enforcement — State Machine

```yaml+symbolic
schema_version: "1.0"
state_machine:
  id: proxmox-node-failure-runbook
  initial_state: symptom_detection
  states:
    - name: symptom_detection
      description: "Catalog symptoms and confirm node failure (not quorum loss)"
      required_evidence:
        - "pvecm status showing specific node offline"
        - "Cluster retains quorum (2 of 3 nodes online)"
      transitions:
        - to: diagnosis
          condition: "Symptoms catalogued; quorum confirmed intact"
          action: "Proceed to diagnosis"

    - name: diagnosis
      description: "Determine root cause: hardware, OS, or storage"
      required_evidence:
        - "iDRAC/IPMI status showing hardware state"
        - "Node ping/SSH results from surviving nodes"
      transitions:
        - to: mitigation_hardware
          condition: "iDRAC shows hardware error or no power"
          action: "Proceed to hardware failure path"
        - to: mitigation_os_panic
          condition: "iDRAC shows powered on but OS unresponsive"
          action: "Proceed to OS panic path"
        - to: mitigation_storage
          condition: "Node responsive but ZFS pool degraded/faulted"
          action: "Proceed to storage failure path"
        - to: escalation
          condition: "Diagnosis inconclusive"
          action: "HALT and escalate"

    - name: mitigation_hardware
      description: "Replace failed hardware component"
      transitions:
        - to: vm_evacuation
          condition: "VM evacuation in progress"
          action: "Evacuate VMs to surviving nodes while hardware is replaced"
        - to: verification
          condition: "Hardware replaced, node boots cleanly"
          action: "Proceed to verification"

    - name: mitigation_os_panic
      description: "Reboot node and investigate kernel panic"
      transitions:
        - to: verification
          condition: "Node reboots successfully and rejoins cluster"
          action: "Proceed to verification"
        - to: escalation
          condition: "Reboot fails or panic recurs"
          action: "Escalate — may be hardware or deeper OS issue"

    - name: mitigation_storage
      description: "Replace failed disk and resilver ZFS pool"
      transitions:
        - to: verification
          condition: "Disk replaced, resilver complete, pool ONLINE"
          action: "Proceed to verification"

    - name: vm_evacuation
      description: "Migrate VMs off failed node to surviving nodes"
      transitions:
        - to: verification
          condition: "All critical VMs running on surviving nodes"
          action: "Proceed to verification after node recovery"

    - name: verification
      description: "Confirm full cluster recovery"
      required_evidence:
        - "All nodes online in pvecm status"
        - "/etc/pve/ synchronized across nodes"
        - "ZFS pools healthy (if storage issue)"
        - "All production VMs running"
      transitions:
        - to: postmortem
          condition: "All verification criteria pass"
          action: "Proceed to postmortem"
        - to: diagnosis
          condition: "Any verification criterion fails"
          action: "Return to diagnosis"

    - name: postmortem
      description: "Document timeline, root cause, and action items"
      transitions:
        - to: resolved
          condition: "Postmortem complete"
          action: "Close incident tracking issue"

    - name: escalation
      description: "HALT — expertise required"
      transitions: []

    - name: resolved
      description: "Incident resolved and documented"
      transitions: []
```

### AI Agent Rules

```yaml+symbolic
rules:
  - id: node-failure-001
    title: "Confirm quorum before focusing on single node"
    conditions:
      all:
        - "cluster_has_quorum == false"
    actions:
      - HALT
      - REQUIRE: "Resolve quorum loss first — this runbook assumes cluster retains quorum"
    source: "proxmox-node-failure-recovery.md §Symptom Catalog"

  - id: node-failure-002
    title: "Verify iDRAC/IPMI before attempting SSH"
    conditions:
      all:
        - "node_unreachable_via_ssh == true"
        - "idrac_status_checked == false"
    actions:
      - REQUIRE: "Check iDRAC/IPMI first — hardware state determines recovery path"
    source: "proxmox-node-failure-recovery.md §Diagnosis Map"

  - id: node-failure-003
    title: "Do not attempt data recovery on FAULTED ZFS pool without backup team"
    conditions:
      all:
        - "zfs_pool_status == 'FAULTED'"
        - "backup_team_notified == false"
    actions:
      - HALT
      - REQUIRE: "Escalate to storage/backup team before any recovery attempt"
    source: "proxmox-node-failure-recovery.md §Diagnosis Map"

  - id: node-failure-004
    title: "Verify cluster rejoin after node recovery"
    conditions:
      all:
        - "node_recovered == true"
        - "cluster_sync_verified == false"
    actions:
      - REQUIRE: "Verify /etc/pve/ consistency and pvecm status before declaring recovery complete"
    source: "proxmox-node-failure-recovery.md §Verification"
```