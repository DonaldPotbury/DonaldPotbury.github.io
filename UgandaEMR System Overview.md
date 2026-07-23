# UgandaEMR+ System Overview

**Ray of Hope Medical Missions — Electronic Medical Records for Uganda**

---

## What Is This?

A complete electronic medical records (EMR) system deployed on small, silent mini PCs (GMKtec NucBox M6 Ultra) at two residences in Uganda, plus a test server in the U.S. for development and training. Doctors, nurses, and lab techs use it daily for patient registration, diagnoses, prescriptions, and lab results.

The system is designed to work **with or without internet** — the EMR runs locally at Residence A and syncs backups to an offsite server at Residence B, which relays them to the cloud. A 4th NUC in the U.S. runs the identical EMR stack with demo data, so engineers can test upgrades and train staff before changes go to production.

---

## The Hardware

```mermaid
graph LR
  subgraph RESA["<b>Residence A</b> · 2 NUCs · 1 UniFi Network"]
    nuc1["<b>NUC 1</b><br/>Main EMR Server<br/>Ryzen 5 7640HS · 32GB RAM<br/>256GB SSD"]
    nuc2["<b>NUC 2</b><br/>Backup & Monitoring<br/>Ryzen 5 7640HS · 32GB RAM<br/>512GB SSD"]
    ups1["UPS<br/>Battery Backup"]
    router1["UniFi Router<br/>WiFi · VPN"]
  end

  subgraph RESB["<b>Residence B</b> · 1 NUC · 1 UniFi Network"]
    nuc3["<b>NUC 3</b><br/>Offsite Backup (MinIO)<br/>Ryzen 5 7640HS · 32GB RAM<br/>256GB SSD"]
    ups2["UPS<br/>Battery Backup"]
    router2["UniFi Router<br/>WiFi · VPN"]
  end

  subgraph USATEST["<b>United States</b> · Test Server"]
    nuc4["<b>NUC 4</b><br/>Test & Development<br/>Ryzen 5 7640HS · 32GB RAM<br/>256GB SSD"]
  end

  nuc1 ---|LAN| nuc2
  nuc2 -.->|"syncs backups<br/>when online"| nuc3
  ups1 -.->|power| nuc1
  ups1 -.->|power| router1
  ups2 -.->|power| nuc3
  ups2 -.->|power| router2

  classDef nuc fill:#d5e8d4,stroke:#82b366,color:#333
  classDef infra fill:#e1d5e7,stroke:#9673a6,color:#333
  classDef test fill:#dae8fc,stroke:#6c8ebf,color:#333
  class nuc1,nuc2,nuc3 nuc
  class nuc4 test
  class ups1,ups2,router1,router2 infra
```

Each mini PC (GMKtec M6 Ultra, AMD Ryzen 5 7640HS) is about the size of a paperback book. Low power (~35W), plugs into any wall outlet. NUC 4 lives at an engineer's home in the U.S. — identical hardware running the same EMR with demo data for testing and training.

---

## Who Uses It and How

```mermaid
graph LR
  subgraph UGANDA["<b>At the Residences (Uganda)</b>"]
    nurse["Nurses & Doctors<br/>iPads · Laptops"]
    lab["Lab Technicians<br/>Desktop PCs"]
    staff["Staff<br/>Any Device"]
  end

  subgraph USA["<b>From the U.S.</b>"]
    board["Board Members<br/>Home Computer"]
    engineer["IT Engineers<br/>Home Computer"]
  end

  emr(("<b>EMR System</b><br/>Patient Records<br/>emr.rohmm.org"))
  monitor(("<b>Dashboards</b><br/>System Health<br/>grafana.rohmm.org"))
  manage(("<b>Management</b><br/>Server Control<br/>portainer.rohmm.org"))
  media(("<b>Media & Files</b><br/>Movies · Documents<br/>jellyfin.rohmm.org"))

  nurse -->|"Patient records<br/>Fingerprints · Scans"| emr
  lab -->|"Lab results"| emr
  staff -->|"Movies · Music<br/>Shared files"| media
  board -->|"Is it running?"| monitor
  board -->|"View patient stats"| emr
  engineer -->|"Full system control"| manage
  engineer -->|"Logs · Metrics"| monitor

  classDef user fill:#f5f5f5,stroke:#666,color:#333
  classDef service fill:#d5e8d4,stroke:#82b366,color:#333
  classDef admin fill:#e1d5e7,stroke:#9673a6,color:#333
  classDef fun fill:#E6D0DE,stroke:#996185,color:#333

  class nurse,lab,staff,board,engineer user
  class emr service
  class monitor,manage admin
  class media fun
```

| Who | Where | What They See | URL |
|-----|-------|---------------|-----|
| **Nurses & Doctors** | Residence WiFi | Patient records, prescriptions, diagnoses | `emr.rohmm.org` |
| **Lab Techs** | Residence WiFi | Lab orders and results | `emr.rohmm.org` |
| **Staff** | Residence WiFi | Movies, music, shared files | `jellyfin.rohmm.org` |
| **Board Members** | Home (U.S.) | System health dashboard, EMR access | `grafana.rohmm.org` |
| **IT Engineers** | Home (U.S.) | Full server management, logs, metrics | `portainer.rohmm.org` |

> Everyone uses the **same URLs** whether they're on-site or remote. No VPN needed for browser access.

---

## How Remote Access Works

```mermaid
graph LR
  subgraph UGANDA["<b>Residences in Uganda</b>"]
    nuc["NUC Cluster<br/>(3 NUCs)"]
    tunnel["Cloudflare Tunnel<br/>(outbound only)"]
  end

  subgraph CLOUDFLARE["<b>Cloudflare (Free)</b>"]
    cf["Encrypted Relay<br/>DDoS Protection"]
  end

  subgraph REMOTE["<b>United States</b>"]
    browser["Board Member<br/>opens emr.rohmm.org"]
    vpn["Engineer<br/>UniFi VPN → SSH"]
  end

  nuc --> tunnel -->|"encrypted"| cf
  browser -->|"HTTPS"| cf
  vpn -->|"VPN to residence LAN"| nuc

  classDef safe fill:#d5e8d4,stroke:#82b366,color:#333
  classDef cf fill:#F6821F,stroke:#F6821F,color:#fff
  classDef user fill:#f5f5f5,stroke:#666,color:#333
  class nuc,tunnel safe
  class cf cf
  class browser,vpn user
```

- The NUCs **never expose ports** to the internet — they only make outbound connections
- Board members just open a URL in their browser — no software to install
- Engineers use the UniFi router's built-in VPN for full server access

---

## How Data Is Protected

```mermaid
graph LR
  subgraph TIER1["<b>On the NUC</b><br/>Always Available"]
    snap["Daily Snapshots<br/>Instant rollback"]
    backup["Daily Database Backup<br/>2 AM automatic"]
    replica["Real-time Copy<br/>NUC 1 → NUC 2"]
  end

  subgraph TIER2["<b>NUC 2</b><br/>Same Residence"]
    central["Central Backups<br/>90-day history"]
  end

  subgraph TIER2B["<b>NUC 3 · Residence B</b><br/>Offsite"]
    offsite["MinIO Offsite Copy<br/>Receives from NUC 2"]
  end

  subgraph TIER3["<b>Cloud</b><br/>When Internet Available"]
    cloud["Cloud Storage<br/>1-year history"]
  end

  backup --> central
  replica --> central
  central -->|"syncs when online"| offsite -->|"uploads when online"| cloud

  classDef t1 fill:#d5e8d4,stroke:#82b366,color:#333
  classDef t2 fill:#fff2cc,stroke:#d6b656,color:#333
  classDef t3 fill:#D4E1F5,stroke:#3A7CA5,color:#333
  class snap,backup,replica t1
  class central t2
  class cloud t3
```

| Protection | What It Covers | Recovery Time |
|------------|---------------|---------------|
| **Daily snapshots** | Everything on the server | Instant (click to revert) |
| **Daily database backup** | All patient records | ~5 minutes |
| **Real-time replication** | Database + scans to NUC 2 | Automatic failover |
| **Cloud backup** | Everything, uploaded when internet is available | ~30 minutes |

**If NUC 1 dies** → patient data exists on NUC 2 (same residence).
**If both NUCs at Residence A are lost** (fire/theft) → restore from NUC 3 at Residence B (offsite MinIO), or from cloud backup. NUC 3 can also be promoted to a temporary EMR using `deploy-standalone.sh` for disaster recovery.

---

## What Happens During a Power Outage

```mermaid
graph TD
  power["Power Goes Out"]
  ups["UPS Battery Kicks In<br/>(~15-30 min runtime)"]
  alert["WhatsApp Alert Sent<br/>to Team"]
  shutdown["NUC Shuts Down Gracefully<br/>(no data corruption)"]
  restore["Power Returns"]
  boot["Everything Starts Automatically<br/>(no manual intervention)"]

  power --> ups --> alert
  ups -->|"battery low"| shutdown
  shutdown --> restore --> boot

  classDef bad fill:#f8cecc,stroke:#b85450,color:#333
  classDef warn fill:#fff2cc,stroke:#d6b656,color:#333
  classDef good fill:#d5e8d4,stroke:#82b366,color:#333
  class power bad
  class ups,alert,shutdown warn
  class restore,boot good
```

The UPS gives the NUC time to shut down safely. When power returns, everything comes back automatically — no one in Uganda or the U.S. needs to do anything.

---

## Alerts (WhatsApp + Email)

The system monitors itself and sends alerts when something needs attention:

| Alert | What It Means |
|-------|---------------|
| **Backup failed** | Nightly backup didn't complete — check the server |
| **Server down** | A service crashed and couldn't restart |
| **Disk filling up** | Storage is getting full — add a drive or clean up |
| **Power outage** | UPS is running on battery |
| **Tunnel disconnected** | Remote access (from U.S.) is down |

Alerts go to **WhatsApp** (instant) and **email** (formal record).

---

## Storage Growth & Scaling

| Data Type | Growth Per Year | Notes |
|-----------|----------------|-------|
| Patient records (database) | ~250 MB | Text data — very small |
| Scans, PDFs, fingerprints | ~12 GB | Ultrasound, X-ray, documents |
| **Total** | **~12 GB/year** | |

At this rate, the 256GB SSD lasts **10+ years** before needing expansion. When more space is needed, each mini PC has **2 M.2 NVMe slots** — just plug in a second SSD ($40-80).

---

## Cost Summary

| Item | Cost | Frequency |
|------|------|-----------|
| NUC hardware (x4) | ~$400-500 each | One-time |
| 32GB RAM per NUC | ~$80 each | One-time |
| 256-512GB SSD per NUC | ~$30-60 each | One-time |
| UPS (x2) | ~$50-100 each | One-time |
| UniFi router (x2) | ~$100-200 each | One-time |
| Cloudflare (DNS + Tunnel) | **Free** | Ongoing |
| Cloud backup (Backblaze B2) | ~$6/TB/month | Ongoing |
| Domain (rohmm.org) | Already owned | Ongoing |
| **Software licenses** | **$0 (all open-source)** | - |

**Estimated ongoing cost: < $1/month** (cloud backup only, until data grows significantly).

---

## Network Diagram (Full Picture)

```mermaid
graph TB
  subgraph INTERNET["<b>Internet</b>"]
    cf["<b>Cloudflare</b><br/>Free Plan<br/>DNS + Tunnel + DDoS Protection"]
    cloud["<b>Cloud Backup</b><br/>Backblaze B2<br/>1-year retention"]
  end

  subgraph RESA["<b>RESIDENCE A</b> · 2 NUCs · UniFi Network"]
    router1["<b>UniFi Router</b><br/>WiFi · DNS · VPN"]
    devices1["iPads · Laptops · Desktops"]

    subgraph NUC1["<b>NUC 1 — k3s Server (Primary)</b>"]
      emr1["<b>EMR</b><br/>Patient Records"]
      backup1["<b>Backups</b><br/>Daily Automated"]
      monitor1["<b>Monitoring</b><br/>Health Checks"]
      media1["<b>Media Server</b><br/>Movies · Files"]
      tunnel1["<b>Cloudflare Tunnel</b>"]
    end

    subgraph NUC2["<b>NUC 2 — k3s Agent (Backup & Monitoring)</b>"]
      replica["<b>Data Replica</b><br/>Real-time copy of NUC 1"]
      central_backup["<b>Central Backups</b><br/>All sites' data"]
      dashboards["<b>Dashboards</b><br/>Grafana · Logs"]
    end

    ups1["UPS (Battery Backup)"]
  end

  subgraph RESB["<b>RESIDENCE B</b> · 1 NUC · UniFi Network"]
    router2["<b>UniFi Router</b><br/>WiFi · DNS · VPN"]

    subgraph NUC3["<b>NUC 3 — Offsite Backup Server</b>"]
      minio3["<b>MinIO</b><br/>Offsite Backup Copy"]
      cloudsync3["<b>Cloud Relay</b><br/>Uploads to Backblaze B2"]
    end

    ups2["UPS (Battery Backup)"]
  end

  subgraph USA["<b>United States</b>"]
    board["<b>Board Members</b><br/>Browser Access"]
    engineers["<b>IT Engineers</b><br/>VPN + Browser"]

    subgraph NUC4["<b>NUC 4 — Test & Development Server</b>"]
      emr4["<b>EMR (Demo Data)</b><br/>Identical stack to NUC 1"]
      test4["<b>Test upgrades</b><br/>before production"]
    end
  end

  %% Backup flow: Residence A → NUC 3 → Cloud
  central_backup ==>|"syncs when online"| minio3
  minio3 --> cloudsync3 ==>|"uploads when online"| cloud

  %% Local access
  devices1 -->|"Residence WiFi"| router1 --> NUC1

  %% Remote access
  tunnel1 -->|"encrypted"| cf
  board -->|"emr.rohmm.org"| cf
  engineers -->|"portainer.rohmm.org"| cf

  %% Backup flow
  NUC1 ==>|"real-time replica"| NUC2
  central_backup ==>|"when online"| cloud

  %% Power
  ups1 -.-> NUC1
  ups1 -.-> NUC2
  ups1 -.-> router1
  ups2 -.-> NUC3
  ups2 -.-> router2

  classDef nuc fill:#d5e8d4,stroke:#82b366,color:#333
  classDef infra fill:#e1d5e7,stroke:#9673a6,color:#333
  classDef cf fill:#F6821F,stroke:#F6821F,color:#fff
  classDef user fill:#f5f5f5,stroke:#666,color:#333
  classDef backup fill:#fff2cc,stroke:#d6b656,color:#333

  class emr1,media1,monitor1 nuc
  class backup1,replica,central_backup,minio3,cloudsync3 backup
  class dashboards nuc
  class tunnel1 cf
  class router1,router2,ups1,ups2 infra
  class cf,cloud cf
  class devices1,board,engineers user
  classDef test fill:#dae8fc,stroke:#6c8ebf,color:#333
  class emr4,test4 test
```

---

## Key URLs

| URL | What It Is | Who Uses It |
|-----|-----------|-------------|
| `emr.rohmm.org` | Patient records (EMR) | Clinical staff, board |
| `grafana.rohmm.org` | System health dashboards | Board, engineers |
| `portainer.rohmm.org` | Server management panel | Engineers, board (read-only) |
| `jellyfin.rohmm.org` | Movie/music streaming | Staff (local only) |
| `rohmm.org` | Organization website | Public (unchanged) |
