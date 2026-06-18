export interface SampleContract {
  name: string;
  text: string;
}

export const SAMPLES: Record<string, SampleContract> = {
  nda: {
    name: "Standard NDA",
    text: `NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT

This Non-Disclosure and Confidentiality Agreement (this "Agreement") is entered into as of the Effective Date by and between:

ACME INNOVATIONS INC., a Delaware corporation with its principal place of business at 1209 Orange Street, Wilmington, DE 19801 ("Disclosing Party"), and

BETA ANALYTICS LLC, a California limited liability company with its principal place of business at 350 California Street, San Francisco, CA 94104 ("Receiving Party").

Disclosing Party and Receiving Party are collectively referred to as the "Parties."

WHEREAS, Disclosing Party possesses certain proprietary and confidential information, including trade secrets, business strategies, technical specifications, customer data, and financial information; and

WHEREAS, Receiving Party desires to receive such information for the limited purpose of evaluating a potential strategic partnership, investment, or business relationship (the "Purpose"); and

WHEREAS, the Parties wish to establish terms governing the protection, use, and non-disclosure of such information.

NOW, THEREFORE, the Parties agree as follows:

1. DEFINITION OF CONFIDENTIAL INFORMATION

1.1. "Confidential Information" means any and all non-public information, regardless of form or medium, disclosed by or on behalf of Disclosing Party to Receiving Party, whether before or after the Effective Date, and whether orally, in writing, electronically, or through observation, that: (a) is marked or designated as "Confidential," "Proprietary," or with a similar legend; (b) is of a nature that a reasonable person would understand to be confidential under the circumstances; or (c) relates to Disclosing Party's business operations, including but not limited to:

    (i) Trade secrets, inventions, know-how, methodologies, algorithms, software source code, and technical architectures;
    (ii) Business plans, strategic roadmaps, marketing strategies, pricing models, and financial projections;
    (iii) Customer and prospect lists, customer contracts, and customer usage data, including any personally identifiable information contained therein;
    (iv) Vendor and supplier relationships, pricing agreements, and supply chain logistics;
    (v) Employee and contractor information, including compensation structures and personnel files;
    (vi) Security protocols, vulnerability assessments, penetration test results, and incident response plans;
    (vii) Product designs, prototypes, specifications, and unpublished patent applications;
    (viii) Merger, acquisition, and financing activities, term sheets, and due diligence materials.

1.2. Confidential Information also includes all notes, summaries, analyses, compilations, derivative works, and other materials prepared by Receiving Party that contain, reflect, or are derived from Confidential Information.

1.3. The existence and terms of this Agreement, and the fact that discussions are taking place between the Parties, shall themselves constitute Confidential Information.

2. OBLIGATIONS OF RECEIVING PARTY

2.1. Receiving Party shall: (a) hold all Confidential Information in the strictest confidence; (b) not disclose, distribute, publish, or otherwise disseminate Confidential Information to any third party without Disclosing Party's prior written consent, such consent to be granted or withheld in Disclosing Party's sole discretion; (c) use Confidential Information solely for the Purpose and for no other purpose whatsoever; (d) limit access to Confidential Information to those of its employees, officers, directors, agents, and independent contractors who: (i) have a genuine need to know for the Purpose; (ii) have been informed of the confidential nature of the information; and (iii) are bound by written confidentiality obligations at least as protective as those set forth in this Agreement; (e) protect Confidential Information using the same degree of care it uses to protect its own confidential and proprietary information of a similar nature, but in no event less than a reasonable standard of care; (f) not reverse engineer, decompile, or disassemble any software, prototypes, or technical materials provided as Confidential Information; (g) promptly notify Disclosing Party in writing upon discovery of any unauthorized access, use, or disclosure of Confidential Information, and cooperate fully with Disclosing Party in mitigating any resulting harm; and (h) upon Disclosing Party's request or upon termination of this Agreement, return or, at Disclosing Party's option, securely and permanently destroy all copies of Confidential Information in Receiving Party's possession or control, and certify such return or destruction in writing within ten (10) business days.

2.2. Receiving Party shall be fully liable for any breach of this Agreement by its employees, contractors, or agents to whom Receiving Party has disclosed Confidential Information.

3. EXCLUSIONS FROM CONFIDENTIAL INFORMATION

3.1. The obligations set forth in Section 2 shall not apply to information that Receiving Party can demonstrate by competent written evidence: (a) is or becomes publicly available through no act or omission of Receiving Party in breach of this Agreement; (b) was rightfully in Receiving Party's possession, free of any confidentiality obligation, prior to disclosure by Disclosing Party; (c) is rightfully disclosed to Receiving Party by a third party who is not under any obligation of confidentiality with respect to such information; or (d) is independently developed by Receiving Party's personnel who had no access to or use of the Confidential Information.

3.2. A disclosure of Confidential Information required by applicable law, regulation, or valid legal process (including by a court, administrative agency, or governmental authority) shall not constitute a breach of this Agreement, provided that Receiving Party: (a) to the extent legally permitted, gives Disclosing Party prompt written notice of such requirement prior to disclosure; (b) cooperates with Disclosing Party, at Disclosing Party's expense, in seeking a protective order or other appropriate remedy; and (c) discloses only that portion of the Confidential Information that Receiving Party's legal counsel advises is legally required.

4. DATA PROTECTION AND PRIVACY COMPLIANCE

4.1. To the extent any Confidential Information includes "personal data," "personal information," "protected health information," "nonpublic personal information," or any equivalent term as defined under applicable data protection laws, Receiving Party shall, in addition to its obligations under Section 2:

    (a) Process such data only in accordance with Disclosing Party's documented written instructions, unless required otherwise by applicable law to which Receiving Party is subject, in which case Receiving Party shall inform Disclosing Party of that legal requirement before processing (unless prohibited by such law);

    (b) Implement and maintain appropriate technical and organizational measures to ensure a level of security appropriate to the risk, including: (i) encryption of personal data both in transit (using TLS 1.3 or higher) and at rest (using AES-256 or equivalent); (ii) multi-factor authentication for all personnel with access to such data; (iii) pseudonymization and data minimization where technically feasible; (iv) regular testing, assessment, and evaluation of the effectiveness of security measures, including annual penetration testing by an independent qualified assessor; and (v) maintaining written information security policies and incident response plans;

    (c) Ensure that any person authorized to process personal data is subject to a duty of confidentiality, whether contractual or statutory;

    (d) Not transfer personal data outside the United States or the European Economic Area, as applicable, without Disclosing Party's prior written consent and without implementing appropriate safeguards as required by applicable law, including Standard Contractual Clauses or Binding Corporate Rules;

    (e) Provide reasonable assistance to Disclosing Party in responding to requests from data subjects exercising their rights under applicable data protection laws (including rights of access, rectification, erasure, restriction, portability, and objection), within ten (10) business days of Disclosing Party's request;

    (f) Notify Disclosing Party without undue delay, and in any event within forty-eight (48) hours, upon becoming aware of any personal data breach affecting Confidential Information, providing: (i) a description of the nature of the breach; (ii) the categories and approximate number of data subjects and records affected; (iii) the name and contact details of a point of contact; (iv) the likely consequences of the breach; and (v) the measures taken or proposed to address the breach and mitigate its effects;

    (g) Maintain complete and accurate records of all processing activities involving personal data, and make such records available to Disclosing Party and applicable supervisory authorities upon request;

    (h) Upon termination of this Agreement, at Disclosing Party's election, securely delete or return all personal data, and delete all existing copies, unless applicable law requires retention of such data.

4.2. Receiving Party shall comply with all applicable data protection laws, regulations, and industry standards, including but not limited to: (a) the General Data Protection Regulation (Regulation (EU) 2016/679) ("GDPR") to the extent it applies; (b) the California Consumer Privacy Act of 2018, as amended by the California Privacy Rights Act of 2020 (collectively, "CCPA/CPRA"); (c) the Health Insurance Portability and Accountability Act of 1996 and its implementing regulations ("HIPAA"), to the extent protected health information is involved; (d) the Gramm-Leach-Bliley Act ("GLBA") and its implementing regulations, to the extent nonpublic personal financial information is involved; and (e) the Digital Personal Data Protection Act, 2023 of India ("DPDPA"), to the extent personal data of individuals located in India is involved.

4.3. Receiving Party shall not sell, share, or otherwise make available any personal data to any third party for monetary or other valuable consideration, or use such data for any purpose other than the Purpose, including for targeted advertising, profiling, or automated decision-making with legal or similarly significant effects.

5. INTELLECTUAL PROPERTY RIGHTS

5.1. All Confidential Information, including all intellectual property rights therein, shall remain the sole and exclusive property of Disclosing Party. Nothing in this Agreement shall be construed as granting, by implication, estoppel, or otherwise, any license, assignment, or transfer of any intellectual property rights from Disclosing Party to Receiving Party.

5.2. Receiving Party acknowledges that the unauthorized use or disclosure of Confidential Information may cause irreparable harm to Disclosing Party for which monetary damages would be an inadequate remedy. Accordingly, Disclosing Party shall be entitled to seek injunctive relief, specific performance, and other equitable remedies for any actual or threatened breach, without the necessity of posting bond or proving actual damages, in addition to any other remedies available at law or in equity.

5.3. Disclosing Party makes no representation or warranty, express or implied, as to the accuracy, completeness, or fitness for any particular purpose of the Confidential Information. All Confidential Information is provided "AS IS."

6. RESIDUAL KNOWLEDGE

6.1. Notwithstanding anything to the contrary in this Agreement, Receiving Party's employees who have had access to Confidential Information may retain and use, without restriction, Residual Knowledge; provided that Residual Knowledge does not include memorized or reduced copies of Confidential Information, and provided that the use of Residual Knowledge does not constitute a misappropriation of Disclosing Party's trade secrets or an infringement of Disclosing Party's intellectual property rights.

6.2. "Residual Knowledge" means ideas, concepts, know-how, techniques, and general skills retained in the unaided memory of Receiving Party's employees who have had access to Confidential Information in the ordinary course of performing their duties, where such retention is the natural result of learning through exposure to the Confidential Information over time, and not an intentional effort to memorize or record specific information for later use.

7. NON-SOLICITATION AND NON-CIRCUMVENTION

7.1. For a period of two (2) years following the later of: (a) the termination of this Agreement; or (b) the last disclosure of Confidential Information by Disclosing Party, Receiving Party shall not, without Disclosing Party's prior written consent, directly or indirectly: (i) solicit, induce, recruit, or hire any employee or independent contractor of Disclosing Party who was involved in discussions or activities related to the Purpose; or (ii) use any Confidential Information to circumvent Disclosing Party in any business transaction, contract, or commercial relationship that is the subject of the Purpose or that would not have been identified to Receiving Party but for the disclosure of Confidential Information.

7.2. The restrictions in Section 7.1(i) shall not apply to general solicitations not specifically targeted at Disclosing Party's employees, such as public job postings, or to employees who have been separated from Disclosing Party for at least six (6) months.

8. TERM AND SURVIVAL

8.1. This Agreement shall commence on the Effective Date and continue in full force and effect for a period of five (5) years, unless earlier terminated in accordance with Section 8.2.

8.2. Either Party may terminate this Agreement at any time upon thirty (30) days written notice to the other Party. Disclosing Party may terminate this Agreement immediately upon written notice in the event of any breach by Receiving Party.

8.3. The obligations of confidentiality, non-use, non-disclosure, data protection, non-solicitation, and non-circumvention set forth in Sections 2, 4, 5, 6, and 7 shall survive termination or expiration of this Agreement: (a) indefinitely, with respect to trade secrets and personal data; and (b) for a period of seven (7) years following termination, with respect to all other Confidential Information.

9. INDEMNIFICATION

9.1. Receiving Party shall indemnify, defend, and hold harmless Disclosing Party and its officers, directors, employees, agents, and affiliates from and against any and all claims, demands, actions, losses, liabilities, damages, costs, and expenses (including reasonable attorneys' fees and court costs) arising out of or in connection with: (a) any breach of this Agreement by Receiving Party or its employees, contractors, or agents; (b) any violation of applicable law by Receiving Party in connection with its handling of Confidential Information; or (c) any claim by a third party alleging that Receiving Party's use, storage, or processing of data provided by Disclosing Party violates such third party's rights or applicable data protection laws.

9.2. Disclosing Party shall promptly notify Receiving Party of any claim for which indemnification is sought and shall reasonably cooperate with Receiving Party in the defense of such claim, at Receiving Party's expense. Receiving Party shall have sole control of the defense and settlement of any such claim, provided that Receiving Party shall not settle any claim that admits liability on the part of Disclosing Party or imposes any obligation on Disclosing Party without Disclosing Party's prior written consent.

10. INSURANCE

10.1. Receiving Party shall, at its own expense, maintain throughout the term of this Agreement and for a period of three (3) years thereafter, the following minimum insurance coverage:

    (a) Commercial General Liability insurance with limits not less than $2,000,000 per occurrence and $5,000,000 in the aggregate;
    (b) Technology Errors and Omissions / Professional Liability insurance with limits not less than $5,000,000 per claim and in the aggregate, covering liability arising from data breaches, unauthorized access, and failure to protect confidential information;
    (c) Cyber Liability / Privacy and Network Security insurance with limits not less than $5,000,000 per claim and in the aggregate, covering breach response costs, notification expenses, credit monitoring services, and regulatory fines and penalties; and
    (d) Workers' Compensation insurance as required by applicable law, and Employers' Liability insurance with limits not less than $1,000,000.

10.2. All policies required under this Section shall: (a) be issued by insurers with an A.M. Best rating of at least A- VII; (b) name Disclosing Party as an additional insured; (c) be primary and non-contributory with respect to any insurance maintained by Disclosing Party; and (d) not be cancelled, non-renewed, or materially modified without at least thirty (30) days prior written notice to Disclosing Party. Upon request, Receiving Party shall provide Disclosing Party with certificates of insurance evidencing compliance with this Section.

11. EXPORT CONTROLS AND SANCTIONS

11.1. Receiving Party acknowledges that Confidential Information may be subject to export controls under the laws and regulations of the United States, including the Export Administration Regulations ("EAR") administered by the U.S. Department of Commerce and the International Traffic in Arms Regulations ("ITAR") administered by the U.S. Department of State. Receiving Party shall not export, re-export, transfer, or otherwise disclose Confidential Information in violation of any applicable export control or economic sanctions laws, including those administered by the U.S. Office of Foreign Assets Control ("OFAC").

11.2. Receiving Party represents and warrants that neither it nor any of its officers, directors, or employees is: (a) a person or entity on any U.S. government restricted-party list; (b) organized or resident in a country or territory subject to comprehensive U.S. economic sanctions (including Cuba, Iran, North Korea, Syria, and the Crimea, Donetsk, and Luhansk regions of Ukraine); or (c) otherwise subject to any U.S. sanctions or export restrictions that would prohibit Receiving Party from receiving Confidential Information.

12. AUDIT RIGHTS

12.1. Disclosing Party shall have the right, upon at least fifteen (15) business days prior written notice and no more than once per calendar year (or at any time upon reasonable suspicion of a breach), to engage an independent third-party auditor, subject to reasonable confidentiality obligations, to audit and assess Receiving Party's compliance with the terms of this Agreement, including Receiving Party's: (a) information security program and technical controls; (b) policies and procedures for handling Confidential Information; and (c) records of access to and disclosure of Confidential Information.

12.2. Receiving Party shall reasonably cooperate with such audit and provide access to relevant personnel, facilities, systems, and records during normal business hours. Any audit shall be conducted in a manner that minimizes disruption to Receiving Party's normal business operations.

12.3. If an audit reveals a material breach of this Agreement, Receiving Party shall reimburse Disclosing Party for the costs of the audit, in addition to any other remedies available to Disclosing Party.

13. GOVERNING LAW, JURISDICTION, AND DISPUTE RESOLUTION

13.1. This Agreement and all matters arising out of or relating to it, including any tort claims and statutory claims, shall be governed by and construed in accordance with the internal laws of the State of Delaware, without giving effect to any choice-of-law or conflict-of-law principles that would result in the application of the laws of any other jurisdiction.

13.2. The Parties hereby irrevocably consent to the exclusive jurisdiction and venue of the state courts of the State of Delaware sitting in New Castle County and the United States District Court for the District of Delaware, for any action, suit, or proceeding arising out of or relating to this Agreement. Each Party waives any objection to venue or any claim of forum non conveniens.

13.3. Prior to initiating any litigation, the Parties shall first attempt to resolve any dispute through good-faith negotiations. If the dispute is not resolved within thirty (30) days, either Party may initiate litigation. Notwithstanding the foregoing, Disclosing Party may seek injunctive or other equitable relief in any court of competent jurisdiction without prior negotiation.

13.4. THE PARTIES HEREBY WAIVE ANY RIGHT TO TRIAL BY JURY IN ANY ACTION OR PROCEEDING ARISING OUT OF OR RELATING TO THIS AGREEMENT.

14. FORCE MAJEURE

14.1. Neither Party shall be liable for any failure or delay in performance under this Agreement (other than payment obligations) to the extent such failure or delay is caused by circumstances beyond its reasonable control, including acts of God, war, terrorism, civil unrest, epidemic or pandemic, governmental action, fire, flood, earthquake, or failure of utilities, telecommunications, or the internet; provided that the affected Party: (a) gives the other Party prompt written notice of the force majeure event and its expected duration; and (b) uses diligent efforts to mitigate the effects of the event and resume performance as soon as reasonably practicable.

15. ASSIGNMENT

15.1. Receiving Party may not assign, delegate, or otherwise transfer this Agreement, or any of its rights or obligations hereunder, whether voluntarily or by operation of law, without Disclosing Party's prior written consent. Any purported assignment or transfer in violation of this Section shall be null and void.

15.2. Disclosing Party may assign this Agreement without Receiving Party's consent to any affiliate or in connection with a merger, acquisition, consolidation, reorganization, or sale of all or substantially all of its assets or equity.

16. SEVERABILITY AND MODIFICATION

16.1. If any provision of this Agreement is held by a court of competent jurisdiction to be invalid, illegal, or unenforceable, such provision shall be modified to the minimum extent necessary to make it enforceable, or if modification is not possible, severed from this Agreement, and the remaining provisions shall continue in full force and effect.

16.2. This Agreement may not be modified or amended except by a written instrument signed by authorized representatives of both Parties. No waiver of any provision of this Agreement shall be effective unless in writing and signed by the Party against whom enforcement of the waiver is sought.

17. ENTIRE AGREEMENT

17.1. This Agreement constitutes the entire agreement between the Parties with respect to the subject matter hereof and supersedes all prior and contemporaneous understandings, agreements, representations, and warranties, whether written or oral, relating to such subject matter.

17.2. In the event of any conflict between the terms of this Agreement and the terms of any purchase order, click-through agreement, or other document submitted by Receiving Party, the terms of this Agreement shall prevail.

IN WITNESS WHEREOF, the Parties have caused this Agreement to be executed by their duly authorized representatives as of the Effective Date.

ACME INNOVATIONS INC.                        BETA ANALYTICS LLC
Signature: ___________________               Signature: ___________________
Name: ________________________               Name: ________________________
Title: _______________________               Title: _______________________
Date: ________________________               Date: ________________________`,
  },
  saas: {
    name: "SaaS Services Agreement",
    text: `SAAS SERVICES AND PLATFORM AGREEMENT

This SaaS Services and Platform Agreement (this "Agreement") is entered into as of the Effective Date by and between:

CLOUDSTACK TECHNOLOGIES PRIVATE LIMITED, a company incorporated under the Companies Act, 2013 of India, with its registered office at 91, 4th Floor, Salarpuria Magnificia, Marathahalli Outer Ring Road, Bengaluru, Karnataka 560103, India ("Provider"); and

MERIDIAN HEALTH SERVICES INC., a Delaware corporation with its principal place of business at 200 State Street, Boston, MA 02109 ("Customer").

Provider and Customer are collectively referred to as the "Parties."

1. DEFINITIONS

1.1. "Authorized Users" means Customer's employees, independent contractors, and agents who are authorized by Customer to access and use the Platform pursuant to the terms of this Agreement.

1.2. "Customer Data" means all data, information, content, and materials, including Personal Data, that Customer or its Authorized Users upload, submit, transmit, or otherwise provide to or through the Platform, and any data, reports, or outputs derived therefrom by the Platform.

1.3. "Documentation" means Provider's standard user manuals, technical specifications, API documentation, and security whitepapers made generally available to Provider's customers.

1.4. "Personal Data" means any information relating to an identified or identifiable natural person, including "personal data" as defined under GDPR, "personal information" as defined under CCPA/CPRA, "protected health information" as defined under HIPAA, "nonpublic personal information" as defined under GLBA, and "personal data" as defined under India's DPDPA 2023.

1.5. "Platform" means Provider's proprietary cloud-based software-as-a-service platform for healthcare claims processing, patient data analytics, and regulatory compliance management, including any updates, upgrades, modifications, and enhancements made generally available by Provider.

1.6. "Subscription Term" means the period during which Customer is authorized to access and use the Platform, as set forth in the applicable Order Form.

2. PLATFORM LICENSE AND ACCESS

2.1. Subject to Customer's compliance with the terms and conditions of this Agreement and payment of all applicable fees, Provider grants Customer a non-exclusive, non-transferable, non-sublicensable, revocable right during the Subscription Term to: (a) access and use the Platform solely for Customer's internal business operations; and (b) permit Authorized Users to access and use the Platform on Customer's behalf, provided Customer remains fully liable for its Authorized Users' compliance with this Agreement.

2.2. Customer shall not, and shall not permit any third party to: (a) copy, modify, adapt, translate, or create derivative works of the Platform or Documentation; (b) reverse engineer, decompile, disassemble, or otherwise attempt to derive the source code, algorithms, or underlying structure of the Platform; (c) rent, lease, sublicense, distribute, sell, or otherwise transfer the Platform to any third party; (d) use the Platform for the benefit of any third party, including on a service bureau, time-sharing, or application service provider basis; (e) remove, obscure, or alter any proprietary notices, labels, or marks on the Platform; (f) access or use the Platform to build a competitive product or service, or to conduct competitive benchmarking without Provider's prior written consent; (g) use the Platform in violation of any applicable law or regulation; or (h) circumvent or bypass any security mechanism, access control, or usage limitation of the Platform.

3. DATA PROCESSING, SECURITY, AND PRIVACY

3.1. The Parties acknowledge and agree that, as between them, Customer is the "Data Controller" (or equivalent concept under applicable law) and Provider is the "Data Processor" (or equivalent concept) with respect to all Personal Data contained within Customer Data. Provider shall process Personal Data only: (a) as necessary to provide the Platform and perform its obligations under this Agreement; (b) in accordance with Customer's documented written instructions; and (c) as required by applicable law.

3.2. Provider shall implement and maintain a comprehensive written information security program that includes administrative, physical, and technical safeguards designed to protect the confidentiality, integrity, and availability of Customer Data. Such safeguards shall include, at a minimum:

    (a) Encryption: (i) Customer Data shall be encrypted in transit using TLS 1.3 or higher with forward secrecy; (ii) Customer Data at rest shall be encrypted using AES-256 or equivalent with keys managed via a FIPS 140-2 Level 3 Hardware Security Module (HSM); (iii) all cryptographic keys shall be rotated at least every ninety (90) days; and (iv) Customer shall have the option to manage its own encryption keys (BYOK) through Provider's key management interface;

    (b) Access Controls: (i) role-based access controls with least-privilege principles enforced across all Provider systems and networks; (ii) multi-factor authentication required for all administrative access, all remote access, and all access to systems storing or processing Customer Data; (iii) unique user IDs with strong password policies (minimum 16 characters, complexity requirements, and 90-day rotation); (iv) quarterly access reviews with automated revocation of inactive accounts after thirty (30) days; and (v) all access to Customer Data logged with immutable audit trails, retained for a minimum of three (3) years;

    (c) Network Security: (i) defense-in-depth network architecture with network segmentation isolating Customer Data environments from corporate IT systems; (ii) next-generation firewalls with intrusion detection and prevention systems (IDS/IPS) at all network boundaries; (iii) distributed denial-of-service (DDoS) protection at the application and network layers; (iv) all administrative access restricted to bastion hosts with session recording, accessible only through encrypted VPN connections; and (v) continuous network monitoring with security information and event management (SIEM) correlation and 24/7/365 security operations center (SOC) coverage;

    (d) Vulnerability Management: (i) continuous automated vulnerability scanning of all production systems, networks, and applications; (ii) annual independent third-party penetration testing covering internal and external attack surfaces, conducted in accordance with industry standards (such as OWASP Testing Guide and PTES); (iii) code security reviews, including static application security testing (SAST) and software composition analysis (SCA), integrated into the CI/CD pipeline for all Platform updates; (iv) critical and high-severity vulnerabilities remediated within fifteen (15) days and thirty (30) days of discovery, respectively; and (v) bug bounty or coordinated vulnerability disclosure program;

    (e) Business Continuity and Disaster Recovery: (i) documented and tested business continuity and disaster recovery plans, tested at least annually through tabletop exercises and full failover testing; (ii) Recovery Time Objective (RTO) of four (4) hours and Recovery Point Objective (RPO) of fifteen (15) minutes for the Platform; (iii) geographically distributed data centers with real-time data replication and automated failover; and (iv) backup copies of Customer Data retained in an immutable, air-gapped format for a minimum of thirty (30) days;

    (f) Vendor and Sub-processor Management: (i) Provider shall maintain a current list of all sub-processors engaged in the delivery of the Platform, published at a publicly accessible URL; (ii) Provider shall notify Customer at least thirty (30) days prior to engaging any new sub-processor; (iii) all sub-processors shall be bound by written agreements imposing data protection obligations no less protective than those set forth in this Agreement; and (iv) Provider shall remain fully liable for the acts and omissions of its sub-processors.

3.3. Provider shall not: (a) sell, rent, or lease Customer Data to any third party; (b) use Customer Data for any purpose other than providing the Platform and related support services; (c) combine Customer Data with data of other customers for any purpose, including training of machine learning models, without Customer's express opt-in consent; or (d) disclose Customer Data to any government authority except as required by law with prior notice to Customer (if legally permitted).

3.4. Data Subject Rights and Breach Notification:

    (a) Provider shall provide Customer with reasonable cooperation and assistance in responding to data subject requests under GDPR, CCPA/CPRA, DPDPA, HIPAA, and other applicable data protection laws, within the timeframes required by such laws;
    (b) Provider shall notify Customer without undue delay, and in no event later than thirty-six (36) hours, after confirming a Security Incident involving Customer Data, providing: (i) a detailed description of the nature and scope of the incident; (ii) the categories and approximate number of data subjects and records affected; (iii) identification of the compromised systems, applications, or networks; (iv) the likely consequences of the incident; and (v) a remediation plan and timeline;
    (c) Provider shall, at its own expense, provide credit monitoring and identity protection services to all affected individuals for a minimum period of twenty-four (24) months for any Security Incident caused by Provider's failure to meet its security obligations under this Agreement.

3.5. Compliance Certifications and Audits:

    (a) Provider shall maintain, at its own expense: (i) SOC 2 Type II certification covering the Platform and all supporting infrastructure, with reports made available to Customer upon request, no more than annually; (ii) ISO/IEC 27001:2022 certification; (iii) PCI DSS Level 1 Service Provider certification (to the extent the Platform processes, stores, or transmits payment card data); and (iv) HIPAA compliance attestation (to the extent the Platform processes protected health information);
    (b) Upon Customer's request and at Customer's expense (except as otherwise provided in this Agreement), Provider shall complete a security questionnaire or risk assessment based on industry standards (such as the Cloud Security Alliance Consensus Assessments Initiative Questionnaire or the NIST Cybersecurity Framework Profile), within thirty (30) business days;
    (c) Customer may, upon at least thirty (30) days advance written notice and no more than once per twelve-month period (or at any time following a Security Incident), conduct or engage an independent auditor to conduct an on-site audit of Provider's security controls relevant to the Platform. Any audit shall be conducted during normal business hours, in a manner that minimizes disruption to Provider's operations, and the auditor shall enter into a non-disclosure agreement reasonably acceptable to Provider.

4. SERVICE LEVEL COMMITMENTS

4.1. Provider shall use commercially reasonable efforts to make the Platform available with a Monthly Uptime Percentage (as defined below) of at least 99.9%, excluding Excused Downtime. "Monthly Uptime Percentage" is calculated as: (Total Minutes in Month − Total Downtime Minutes) / Total Minutes in Month × 100.

4.2. "Excused Downtime" means downtime resulting from: (a) scheduled maintenance, provided Provider gives Customer at least seventy-two (72) hours advance notice and such maintenance does not exceed eight (8) hours per calendar month; (b) emergency maintenance required to address critical security vulnerabilities, provided Provider gives Customer as much advance notice as reasonably practicable; (c) Customer's equipment, software, network connections, or other technology; (d) force majeure events as described in Section 13; or (e) Customer's breach of this Agreement or misuse of the Platform.

4.3. If Provider fails to meet the Monthly Uptime Percentage in any calendar month, Customer shall be entitled to the following service credits:

    (a) Monthly Uptime Percentage below 99.9% but at or above 99.0%: Service credit equal to 10% of the monthly subscription fee for the affected month;
    (b) Monthly Uptime Percentage below 99.0% but at or above 95.0%: Service credit equal to 25% of the monthly subscription fee for the affected month;
    (c) Monthly Uptime Percentage below 95.0%: Service credit equal to 50% of the monthly subscription fee for the affected month;
    (d) If Provider fails to meet the 99.9% SLA for three (3) consecutive months or any four (4) months in a rolling twelve-month period, Customer may terminate this Agreement for cause without penalty and receive a pro-rata refund of prepaid fees, in addition to any accrued service credits.

4.4. Service credits shall be Customer's sole and exclusive remedy for any failure to meet the service level commitments.

5. FEES, PAYMENT, AND TAXES

5.1. Customer shall pay Provider the fees set forth in each Order Form. Unless otherwise specified in the applicable Order Form: (a) all fees are denominated and payable in United States Dollars; (b) fees are invoiced annually in advance; and (c) payment is due within thirty (30) days of the invoice date.

5.2. Late payments shall bear interest at the lesser of 1.5% per month or the maximum rate permitted by applicable law, calculated from the due date until the date of payment in full. Provider may suspend access to the Platform if any undisputed fees remain unpaid for more than sixty (60) days after the due date, provided Provider has given Customer at least ten (10) business days prior written notice of such suspension.

5.3. All fees are exclusive of applicable taxes. Customer shall be responsible for all sales, use, value-added, goods and services, withholding, and similar taxes (other than taxes based on Provider's net income). If Customer is required to deduct or withhold any tax, Customer shall gross-up the payment such that Provider receives the full amount that would have been received absent such withholding.

5.4. Except as expressly set forth in this Agreement, all fees are non-cancellable and non-refundable. Fees for any renewal Subscription Term shall be at Provider's then-current list prices unless otherwise agreed in writing.

6. OWNERSHIP AND INTELLECTUAL PROPERTY

6.1. As between the Parties, Provider owns and retains all right, title, and interest in and to: (a) the Platform (including all software, code, algorithms, user interfaces, APIs, and Documentation); (b) all improvements, enhancements, modifications, and derivative works of the Platform; (c) all de-identified, aggregated data derived from use of the Platform that does not identify Customer or any individual natural person ("Aggregated Data"); and (d) all intellectual property rights embodied in any of the foregoing.

6.2. As between the Parties, Customer owns and retains all right, title, and interest in and to: (a) Customer Data; (b) all reports, analyses, and outputs generated by the Platform based on Customer Data; and (c) all intellectual property rights embodied in any of the foregoing. Provider hereby assigns to Customer all right, title, and interest it may acquire in Customer Data by operation of law.

6.3. Customer grants Provider a non-exclusive, worldwide, royalty-free, fully paid-up license during the Subscription Term to: (a) host, copy, transmit, and display Customer Data as necessary to provide the Platform and fulfill Provider's obligations under this Agreement; and (b) use Aggregated Data for Provider's business purposes, including improving and enhancing the Platform, developing new products and services, and publishing industry research, provided such Aggregated Data cannot be re-identified or used to identify Customer or any individual.

7. CONFIDENTIALITY

7.1. Each Party (the "Receiving Party") agrees to protect the Confidential Information of the other Party (the "Disclosing Party") with the same degree of care it uses to protect its own confidential information of a similar nature, but in no event less than a reasonable standard of care. Neither Party shall use or disclose the other Party's Confidential Information except as necessary to perform its obligations or exercise its rights under this Agreement.

7.2. The obligations in Section 7.1 shall not apply to information that: (a) is or becomes publicly available through no breach by Receiving Party; (b) was rightfully in Receiving Party's possession prior to disclosure; (c) is rightfully obtained by Receiving Party from a third party without restriction; or (d) is independently developed by Receiving Party without reference to Confidential Information.

7.3. If Receiving Party is required by law to disclose Confidential Information, it shall: (a) give Disclosing Party prompt written notice, if legally permitted; (b) limit disclosure to the minimum legally required; and (c) cooperate with Disclosing Party in seeking confidential treatment or a protective order.

8. INDEMNIFICATION

8.1. Provider shall indemnify, defend, and hold harmless Customer and its officers, directors, employees, and agents from and against any third-party claim, demand, action, suit, or proceeding alleging that the Platform infringes or misappropriates any intellectual property rights of such third party. If the Platform becomes, or in Provider's opinion is likely to become, the subject of an infringement claim, Provider may, at its option and expense: (a) procure for Customer the right to continue using the Platform; (b) modify the Platform to make it non-infringing while retaining substantially equivalent functionality; (c) replace the Platform with a substantially equivalent non-infringing alternative; or (d) if (a), (b), and (c) are not commercially reasonable, terminate this Agreement and refund to Customer a pro-rata portion of any prepaid fees.

8.2. Provider's indemnification obligations under Section 8.1 shall not apply to the extent a claim arises from: (a) Customer Data; (b) use of the Platform in combination with third-party products, services, or data not provided by Provider, where the Platform alone would not give rise to the claim; (c) modifications to the Platform made by anyone other than Provider; or (d) Customer's use of the Platform in breach of this Agreement.

8.3. Customer shall indemnify, defend, and hold harmless Provider from and against any third-party claim arising from: (a) Customer Data, including any claim that Customer Data infringes or violates any third party's rights or applicable law; (b) Customer's use of the Platform in violation of applicable law; or (c) Customer's breach of Section 2.2.

8.4. The indemnified Party shall: (a) give the indemnifying Party prompt written notice of any claim; (b) give the indemnifying Party sole control of the defense and settlement; and (c) provide reasonable cooperation, at the indemnifying Party's expense. The indemnifying Party shall not settle any claim that requires the indemnified Party to admit fault or liability, pay amounts not covered by the indemnity, or take or refrain from taking any action, without the indemnified Party's prior written consent.

9. LIMITATION OF LIABILITY

9.1. EXCEPT FOR: (A) A PARTY'S INDEMNIFICATION OBLIGATIONS; (B) A PARTY'S BREACH OF CONFIDENTIALITY; (C) CUSTOMER'S BREACH OF SECTION 2.2 (LICENSE RESTRICTIONS); OR (D) A PARTY'S GROSS NEGLIGENCE, FRAUD, OR WILLFUL MISCONDUCT, IN NO EVENT SHALL EITHER PARTY BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, EXEMPLARY, OR PUNITIVE DAMAGES, INCLUDING LOST PROFITS, LOST REVENUE, LOST DATA, LOSS OF GOODWILL, OR BUSINESS INTERRUPTION, HOWEVER CAUSED AND REGARDLESS OF THE THEORY OF LIABILITY, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

9.2. EXCEPT FOR: (A) A PARTY'S INDEMNIFICATION OBLIGATIONS; OR (B) A PARTY'S GROSS NEGLIGENCE, FRAUD, OR WILLFUL MISCONDUCT, EACH PARTY'S TOTAL AGGREGATE LIABILITY FOR ALL CLAIMS ARISING OUT OF OR RELATING TO THIS AGREEMENT SHALL NOT EXCEED THE GREATER OF: (I) THE FEES PAID OR PAYABLE BY CUSTOMER TO PROVIDER DURING THE TWELVE (12) MONTHS IMMEDIATELY PRECEDING THE EVENT GIVING RISE TO THE CLAIM; OR (II) ONE MILLION DOLLARS ($1,000,000).

9.3. THE LIMITATIONS IN THIS SECTION 9 SHALL APPLY TO THE FULLEST EXTENT PERMITTED BY APPLICABLE LAW, AND SHALL APPLY REGARDLESS OF WHETHER THE LIABILITY ARISES IN CONTRACT, TORT (INCLUDING NEGLIGENCE), STRICT LIABILITY, STATUTORY LIABILITY, OR OTHERWISE.

10. REPRESENTATIONS, WARRANTIES, AND COVENANTS

10.1. Each Party represents and warrants that: (a) it is duly organized, validly existing, and in good standing under the laws of its jurisdiction of incorporation or formation; (b) it has full power and authority to enter into this Agreement and to perform its obligations hereunder; and (c) this Agreement has been duly authorized, executed, and delivered and constitutes a valid and binding obligation, enforceable in accordance with its terms.

10.2. Provider represents and warrants that: (a) the Platform will perform materially in accordance with the Documentation under normal use; (b) Provider will not materially decrease the functionality of the Platform during the Subscription Term; (c) the Platform does not contain any virus, malware, backdoor, time bomb, or other malicious code; and (d) Provider has all necessary rights, licenses, and permissions to grant the rights granted to Customer under this Agreement.

10.3. EXCEPT AS EXPRESSLY SET FORTH IN THIS AGREEMENT, PROVIDER MAKES NO WARRANTIES, EXPRESS OR IMPLIED, INCLUDING ANY IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE, NON-INFRINGEMENT, OR ACCURACY OF DATA. THE PLATFORM IS PROVIDED ON AN "AS IS" AND "AS AVAILABLE" BASIS.

11. INSURANCE

11.1. Provider shall maintain, at its own expense, the following minimum insurance coverage throughout the Subscription Term and for a period of three (3) years thereafter:

    (a) Commercial General Liability: $5,000,000 per occurrence and $10,000,000 in the aggregate, including coverage for bodily injury, property damage, and personal and advertising injury;
    (b) Technology Errors and Omissions / Professional Liability: $10,000,000 per claim and in the aggregate, covering liability arising from errors, omissions, or negligent acts in the performance of professional services, including data breach response costs;
    (c) Cyber Liability / Privacy and Network Security: $10,000,000 per claim and in the aggregate, covering breach response costs, forensic investigation, notification expenses, credit and identity monitoring, public relations, cyber extortion, and regulatory defense and penalties; and
    (d) Workers' Compensation and Employers' Liability: As required by applicable law, with Employers' Liability limits of not less than $2,000,000.

11.2. Provider shall name Customer as an additional insured on the Commercial General Liability policy and as a loss payee on the Cyber Liability policy. All policies shall be primary and non-contributory. Upon Customer's request, Provider shall provide certificates of insurance within fifteen (15) business days.

12. TERM, TERMINATION, AND TRANSITION ASSISTANCE

12.1. This Agreement commences on the Effective Date and continues for the duration of the Subscription Term. The Subscription Term shall automatically renew for successive periods equal in length to the expiring term, unless either Party provides written notice of non-renewal at least ninety (90) days prior to the end of the then-current term.

12.2. Either Party may terminate this Agreement: (a) upon thirty (30) days written notice if the other Party materially breaches any provision of this Agreement and fails to cure such breach within such 30-day period; (b) immediately upon written notice if the other Party files for, or has filed against it, a petition in bankruptcy, or makes an assignment for the benefit of creditors; or (c) as otherwise expressly provided in this Agreement.

12.3. Upon termination or expiration of this Agreement, Provider shall, within thirty (30) days: (a) make Customer Data available to Customer for electronic retrieval in a standard, machine-readable format (such as CSV, JSON, or Parquet); (b) securely and permanently delete all Customer Data from Provider's systems, except for copies retained in encrypted backups that are inaccessible to Provider's personnel and are scheduled for deletion in the ordinary course as part of Provider's backup rotation (not to exceed sixty (60) days); and (c) provide Customer with a written certification of such deletion.

12.4. During the thirty (30) day period following termination or expiration, Provider shall provide, at Customer's request and at Customer's expense (at Provider's then-current time and materials rates), reasonable transition assistance, including data migration support, to facilitate Customer's orderly transition to an alternative solution.

13. FORCE MAJEURE

13.1. Neither Party shall be liable for any failure or delay in performance (other than payment obligations) arising from circumstances beyond its reasonable control, including acts of God, natural disasters, war, terrorism, civil unrest, epidemic or pandemic, governmental action, fire, flood, earthquake, telecommunications failures, or internet disruptions; provided that the affected Party: (a) gives the other Party prompt notice; and (b) uses diligent efforts to mitigate the effects and resume performance. If a force majeure event continues for more than thirty (30) days, the unaffected Party may terminate this Agreement upon written notice.

14. COMPLIANCE WITH LAWS

14.1. Each Party shall comply with all applicable laws, regulations, and industry standards in connection with its performance under this Agreement, including: (a) United States federal, state, and local laws; (b) the laws of the Republic of India; (c) laws of any other jurisdiction applicable to the processing of Customer Data; (d) export control and economic sanctions laws administered by the U.S. Department of Commerce, U.S. Department of State, and U.S. Department of the Treasury; and (e) anti-corruption and anti-bribery laws, including the U.S. Foreign Corrupt Practices Act and the Prevention of Corruption Act, 1988 of India.

14.2. Provider represents and warrants that it is not, and shall ensure that its sub-processors are not, subject to any sanctions, embargoes, or export restrictions administered by applicable governmental authorities that would restrict or prohibit the provision of the Platform to Customer.

15. PAYMENT CARD INDUSTRY COMPLIANCE

15.1. To the extent the Platform is used to process, store, transmit, or otherwise handle payment card data, Provider shall: (a) maintain PCI DSS Level 1 Service Provider certification at all times; (b) provide Customer with a copy of Provider's current Attestation of Compliance (AOC) upon request, no more than annually; (c) ensure all third-party service providers handling payment card data on Provider's behalf maintain PCI DSS certification; and (d) not store card verification codes (CVV/CVC/CID), full track data, or PIN block data after authorization, in accordance with PCI DSS requirements.

15.2. Provider shall notify Customer within twenty-four (24) hours of becoming aware of any failure to maintain PCI DSS compliance or any breach or suspected breach of payment card data.

16. NON-COMPETE AND NON-SOLICITATION

16.1. During the Subscription Term and for a period of twelve (12) months following termination, neither Party shall, directly or indirectly: (a) solicit, induce, or hire any employee of the other Party who was materially involved in the performance, delivery, or receipt of the Platform; or (b) solicit the business of any customer or client of the other Party with whom such Party had contact or about whom such Party obtained Confidential Information through the relationship established by this Agreement. The restrictions in Section 16.1(a) shall not apply to general public solicitations not targeted at the other Party's personnel.

17. GOVERNING LAW AND DISPUTE RESOLUTION

17.1. This Agreement shall be governed by and construed in accordance with the laws of the Republic of India, without giving effect to conflict of laws principles.

17.2. Any dispute arising out of or relating to this Agreement shall be resolved through binding arbitration administered by the Singapore International Arbitration Centre (SIAC) in accordance with the SIAC Rules in effect at the time of the arbitration. The arbitration shall be conducted in English, before a panel of three (3) arbitrators. The seat of arbitration shall be Singapore. The arbitration award shall be final and binding, and judgment on the award may be entered in any court of competent jurisdiction.

17.3. Notwithstanding Section 17.2, either Party may seek injunctive or other equitable relief in any court of competent jurisdiction to protect its Confidential Information, intellectual property rights, or other proprietary interests, without the need to post bond.

18. MISCELLANEOUS

18.1. Assignment: Neither Party may assign or transfer this Agreement, by operation of law or otherwise, without the other Party's prior written consent, not to be unreasonably withheld, except that either Party may assign this Agreement to an affiliate or in connection with a merger, acquisition, or sale of all or substantially all of its assets or equity, provided the assignee assumes all obligations in writing. Any attempted assignment in violation of this Section is void.

18.2. Relationship of the Parties: The Parties are independent contractors. Nothing in this Agreement shall be construed to create a partnership, joint venture, agency, or employment relationship.

18.3. Notices: All notices shall be in writing and sent to the addresses set forth in the preamble, and shall be deemed given: (a) upon delivery, if personally delivered; (b) upon confirmation of receipt, if sent by email (provided confirmation is retained); or (c) five (5) business days after mailing, if sent by registered or certified mail, return receipt requested.

18.4. Severability: If any provision of this Agreement is held unenforceable, the remaining provisions shall continue in effect, and the Parties shall negotiate in good faith to replace the unenforceable provision with an enforceable provision that comes closest to the original intent.

18.5. Entire Agreement: This Agreement, together with all Order Forms, exhibits, and schedules, constitutes the complete agreement between the Parties and supersedes all prior agreements, whether written or oral. No modification shall be effective unless in writing and signed by both Parties.

18.6. No Third-Party Beneficiaries: This Agreement is for the sole benefit of the Parties and their successors and permitted assigns. Nothing in this Agreement shall confer any rights or remedies on any third party.

IN WITNESS WHEREOF, the Parties have executed this Agreement as of the Effective Date.

CLOUDSTACK TECHNOLOGIES PVT LTD              MERIDIAN HEALTH SERVICES INC.
Signature: ___________________               Signature: ___________________
Name: ________________________               Name: ________________________
Title: _______________________               Title: _______________________
Date: ________________________               Date: ________________________`,
  },
};
