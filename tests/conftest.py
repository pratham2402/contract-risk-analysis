"""Shared fixtures and configuration for the test suite."""

import pytest

from contract_analyzer.models.output import (
    ClauseType,
    Finding,
    ParsedClause,
    RiskLevel,
    StandardRef,
)


@pytest.fixture
def sample_clause() -> ParsedClause:
    return ParsedClause(
        id="clause-001",
        clause_type=ClauseType.DATA_PROTECTION,
        clause_number="4.1",
        title="Data Protection and Privacy Compliance",
        text="Receiving Party shall implement and maintain appropriate technical "
             "and organizational measures to ensure a level of security appropriate "
             "to the risk, including encryption of personal data both in transit "
             "(using TLS 1.3 or higher) and at rest (using AES-256 or equivalent).",
        start_line=50,
        end_line=55,
    )


@pytest.fixture
def sample_finding(sample_clause) -> Finding:
    return Finding(
        id="finding-001",
        clause_id=sample_clause.id,
        issue_description="Insufficiently specific encryption standards — must use TLS 1.3 and AES-256",
        risk_level=RiskLevel.MEDIUM,
        category="data_protection",
        referenced_standards=[
            StandardRef(
                standard="GDPR",
                article="Art. 32",
                clause="1(a)",
                description="Encryption of personal data",
                relevance_score=0.92,
            ),
            StandardRef(
                standard="CCPA/CPRA",
                article="§ 1798.100",
                clause="(e)",
                description="Reasonable security procedures",
                relevance_score=0.85,
            ),
        ],
        explanation="While the clause references encryption, it does not mandate "
                     "specific algorithms as required by GDPR Art. 32.",
        reasoning_trace="Step 1: Identified data protection clause. Step 2: Retrieved "
                         "GDPR Art. 32 and CCPA/CPRA § 1798.100. Step 3: Compared "
                         "requirements — GDPR mandates specific measures.",
        confidence=0.88,
    )


@pytest.fixture
def nda_contract_text() -> str:
    return """NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT

This Non-Disclosure and Confidentiality Agreement (this "Agreement") is entered into
as of the Effective Date by and between:

ACME INNOVATIONS INC., a Delaware corporation ("Disclosing Party"), and
BETA ANALYTICS LLC, a California limited liability company ("Receiving Party").

1. DEFINITION OF CONFIDENTIAL INFORMATION
"Confidential Information" means any non-public information disclosed by Disclosing
Party to Receiving Party, whether orally or in writing, that is designated as
confidential, including trade secrets, know-how, customer lists, financial
information, and business plans.

2. OBLIGATIONS OF RECEIVING PARTY
Receiving Party shall: (a) hold Confidential Information in strict confidence;
(b) not disclose it to any third party without prior written consent;
(c) use it solely for the Purpose; and (d) protect it using reasonable care.

3. EXCLUSIONS
The obligations shall not apply to information that: (a) is or becomes publicly
available through no breach; (b) was in Receiving Party's possession prior to
disclosure; (c) is rightfully disclosed by a third party; or (d) is independently
developed without use of Confidential Information.

4. DATA PROTECTION
Receiving Party shall comply with all applicable data protection laws including
GDPR, CCPA, and HIPAA. Personal data shall be encrypted in transit using TLS 1.2
or higher and at rest using AES-256.

5. TERM AND TERMINATION
This Agreement remains in effect for five (5) years. Confidentiality obligations
survive termination for seven (7) years. Either party may terminate upon thirty
(30) days written notice.

6. INDEMNIFICATION
Receiving Party shall indemnify Disclosing Party against any claims arising from
breach of this Agreement or violation of applicable law.

7. GOVERNING LAW
This Agreement shall be governed by the laws of the State of Delaware. Any disputes
shall be resolved in the courts of Delaware.

IN WITNESS WHEREOF, the Parties have executed this Agreement.

ACME INNOVATIONS INC.              BETA ANALYTICS LLC
Signature: ____________            Signature: ____________
"""


@pytest.fixture
def saas_contract_text() -> str:
    return """SAAS SERVICES AGREEMENT

This SaaS Services Agreement is entered into between:

CLOUDSTACK TECHNOLOGIES PVT LTD, a company incorporated under the Companies Act,
2013 of India ("Provider"), and

MERIDIAN HEALTH SERVICES INC., a Delaware corporation ("Customer").

1. SERVICES
Provider shall make the Platform available to Customer during the Subscription Term
with a Monthly Uptime Percentage of at least 99.9%.

2. DATA PROCESSING AND SECURITY
Provider shall implement administrative, physical, and technical safeguards to
protect Customer Data. Such safeguards shall include encryption in transit using
TLS 1.3 and at rest using AES-256, role-based access controls with multi-factor
authentication, and annual penetration testing.

3. LIMITATION OF LIABILITY
TO THE MAXIMUM EXTENT PERMITTED BY LAW, PROVIDER'S TOTAL AGGREGATE LIABILITY SHALL
NOT EXCEED THE FEES PAID BY CUSTOMER DURING THE TWELVE (12) MONTHS PRECEDING THE
CLAIM. PROVIDER SHALL NOT BE LIABLE FOR INDIRECT, INCIDENTAL, OR CONSEQUENTIAL
DAMAGES.

4. INDEMNIFICATION
Customer agrees to indemnify Provider against any third-party claims arising from
Customer Data or Customer's use of the Platform in violation of this Agreement.

5. TERMINATION
Either party may terminate this Agreement upon thirty (30) days written notice if
the other party materially breaches. Upon termination, Provider shall delete all
Customer Data within 60 days.

6. GOVERNING LAW
This Agreement shall be governed by the laws of the Republic of India. The courts
of Bengaluru shall have exclusive jurisdiction.

IN WITNESS WHEREOF, the Parties have executed this Agreement.

CLOUDSTACK TECHNOLOGIES PVT LTD    MERIDIAN HEALTH SERVICES INC.
Signature: ____________            Signature: ____________
"""
