"""Curated summaries of compliance standards across 17 frameworks.

Each entry is a self-contained knowledge fragment suitable for semantic
retrieval with metadata-aware hybrid search (BM25 + vector). Content is
derived from official regulatory texts and security frameworks.
"""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class StandardEntry:
    id: str
    standard: str  # GDPR, ISO27001, SOC2, US_RESTATEMENT, etc.
    topic: str
    article: str | None  # e.g., "Art. 5", "A.9", "CC6.1"
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    jurisdiction: str = "Global"        # "US", "India", "EU", "UK", "Global"
    standard_category: str = "general"   # "data_protection", "security", "contract_law",
                                         # "industry", "financial_reporting"
    effective_date: date | None = None   # when this version became effective
    last_amended: date | None = None     # last amendment date
    authority_level: str = "framework"   # "statute", "regulation", "framework",
                                         # "treaty", "common_law", "industry_standard"


STANDARDS_ENTRIES: list[StandardEntry] = [
    # ── GDPR ───────────────────────────────────────────────────
    StandardEntry(
        id="gdpr-001",
        standard="GDPR",
        topic="Data Protection Principles",
        article="Art. 5",
        title="Principles Relating to Processing of Personal Data",
        content=(
            "Personal data must be processed lawfully, fairly, and transparently. "
            "Data must be collected for specified, explicit, and legitimate purposes "
            "and not further processed in a manner incompatible with those purposes. "
            "Processing must be adequate, relevant, and limited to what is necessary "
            "(data minimization). Data must be accurate and kept up to date. Data must "
            "be kept in a form which permits identification of data subjects for no "
            "longer than necessary (storage limitation). Data must be processed in a "
            "manner that ensures appropriate security, including protection against "
            "unauthorized or unlawful processing and against accidental loss, "
            "destruction, or damage (integrity and confidentiality). The controller "
            "is responsible for and must be able to demonstrate compliance with all "
            "these principles (accountability)."
        ),
        tags=["principles", "data minimization", "accountability", "purpose limitation"],
        jurisdiction="EU",
        standard_category="data_protection",
        effective_date=date(2018, 5, 25),
        last_amended=None,
        authority_level="regulation",
    ),
    StandardEntry(
        id="gdpr-002",
        standard="GDPR",
        topic="Lawful Basis for Processing",
        article="Art. 6",
        title="Lawfulness of Processing",
        content=(
            "Processing is lawful only if at least one of these bases applies: "
            "(a) the data subject has given consent for specific purposes; "
            "(b) processing is necessary for performance of a contract to which the "
            "data subject is party; (c) processing is necessary for compliance with "
            "a legal obligation; (d) processing is necessary to protect vital interests; "
            "(e) processing is necessary for performance of a task carried out in the "
            "public interest; (f) processing is necessary for legitimate interests "
            "pursued by the controller or a third party, except where overridden by "
            "the interests or fundamental rights of the data subject. Contracts must "
            "explicitly specify which lawful basis applies to each data processing "
            "activity. Consent must be freely given, specific, informed, unambiguous, "
            "and withdrawable at any time."
        ),
        tags=["lawful basis", "consent", "legitimate interest", "contract"],
        jurisdiction="EU",
        standard_category="data_protection",
        effective_date=date(2018, 5, 25),
        last_amended=None,
        authority_level="regulation",
    ),
    StandardEntry(
        id="gdpr-003",
        standard="GDPR",
        topic="Data Subject Rights",
        article="Art. 12-23",
        title="Rights of the Data Subject",
        content=(
            "Data subjects have the right to: access their personal data (Art. 15), "
            "rectify inaccurate data (Art. 16), erase data / right to be forgotten "
            "(Art. 17), restrict processing (Art. 18), data portability (Art. 20), "
            "and object to processing including profiling (Art. 21). Requests must "
            "be responded to within one month. Contracts must include provisions for "
            "how these rights are supported by the processor. Failure to facilitate "
            "these rights can result in fines up to 4% of annual global turnover."
        ),
        tags=["data subject", "access", "erasure", "portability", "rights"],
        jurisdiction="EU",
        standard_category="data_protection",
        effective_date=date(2018, 5, 25),
        last_amended=None,
        authority_level="regulation",
    ),
    StandardEntry(
        id="gdpr-004",
        standard="GDPR",
        topic="Data Breach Notification",
        article="Art. 33-34",
        title="Notification of Personal Data Breach",
        content=(
            "In the case of a personal data breach, the controller must notify the "
            "supervisory authority without undue delay and, where feasible, not later "
            "than 72 hours after becoming aware of it. If notification is not made "
            "within 72 hours, it must be accompanied by reasons for the delay. The "
            "notification must describe the nature of the breach, categories and "
            "approximate number of data subjects and records concerned, likely "
            "consequences, and measures taken or proposed. When the breach is likely "
            "to result in high risk to data subjects, the controller must also "
            "communicate the breach to the affected individuals without undue delay. "
            "Contracts must define breach notification timelines and responsibilities "
            "between controllers and processors."
        ),
        tags=["breach", "notification", "72 hours", "incident response"],
        jurisdiction="EU",
        standard_category="data_protection",
        effective_date=date(2018, 5, 25),
        last_amended=None,
        authority_level="regulation",
    ),
    StandardEntry(
        id="gdpr-005",
        standard="GDPR",
        topic="Data Protection by Design and Default",
        article="Art. 25",
        title="Data Protection by Design and by Default",
        content=(
            "The controller must implement appropriate technical and organizational "
            "measures both at the time of determination of the means for processing "
            "and at the time of processing itself. Measures must be designed to "
            "implement data-protection principles in an effective manner and to "
            "integrate necessary safeguards into the processing. By default, only "
            "personal data necessary for each specific purpose must be processed. "
            "This applies to the amount of data collected, the extent of processing, "
            "the period of storage, and accessibility. Contracts with processors must "
            "require data protection by design and default."
        ),
        tags=["privacy by design", "data minimization", "safeguards"],
        jurisdiction="EU",
        standard_category="data_protection",
        effective_date=date(2018, 5, 25),
        last_amended=None,
        authority_level="regulation",
    ),
    StandardEntry(
        id="gdpr-006",
        standard="GDPR",
        topic="Data Processing Agreement",
        article="Art. 28",
        title="Processor Obligations",
        content=(
            "Processing by a processor must be governed by a contract or other legal "
            "act that is binding on the processor with regard to the controller. The "
            "contract must set out: the subject-matter and duration of processing, "
            "nature and purpose of processing, type of personal data and categories "
            "of data subjects, and obligations and rights of the controller. The "
            "processor must: process only on documented instructions, ensure persons "
            "authorized to process are committed to confidentiality, take security "
            "measures per Art. 32, respect conditions for engaging sub-processors "
            "(written authorization required), assist the controller with data subject "
            "rights and breach notifications, delete or return data at end of services, "
            "and make available all information necessary to demonstrate compliance "
            "and allow for audits."
        ),
        tags=["DPA", "processor", "sub-processor", "audit", "contract requirements"],
        jurisdiction="EU",
        standard_category="data_protection",
        effective_date=date(2018, 5, 25),
        last_amended=None,
        authority_level="regulation",
    ),
    StandardEntry(
        id="gdpr-007",
        standard="GDPR",
        topic="Security of Processing",
        article="Art. 32",
        title="Security of Processing Measures",
        content=(
            "The controller and processor must implement appropriate technical and "
            "organizational measures to ensure a level of security appropriate to the "
            "risk. Measures must include: pseudonymization and encryption of personal "
            "data; ability to ensure ongoing confidentiality, integrity, availability "
            "and resilience of processing systems; ability to restore availability and "
            "access to personal data in a timely manner in the event of a physical or "
            "technical incident; and a process for regularly testing, assessing and "
            "evaluating the effectiveness of technical and organizational measures. "
            "Adherence to an approved code of conduct or certification mechanism may "
            "be used as an element to demonstrate compliance."
        ),
        tags=["security", "encryption", "resilience", "testing", "pseudonymization"],
        jurisdiction="EU",
        standard_category="data_protection",
        effective_date=date(2018, 5, 25),
        last_amended=None,
        authority_level="regulation",
    ),
    StandardEntry(
        id="gdpr-008",
        standard="GDPR",
        topic="Cross-Border Data Transfers",
        article="Art. 44-49",
        title="Transfers of Personal Data to Third Countries",
        content=(
            "Any transfer of personal data to a third country or international "
            "organization may take place only if the controller and processor comply "
            "with the conditions laid down in Chapter V. Transfers require: an "
            "adequacy decision by the European Commission, or appropriate safeguards "
            "such as Standard Contractual Clauses (SCCs), Binding Corporate Rules "
            "(BCRs), approved codes of conduct, or certification mechanisms. Derogations "
            "for specific situations (consent, contract performance, public interest) "
            "apply only in limited circumstances. Contracts must specify the legal "
            "basis for transfer and identify all sub-processors and their locations."
        ),
        tags=["cross-border", "SCCs", "adequacy", "third country", "data transfer"],
        jurisdiction="EU",
        standard_category="data_protection",
        effective_date=date(2018, 5, 25),
        last_amended=None,
        authority_level="regulation",
    ),
    StandardEntry(
        id="gdpr-009",
        standard="GDPR",
        topic="Data Protection Impact Assessment",
        article="Art. 35",
        title="Data Protection Impact Assessment (DPIA)",
        content=(
            "Where a type of processing is likely to result in a high risk to the "
            "rights and freedoms of natural persons, the controller must carry out a "
            "DPIA prior to the processing. A DPIA is required for: systematic and "
            "extensive evaluation of personal aspects based on automated processing "
            "including profiling; processing on a large scale of special categories "
            "of data or personal data relating to criminal convictions; and systematic "
            "monitoring of a publicly accessible area on a large scale. The DPIA must "
            "contain a systematic description of the processing, assessment of necessity "
            "and proportionality, assessment of risks, and measures to address risks."
        ),
        tags=["DPIA", "risk assessment", "high risk", "impact assessment"],
        jurisdiction="EU",
        standard_category="data_protection",
        effective_date=date(2018, 5, 25),
        last_amended=None,
        authority_level="regulation",
    ),
    StandardEntry(
        id="gdpr-010",
        standard="GDPR",
        topic="Data Protection Officer",
        article="Art. 37-39",
        title="Designation of the Data Protection Officer",
        content=(
            "A DPO must be designated where: processing is carried out by a public "
            "authority; core activities consist of processing operations requiring "
            "regular and systematic monitoring of data subjects on a large scale; or "
            "core activities consist of processing on a large scale of special "
            "categories of data or data relating to criminal convictions. The DPO "
            "must be involved in all issues relating to protection of personal data, "
            "act independently, and report to the highest management level. Contracts "
            "involving high-risk data processing should ensure DPO involvement in "
            "oversight and vendor assessment."
        ),
        tags=["DPO", "governance", "oversight", "compliance"],
        jurisdiction="EU",
        standard_category="data_protection",
        effective_date=date(2018, 5, 25),
        last_amended=None,
        authority_level="regulation",
    ),

    # ── ISO 27001 ──────────────────────────────────────────────
    StandardEntry(
        id="iso-001",
        standard="ISO27001",
        topic="Information Security Management System",
        article="Clause 4",
        title="Context of the Organization and ISMS Scope",
        content=(
            "The organization must determine external and internal issues relevant "
            "to its purpose that affect the ability to achieve the intended outcomes "
            "of the ISMS. The organization must determine: interested parties relevant "
            "to the ISMS and their requirements; the scope of the ISMS considering "
            "these issues, requirements, and interfaces/dependencies between "
            "activities performed by the organization and those performed by other "
            "organizations. The ISMS must be established, implemented, maintained, "
            "and continually improved in accordance with the standard. Third-party "
            "contracts must fall within the ISMS scope when they access or process "
            "the organization's information assets."
        ),
        tags=["ISMS", "scope", "context", "interested parties"],
        jurisdiction="Global",
        standard_category="security",
        effective_date=date(2022, 10, 25),
        last_amended=None,
        authority_level="framework",
    ),
    StandardEntry(
        id="iso-002",
        standard="ISO27001",
        topic="Leadership and Commitment",
        article="Clause 5",
        title="Leadership and Commitment to the ISMS",
        content=(
            "Top management must demonstrate leadership and commitment by: ensuring "
            "the information security policy and objectives are established and "
            "compatible with strategic direction; integrating ISMS requirements into "
            "organization processes; ensuring resources needed for the ISMS are "
            "available; communicating the importance of effective information security "
            "management; ensuring the ISMS achieves its intended outcomes; directing "
            "and supporting persons to contribute to ISMS effectiveness; promoting "
            "continual improvement. An information security policy must be documented, "
            "communicated within the organization, and available to interested parties."
        ),
        tags=["leadership", "policy", "commitment", "management"],
        jurisdiction="Global",
        standard_category="security",
        effective_date=date(2022, 10, 25),
        last_amended=None,
        authority_level="framework",
    ),
    StandardEntry(
        id="iso-003",
        standard="ISO27001",
        topic="Risk Assessment and Treatment",
        article="Clause 6.1",
        title="Actions to Address Risks and Opportunities",
        content=(
            "The organization must define and apply an information security risk "
            "assessment process that: establishes and maintains information security "
            "risk criteria; ensures repeated assessments produce consistent, valid, "
            "comparable results; identifies risks related to loss of confidentiality, "
            "integrity, and availability; identifies risk owners; analyzes and "
            "evaluates risks per the criteria. A risk treatment plan must be produced "
            "that selects appropriate treatment options (avoid, transfer, accept, "
            "mitigate), determines all controls necessary, and obtains risk owner "
            "approval. The Statement of Applicability (SoA) must list all controls "
            "from Annex A and justify inclusions and exclusions."
        ),
        tags=["risk assessment", "risk treatment", "SoA", "risk owner"],
        jurisdiction="Global",
        standard_category="security",
        effective_date=date(2022, 10, 25),
        last_amended=None,
        authority_level="framework",
    ),
    StandardEntry(
        id="iso-004",
        standard="ISO27001",
        topic="Access Control",
        article="Annex A.9",
        title="Access Control",
        content=(
            "Access to information and information processing facilities must be "
            "controlled per business and security requirements. Requirements: "
            "implement an access control policy (A.9.1.1); manage access rights "
            "including provisioning, review, and removal (A.9.2.1-9.2.6); users "
            "must follow organizational procedures for secret authentication "
            "information (A.9.3.1); restrict access to systems and applications "
            "(A.9.4.1-9.4.5) including secure logon, password management, "
            "privileged utility restriction, and access control to program source "
            "code. Role-based access control (RBAC) and principle of least privilege "
            "are mandatory. Contracts must specify access control requirements for "
            "all vendor personnel accessing the organization's systems or data."
        ),
        tags=["access control", "RBAC", "least privilege", "authentication"],
        jurisdiction="Global",
        standard_category="security",
        effective_date=date(2022, 10, 25),
        last_amended=None,
        authority_level="framework",
    ),
    StandardEntry(
        id="iso-005",
        standard="ISO27001",
        topic="Cryptography",
        article="Annex A.8.24",
        title="Use of Cryptography",
        content=(
            "Cryptographic controls must be used to protect information in accordance "
            "with a defined policy on the use of cryptography. Requirements include: "
            "implement a policy on the use of cryptographic controls (A.8.24.1); "
            "manage cryptographic keys throughout their lifecycle including generation, "
            "distribution, storage, archiving, and destruction (A.8.24.2). Encryption "
            "must be applied to data at rest (AES-256 minimum) and data in transit "
            "(TLS 1.2+ minimum). The cryptographic policy must be reviewed when "
            "significant changes occur or at least annually. Contracts must specify "
            "encryption standards and key management responsibilities."
        ),
        tags=["cryptography", "encryption", "key management", "TLS", "AES"],
        jurisdiction="Global",
        standard_category="security",
        effective_date=date(2022, 10, 25),
        last_amended=None,
        authority_level="framework",
    ),
    StandardEntry(
        id="iso-006",
        standard="ISO27001",
        topic="Supplier Relationships",
        article="Annex A.15",
        title="Supplier Relationships",
        content=(
            "Information security requirements for mitigating risks associated with "
            "supplier access to organizational assets must be agreed upon and documented. "
            "Requirements include: establish an information security policy for supplier "
            "relationships (A.15.1.1); address security within supplier agreements "
            "(A.15.1.2) including acceptable use of assets, personnel screening, "
            "compliance with legal and contractual requirements, monitoring and review "
            "of supplier services, and management of security incidents; address "
            "information and communication technology supply chain risks (A.15.1.3); "
            "monitor, review, and audit supplier service delivery regularly (A.15.2.1); "
            "manage changes to supplier services including re-assessment of risks "
            "(A.15.2.2). Contracts must include security schedules or exhibits."
        ),
        tags=["supplier", "vendor management", "audit", "supply chain", "third-party"],
        jurisdiction="Global",
        standard_category="security",
        effective_date=date(2022, 10, 25),
        last_amended=None,
        authority_level="framework",
    ),
    StandardEntry(
        id="iso-007",
        standard="ISO27001",
        topic="Incident Management",
        article="Annex A.5.24-25",
        title="Information Security Incident Management",
        content=(
            "The organization must plan and prepare for managing information security "
            "incidents. Requirements include: establish responsibilities and procedures "
            "for incident management (A.5.24); ensure incidents are reported through "
            "appropriate channels as quickly as possible (A.5.25); assess and decide "
            "on information security events to determine if they should be classified "
            "as incidents (A.5.26); respond to incidents in accordance with documented "
            "procedures (A.5.27); collect and preserve evidence related to security "
            "incidents (A.5.28); and use knowledge gained from incidents to strengthen "
            "controls and reduce likelihood or impact of future incidents (A.5.29). "
            "Contracts must define incident notification timelines, joint investigation "
            "procedures, and information sharing protocols."
        ),
        tags=["incident", "response", "reporting", "forensics", "lessons learned"],
        jurisdiction="Global",
        standard_category="security",
        effective_date=date(2022, 10, 25),
        last_amended=None,
        authority_level="framework",
    ),
    StandardEntry(
        id="iso-008",
        standard="ISO27001",
        topic="Secure Development",
        article="Annex A.8.28-29",
        title="Security in Development and Support Processes",
        content=(
            "Secure development practices must be applied to all development activities. "
            "Requirements: establish rules for secure development of software and "
            "systems and apply them (A.8.25); apply security requirements in the "
            "development lifecycle, including requirements analysis, design, "
            "implementation, testing, and deployment (A.8.26); security testing must "
            "be performed during development (A.8.29); test data must be carefully "
            "selected, protected, and controlled (A.8.33); change control procedures "
            "must be applied to all system changes (A.8.32). Production data must not "
            "be used for testing without appropriate sanitization. Contracts for "
            "software services must include secure development obligations."
        ),
        tags=["SDLC", "secure coding", "testing", "change management", "development"],
        jurisdiction="Global",
        standard_category="security",
        effective_date=date(2022, 10, 25),
        last_amended=None,
        authority_level="framework",
    ),
    StandardEntry(
        id="iso-009",
        standard="ISO27001",
        topic="Operational Security",
        article="Annex A.12",
        title="Operations Security",
        content=(
            "Information processing facilities must be operated securely through "
            "documented operating procedures (A.12.1.1); changes to organization, "
            "business processes, information processing facilities, and systems must "
            "be controlled (A.12.1.2); capacity management must ensure required "
            "performance (A.12.1.3); development, test, and operational environments "
            "must be separated (A.12.1.4); protection against malware must be "
            "implemented (A.12.2.1); technical vulnerabilities must be managed and "
            "remediated (A.12.6.1); audit logging must be enabled and audit logs "
            "protected (A.12.4.1-4.3); clocks must be synchronized (A.12.4.4)."
        ),
        tags=["operations", "malware", "vulnerability", "logging", "change control"],
        jurisdiction="Global",
        standard_category="security",
        effective_date=date(2022, 10, 25),
        last_amended=None,
        authority_level="framework",
    ),
    StandardEntry(
        id="iso-010",
        standard="ISO27001",
        topic="Compliance",
        article="Clause 9 / Annex A.18",
        title="Performance Evaluation and Compliance",
        content=(
            "The organization must evaluate information security performance and "
            "ISMS effectiveness (Clause 9). Internal audits must be conducted at "
            "planned intervals (Clause 9.2). Management reviews must be conducted "
            "at planned intervals (Clause 9.3). Legal, statutory, regulatory, and "
            "contractual requirements related to information security must be "
            "identified and documented (A.18.1.1); appropriate controls must be "
            "implemented to ensure compliance (A.18.1.2); records must be protected "
            "from loss, destruction, falsification, unauthorized access, and "
            "unauthorized release (A.18.1.3); privacy and PII protection must be "
            "ensured (A.18.1.4); independent review of information security must "
            "be performed at planned intervals or when significant changes occur "
            "(A.18.2.1); compliance with security policies, standards, and technical "
            "requirements must be reviewed regularly (A.18.2.2)."
        ),
        tags=["compliance", "audit", "management review", "legal", "PII"],
        jurisdiction="Global",
        standard_category="security",
        effective_date=date(2022, 10, 25),
        last_amended=None,
        authority_level="framework",
    ),

    # ── SOC 2 ──────────────────────────────────────────────────
    StandardEntry(
        id="soc2-001",
        standard="SOC2",
        topic="Security Criterion",
        article="CC6",
        title="Logical and Physical Access Controls",
        content=(
            "The entity must implement logical access security measures to protect "
            "against unauthorized access to system resources. Requirements include: "
            "logical access credentials must be uniquely identified (CC6.1); "
            "credential issuance, modification, and removal must be authorized and "
            "controlled (CC6.2); access to data, software, functions, and other "
            "information resources must be restricted based on role or attribute "
            "using RBAC with least privilege (CC6.3); physical access to facilities "
            "and assets must be restricted to authorized personnel (CC6.4); access "
            "must be deprovisioned promptly upon termination or role change (CC6.5); "
            "access must be reviewed at least quarterly for appropriateness (CC6.6). "
            "Contracts must define access provisioning, review, and deprovisioning "
            "obligations for vendor personnel."
        ),
        tags=["access control", "RBAC", "provisioning", "deprovisioning", "review"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2017, 12, 15),
        last_amended=date(2022, 6, 15),
        authority_level="framework",
    ),
    StandardEntry(
        id="soc2-002",
        standard="SOC2",
        topic="Security Criterion",
        article="CC7",
        title="System Operations and Monitoring",
        content=(
            "The entity must implement detection and monitoring controls to identify "
            "anomalies and security events. Requirements include: system and data "
            "classifications based on criticality and sensitivity (CC7.1); system "
            "monitoring to detect anomalies and security events (CC7.2); incident "
            "response procedures including detection, analysis, containment, "
            "eradication, recovery, and post-incident review (CC7.3); threat "
            "intelligence and vulnerability management programs (CC7.4); security "
            "incidents must be reported to appropriate parties including customers "
            "where required (CC7.5). Contracts must specify monitoring scope, alert "
            "thresholds, incident notification SLAs (typically within 24-48 hours), "
            "and post-incident reporting obligations."
        ),
        tags=["monitoring", "incident response", "vulnerability", "detection"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2017, 12, 15),
        last_amended=date(2022, 6, 15),
        authority_level="framework",
    ),
    StandardEntry(
        id="soc2-003",
        standard="SOC2",
        topic="Security Criterion",
        article="CC8",
        title="Change Management",
        content=(
            "The entity must authorize, design, develop, test, and deploy changes "
            "to infrastructure, data, software, and procedures in a controlled manner "
            "to meet objectives. Requirements include: an established change management "
            "process (CC8.1); infrastructure and software changes must be documented, "
            "tested, approved, and deployed through controlled processes (CC8.2); "
            "emergency changes must follow a documented process with appropriate "
            "post-implementation review; segregation of duties must be maintained "
            "between development/test and production environments; unauthorized "
            "changes must be detected and addressed. Contracts must define change "
            "management notification requirements, especially for changes affecting "
            "security controls or customer data handling."
        ),
        tags=["change management", "SDLC", "testing", "emergency changes", "segregation"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2017, 12, 15),
        last_amended=date(2022, 6, 15),
        authority_level="framework",
    ),
    StandardEntry(
        id="soc2-004",
        standard="SOC2",
        topic="Availability Criterion",
        article="A1",
        title="Availability and Capacity Management",
        content=(
            "The entity must maintain system availability to meet its commitments and "
            "system requirements. Controls include: monitoring system capacity and "
            "performance against established thresholds (A1.1); implementing "
            "redundancy and failover capabilities for critical components (A1.2); "
            "backup and recovery procedures with defined RPO (Recovery Point "
            "Objective) and RTO (Recovery Time Objective) targets (A1.3); a documented "
            "disaster recovery plan that is tested at least annually (A1.4). Contracts "
            "must define availability SLA commitments, penalties for non-performance, "
            "and DR/BCP capabilities and testing schedules."
        ),
        tags=["availability", "capacity", "DR", "backup", "SLA"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2017, 12, 15),
        last_amended=date(2022, 6, 15),
        authority_level="framework",
    ),
    StandardEntry(
        id="soc2-005",
        standard="SOC2",
        topic="Processing Integrity Criterion",
        article="PI1",
        title="Processing Integrity",
        content=(
            "System processing must be complete, valid, accurate, timely, and "
            "authorized. Controls include: defining processing specifications aligned "
            "with product/service commitments (PI1.1); detecting and correcting "
            "processing errors in a timely manner (PI1.2); implementing quality "
            "assurance procedures including input validation, processing verification, "
            "and output validation (PI1.3); maintaining data integrity through all "
            "processing stages including ingestion, transformation, storage, and "
            "output (PI1.4); ensuring accurate and complete storage of inputs, "
            "processing activities, and outputs (PI1.5). Contracts involving data "
            "processing must include data quality and integrity commitments."
        ),
        tags=["integrity", "accuracy", "quality", "validation", "processing"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2017, 12, 15),
        last_amended=date(2022, 6, 15),
        authority_level="framework",
    ),
    StandardEntry(
        id="soc2-006",
        standard="SOC2",
        topic="Confidentiality Criterion",
        article="C1",
        title="Confidentiality of Information",
        content=(
            "Confidential information must be protected commensurate with its "
            "classification. Controls include: identifying and classifying confidential "
            "information per the entity's data classification policy (C1.1); restricting "
            "access to confidential information to authorized personnel only (C1.2); "
            "encrypting confidential information at rest and in transit (C1.3); "
            "procedures for secure disposal of confidential information when no longer "
            "needed (C1.4); monitoring for unauthorized access or disclosure of "
            "confidential information (C1.5). Contracts must define what constitutes "
            "confidential information, handling requirements, and breach consequences."
        ),
        tags=["confidentiality", "classification", "encryption", "disposal", "monitoring"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2017, 12, 15),
        last_amended=date(2022, 6, 15),
        authority_level="framework",
    ),
    StandardEntry(
        id="soc2-007",
        standard="SOC2",
        topic="Privacy Criterion",
        article="P1-P8",
        title="Privacy Practices",
        content=(
            "The entity must protect personal information throughout its lifecycle. "
            "Requirements: provide notice of privacy practices including purpose of "
            "collection, use, retention, and disclosure (P2); provide choice and "
            "consent mechanisms for data collection and use (P3); collect only the "
            "personal information needed for specified purposes (P4); limit use, "
            "retention, and disposal of personal information to that which is necessary "
            "(P5); provide individuals with access to their personal information for "
            "review and correction (P6); disclose personal information to third parties "
            "only for purposes described in notice and with appropriate agreements "
            "(P7); implement security for privacy including administrative, technical, "
            "physical safeguards (P8). Contracts must address all privacy criteria "
            "and define sub-processor management."
        ),
        tags=["privacy", "PII", "notice", "consent", "retention", "disposal"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2017, 12, 15),
        last_amended=date(2022, 6, 15),
        authority_level="framework",
    ),
    StandardEntry(
        id="soc2-008",
        standard="SOC2",
        topic="Risk Assessment",
        article="CC3",
        title="Risk Assessment",
        content=(
            "The entity must identify risks to the achievement of its objectives and "
            "assess the severity and likelihood of each risk. Requirements include: "
            "identifying risks that threaten the achievement of system objectives "
            "(CC3.1); analyzing the significance of identified risks considering "
            "likelihood and magnitude of impact (CC3.2); determining how risks should "
            "be managed including acceptance, avoidance, reduction, or sharing (CC3.3); "
            "identifying and assessing changes that could significantly impact the "
            "system of internal control (CC3.4). Risk assessment must be performed "
            "at least annually and when significant changes occur. Contracts must "
            "identify shared risks and define joint risk management obligations."
        ),
        tags=["risk assessment", "risk management", "impact", "likelihood"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2017, 12, 15),
        last_amended=date(2022, 6, 15),
        authority_level="framework",
    ),
    StandardEntry(
        id="soc2-009",
        standard="SOC2",
        topic="Vendor Management",
        article="CC9",
        title="Risk Mitigation for Subservice Organizations",
        content=(
            "The entity must assess and manage risks associated with vendors and "
            "business partners. Requirements include: conducting due diligence before "
            "engaging third-party vendors (CC9.1); assessing vendor suitability "
            "considering information security practices, financial stability, and "
            "compliance posture (CC9.2); contracts must assign responsibility for "
            "controls shared between the entity and vendor; monitoring and reviewing "
            "vendor performance and compliance at least annually (CC9.3); implementing "
            "a formal vendor risk management program with tiered assessments based on "
            "data sensitivity and access levels. SOC 2 reports from vendors should be "
            "reviewed and complemented by the entity's own risk assessment."
        ),
        tags=["vendor", "third-party", "due diligence", "risk", "supply chain"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2017, 12, 15),
        last_amended=date(2022, 6, 15),
        authority_level="framework",
    ),
    StandardEntry(
        id="soc2-010",
        standard="SOC2",
        topic="Continuous Monitoring",
        article="CC4",
        title="Monitoring of Controls",
        content=(
            "The entity must continuously monitor the design and operating effectiveness "
            "of internal controls. Requirements: establishing baseline configurations "
            "and monitoring for deviations (CC4.1); evaluating controls through "
            "ongoing monitoring and separate evaluations such as internal audits "
            "(CC4.2); reporting control deficiencies to parties responsible for "
            "corrective action including senior management and board as appropriate "
            "(CC4.3). Penetration testing is universally expected by auditors as "
            "evidence of control effectiveness. Contracts should define the right "
            "to audit vendor controls, frequency of assessments, and remediation "
            "timelines for identified deficiencies."
        ),
        tags=["monitoring", "audit", "penetration testing", "deficiencies", "controls"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2017, 12, 15),
        last_amended=date(2022, 6, 15),
        authority_level="framework",
    ),

    # ── PCI DSS v4.0.1 ─────────────────────────────────────────
    StandardEntry(
        id="pci-001",
        standard="PCI_DSS",
        topic="Build and Maintain Secure Network",
        article="Req. 1-2",
        title="Network Security Controls and Secure Configurations",
        content=(
            "Install and maintain network security controls to protect cardholder data "
            "environments (Req. 1). Network security controls must include firewalls, "
            "network segmentation, and documented CDE boundaries. Apply secure "
            "configurations to all system components (Req. 2): no vendor default "
            "passwords, hardened configurations, and documented security baselines. "
            "All non-console administrative access must be encrypted with strong "
            "cryptography. Contracts involving payment processing must specify CDE "
            "scope, segmentation requirements, and configuration standards."
        ),
        tags=["network security", "firewall", "CDE", "segmentation", "hardening"],
        jurisdiction="Global",
        standard_category="industry",
        effective_date=date(2022, 3, 31),
        last_amended=date(2024, 6, 30),
        authority_level="industry_standard",
    ),
    StandardEntry(
        id="pci-002",
        standard="PCI_DSS",
        topic="Protect Account Data",
        article="Req. 3-4",
        title="Stored Account Data and Encryption in Transit",
        content=(
            "Protect stored account data using encryption, tokenization, or keyed "
            "cryptographic hashes (Req. 3). Sensitive Authentication Data (SAD) must "
            "not be stored after authorization, even if encrypted. Primary Account "
            "Numbers (PANs) must be rendered unreadable everywhere they are stored. "
            "Encrypt cardholder data during transmission over open, public networks "
            "using strong cryptography - TLS 1.2+ minimum, with valid certificates "
            "(Req. 4). Contracts must specify encryption standards, key management "
            "responsibilities, and prohibition on SAD storage."
        ),
        tags=["encryption", "tokenization", "PAN", "SAD", "data-at-rest", "TLS"],
        jurisdiction="Global",
        standard_category="industry",
        effective_date=date(2022, 3, 31),
        last_amended=date(2024, 6, 30),
        authority_level="industry_standard",
    ),
    StandardEntry(
        id="pci-003",
        standard="PCI_DSS",
        topic="Access Control and Authentication",
        article="Req. 7-8",
        title="Least Privilege and Strong Authentication",
        content=(
            "Restrict access to cardholder data by business need-to-know using least "
            "privilege principles (Req. 7). Role-based access control (RBAC) must be "
            "implemented with documented access rights. Identify and authenticate all "
            "access to system components: MFA is mandatory for ALL access into the "
            "CDE - users, admins, and vendors (Req. 8). Minimum password length is "
            "12 characters (up from 7 in v3.2.1). No hard-coded passwords in scripts "
            "or files. Contracts must define access provisioning, quarterly access "
            "reviews, and immediate deprovisioning on termination."
        ),
        tags=["access control", "RBAC", "MFA", "passwords", "least privilege"],
        jurisdiction="Global",
        standard_category="industry",
        effective_date=date(2022, 3, 31),
        last_amended=date(2024, 6, 30),
        authority_level="industry_standard",
    ),
    StandardEntry(
        id="pci-004",
        standard="PCI_DSS",
        topic="Vulnerability Management",
        article="Req. 5-6",
        title="Anti-Malware and Secure Software Development",
        content=(
            "Protect all systems against malware using anti-malware solutions with "
            "automatic updates, periodic scans, and audit logging (Req. 5). Develop "
            "and maintain secure systems and software: apply security patches within "
            "30 days of release; maintain a Software Bill of Materials (SBOM) for "
            "all payment applications (Req. 6). Maintain an inventory of all "
            "client-side scripts on payment pages and authorize each - critical for "
            "preventing Magecart/formjacking attacks (Req. 6.4.3). Deploy tamper "
            "detection and change-detection mechanisms on payment pages (Req. 11.6.1). "
            "Contracts for software services must mandate secure SDLC practices and "
            "SBOM delivery."
        ),
        tags=["malware", "patching", "SDLC", "SBOM", "payment page", "scripts"],
        jurisdiction="Global",
        standard_category="industry",
        effective_date=date(2022, 3, 31),
        last_amended=date(2024, 6, 30),
        authority_level="industry_standard",
    ),
    StandardEntry(
        id="pci-005",
        standard="PCI_DSS",
        topic="Monitoring and Testing",
        article="Req. 10-11",
        title="Logging, Monitoring, and Security Testing",
        content=(
            "Log and monitor all access to system components and cardholder data using "
            "automated audit trails with anomaly detection (Req. 10). Audit logs must "
            "be centralized, tamper-proof, and retained for at least 12 months. Test "
            "security systems and processes regularly: quarterly credentialed internal "
            "vulnerability scans; annual penetration tests covering both network and "
            "application layers (Req. 11). IDS/IPS must detect covert malware "
            "communications such as DNS tunneling. Contracts must define incident "
            "notification timelines (typically within 24 hours), joint investigation "
            "protocols, and forensic evidence handling."
        ),
        tags=["logging", "monitoring", "penetration testing", "vulnerability scan", "IDS"],
        jurisdiction="Global",
        standard_category="industry",
        effective_date=date(2022, 3, 31),
        last_amended=date(2024, 6, 30),
        authority_level="industry_standard",
    ),
    StandardEntry(
        id="pci-006",
        standard="PCI_DSS",
        topic="Third-Party Service Provider Management",
        article="Req. 12",
        title="Organizational Policies and TPSP Oversight",
        content=(
            "Maintain a comprehensive information security policy that is reviewed "
            "at least annually and communicated to all personnel (Req. 12). Formal "
            "risk assessments must be performed for all significant changes. Third-Party "
            "Service Providers (TPSPs) must be managed through a documented due diligence "
            "process: validate PCI DSS compliance status, obtain annual compliance "
            "attestations, and define security responsibilities in written agreements. "
            "Contracts must specify which PCI DSS requirements are the responsibility "
            "of each party, include breach notification obligations, and maintain "
            "the right to audit. TPSP responsibilities were significantly clarified "
            "in v4.0.1."
        ),
        tags=["policy", "TPSP", "third-party", "due diligence", "risk assessment"],
        jurisdiction="Global",
        standard_category="industry",
        effective_date=date(2022, 3, 31),
        last_amended=date(2024, 6, 30),
        authority_level="industry_standard",
    ),

    # ── HIPAA ───────────────────────────────────────────────────
    StandardEntry(
        id="hipaa-001",
        standard="HIPAA",
        topic="Privacy Rule",
        article="45 CFR 164.502",
        title="Use and Disclosure of Protected Health Information",
        content=(
            "Covered entities and business associates may only use and disclose Protected "
            "Health Information (PHI) as permitted by the Privacy Rule. PHI includes "
            "all individually identifiable health information held or transmitted in "
            "any form. Permitted uses without authorization include: treatment, payment, "
            "and health care operations (TPO); public health activities; and as required "
            "by law. All other uses require written patient authorization. The minimum "
            "necessary standard applies: only the minimum PHI needed for the intended "
            "purpose may be used, disclosed, or requested. A signed Business Associate "
            "Agreement (BAA) is required before any PHI is shared with a vendor. "
            "Contracts must specify permitted uses, minimum necessary limits, and "
            "prohibition on re-disclosure."
        ),
        tags=["PHI", "privacy", "BAA", "minimum necessary", "TPO", "authorization"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(1996, 8, 21),
        last_amended=date(2013, 3, 26),
        authority_level="statute",
    ),
    StandardEntry(
        id="hipaa-002",
        standard="HIPAA",
        topic="Security Rule",
        article="45 CFR 164.306",
        title="Administrative, Physical, and Technical Safeguards for ePHI",
        content=(
            "Covered entities and business associates must implement administrative, "
            "physical, and technical safeguards to protect electronic Protected Health "
            "Information (ePHI). Administrative safeguards include: security management "
            "process (risk analysis and risk management), designated security official, "
            "workforce security, information access management, security awareness "
            "training, security incident procedures, contingency planning, and evaluation. "
            "Physical safeguards include: facility access controls, workstation use and "
            "security, and device and media controls. Technical safeguards include: "
            "access controls (unique user IDs, automatic logoff, encryption), audit "
            "controls, integrity controls, person or entity authentication, and "
            "transmission security. Contracts must require vendors to implement all "
            "three categories of safeguards commensurate with risk."
        ),
        tags=["ePHI", "safeguards", "administrative", "physical", "technical", "risk analysis"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(1996, 8, 21),
        last_amended=date(2013, 3, 26),
        authority_level="statute",
    ),
    StandardEntry(
        id="hipaa-003",
        standard="HIPAA",
        topic="Breach Notification Rule",
        article="45 CFR 164.400",
        title="Notification Requirements for PHI Breaches",
        content=(
            "Following a breach of unsecured PHI, business associates must notify "
            "covered entities without unreasonable delay, typically within 10 days "
            "of discovery. Covered entities must notify affected individuals within "
            "60 days of discovery. Breaches affecting 500 or more individuals must "
            "be reported to the Secretary of HHS concurrently with individual notice "
            "and trigger media notification in the affected jurisdiction. Breaches "
            "affecting fewer than 500 individuals must be logged and reported to HHS "
            "within 60 days of calendar year end. Notification must describe the "
            "breach, types of PHI involved, steps individuals should take, and the "
            "entity's response. Contracts must specify shorter breach notification "
            "timelines for vendors (commonly 10 days maximum)."
        ),
        tags=["breach", "notification", "60 days", "500 threshold", "media notice"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(1996, 8, 21),
        last_amended=date(2013, 3, 26),
        authority_level="statute",
    ),
    StandardEntry(
        id="hipaa-004",
        standard="HIPAA",
        topic="Business Associate Agreements",
        article="45 CFR 164.504",
        title="Required BAA Provisions",
        content=(
            "A Business Associate Agreement (BAA) must be executed before a covered "
            "entity discloses PHI to a business associate. The BAA must: (1) establish "
            "permitted uses and disclosures of PHI; (2) require the BA to implement "
            "appropriate safeguards; (3) require breach reporting within a defined "
            "timeframe; (4) require the BA to ensure subcontractors agree to the same "
            "restrictions; (5) require the BA to make PHI available for individual "
            "access, amendment, and accounting requests; (6) require the BA to return "
            "or destroy all PHI at contract termination; (7) authorize the covered "
            "entity to terminate for material breach. Business associates are now "
            "directly liable for HIPAA compliance under the HITECH Act and subject "
            "to OCR audits and civil money penalties."
        ),
        tags=["BAA", "subcontractor", "audit", "termination", "destruction", "liability"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(1996, 8, 21),
        last_amended=date(2013, 3, 26),
        authority_level="statute",
    ),
    StandardEntry(
        id="hipaa-005",
        standard="HIPAA",
        topic="Patient Rights",
        article="45 CFR 164.520",
        title="Individual Rights Under HIPAA",
        content=(
            "Individuals have the right to: access and obtain a copy of their PHI within "
            "30 days (Right of Access); request amendment of inaccurate PHI (Right to "
            "Amend); receive an accounting of disclosures of their PHI made in the "
            "prior 6 years (Right to Accounting); request restrictions on uses and "
            "disclosures (Right to Restrict); request confidential communications at "
            "alternative locations or by alternative means; and receive a Notice of "
            "Privacy Practices (NPP) describing how PHI is used and individual rights. "
            "Covered entities must provide the NPP at first service delivery and post "
            "it prominently. Contracts must ensure vendors can support these rights, "
            "particularly access, amendment, and accounting of disclosures."
        ),
        tags=["patient rights", "access", "amendment", "accounting", "NPP", "restrict"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(1996, 8, 21),
        last_amended=date(2013, 3, 26),
        authority_level="statute",
    ),

    # ── DPDPA 2023 (India) ──────────────────────────────────────
    StandardEntry(
        id="dpdpa-001",
        standard="DPDPA",
        topic="Scope and Applicability",
        article="S. 3",
        title="Application of the DPDP Act",
        content=(
            "The Digital Personal Data Protection Act, 2023 applies to the processing "
            "of digital personal data within India and to processing outside India "
            "if it is in connection with offering goods or services to individuals "
            "(Data Principals) in India. Personal data is defined broadly as any data "
            "about an individual who is identifiable by or in relation to such data. "
            "The Act does not apply to: personal data processed by an individual for "
            "personal or domestic purposes; or personal data that is made or caused "
            "to be made publicly available by the Data Principal or under any legal "
            "obligation. The Act was fully operationalised on 14 November 2025 with "
            "the notification of the DPDP Rules, 2025. Contracts involving processing "
            "of Indian residents' digital personal data must incorporate DPDPA "
            "compliance regardless of where the processor is located."
        ),
        tags=["scope", "extraterritorial", "digital personal data", "Data Principal"],
        jurisdiction="India",
        standard_category="data_protection",
        effective_date=date(2023, 8, 11),
        last_amended=None,
        authority_level="statute",
    ),
    StandardEntry(
        id="dpdpa-002",
        standard="DPDPA",
        topic="Consent and Lawful Processing",
        article="S. 4-7",
        title="Consent as the Primary Basis for Processing",
        content=(
            "Consent is the primary lawful basis for processing personal data under "
            "the DPDPA. Consent must be free, specific, informed, unconditional, and "
            "unambiguous with clear affirmative action. A standalone privacy notice "
            "must precede or accompany every consent request, specifying: the personal "
            "data to be collected, the purpose of processing, the rights of the Data "
            "Principal, and the grievance redressal mechanism. Consent may be withdrawn "
            "at any time, and withdrawal must be as easy as giving consent. Unlike GDPR, "
            "there is no 'legitimate interest' or 'contractual necessity' basis. Limited "
            "legitimate uses without consent exist under S. 7: voluntary provision, "
            "state functions, legal compliance, medical emergencies, and employment "
            "purposes. Contracts must identify the consent basis for each processing "
            "activity."
        ),
        tags=["consent", "lawful basis", "notice", "withdrawal", "legitimate uses"],
        jurisdiction="India",
        standard_category="data_protection",
        effective_date=date(2023, 8, 11),
        last_amended=None,
        authority_level="statute",
    ),
    StandardEntry(
        id="dpdpa-003",
        standard="DPDPA",
        topic="Data Fiduciary Obligations",
        article="S. 8",
        title="Duties of Data Fiduciaries",
        content=(
            "Data Fiduciaries (entities determining purpose and means of processing, "
            "analogous to GDPR data controllers) must: make reasonable efforts to "
            "ensure the accuracy and completeness of data; implement reasonable "
            "security safeguards including encryption, obfuscation, masking, access "
            "controls, monitoring, and backups; notify the Data Protection Board and "
            "affected Data Principals of any personal data breach without delay, with "
            "a detailed report to the Board within 72 hours; erase personal data when "
            "the purpose is no longer served or consent is withdrawn (subject to legal "
            "retention); publish contact details of a Data Protection Officer or "
            "designated point of contact; and establish an effective grievance redressal "
            "mechanism. Contracts with Data Processors must include binding contractual "
            "safeguards mandating these obligations."
        ),
        tags=["Data Fiduciary", "safeguards", "breach", "erasure", "accountability"],
        jurisdiction="India",
        standard_category="data_protection",
        effective_date=date(2023, 8, 11),
        last_amended=None,
        authority_level="statute",
    ),
    StandardEntry(
        id="dpdpa-004",
        standard="DPDPA",
        topic="Data Principal Rights",
        article="S. 11-13",
        title="Rights of the Data Principal",
        content=(
            "Data Principals (individuals) have the right to: obtain a summary of their "
            "personal data being processed and the processing activities (Right to "
            "Information); correct, complete, update, or erase their personal data "
            "(Right to Correction and Erasure); access grievance redressal mechanisms "
            "with escalation to the Data Protection Board of India; and nominate "
            "another individual to exercise rights in the event of death or incapacity "
            "(Right to Nominate). Data Fiduciaries must respond to rights requests "
            "within a prescribed time. Unlike GDPR, the DPDPA does not provide explicit "
            "data portability rights or a right to object to processing based on "
            "automated decision-making. Contracts must enable processors to assist "
            "the Data Fiduciary in fulfilling these rights."
        ),
        tags=["rights", "Data Principal", "grievance", "nomination", "correction"],
        jurisdiction="India",
        standard_category="data_protection",
        effective_date=date(2023, 8, 11),
        last_amended=None,
        authority_level="statute",
    ),
    StandardEntry(
        id="dpdpa-005",
        standard="DPDPA",
        topic="Cross-Border Data Transfers",
        article="S. 16",
        title="Transfer of Personal Data Outside India",
        content=(
            "The DPDPA adopts a 'blacklist' approach to cross-border data transfers: "
            "transfers are generally permitted except to countries or territories "
            "specifically restricted by the Central Government by notification. This "
            "is more permissive than GDPR's adequacy framework. However, Significant "
            "Data Fiduciaries (SDFs) may face stricter data localisation requirements "
            "for designated categories of data. Existing sectoral localisation "
            "requirements under RBI, SEBI, IRDAI, and other Indian regulators continue "
            "to apply independently. Contracts involving cross-border data transfers "
            "must identify all data storage and processing locations and monitor the "
            "Central Government's restricted territories list."
        ),
        tags=["cross-border", "blacklist", "localisation", "SDF", "transfer"],
        jurisdiction="India",
        standard_category="data_protection",
        effective_date=date(2023, 8, 11),
        last_amended=None,
        authority_level="statute",
    ),
    StandardEntry(
        id="dpdpa-006",
        standard="DPDPA",
        topic="Significant Data Fiduciaries",
        article="S. 10",
        title="Additional Obligations for SDFs",
        content=(
            "The Central Government may designate certain Data Fiduciaries as Significant "
            "Data Fiduciaries (SDFs) based on data volume, sensitivity, risk to "
            "electoral democracy, security of the state, or public order. SDFs have "
            "additional obligations: appoint a Data Protection Officer (DPO) based in "
            "India; appoint an independent data auditor for annual compliance audits; "
            "conduct annual Data Protection Impact Assessments (DPIAs); and implement "
            "algorithmic due diligence to ensure processing systems do not harm Data "
            "Principals' rights. Contracts involving SDFs must reflect these heightened "
            "obligations and enable auditor access."
        ),
        tags=["SDF", "DPO", "auditor", "DPIA", "algorithmic due diligence"],
        jurisdiction="India",
        standard_category="data_protection",
        effective_date=date(2023, 8, 11),
        last_amended=None,
        authority_level="statute",
    ),
    StandardEntry(
        id="dpdpa-007",
        standard="DPDPA",
        topic="Penalties and Enforcement",
        article="S. 33",
        title="Financial Penalties for Non-Compliance",
        content=(
            "The Data Protection Board of India can impose substantial financial penalties: "
            "up to ₹250 crore (~USD 30 million) for failure to maintain reasonable "
            "security safeguards resulting in a breach; up to ₹200 crore for failure "
            "to notify the Board or affected Data Principals of a breach; up to ₹200 "
            "crore for violation of provisions relating to children's data; up to ₹150 "
            "crore for non-compliance by SDFs with additional obligations; and up to "
            "₹50 crore for breach of any other provision. Penalties are determined "
            "considering the nature, gravity, duration, and repetitive character of "
            "the breach. Contracts must reflect the severity of these penalties in "
            "risk allocation and indemnification provisions."
        ),
        tags=["penalties", "Data Protection Board", "enforcement", "fines", "liability"],
        jurisdiction="India",
        standard_category="data_protection",
        effective_date=date(2023, 8, 11),
        last_amended=None,
        authority_level="statute",
    ),

    # ── Indian Contract Act, 1872 ───────────────────────────────
    StandardEntry(
        id="ica-001",
        standard="IND_CONTRACT",
        topic="Formation of Valid Contracts",
        article="S. 2, 10",
        title="Essentials of a Valid Contract Under Indian Law",
        content=(
            "Section 10 of the Indian Contract Act, 1872 establishes that all agreements "
            "are contracts if made by free consent of parties competent to contract, "
            "for lawful consideration and with a lawful object, and not expressly "
            "declared void. The seven essentials of a valid contract are: (1) offer "
            "and acceptance constituting an agreement (S.2(a),(b)); (2) intention to "
            "create legal relations; (3) competent parties - age of majority, sound "
            "mind, not disqualified by law (S.11); (4) lawful consideration - something "
            "of value exchanged at the desire of the promisor (S.2(d)); (5) free consent "
            "- not caused by coercion, undue influence, fraud, misrepresentation, or "
            "mistake (S.14-22); (6) lawful object - not forbidden by law, fraudulent, "
            "immoral, or opposed to public policy (S.23); and (7) not expressly declared "
            "void. Indian contract law always applies as the baseline for contracts "
            "governed by Indian law."
        ),
        tags=["formation", "agreement", "consideration", "consent", "competent", "lawful object"],
        jurisdiction="India",
        standard_category="contract_law",
        effective_date=date(1872, 9, 1),
        last_amended=date(2018, 8, 9),
        authority_level="statute",
    ),
    StandardEntry(
        id="ica-002",
        standard="IND_CONTRACT",
        topic="Free Consent and Voidability",
        article="S. 14-22",
        title="Coercion, Undue Influence, Fraud, and Misrepresentation",
        content=(
            "Consent is free when not caused by: coercion (S.15 - committing or "
            "threatening acts forbidden by IPC, or unlawful detention of property); "
            "undue influence (S.16 - one party dominates the will of another, especially "
            "in fiduciary or real/ apparent authority relationships); fraud (S.17 - "
            "false suggestion of fact, active concealment of material facts, promise "
            "without intention to perform, or any act intended to deceive); "
            "misrepresentation (S.18 - positive assertion believed true but not "
            "warranted by information, breach of duty without intent to deceive); or "
            "mistake (S.20-22 - bilateral mistake of fact makes agreement void; "
            "unilateral mistake does not affect validity). Coercion, fraud, or "
            "misrepresentation make the contract voidable at the option of the "
            "aggrieved party (S.19). Contracts must demonstrate genuine consent "
            "from both parties."
        ),
        tags=["consent", "coercion", "undue influence", "fraud", "misrepresentation", "voidable"],
        jurisdiction="India",
        standard_category="contract_law",
        effective_date=date(1872, 9, 1),
        last_amended=date(2018, 8, 9),
        authority_level="statute",
    ),
    StandardEntry(
        id="ica-003",
        standard="IND_CONTRACT",
        topic="Void Agreements",
        article="S. 23-30",
        title="Agreements Expressly Declared Void",
        content=(
            "The Indian Contract Act declares certain agreements void as a matter of "
            "law: agreements with unlawful consideration or object - forbidden by law, "
            "defeating any law, fraudulent, injurious to person/property, immoral, or "
            "opposed to public policy (S.23); agreements in restraint of marriage "
            "other than a minor (S.26); agreements in restraint of trade - any "
            "restriction on lawful profession, trade, or business (S.27, except sale "
            "of goodwill with reasonable limits); agreements in restraint of legal "
            "proceedings - absolutely restricting parties from enforcing rights through "
            "legal process (S.28); agreements void for uncertainty (S.29); and wagering "
            "agreements (S.30). Non-compete clauses, exclusive dealing provisions, "
            "and dispute resolution clauses in contracts governed by Indian law must "
            "be carefully assessed against these voidness provisions."
        ),
        tags=["void", "restraint of trade", "public policy", "wager", "uncertainty"],
        jurisdiction="India",
        standard_category="contract_law",
        effective_date=date(1872, 9, 1),
        last_amended=date(2018, 8, 9),
        authority_level="statute",
    ),
    StandardEntry(
        id="ica-004",
        standard="IND_CONTRACT",
        topic="Performance and Breach",
        article="S. 37, 39, 55, 73, 74",
        title="Performance, Time, and Damages for Breach",
        content=(
            "Parties to a contract must perform or offer to perform their respective "
            "promises (S.37). If a party refuses to perform wholly, the promisee may "
            "put an end to the contract (S.39). Where time is of the essence and a "
            "party fails to perform by the specified time, the contract becomes "
            "voidable at the option of the promisee (S.55). Compensation for breach "
            "under S.73 includes: general damages - loss arising naturally in the "
            "usual course of things from the breach; and special damages - loss the "
            "parties knew at contracting to be likely to result from breach. Remote "
            "or indirect loss is not compensable. Where a contract names a sum to be "
            "paid in case of breach (liquidated damages), the court will award "
            "reasonable compensation not exceeding the named sum, regardless of "
            "whether actual loss is proved (S.74). Penalty clauses are not enforceable "
            "under Indian law; only reasonable pre-estimates of loss."
        ),
        tags=["performance", "breach", "damages", "liquidated damages", "penalty", "time"],
        jurisdiction="India",
        standard_category="contract_law",
        effective_date=date(1872, 9, 1),
        last_amended=date(2018, 8, 9),
        authority_level="statute",
    ),
    StandardEntry(
        id="ica-005",
        standard="IND_CONTRACT",
        topic="Indemnity and Guarantee",
        article="S. 124-128, 145-147",
        title="Contracts of Indemnity and Guarantee",
        content=(
            "A contract of indemnity is a contract by which one party promises to save "
            "the other from loss caused by the promisor's own conduct or that of any "
            "other person (S.124). A contract of guarantee is a promise to perform the "
            "promise or discharge the liability of a third person in case of his default "
            "(S.126). The surety's liability is co-extensive with that of the principal "
            "debtor unless the contract provides otherwise (S.128). A guarantee obtained "
            "by misrepresentation or concealment of material facts is invalid (S.142-143). "
            "A surety is discharged by: variance in terms of the contract between "
            "creditor and principal debtor without surety's consent (S.133); release "
            "or discharge of the principal debtor (S.134); or creditor's act or omission "
            "impairing the surety's eventual remedy (S.139). Contracts with indemnity "
            "and guarantee provisions under Indian law must respect these statutory "
            "protections."
        ),
        tags=["indemnity", "guarantee", "surety", "co-extensive", "discharge"],
        jurisdiction="India",
        standard_category="contract_law",
        effective_date=date(1872, 9, 1),
        last_amended=date(2018, 8, 9),
        authority_level="statute",
    ),
    StandardEntry(
        id="ica-006",
        standard="IND_CONTRACT",
        topic="Agency",
        article="S. 182, 188, 201, 226",
        title="Principal-Agent Relationships",
        content=(
            "An agent is a person employed to do any act for another or to represent "
            "another in dealings with third persons (S.182). No consideration is "
            "necessary to create an agency (S.185). An agent's authority extends to "
            "every lawful thing necessary for doing the act for which the agent is "
            "appointed (S.188). An agent having authority to carry on a business has "
            "authority to do every lawful thing necessary for the purpose, or usually "
            "done in the course of conducting such business (S.188). Agency may be "
            "terminated by revocation, renunciation, completion of business, death or "
            "insanity of principal or agent, or insolvency of principal (S.201). "
            "Contracts entered into through an agent and obligations arising from such "
            "acts are enforced in the same manner as if the contracts had been entered "
            "into and the acts done by the principal in person (S.226)."
        ),
        tags=["agency", "principal", "agent", "authority", "termination"],
        jurisdiction="India",
        standard_category="contract_law",
        effective_date=date(1872, 9, 1),
        last_amended=date(2018, 8, 9),
        authority_level="statute",
    ),

    # ── IT Act 2000 (India) ─────────────────────────────────────
    StandardEntry(
        id="itact-001",
        standard="IT_ACT",
        topic="Electronic Contracts and Signatures",
        article="S. 3-5, 10A",
        title="Legal Recognition of Electronic Records and Contracts",
        content=(
            "The Information Technology Act, 2000 provides legal recognition to "
            "electronic records, electronic signatures, and contracts formed through "
            "electronic means. Section 4: any information in electronic form satisfies "
            "any legal requirement that it be in writing. Section 5: electronic "
            "signatures are given legal validity equivalent to handwritten signatures. "
            "Section 10A: electronic contracts are presumptively enforceable and cannot "
            "be denied validity solely because they were formed electronically. Sections "
            "11-13 establish rules for attribution, acknowledgment, and time/place of "
            "dispatch and receipt of electronic records - critical for determining when "
            "and where an e-contract is formed. All electronic contracts governed by "
            "Indian law must satisfy these provisions."
        ),
        tags=["electronic contracts", "digital signatures", "e-signatures", "validity"],
        jurisdiction="India",
        standard_category="contract_law",
        effective_date=date(2000, 10, 17),
        last_amended=date(2008, 12, 22),
        authority_level="statute",
    ),
    StandardEntry(
        id="itact-002",
        standard="IT_ACT",
        topic="Data Protection and Compensation",
        article="S. 43A",
        title="Compensation for Failure to Protect Sensitive Personal Data",
        content=(
            "Section 43A (effective until May 14, 2027, then superseded by DPDPA 2023): "
            "A body corporate possessing, dealing with, or handling any sensitive "
            "personal data or information in a computer resource that it owns, controls, "
            "or operates is liable to pay compensation to affected persons if it is "
            "negligent in implementing and maintaining reasonable security practices "
            "and procedures, resulting in wrongful loss or wrongful gain. The SPDI Rules, "
            "2011 issued under this section require: publication of a privacy policy; "
            "obtaining consent before collecting sensitive personal data; limiting "
            "collection to lawful purposes connected with the body corporate's functions; "
            "and implementing documented security standards such as ISO 27001. Contracts "
            "involving sensitive personal data processed in India must ensure compliance "
            "with this section and the SPDI Rules."
        ),
        tags=["compensation", "sensitive personal data", "negligence", "SPDI Rules", "security practices"],
        jurisdiction="India",
        standard_category="contract_law",
        effective_date=date(2000, 10, 17),
        last_amended=date(2008, 12, 22),
        authority_level="statute",
    ),
    StandardEntry(
        id="itact-003",
        standard="IT_ACT",
        topic="Cybercrime Offences",
        article="S. 65, 66, 66C-66F",
        title="Computer-Related Offences and Penalties",
        content=(
            "The IT Act criminalizes: tampering with computer source code - knowingly "
            "concealing, destroying, or altering source code (S.65, up to 3 years "
            "imprisonment); computer-related offences including hacking and data theft "
            "(S.66, up to 3 years); identity theft - fraudulent use of another's "
            "electronic signature, password, or unique identification (S.66C, up to "
            "3 years); cheating by personation using computer resources (S.66D, up to "
            "3 years); violation of privacy - capturing or transmitting private images "
            "without consent (S.66E, up to 3 years); and cyber terrorism - threatening "
            "India's sovereignty or security via computer resources (S.66F, life "
            "imprisonment). Contracts involving access to Indian computer systems must "
            "require compliance with these provisions and reporting of suspected offences."
        ),
        tags=["cybercrime", "hacking", "identity theft", "privacy", "penalties"],
        jurisdiction="India",
        standard_category="contract_law",
        effective_date=date(2000, 10, 17),
        last_amended=date(2008, 12, 22),
        authority_level="statute",
    ),
    StandardEntry(
        id="itact-004",
        standard="IT_ACT",
        topic="Intermediary Liability",
        article="S. 79",
        title="Safe Harbour for Intermediaries",
        content=(
            "Section 79 provides safe harbour protection to intermediaries - entities "
            "that receive, store, or transmit electronic records on behalf of others "
            "(ISPs, cloud providers, social media platforms, marketplaces, payment "
            "gateways). An intermediary is not liable for third-party information, data, "
            "or communication link made available or hosted by it if: (1) the "
            "intermediary's function is limited to providing access to a communication "
            "system; (2) the intermediary does not initiate the transmission, select "
            "the receiver, or modify the information; and (3) the intermediary observes "
            "due diligence as prescribed. The safe harbour is lost if the intermediary "
            "conspires, abets, or induces unlawful acts, or fails to comply with "
            "government takedown orders. The IT (Intermediary Guidelines) Rules, 2021 "
            "prescribe detailed due diligence requirements including grievance officers, "
            "content moderation, and compliance reporting."
        ),
        tags=["intermediary", "safe harbour", "due diligence", "liability shield", "takedown"],
        jurisdiction="India",
        standard_category="contract_law",
        effective_date=date(2000, 10, 17),
        last_amended=date(2008, 12, 22),
        authority_level="statute",
    ),
    StandardEntry(
        id="itact-005",
        standard="IT_ACT",
        topic="Breach of Privacy and Confidentiality",
        article="S. 72, 72A",
        title="Disclosure of Personal Information in Breach of Contract",
        content=(
            "Section 72: any person who, in pursuance of powers conferred under the "
            "IT Act, has secured access to any electronic record, book, register, "
            "correspondence, or information and discloses it to another person without "
            "the consent of the person concerned is punishable with imprisonment up to "
            "2 years and/ or fine up to ₹1 lakh. Section 72A: any person (including "
            "an intermediary) who, while providing services under a lawful contract, "
            "has secured access to material containing personal information about "
            "another person and discloses such material without consent or in breach "
            "of the contract, with intent to cause or knowing that disclosure is likely "
            "to cause wrongful loss or gain, is punishable with imprisonment up to 3 "
            "years and/ or fine up to ₹5 lakh. Contracts must include confidentiality "
            "obligations reflecting these statutory prohibitions."
        ),
        tags=["privacy", "confidentiality", "disclosure", "penalties", "intermediary"],
        jurisdiction="India",
        standard_category="contract_law",
        effective_date=date(2000, 10, 17),
        last_amended=date(2008, 12, 22),
        authority_level="statute",
    ),

    # ── CCPA / CPRA ─────────────────────────────────────────────
    StandardEntry(
        id="ccpa-001",
        standard="CCPA",
        topic="Scope and Applicability",
        article="1798.140",
        title="Businesses Covered by the CCPA/CPRA",
        content=(
            "The California Consumer Privacy Act (CCPA), as amended by the California "
            "Privacy Rights Act (CPRA), applies to for-profit businesses that collect "
            "personal information of California residents and meet any one of: annual "
            "gross revenue over $26,625,000; buying, selling, or sharing personal "
            "information of 100,000+ consumers or households per year; or deriving "
            "50%+ of annual revenue from selling or sharing personal information. "
            "Personal information is broadly defined to include any information that "
            "identifies, relates to, or could reasonably be linked to a consumer or "
            "household, including identifiers, commercial information, biometric data, "
            "internet activity, geolocation, audio/visual data, professional/employment "
            "information, education information, and inferences drawn from any of "
            "these. Contracts with businesses meeting these thresholds must include "
            "CCPA-compliant data processing terms."
        ),
        tags=["scope", "thresholds", "personal information", "California", "CPRA"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(2020, 1, 1),
        last_amended=date(2023, 1, 1),
        authority_level="statute",
    ),
    StandardEntry(
        id="ccpa-002",
        standard="CCPA",
        topic="Consumer Rights",
        article="1798.100-1798.125",
        title="Consumer Rights Under CCPA/CPRA",
        content=(
            "California consumers have the right to: know what personal information "
            "is collected, used, shared, or sold (including for the preceding 12 "
            "months and, if retained >12 months, back to January 1, 2022); delete "
            "personal information held by the business and its service providers; "
            "correct inaccurate personal information; opt out of the sale or sharing "
            "of personal information and limit the use of sensitive personal "
            "information; and not be discriminated against for exercising CCPA rights. "
            "Businesses must respond to access and deletion requests within 45 days. "
            "Opt-out mechanisms must include a clear 'Do Not Sell or Share My Personal "
            "Information' link and honor Global Privacy Control (GPC) signals. "
            "Contracts must enable service providers to assist businesses in fulfilling "
            "these rights within statutory timeframes."
        ),
        tags=["consumer rights", "access", "deletion", "opt-out", "GPC", "correction"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(2020, 1, 1),
        last_amended=date(2023, 1, 1),
        authority_level="statute",
    ),
    StandardEntry(
        id="ccpa-003",
        standard="CCPA",
        topic="Cybersecurity Audits",
        article="Regs. Art. 9",
        title="Mandatory Annual Cybersecurity Audits",
        content=(
            "Under final 2025 regulations (effective from OAL approval on September 23, "
            "2025), businesses deriving 50%+ revenue from selling/sharing personal "
            "information OR with >$26.6M revenue that processed PI of 250,000+ "
            "consumers/households or sensitive PI of 50,000+ consumers must undergo "
            "annual independent cybersecurity audits. Audits must assess 18 specified "
            "components including: multi-factor authentication, data encryption, access "
            "controls, penetration testing, vulnerability scanning, data loss prevention, "
            "network monitoring, incident response, disaster recovery, employee training, "
            "and vendor oversight. Audit certifications are due on a phased schedule: "
            "April 1, 2028 (>$100M revenue), April 1, 2029 ($50-100M), and April 1, "
            "2030 (<$50M). Contracts must preserve the right to review vendor audit "
            "results."
        ),
        tags=["cybersecurity audit", "penetration testing", "annual", "phased", "certification"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(2020, 1, 1),
        last_amended=date(2023, 1, 1),
        authority_level="statute",
    ),
    StandardEntry(
        id="ccpa-004",
        standard="CCPA",
        topic="Privacy Risk Assessments",
        article="Regs. Art. 10",
        title="Mandatory Privacy Risk Assessments Before High-Risk Processing",
        content=(
            "Effective January 1, 2026, businesses must conduct and document privacy "
            "risk assessments before engaging in processing presenting 'significant "
            "risk' to consumers. Triggering activities include: selling or sharing "
            "personal information; processing sensitive personal information; using "
            "automated decision-making technology (ADMT) for significant decisions; "
            "profiling employees, applicants, or students; and training AI, facial "
            "recognition, or identity verification systems. Assessments must document: "
            "purpose, data categories, benefits, risks, safeguards, and a go/no-go "
            "decision. They must involve relevant stakeholders, be reviewed every 3 "
            "years (or within 45 days of material changes), and be certified by a "
            "senior executive. First attestations and summaries are due to the CPPA "
            "by April 1, 2028. Contracts involving high-risk processing must address "
            "risk assessment obligations."
        ),
        tags=["risk assessment", "ADMT", "AI", "significant risk", "stakeholder", "attestation"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(2020, 1, 1),
        last_amended=date(2023, 1, 1),
        authority_level="statute",
    ),
    StandardEntry(
        id="ccpa-005",
        standard="CCPA",
        topic="Automated Decision-Making Technology",
        article="Regs. Art. 11",
        title="ADMT Consumer Rights and Obligations",
        content=(
            "Effective January 1, 2027, businesses using ADMT for significant decisions "
            "about consumers (financial services, housing, education, employment, "
            "healthcare) must: provide prominent pre-use notice disclosing ADMT use, "
            "purpose, and consumer rights; offer at least two opt-out methods (one "
            "matching the primary interaction channel); and provide access to the logic, "
            "key parameters, inputs/outputs, and explanation of how the decision was "
            "made in plain language. Opt-in consent is required when ADMT processes "
            "sensitive PI or minors' data. Businesses must stop ADMT use within 15 "
            "business days of opt-out and wait 12 months before resoliciting consent. "
            "Services involving ADMT-based decision-making in contracts must meet these "
            "requirements."
        ),
        tags=["ADMT", "automated decisions", "opt-out", "notice", "explanation"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(2020, 1, 1),
        last_amended=date(2023, 1, 1),
        authority_level="statute",
    ),

    # ── NIST CSF 2.0 ────────────────────────────────────────────
    StandardEntry(
        id="nist-001",
        standard="NIST_CSF",
        topic="Govern Function",
        article="GV",
        title="Governance and Risk Management Foundation",
        content=(
            "The NIST Cybersecurity Framework 2.0 (released February 26, 2024) "
            "introduces the Govern (GV) function as the foundational layer for "
            "organizational cybersecurity risk management. Key subcategories include: "
            "organizational context - understanding mission, stakeholder expectations, "
            "and legal/regulatory requirements (GV.OC); risk management strategy - "
            "defining risk appetite, tolerance, and standardized risk calculation "
            "methods (GV.RM); roles, responsibilities, and authorities - leadership "
            "accountability, appropriate resourcing (GV.RR); policies establishing "
            "and communicating cybersecurity expectations (GV.PO); oversight of "
            "strategy, performance, and continuous improvement (GV.OV); and supply "
            "chain risk management - supplier prioritization, contractual cybersecurity "
            "requirements, and lifecycle monitoring (GV.SC). Contracts should align "
            "vendor governance with the GV function's supply chain subcategories."
        ),
        tags=["governance", "risk management", "supply chain", "policy", "oversight"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2024, 2, 26),
        last_amended=None,
        authority_level="framework",
    ),
    StandardEntry(
        id="nist-002",
        standard="NIST_CSF",
        topic="Identify Function",
        article="ID",
        title="Asset Discovery and Risk Identification",
        content=(
            "The Identify (ID) function covers: asset management - hardware, software, "
            "data, and supplier service inventories with prioritization criteria "
            "(ID.AM); risk assessment - vulnerability identification, threat "
            "intelligence integration, likelihood and impact analysis, risk response "
            "prioritization (ID.RA); and improvement - lessons learned from past "
            "evaluations, security tests, and operational events (ID.IM). Organizations "
            "must maintain current, comprehensive asset inventories and perform risk "
            "assessments at least annually or upon significant changes. Contracts must "
            "require vendors to identify and disclose all information assets involved "
            "in service delivery and to participate in joint risk assessments."
        ),
        tags=["asset management", "risk assessment", "vulnerability", "threat intelligence", "inventory"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2024, 2, 26),
        last_amended=None,
        authority_level="framework",
    ),
    StandardEntry(
        id="nist-003",
        standard="NIST_CSF",
        topic="Protect Function",
        article="PR",
        title="Safeguards and Defensive Measures",
        content=(
            "The Protect (PR) function implements safeguards to prevent or reduce "
            "cybersecurity risk. Key subcategories: identity management, authentication, "
            "and access control aligned with zero-trust principles - least privilege, "
            "separation of duties, and continuous validation (PR.AA); awareness and "
            "training - general and role-specific security education (PR.AT); data "
            "security - protection for data-at-rest, data-in-transit, and data-in-use "
            "in memory (PR.DS, with PR.DS-10 being new in CSF 2.0); platform security - "
            "configuration management, secure SDLC, patch management, and logging "
            "(PR.PS); and technology infrastructure resilience - network protection, "
            "environmental safeguards, and capacity management (PR.IR). Contracts must "
            "require vendors to demonstrate all Protect subcategory controls at levels "
            "commensurate with data sensitivity."
        ),
        tags=["identity", "zero trust", "data security", "data-in-use", "SDLC", "resilience"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2024, 2, 26),
        last_amended=None,
        authority_level="framework",
    ),
    StandardEntry(
        id="nist-004",
        standard="NIST_CSF",
        topic="Detect, Respond, Recover",
        article="DE, RS, RC",
        title="Detection, Incident Response, and Recovery",
        content=(
            "The Detect (DE) function provides continuous monitoring of networks, "
            "physical environments, personnel activity, and external service providers, "
            "with analysis of adverse events through correlation, impact scoping, and "
            "incident declaration (DE.CM, DE.AE). The Respond (RS) function covers "
            "incident management: triage, categorization, prioritization, escalation, "
            "root cause analysis, evidence collection, internal/external notification, "
            "and mitigation through containment and eradication (RS.MA, RS.AN, RS.CO, "
            "RS.MI). The Recover (RC) function ensures restoration: recovery plan "
            "execution with backup integrity verification and stakeholder communications "
            "(RC.RP, RC.CO). NIST CSF 2.0 applies to all organizations, not just "
            "critical infrastructure. Contracts must define incident notification SLAs "
            "aligned with the Respond function and recovery RTO/RPO aligned with the "
            "Recover function."
        ),
        tags=["detection", "monitoring", "incident response", "recovery", "backup", "forensics"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2024, 2, 26),
        last_amended=None,
        authority_level="framework",
    ),

    # ── SOX ─────────────────────────────────────────────────────
    StandardEntry(
        id="sox-001",
        standard="SOX",
        topic="Management Certification",
        article="S. 302",
        title="CEO and CFO Certification of Financial Reports",
        content=(
            "Section 302 of the Sarbanes-Oxley Act requires the CEO and CFO of public "
            "companies to personally certify the accuracy and fairness of quarterly "
            "and annual financial reports. Executives must attest that they are "
            "responsible for establishing and maintaining internal controls over "
            "financial reporting (ICFR) and have evaluated their effectiveness within "
            "90 days prior to the report. They must disclose all significant deficiencies "
            "and material weaknesses in internal controls to the audit committee and "
            "external auditors. Knowingly or willfully certifying false or misleading "
            "financial statements carries criminal penalties. IT service contracts "
            "supporting financial reporting systems must enable the company to assess "
            "and certify ICFR effectiveness, and vendors must report control deficiencies "
            "promptly."
        ),
        tags=["CEO", "CFO", "certification", "ICFR", "internal controls", "financial reporting"],
        jurisdiction="US",
        standard_category="financial_reporting",
        effective_date=date(2002, 7, 30),
        last_amended=None,
        authority_level="statute",
    ),
    StandardEntry(
        id="sox-002",
        standard="SOX",
        topic="Internal Controls Over Financial Reporting",
        article="S. 404",
        title="Management Assessment and Auditor Attestation of ICFR",
        content=(
            "Section 404(a) requires management to establish, maintain, and annually "
            "assess the effectiveness of internal controls over financial reporting "
            "(ICFR). Documentation is mandatory - insufficient documentation itself "
            "is considered a material weakness. Section 404(b) requires the independent "
            "external auditor to attest to and report on management's assessment of "
            "ICFR effectiveness. IT General Controls (ITGCs) form the foundational "
            "layer supporting ICFR: access controls (RBAC, least privilege, MFA, "
            "segregation of duties, regular access reviews); change management (formal "
            "approval workflows, testing before production, documented change history, "
            "separation of dev and production); data backup and recovery (regular tested "
            "backups, off-site storage, restore testing); system monitoring and audit "
            "logging (centralized tamper-proof logs); and patch and vulnerability "
            "management (timely patching, scanning, penetration testing). Contracts "
            "with IT vendors supporting financial systems must include these ITGCs."
        ),
        tags=["ICFR", "ITGC", "audit", "access controls", "change management", "SOX 404"],
        jurisdiction="US",
        standard_category="financial_reporting",
        effective_date=date(2002, 7, 30),
        last_amended=None,
        authority_level="statute",
    ),
    StandardEntry(
        id="sox-003",
        standard="SOX",
        topic="Record Retention and Penalties",
        article="S. 802, 906",
        title="Document Retention and Criminal Penalties",
        content=(
            "Section 802 establishes criminal penalties for altering, destroying, "
            "mutilating, concealing, or falsifying records, documents, or tangible "
            "objects with the intent to impede, obstruct, or influence a federal "
            "investigation or bankruptcy proceeding. Audit and review work papers must "
            "be retained for at least 5 years. Section 906 imposes criminal penalties "
            "(fines up to $5 million and/ or imprisonment up to 20 years) for CEOs "
            "and CFOs who knowingly or willfully certify false or misleading financial "
            "reports. Section 409 requires near-real-time disclosure of material changes "
            "in financial condition or operations. Contracts involving financial "
            "recordkeeping or reporting must include data retention obligations aligned "
            "with SOX retention periods and prohibit unauthorized destruction of "
            "financial records."
        ),
        tags=["record retention", "penalties", "destruction", "disclosure", "criminal"],
        jurisdiction="US",
        standard_category="financial_reporting",
        effective_date=date(2002, 7, 30),
        last_amended=None,
        authority_level="statute",
    ),

    # ── FedRAMP ─────────────────────────────────────────────────
    StandardEntry(
        id="fedramp-001",
        standard="FedRAMP",
        topic="Authorization Baselines",
        article="NIST SP 800-53 Rev. 5",
        title="FedRAMP Impact Levels and Control Requirements",
        content=(
            "The Federal Risk and Authorization Management Program (FedRAMP) "
            "standardizes security assessment and authorization for cloud services "
            "used by US federal agencies, built on NIST SP 800-53 Rev. 5 controls. "
            "Three baseline impact levels: LI-SaaS (Tailored Low: ~156 controls, "
            "public-facing, no PII beyond login credentials); Low (~156 controls, "
            "minimal sensitive data, limited adverse impact if breached); Moderate "
            "(~323 controls, Controlled Unclassified Information (CUI), PII, mission "
            "data); and High (~421 controls, highly sensitive data - law enforcement, "
            "PHI, financial, critical infrastructure). Required authorization "
            "documentation includes the System Security Plan (SSP), Security Assessment "
            "Plan (SAP), Security Assessment Report (SAR), and Plan of Action & "
            "Milestones (POA&M). Contracts with cloud service providers handling federal "
            "data must require FedRAMP authorization at the appropriate impact level."
        ),
        tags=["FedRAMP", "NIST 800-53", "impact levels", "CUI", "authorization", "SSP"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2023, 12, 8),
        last_amended=None,
        authority_level="regulation",
    ),
    StandardEntry(
        id="fedramp-002",
        standard="FedRAMP",
        topic="Access Control and Authentication",
        article="AC, IA Families",
        title="Identity, Authentication, and Access Controls",
        content=(
            "FedRAMP mandates rigorous access controls aligned with NIST SP 800-53 "
            "families AC and IA: multi-factor authentication (MFA) is required for "
            "all user access; phishing-resistant MFA is mandatory for the High "
            "baseline; conditional access policies and least privilege enforcement; "
            "separation of duties; wireless access hardening at High; in-person "
            "identity proofing at High; and cached authenticator controls at High. "
            "Access must be revoked within mandated timeframes upon personnel "
            "termination or role change. Contracts must specify MFA requirements, "
            "access provisioning/deprovisioning procedures, and identity proofing "
            "standards commensurate with the data sensitivity level."
        ),
        tags=["MFA", "phishing-resistant", "authentication", "least privilege", "identity"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2023, 12, 8),
        last_amended=None,
        authority_level="regulation",
    ),
    StandardEntry(
        id="fedramp-003",
        standard="FedRAMP",
        topic="System and Communications Protection",
        article="SC Family",
        title="Encryption, Isolation, and Transmission Security",
        content=(
            "FedRAMP requires FIPS-validated encryption for data-at-rest (SC-28) and "
            "data-in-transit (SC-8) at all impact levels. The High baseline adds: "
            "security function isolation, data exfiltration prevention, fail-safe "
            "mechanisms, and encrypted traffic visibility. All cryptography must use "
            "FIPS 140-2/140-3 validated modules. Contracts must specify: FIPS-validated "
            "cryptographic standards, encryption coverage (at-rest, in-transit, and "
            "potentially in-use for High), key management responsibilities, and "
            "certificate validation procedures. Cryptographic key lifecycle management "
            "must be documented and auditable."
        ),
        tags=["FIPS", "encryption", "data-at-rest", "data-in-transit", "isolation", "exfiltration"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2023, 12, 8),
        last_amended=None,
        authority_level="regulation",
    ),
    StandardEntry(
        id="fedramp-004",
        standard="FedRAMP",
        topic="Continuous Monitoring",
        article="CA, RA, SI Families",
        title="Ongoing Assessment and Vulnerability Management",
        content=(
            "Post-authorization continuous monitoring (ConMon) requires: monthly "
            "vulnerability scans and reporting; incident reporting to sponsoring "
            "agencies and the FedRAMP PMO; monthly security posture reports; annual "
            "assessments by an accredited Third-Party Assessment Organization (3PAO); "
            "and Red Team exercises at least annually for Moderate and High impact "
            "systems under Rev. 5. Vulnerability remediation must be tracked and "
            "prioritized centrally; public disclosure programs for vulnerability "
            "reporting are required (RA-5(11)). Contracts must define ConMon "
            "obligations, vulnerability scan schedules, incident reporting timeframes "
            "(typically within 1 hour for major incidents), and 3PAO access rights."
        ),
        tags=["continuous monitoring", "ConMon", "3PAO", "vulnerability", "Red Team", "incident"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2023, 12, 8),
        last_amended=None,
        authority_level="regulation",
    ),
    StandardEntry(
        id="fedramp-005",
        standard="FedRAMP",
        topic="Supply Chain Risk Management",
        article="SR Family",
        title="Software Supply Chain and SBOM Requirements",
        content=(
            "FedRAMP Rev. 5 introduces the Supply Chain Risk Management (SR) family, "
            "requiring: tamper resistance throughout the software development lifecycle; "
            "third-party service and product risk management; Software Bill of Materials "
            "(SBOM) for all components; Secure Software Development Framework (SSDF) "
            "attestation per NIST SP 800-218; CI/CD pipeline security controls and "
            "artifact validation; and inspection of software and systems for potential "
            "tampering. The FedRAMP program has proposed additional software supply "
            "chain rules through RFCs, including enhanced SBOM requirements. Contracts "
            "with CSPs serving federal agencies must include SBOM delivery, SSDF "
            "conformance, and supply chain transparency obligations."
        ),
        tags=["supply chain", "SBOM", "SSDF", "tamper resistance", "CI/CD", "software"],
        jurisdiction="US",
        standard_category="security",
        effective_date=date(2023, 12, 8),
        last_amended=None,
        authority_level="regulation",
    ),

    # ── FERPA ───────────────────────────────────────────────────
    StandardEntry(
        id="ferpa-001",
        standard="FERPA",
        topic="Student Education Records",
        article="20 USC 1232g",
        title="Protection of Education Records and PII",
        content=(
            "The Family Educational Rights and Privacy Act (FERPA) protects the "
            "privacy of student education records at institutions receiving U.S. "
            "Department of Education funding. Education records include any record "
            "directly related to a student and maintained by the institution or a "
            "party acting on its behalf. Students and parents have three core rights: "
            "inspect and review records within 45 days, request amendment of inaccurate "
            "records with a right to a hearing if denied, and provide written consent "
            "before disclosure of personally identifiable information (PII) from "
            "records. PII includes direct identifiers (name, SSN, student ID) and "
            "indirect identifiers that alone or in combination would allow a reasonable "
            "person in the school community to identify the student. Contracts with "
            "ed-tech vendors and education service providers must recognize FERPA "
            "restrictions on use and re-disclosure."
        ),
        tags=["education records", "student privacy", "PII", "consent", "parental rights"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(1974, 8, 21),
        last_amended=date(2011, 12, 9),
        authority_level="statute",
    ),
    StandardEntry(
        id="ferpa-002",
        standard="FERPA",
        topic="School Official Exception",
        article="34 CFR 99.31",
        title="Third-Party Vendors as School Officials",
        content=(
            "FERPA permits disclosure of education records without consent to 'school "
            "officials' with a 'legitimate educational interest.' This exception is "
            "the primary basis for engaging third-party vendors (ed-tech providers, "
            "cloud storage, data analytics, LMS platforms). To qualify, the institution "
            "must: define 'school official' in its annual FERPA notice; include the "
            "vendor within that definition; establish the 'legitimate educational "
            "interest' for the vendor's access; and maintain direct control over the "
            "education records even when held by the vendor. Written agreements must: "
            "specify the vendor's permitted uses; require the vendor to use PII only "
            "for authorized purposes; prohibit re-disclosure; include data breach "
            "notification procedures; and require return or destruction of records "
            "upon contract termination. Contracts must explicitly invoke the school "
            "official exception."
        ),
        tags=["school official", "third-party", "vendor", "ed-tech", "legitimate interest"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(1974, 8, 21),
        last_amended=date(2011, 12, 9),
        authority_level="statute",
    ),
    StandardEntry(
        id="ferpa-003",
        standard="FERPA",
        topic="Directory Information and Exceptions",
        article="34 CFR 99.37",
        title="Directory Information Opt-Out and Disclosure Exceptions",
        content=(
            "Institutions may designate certain categories as 'directory information' "
            "- typically name, address, phone, email, dates of attendance, degrees, "
            "awards, and photographs - and disclose it without consent, provided they "
            "give annual public notice and allow students/parents a reasonable time to "
            "opt out. Social Security Numbers are never directory information. "
            "Additional consent exceptions include: transfer to another school where "
            "the student intends to enroll; financial aid administration; audits and "
            "evaluations by authorized officials; studies conducted by organizations "
            "under written agreement; accrediting organizations; judicial orders or "
            "subpoenas (with reasonable effort to notify student); health/safety "
            "emergencies; and de-identified records. Contracts must respect the "
            "directory information framework and opt-out rights."
        ),
        tags=["directory information", "opt-out", "exceptions", "disclosure", "emergency"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(1974, 8, 21),
        last_amended=date(2011, 12, 9),
        authority_level="statute",
    ),

    # ── GLBA ────────────────────────────────────────────────────
    StandardEntry(
        id="glba-001",
        standard="GLBA",
        topic="Privacy Rule",
        article="Regulation P",
        title="Notice and Opt-Out Requirements for Financial Institutions",
        content=(
            "The Gramm-Leach-Bliley Act Privacy Rule governs how financial institutions "
            "collect and share Nonpublic Personal Information (NPI). Institutions must "
            "provide a 'clear and conspicuous' written privacy notice when a customer "
            "relationship is established and annually thereafter. The notice must "
            "disclose: categories of NPI collected, categories disclosed, affiliated "
            "and nonaffiliated third parties receiving NPI, and how NPI is safeguarded. "
            "Consumers must be given a reasonable opt-out mechanism before NPI is "
            "shared with unaffiliated third parties. Under the FAST Act (2015), annual "
            "notices may be waived if NPI is shared only under limited exceptions and "
            "policies have not changed. Contracts involving NPI must incorporate GLBA "
            "privacy notice and opt-out obligations."
        ),
        tags=["NPI", "privacy notice", "opt-out", "annual notice", "consumer"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(1999, 11, 12),
        last_amended=date(2021, 12, 9),
        authority_level="statute",
    ),
    StandardEntry(
        id="glba-002",
        standard="GLBA",
        topic="Safeguards Rule",
        article="16 CFR Part 314",
        title="Written Information Security Program Requirements",
        content=(
            "The GLBA Safeguards Rule (as amended by the FTC in 2021) requires financial "
            "institutions to develop, implement, and maintain a comprehensive written "
            "information security program. Key mandatory elements: designate a single "
            "Qualified Individual responsible for the program who reports annually to "
            "the board or governing body; conduct a written risk assessment of risks "
            "to customer information across all relevant areas of operation; implement "
            "and periodically review access controls with monitoring and logging of "
            "authorized user activity; encrypt customer information at rest and in "
            "transit (or use compensating controls if encryption is infeasible); "
            "implement multi-factor authentication for all access to customer information "
            "systems; conduct annual penetration testing and vulnerability scans every "
            "six months; provide security awareness training for all employees and "
            "specialized training for security personnel; assess service providers and "
            "include contractual safeguards; implement a written incident response plan; "
            "and dispose of customer information no later than 2 years after last use. "
            "Small institutions (<5,000 consumers) are exempt from certain requirements."
        ),
        tags=["safeguards", "risk assessment", "MFA", "encryption", "penetration testing", "training"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(1999, 11, 12),
        last_amended=date(2021, 12, 9),
        authority_level="statute",
    ),
    StandardEntry(
        id="glba-003",
        standard="GLBA",
        topic="Service Provider Oversight",
        article="16 CFR 314.4",
        title="Vendor Management and Contractual Safeguards",
        content=(
            "Financial institutions must take reasonable steps to select and retain "
            "service providers capable of maintaining appropriate safeguards for "
            "customer information. Contracts with service providers must require "
            "implementation and maintenance of such safeguards. Institutions must "
            "periodically assess service providers' adequacy based on the risk "
            "presented and the continued appropriateness of their safeguards. This "
            "creates a cascading obligation: not only must the institution itself "
            "be GLBA-compliant, but all its vendors handling NPI must also meet "
            "GLBA Safeguards Rule requirements. Contracts must include: data "
            "protection obligations; audit rights; security incident notification "
            "timelines; and cooperation obligations for regulatory examinations. "
            "Service providers that fail to maintain adequate safeguards expose both "
            "themselves and the institution to enforcement action."
        ),
        tags=["service provider", "vendor", "oversight", "safeguards", "assessment", "audit"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(1999, 11, 12),
        last_amended=date(2021, 12, 9),
        authority_level="statute",
    ),
    StandardEntry(
        id="glba-004",
        standard="GLBA",
        topic="Breach Notification",
        article="FTC Rule",
        title="Notification of Unauthorized Access to Customer Information",
        content=(
            "Under the FTC's GLBA breach notification rule, financial institutions must "
            "notify the FTC as soon as possible and no later than 30 days after "
            "discovering a breach involving unencrypted customer information of 500 "
            "or more consumers. A 'breach' is defined as unauthorized acquisition of "
            "unencrypted customer information (or encrypted information where the "
            "encryption key has also been compromised) that is reasonably likely to "
            "cause substantial consumer harm or inconvenience. Notification must be "
            "made electronically through the FTC's designated portal. Contracts with "
            "service providers must require notification to the institution within a "
            "shorter timeframe (commonly 48-72 hours) to enable the institution to "
            "meet its own 30-day deadline. Institutions may also face state-specific "
            "breach notification laws with shorter deadlines. Penalties include up to "
            "$100,000 per violation for institutions and $10,000 per violation for "
            "officers/directors personally."
        ),
        tags=["breach", "notification", "FTC", "30 days", "500 threshold", "penalties"],
        jurisdiction="US",
        standard_category="data_protection",
        effective_date=date(1999, 11, 12),
        last_amended=date(2021, 12, 9),
        authority_level="statute",
    ),

    # ── US Restatement (Second) of Contracts ─────────────────────
    StandardEntry(
        id="rest-001",
        standard="US_RESTATEMENT",
        topic="Contract Formation",
        article="§§ 17, 24, 50, 61",
        title="Mutual Assent: Offer, Acceptance, and Formation of a Bargain",
        content=(
            "Section 17: Formation of a contract requires a bargain in which there is "
            "a manifestation of mutual assent to the exchange and a consideration. "
            "Section 24: An offer is the manifestation of willingness to enter into a "
            "bargain, so made as to justify another person in understanding that his "
            "assent to that bargain is invited and will conclude it. Section 26: A "
            "manifestation of willingness to enter into a bargain is not an offer if "
            "the person to whom it is addressed knows or has reason to know that the "
            "person making it does not intend to conclude a bargain until he has made "
            "a further manifestation of assent. Section 35: An offer gives to the "
            "offeree a continuing power to complete the manifestation of mutual assent "
            "by acceptance. Section 36: The offeree's power of acceptance may be "
            "terminated by rejection or counter-offer, lapse of time, revocation by "
            "the offeror, or death or incapacity of either party. Section 50: "
            "Acceptance by performance requires that at least part of what the offer "
            "requests be performed or tendered; acceptance by promise requires that "
            "the offeree complete every act essential to the making of the promise. "
            "Section 61: An acceptance which requests a change or addition to terms "
            "is not invalidated unless the acceptance is made to depend on assent to "
            "the changed or added terms. US contract law always applies as the baseline "
            "for contracts governed by US state law."
        ),
        tags=["formation", "offer", "acceptance", "mutual assent", "bargain", "revocation"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1981, 5, 19),
        last_amended=None,
        authority_level="common_law",
    ),
    StandardEntry(
        id="rest-002",
        standard="US_RESTATEMENT",
        topic="Consideration",
        article="§§ 71, 73, 79, 81",
        title="The Doctrine of Consideration and Bargained-For Exchange",
        content=(
            "Section 71: To constitute consideration, a performance or a return promise "
            "must be bargained for. A performance or return promise is bargained for if "
            "it is sought by the promisor in exchange for his promise and is given by "
            "the promisee in exchange for that promise. The performance may consist of "
            "an act other than a promise, a forbearance, or the creation, modification, "
            "or destruction of a legal relation. Section 73: Performance of a legal duty "
            "owed to a promisor which is neither doubtful nor the subject of honest "
            "dispute is not consideration (the pre-existing duty rule). Section 77: A "
            "promise is not consideration if the promisor reserves a choice of "
            "alternative performances unless each alternative would have been "
            "consideration. Section 79: If the requirement of consideration is met, "
            "there is no additional requirement of equivalence in the values exchanged "
            "or mutuality of obligation. Section 81: The fact that what is bargained "
            "for does not of itself induce the making of a promise does not prevent it "
            "from being consideration. Under US common law, contracts generally require "
            "consideration to be enforceable, unlike civil law systems."
        ),
        tags=["consideration", "bargained-for", "pre-existing duty", "mutuality", "exchange"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1981, 5, 19),
        last_amended=None,
        authority_level="common_law",
    ),
    StandardEntry(
        id="rest-003",
        standard="US_RESTATEMENT",
        topic="Breach and Damages",
        article="§§ 344, 346, 347, 349-352, 356",
        title="Breach of Contract and the Measure of Damages",
        content=(
            "Section 344: Judicial remedies serve three principal interests: the "
            "expectation interest - putting the injured party in as good a position as "
            "if the contract had been performed; the reliance interest - reimbursing "
            "for loss caused by reliance on the contract; and the restitution interest "
            "- restoring any benefit conferred on the other party. Section 346: The "
            "injured party has a right to damages for any breach unless the claim has "
            "been suspended or discharged. Section 347: Expectation damages are measured "
            "by (a) loss in value of the other party's performance, plus (b) incidental "
            "and consequential loss, less (c) any cost avoided by not having to perform. "
            "Section 349: When expectation damages cannot be proved with reasonable "
            "certainty, the injured party may recover reliance damages. Section 350: "
            "Damages are not recoverable for loss that the injured party could have "
            "avoided without undue risk, burden, or humiliation (mitigation). Section "
            "351: Damages are not recoverable for loss that the party in breach did "
            "not have reason to foresee as a probable result of the breach at the time "
            "of contracting. Section 352: Damages are not recoverable beyond an amount "
            "that the evidence permits to be established with reasonable certainty. "
            "Section 356: Liquidated damages are enforceable only at an amount that is "
            "reasonable in light of anticipated or actual loss; a term fixing "
            "unreasonably large liquidated damages is unenforceable as a penalty."
        ),
        tags=["breach", "expectation damages", "reliance", "restitution", "mitigation", "foreseeability", "liquidated damages", "penalty"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1981, 5, 19),
        last_amended=None,
        authority_level="common_law",
    ),
    StandardEntry(
        id="rest-004",
        standard="US_RESTATEMENT",
        topic="Contract Defenses",
        article="§§ 12-16, 20, 151-177, 208",
        title="Voidability: Capacity, Misunderstanding, Mistake, Misrepresentation, Duress, and Unconscionability",
        content=(
            "Incapacity (§§ 12-16): Contracts with minors, mentally incapacitated "
            "persons, or intoxicated persons are generally voidable at the option of "
            "the incapacitated party. Section 20: There is no manifestation of mutual "
            "assent if the parties attach materially different meanings to the agreement "
            "and neither party knows or both parties know of the difference. Mistake "
            "(§§ 151-154): A mutual mistake of material fact existing at the time of "
            "contracting makes the contract voidable by the adversely affected party. "
            "Unilateral mistake generally does not provide relief unless the other party "
            "knew or had reason to know of the mistake. Misrepresentation (§§ 159-164): "
            "A fraudulent or material misrepresentation upon which the other party is "
            "justified in relying makes the contract voidable. Duress (§§ 174-176): "
            "A contract induced by an improper threat that leaves the victim no "
            "reasonable alternative is voidable. Undue Influence (§ 177): A contract "
            "induced by unfair persuasion of a party under the domination of another "
            "or in a confidential relationship is voidable. Section 208: If a contract "
            "or term is unconscionable at the time the contract is made, a court may "
            "refuse to enforce the contract, enforce the remainder without the "
            "unconscionable term, or limit application of the unconscionable term to "
            "avoid an unconscionable result."
        ),
        tags=["defenses", "capacity", "mistake", "misrepresentation", "duress", "undue influence", "unconscionability"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1981, 5, 19),
        last_amended=None,
        authority_level="common_law",
    ),
    StandardEntry(
        id="rest-005",
        standard="US_RESTATEMENT",
        topic="Promissory Estoppel and Reliance",
        article="§§ 87, 90",
        title="Contracts Without Consideration: Promissory Estoppel and Option Contracts",
        content=(
            "Section 90: A promise which the promisor should reasonably expect to induce "
            "action or forbearance on the part of the promisee or a third person and "
            "which does induce such action or forbearance is binding if injustice can "
            "be avoided only by enforcement of the promise. The remedy granted for "
            "breach may be limited as justice requires. This is the doctrine of "
            "promissory estoppel - it provides a basis for enforcing promises even in "
            "the absence of consideration. Section 87: An offer is binding as an option "
            "contract if it (a) is in writing and signed by the offeror, recites a "
            "purported consideration for the making of the offer, and proposes an "
            "exchange on fair terms within a reasonable time; or (b) is made irrevocable "
            "by statute; or (c) the offeror should reasonably expect the offeree to "
            "rely on the offer to their detriment and such reliance actually occurs. "
            "Promissory estoppel is frequently applied in the commercial context: "
            "construction bids, franchise agreements, and negotiated but unsigned "
            "agreements. NDAs and preliminary agreements may be partially enforceable "
            "under this doctrine even if the main contract is not fully formed."
        ),
        tags=["promissory estoppel", "reliance", "option contract", "consideration substitute", "detrimental reliance"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1981, 5, 19),
        last_amended=None,
        authority_level="common_law",
    ),
    StandardEntry(
        id="rest-006",
        standard="US_RESTATEMENT",
        topic="Remedies and Performance",
        article="§§ 234-243, 345-377",
        title="Performance, Conditions, and Specific Remedies",
        content=(
            "Conditions (§§ 224-230): A condition is an event, not certain to occur, "
            "which must occur before performance of a duty becomes due, unless its "
            "non-occurrence is excused. Conditions precedent must be strictly satisfied; "
            "conditions subsequent terminate an existing duty. The doctrine of "
            "substantial performance (§ 237): a party who has substantially performed "
            "can enforce the contract despite minor deficiencies, but must compensate "
            "for the incomplete or defective performance. Material Breach (§ 241): "
            "A breach is material if it deprives the injured party of the benefit "
            "reasonably expected, considering the extent of the benefit deprived, "
            "adequacy of damages, likelihood of cure, and good faith of the breaching "
            "party. Only a material breach discharges the other party's duties. "
            "Specific Performance (§ 359): Specific performance or an injunction will "
            "be granted only where damages are inadequate - typically for unique goods, "
            "real property, or rare intangibles. Restitution (§ 370-377): A party is "
            "entitled to restitution for any benefit conferred on the other party by "
            "way of part performance or reliance if the contract is unenforceable or "
            "the other party has committed a material breach. The Statute of Frauds "
            "(§ 110): Certain contracts must be evidenced by a signed writing - "
            "including contracts not performable within one year, suretyship agreements, "
            "and contracts for the sale of land."
        ),
        tags=["conditions", "substantial performance", "material breach", "specific performance", "restitution", "Statute of Frauds"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1981, 5, 19),
        last_amended=None,
        authority_level="common_law",
    ),

    # ── UCC Article 2 (Sale of Goods) ─────────────────────────────
    StandardEntry(
        id="ucc-001",
        standard="US_UCC",
        topic="Scope and Formation",
        article="§§ 2-102, 2-105, 2-204, 2-206",
        title="Scope of Article 2 and Contract Formation for Goods",
        content=(
            "Section 2-102: Article 2 applies to transactions in goods. Section 2-105: "
            "Goods are all things movable at the time of identification to the contract, "
            "excluding money, investment securities, and choses in action. Article 2 "
            "governs sale of goods regardless of whether the parties are merchants. "
            "Section 2-204: A contract for sale of goods may be made in any manner "
            "sufficient to show agreement, including conduct by both parties which "
            "recognizes the existence of a contract. Even if one or more terms are "
            "left open, a contract does not fail for indefiniteness if the parties "
            "have intended to make a contract and there is a reasonably certain basis "
            "for giving an appropriate remedy. Section 2-206: Unless otherwise "
            "unambiguously indicated by the language or circumstances, an offer to "
            "make a contract shall be construed as inviting acceptance in any manner "
            "and by any medium reasonable in the circumstances. An order or offer to "
            "buy goods for prompt or current shipment shall be construed as inviting "
            "acceptance either by a prompt promise to ship or by prompt shipment of "
            "conforming or non-conforming goods. Shipment of non-conforming goods does "
            "not constitute acceptance if the seller seasonably notifies the buyer "
            "that the shipment is offered only as an accommodation to the buyer. "
            "Article 2 displaces the common law for goods transactions."
        ),
        tags=["goods", "formation", "acceptance", "accommodation", "indefiniteness", "merchants"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1952, 1, 1),
        last_amended=date(2022, 12, 31),
        authority_level="statute",
    ),
    StandardEntry(
        id="ucc-002",
        standard="US_UCC",
        topic="Firm Offers and Battle of the Forms",
        article="§§ 2-205, 2-207, 2-209",
        title="Merchant's Firm Offer, Battle of the Forms, and Modification",
        content=(
            "Section 2-205 (Merchant's Firm Offer): An offer by a merchant to buy or "
            "sell goods in a signed writing which by its terms gives assurance that it "
            "will be held open is not revocable for lack of consideration during the "
            "time stated, or if no time is stated, for a reasonable time - but in no "
            "event may such irrevocability exceed three months. Section 2-207 (Battle "
            "of the Forms): A definite and seasonable expression of acceptance operates "
            "as an acceptance even if it contains terms additional to or different from "
            "those offered, unless acceptance is expressly made conditional on assent "
            "to the additional or different terms. Between merchants, additional terms "
            "become part of the contract unless: (a) the offer expressly limits "
            "acceptance to its terms; (b) they materially alter the contract; or (c) "
            "notification of objection has already been given or is given within a "
            "reasonable time. If the parties' conduct recognizes a contract but their "
            "writings do not agree, the contract consists of terms on which the "
            "writings agree together with UCC gap-filler provisions. Section 2-209: "
            "An agreement modifying a contract for the sale of goods needs no "
            "consideration to be binding, but must satisfy the Statute of Frauds if "
            "the contract as modified is within its provisions."
        ),
        tags=["firm offer", "battle of the forms", "merchant", "material alteration", "modification", "gap fillers"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1952, 1, 1),
        last_amended=date(2022, 12, 31),
        authority_level="statute",
    ),
    StandardEntry(
        id="ucc-003",
        standard="US_UCC",
        topic="Warranties",
        article="§§ 2-312, 2-313, 2-314, 2-315, 2-316",
        title="Express and Implied Warranties and Their Disclaimer",
        content=(
            "Section 2-312: In a contract for sale, the seller warrants that title "
            "conveyed is good, transfer is rightful, and goods are delivered free of "
            "any security interest or lien of which the buyer lacks knowledge. "
            "Section 2-313: Express warranties are created by any affirmation of fact "
            "or promise made by the seller to the buyer relating to the goods that "
            "becomes part of the basis of the bargain, any description of the goods, "
            "and any sample or model made part of the basis of the bargain. No formal "
            "words or specific intent to warrant is necessary. Seller's opinion or "
            "commendation (puffery) does not create a warranty. Section 2-314: A "
            "warranty of merchantability is implied in every sale by a merchant of "
            "goods of that kind. Goods must pass without objection in the trade, be "
            "of fair average quality, be fit for ordinary purposes, and conform to "
            "promises on the label. Section 2-315: A warranty of fitness for a "
            "particular purpose arises where the seller at the time of contracting has "
            "reason to know the buyer's particular purpose and that the buyer is relying "
            "on the seller's skill to select suitable goods. Section 2-316: Express "
            "warranties cannot be disclaimed. Implied warranties may be disclaimed: "
            "merchantability disclaimer must mention 'merchantability' and be "
            "conspicuous; fitness disclaimer must be in writing and conspicuous. "
            "Implied warranties can also be excluded by 'as is' or 'with all faults' "
            "language, or where the buyer has examined or refused to examine the goods."
        ),
        tags=["warranties", "express warranty", "merchantability", "fitness", "disclaimer", "as is", "puffery"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1952, 1, 1),
        last_amended=date(2022, 12, 31),
        authority_level="statute",
    ),
    StandardEntry(
        id="ucc-004",
        standard="US_UCC",
        topic="Performance and Breach",
        article="§§ 2-508, 2-601, 2-602, 2-608-2-612",
        title="Performance, Perfect Tender, Cure, Rejection, and Repudiation",
        content=(
            "Section 2-601 (Perfect Tender Rule): If goods or tender of delivery fail "
            "in any respect to conform to the contract, the buyer may (a) reject the "
            "whole, (b) accept the whole, or (c) accept any commercial unit or units "
            "and reject the rest. Section 2-508 (Cure): The seller may cure a "
            "non-conforming tender if the time for performance has not yet expired, "
            "or if the seller had reasonable grounds to believe the tender would be "
            "acceptable, the seller may have a further reasonable time to substitute "
            "a conforming tender. Section 2-602: Rejection must be within a reasonable "
            "time after delivery or tender and the buyer must seasonably notify the "
            "seller. Section 2-608: The buyer may revoke acceptance of a lot or "
            "commercial unit whose non-conformity substantially impairs its value if "
            "the buyer accepted it on the reasonable assumption that its non-conformity "
            "would be cured and it has not been, or if the non-conformity was difficult "
            "to discover before acceptance. Section 2-609: When reasonable grounds for "
            "insecurity arise, either party may demand adequate assurance of due "
            "performance and suspend their own performance until they receive it. "
            "Section 2-610: If a party repudiates the contract with respect to a "
            "performance not yet due, the aggrieved party may await performance, resort "
            "to any remedy, or suspend their own performance. Section 2-612: In "
            "installment contracts, the buyer may reject a non-conforming installment "
            "only if it substantially impairs the value of that installment and cannot "
            "be cured."
        ),
        tags=["perfect tender", "cure", "rejection", "revocation", "adequate assurance", "repudiation", "installment"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1952, 1, 1),
        last_amended=date(2022, 12, 31),
        authority_level="statute",
    ),
    StandardEntry(
        id="ucc-005",
        standard="US_UCC",
        topic="Buyer's Remedies",
        article="§§ 2-711-2-717",
        title="Remedies for Buyer: Cover, Market Damages, Specific Performance, and Deduction",
        content=(
            "Section 2-711: Where the seller fails to deliver, repudiates, or the buyer "
            "rightfully rejects or revokes acceptance, the buyer may cancel and recover "
            "the price paid. Section 2-712 (Cover): The buyer may purchase substitute "
            "goods in good faith and without unreasonable delay. Damages are the "
            "difference between the cost of cover and the contract price, plus "
            "incidental and consequential damages, less expenses saved. Section 2-713 "
            "(Market Damages): The measure is the difference between the market price "
            "at the time the buyer learned of the breach and the contract price, plus "
            "incidental and consequential damages. Section 2-714: Where the buyer has "
            "accepted non-conforming goods, damages for breach of warranty are the "
            "difference between the value of goods as accepted and the value they would "
            "have had if as warranted. Section 2-715: Incidental damages include "
            "expenses reasonably incurred in inspection, receipt, transportation, care "
            "and custody of rejected goods, and cover. Consequential damages include "
            "any loss resulting from the buyer's requirements of which the seller had "
            "reason to know at the time of contracting, and injury to person or property "
            "proximately resulting from any breach. Section 2-716: Specific performance "
            "may be decreed where goods are unique or in other proper circumstances. "
            "Section 2-717: The buyer on notifying the seller may deduct all or part "
            "of damages from any part of the price still due under the same contract."
        ),
        tags=["buyer remedies", "cover", "market damages", "consequential damages", "specific performance", "deduction"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1952, 1, 1),
        last_amended=date(2022, 12, 31),
        authority_level="statute",
    ),
    StandardEntry(
        id="ucc-006",
        standard="US_UCC",
        topic="Seller's Remedies",
        article="§§ 2-702-2-710",
        title="Remedies for Seller: Price, Resale, Market Damages, and Lost Volume",
        content=(
            "Section 2-702: Where the buyer is insolvent, the seller may refuse delivery "
            "except for cash and reclaim goods if the buyer received them on credit while "
            "insolvent. Section 2-703: Upon buyer's breach, the seller may withhold "
            "delivery, stop delivery, resell and recover damages, recover damages for "
            "non-acceptance, recover the price, cancel, and recover incidental damages. "
            "Section 2-706 (Resale): The seller may resell the goods and recover the "
            "difference between the resale price and the contract price, plus incidental "
            "damages, less expenses saved. Resale must be commercially reasonable. "
            "Section 2-708 (Market Damages): The measure is the difference between the "
            "market price at the time and place for tender and the unpaid contract price, "
            "plus incidental damages. For lost volume sellers - where the market measure "
            "is inadequate - the seller recovers the profit (including reasonable "
            "overhead) the seller would have made from full performance. Section 2-709 "
            "(Action for the Price): Available when the buyer has accepted the goods, "
            "conforming goods are lost or damaged after risk of loss has passed, or "
            "goods identified to the contract cannot reasonably be resold. Section "
            "2-710: Incidental damages to an aggrieved seller include commercially "
            "reasonable charges incurred in stopping delivery, transportation, care "
            "and custody of goods, and resale commissions. Section 2-725: The statute "
            "of limitations for breach of a sales contract is four years."
        ),
        tags=["seller remedies", "resale", "lost volume seller", "action for price", "incidental damages", "statute of limitations"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1952, 1, 1),
        last_amended=date(2022, 12, 31),
        authority_level="statute",
    ),

    # ── Delaware General Corporation Law (DGCL) ──────────────────
    StandardEntry(
        id="dgcl-001",
        standard="US_DGCL",
        topic="Corporate Formation and Powers",
        article="§§ 101-102, 122",
        title="Incorporation, Certificate Provisions, and Corporate Powers",
        content=(
            "Section 101: A corporation may be formed by any person or entity for any "
            "lawful purpose by filing a certificate of incorporation with the Delaware "
            "Secretary of State. Section 102(a): The certificate of incorporation must "
            "set forth the corporate name (containing an appropriate ending such as "
            "'Inc.' or 'Corp.'), the registered office address and registered agent in "
            "Delaware, the nature of business (a general 'any lawful act or activity' "
            "statement suffices), the authorized capital stock, and incorporator details. "
            "Section 102(b): The certificate may optionally include: provisions managing "
            "the business and regulating the corporation's powers (b)(1); supermajority "
            "voting requirements (b)(4); and exculpation clauses eliminating directors' "
            "personal monetary liability for breach of fiduciary duty, except for duty "
            "of loyalty violations, acts not in good faith, unlawful distributions, or "
            "improper personal benefit (b)(7). Section 122: Every corporation has "
            "automatic powers including: perpetual succession (1); sue and be sued (2); "
            "own and transfer property (4); adopt and amend bylaws (6); make contracts, "
            "incur liabilities, borrow money, and issue guarantees including for "
            "subsidiaries (13); and make contracts with current or prospective "
            "stockholders concerning corporate governance matters (18). The power to "
            "contract is fundamental - DGCL corporations can enter into any commercial "
            "agreement not contrary to law or public policy."
        ),
        tags=["incorporation", "certificate", "corporate powers", "exculpation", "contracting", "bylaws"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1967, 7, 3),
        last_amended=date(2025, 3, 1),
        authority_level="statute",
    ),
    StandardEntry(
        id="dgcl-002",
        standard="US_DGCL",
        topic="Board Authority and Fiduciary Duties",
        article="§ 141",
        title="Board of Directors: Governance Powers and Fiduciary Framework",
        content=(
            "Section 141(a): The business and affairs of every Delaware corporation "
            "shall be managed by or under the direction of a board of directors, except "
            "as otherwise provided in the certificate of incorporation. This is the "
            "cornerstone of Delaware's board-centric governance model. The board must "
            "consist of one or more natural persons; the number is fixed by or in the "
            "manner provided in the bylaws. A majority of the total number of directors "
            "constitutes a quorum (minimum one-third), and the vote of a majority of "
            "directors present at a meeting with a quorum constitutes the act of the "
            "board. The board may designate committees with full board authority, except "
            "committees cannot amend the certificate, adopt merger agreements, recommend "
            "sale of substantially all assets, or recommend dissolution. Section 141(e): "
            "Directors are fully protected when relying in good faith on corporate "
            "records, officers, employees, committees, or expert advisors. Fiduciary "
            "duties arise under § 141(a) and Delaware common law: the duty of care "
            "requires informed decision-making (gross negligence standard, protected "
            "by the business judgment rule); the duty of loyalty requires good faith, "
            "acting in the best interests of the corporation and stockholders, and no "
            "self-dealing. Conflicted transactions are subject to entire fairness review "
            "unless cleansed through independent director or stockholder approval. "
            "Contracts with Delaware corporations must be evaluated against whether "
            "the board acted within its authority and in compliance with fiduciary duties."
        ),
        tags=["board of directors", "fiduciary duty", "duty of care", "duty of loyalty", "business judgment rule", "governance"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1967, 7, 3),
        last_amended=date(2025, 3, 1),
        authority_level="statute",
    ),
    StandardEntry(
        id="dgcl-003",
        standard="US_DGCL",
        topic="Indemnification and Advancement",
        article="§ 145",
        title="Indemnification of Directors, Officers, Employees, and Agents",
        content=(
            "Section 145(a) (Third-party actions): A corporation may indemnify any "
            "person made a party to any action (other than by or in the right of the "
            "corporation) against expenses, judgments, fines, and settlement amounts if "
            "the person acted in good faith and in a manner reasonably believed to be "
            "in or not opposed to the corporation's best interests. Section 145(b) "
            "(Derivative actions): The corporation may indemnify against expenses in "
            "actions by or in the right of the corporation, with the same good faith "
            "standard, but no indemnification if the person is adjudged liable to the "
            "corporation unless the Court of Chancery determines indemnity is fair. "
            "Section 145(c) (Mandatory indemnification): If a present or former director "
            "or officer is successful on the merits or otherwise, the corporation shall "
            "indemnify against expenses actually and reasonably incurred. Section 145(e) "
            "(Advancement): Expenses may be advanced upon receipt of an undertaking to "
            "repay if it is ultimately determined the person is not entitled to "
            "indemnification. Section 145(f) (Non-exclusivity): Indemnification rights "
            "are not exclusive of other rights under bylaws, agreements, or stockholder "
            "votes. Section 145(g) (Insurance): The corporation may purchase D&O "
            "insurance whether or not it could indemnify directly. Contracts involving "
            "Delaware corporations should assess whether indemnification and insurance "
            "provisions align with DGCL § 145 requirements, particularly for third-party "
            "vendor, service, and partnership agreements where cross-indemnities apply."
        ),
        tags=["indemnification", "advancement", "D&O insurance", "good faith", "derivative actions", "non-exclusivity"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1967, 7, 3),
        last_amended=date(2025, 3, 1),
        authority_level="statute",
    ),
    StandardEntry(
        id="dgcl-004",
        standard="US_DGCL",
        topic="Director Liability and Exculpation",
        article="§ 102(b)(7), § 144",
        title="Limitation of Director Liability and Safe Harbors for Conflicted Transactions",
        content=(
            "Section 102(b)(7): The certificate of incorporation may eliminate or limit "
            "directors' personal monetary liability for breach of fiduciary duty, except "
            "liability for: (i) breach of the duty of loyalty to the corporation or its "
            "stockholders; (ii) acts or omissions not in good faith or involving "
            "intentional misconduct or knowing violation of law; (iii) unlawful payment "
            "of dividends or unlawful stock purchases/redemptions under § 174; or (iv) "
            "any transaction from which the director derived an improper personal benefit. "
            "This exculpation applies only to directors (not officers) and only to "
            "monetary damages (not equitable relief). Amended Section 144 (2025): "
            "Provides statutory safe harbor procedures for transactions involving "
            "interested directors, officers, and controlling stockholders. If the "
            "transaction is approved by either (a) a fully informed disinterested "
            "committee of at least two directors, or (b) a majority of fully informed, "
            "disinterested, uncoerced minority stockholders, the transaction is shielded "
            "from equitable relief and monetary damages for breach of fiduciary duty "
            "(except for going-private transactions, which require both). This is a "
            "shift from the prior MFW framework - either mechanism now provides outright "
            "liability protection. Contracts with Delaware entities involving interested "
            "party transactions should document compliance with § 144 safe harbor "
            "procedures to minimize litigation risk."
        ),
        tags=["exculpation", "director liability", "safe harbor", "conflicted transactions", "duty of loyalty", "MFW"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1967, 7, 3),
        last_amended=date(2025, 3, 1),
        authority_level="statute",
    ),
    StandardEntry(
        id="dgcl-005",
        standard="US_DGCL",
        topic="Corporate Contracting and Veil Piercing",
        article="§§ 122(13), 122(18), Common Law",
        title="Corporate Contract Authority, Stockholder Agreements, and Limited Liability",
        content=(
            "Section 122(13): Every Delaware corporation may make contracts, incur "
            "liabilities, borrow money, issue notes and bonds, and make guarantees "
            "(including guarantees of obligations of subsidiaries, parents, or "
            "affiliates whether or not in furtherance of the corporation's own business). "
            "Section 122(18) (2024 amendment): A corporation may make contracts with "
            "current or prospective stockholders that impose consent rights, veto "
            "rights, board composition agreements, and covenants concerning corporate "
            "actions, even if such contracts constrain the board's authority under "
            "§ 141(a). This was a direct response to Moelis and provides statutory "
            "authority for stockholder governance agreements. Limited Liability: A "
            "fundamental principle of Delaware corporate law is that stockholders are "
            "not personally liable for corporate debts. However, the corporate veil "
            "may be pierced in exceptional circumstances where: (a) the corporation "
            "is a mere alter ego of the stockholder with no independent existence; "
            "(b) the corporation was used to perpetrate fraud or injustice; and (c) "
            "adherence to the corporate form would sanction fraud or promote injustice. "
            "Delaware courts rarely pierce the veil and only upon a strong showing. "
            "Related-party contracts between parent and subsidiary corporations, "
            "management agreements, and inter-corporate guarantees must respect "
            "corporate separateness - failure to observe formalities, co-mingling of "
            "assets, and undercapitalization are key factors in veil-piercing analysis. "
            "Contracts with Delaware entities should include representations confirming "
            "the signatory's corporate authority and that the contract does not violate "
            "its organizational documents."
        ),
        tags=["contracting power", "stockholder agreements", "veil piercing", "limited liability", "alter ego", "corporate authority"],
        jurisdiction="US",
        standard_category="contract_law",
        effective_date=date(1967, 7, 3),
        last_amended=date(2025, 3, 1),
        authority_level="statute",
    ),
]
