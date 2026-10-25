import re
import fitz
import nltk
from nltk.tokenize import sent_tokenize

# Ensure tokenizer resources are available
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

SECTION_PATTERNS = {'abstract': ['^abstract$'],
 'competing_interests': ['^(?:\\d+\\.?\\s*)?(competing interests|conflict of interest|conflicts of '
                         'interest)$'],
 'conclusion': ['^(?:\\d+\\.?\\s*)?(conclusion|conclusions)$'],
 'data_availability': ['^(?:\\d+\\.?\\s*)?(data availability|availability of data and materials)$'],
 'discussion': ['^(?:\\d+\\.?\\s*)?discussion$'],
 'ethics': ['^(?:\\d+\\.?\\s*)?(ethics|ethics statement|ethical approval|ethics approval)$'],
 'experiments': ['^(?:\\d+\\.?\\s*)?experiments$'],
 'introduction': ['^(?:\\d+\\.?\\s*)?introduction$'],
 'limitations': ['^(?:\\d+\\.?\\s*)?limitations$'],
 'methods': ['^(?:\\d+\\.?\\s*)?(method|methods|materials and methods|methodology)$'],
 'references': ['^(?:\\d+\\.?\\s*)?references$'],
 'related_work': ['^(?:\\d+\\.?\\s*)?related work$'],
 'results': ['^(?:\\d+\\.?\\s*)?results$']}

STUDY_INDICATORS = {
 'animal_study': [
    # General animal-study terminology
    'animal model',
    'animal models',
    'animal study',
    'animal studies',
    'animal experiment',
    'animal experiments',
    'animal experimentation',
    'animal manipulation',
    'animal manipulations',
    'animal husbandry',

    # Common laboratory mammals
    'mouse',
    'mice',
    'rat',
    'rats',
    'rabbit',
    'rabbits',
    'hamster',
    'hamsters',
    'guinea pig',
    'guinea pigs',

    # Other common research organisms
    'zebrafish',
    'drosophila',
    'fruit fly',
    'fruit flies',
    'cricket',
    'crickets',
    'crustacean',
    'crustaceans',

    # Experimental animal procedures
    'euthanasia',
    'euthanized',
    'euthanised',
    'sacrificed',
    'anaesthetized',
    'anaesthetised'
],
'clinical_trial': [
    'clinical trial',
    'randomized controlled trial',
    'randomised controlled trial',
    'randomized trial',
    'randomised trial',
    'randomized study',
    'randomised study',
    'phase I study',
    'phase II study',
    'phase III study',
    'phase IV study',
    'phase 1 study',
    'phase 2 study',
    'phase 3 study',
    'phase 4 study',
    'trial registration',
    'ClinicalTrials.gov',
    'RCT'
],
 'computational_study': ['computational',
                         'simulation',
                         'modeling',
                         'modelling',
                         'benchmark',
                         'algorithm'],
 'human_study': ['patients',
                 'participants',
                 'subjects',
                 'volunteers',
                 'human participants',
                 'human subjects'],
 'systematic_review': ['systematic review', 'meta-analysis', 'meta analysis', 'PRISMA']}

ETHICS_INDICATORS = {'consent_waiver': ['waiver of consent',
                    'consent was waived',
                    'informed consent was waived',
                    'waived the requirement for informed consent'],
 'ethics_approval': [
    'ethics approval',
    'ethical approval',
    'ethics committee',
    'ethics committees',
    'ethical committee',
    'ethical committees',
    'institutional review board',
    'IRB',
    'research ethics committee',
    'research ethics committees',
    'ethics review board',
    'ethics review boards'
],

'accordance_statement': [
    # Generic accordance wording
    'in accordance with relevant guidelines and regulations',
    'in accordance with relevant named guidelines and regulations',
    'performed in accordance with relevant guidelines and regulations',
    'performed in accordance with relevant named guidelines and regulations',
    'conducted in accordance with relevant guidelines and regulations',
    'conducted in accordance with relevant named guidelines and regulations',
    'carried out in accordance with relevant guidelines and regulations',
    'all methods were carried out in accordance with relevant guidelines and regulations',
    'methods were carried out in accordance with relevant guidelines and regulations',

    # Declaration of Helsinki wording
    'in accordance with the declaration of helsinki',
    'in accordance with declaration of helsinki',
    'according to the declaration of helsinki',
    'complied with the declaration of helsinki',
    'compliance with the declaration of helsinki',
    'following the declaration of helsinki',
    'declaration of helsinki',

    # Alternative word order
    'helsinki declaration'
],
 'ethics_exemption': ['ethics approval was not required',
                      'ethical approval was not required',
                      'exempt from ethical review',
                      'exempt from ethics review'],
 'informed_consent': ['informed consent',
                      'written consent',
                      'written informed consent',
                      'consent to participate',
                      'participant consent']}

Mandated_Data_Rules = {'crystallographic_data': {'keywords': ['crystallographic data',
                                        'crystal structure data',
                                        'crystal structure'],
                           'repositories': ['ccdc', 'csd', 'cod']},
 'dna_rna_sequence': {'keywords': ['dna sequence',
                                   'rna sequence',
                                   'sequencing data',
                                   'sequence data',
                                   'whole genome sequencing',
                                   'rna-seq',
                                   'rna seq'],
                      'repositories': ['genbank', 'ena', 'ddbj', 'gsa']},
 'gene_expression': {'keywords': ['gene expression data', 'microarray data', 'transcriptomic data'],
                     'repositories': ['geo', 'arrayexpress']},
 'genetic_variation': {'keywords': ['genetic variation',
                                    'genetic variants',
                                    'variant data',
                                    'snp data'],
                       'repositories': ['dbsnp', 'dbvar', 'eva', 'clinvar']},
 'genome_assembly': {'keywords': ['genome assembly', 'assembled genome'],
                     'repositories': ['genbank', 'ena', 'ddbj', 'gsa']},
 'macromolecular_structure': {'keywords': ['protein structure',
                                           'macromolecular structure',
                                           'structural coordinates'],
                              'repositories': ['pdb', 'wwpdb', 'bmrb', 'emdb']},
 'protein_sequence': {'keywords': ['protein sequence', 'protein sequences'],
                      'repositories': ['uniprot']},
 'proteomics': {'keywords': ['proteomics', 'proteomic data', 'mass spectrometry data'],
                'repositories': ['proteomexchange', 'pride']},
 'sensitive_human_genomic': {'keywords': ['human genomic data',
                                          'human genome data',
                                          'human sequencing data'],
                             'repositories': ['ega', 'jga', 'dbgap']}}

Data_Availability_Patterns = ['data availability',
 'availability of data',
 'availability of data and materials',
 'data availability statement',
 'data are available',
 'data is available',
 'datasets are available',
 'dataset is available',
 'data generated during',
 'data used in this study',
 'supporting data']

Data_Access_Patterns = {'available_on_request': ['available on request',
                          'available from the corresponding author',
                          'reasonable request',
                          'upon request'],
 'public_repository': ['public repository',
                       'publicly available',
                       'deposited in',
                       'available at',
                       'figshare',
                       'zenodo',
                       'dryad'],
 'restricted': ['restricted',
                'controlled access',
                'privacy restrictions',
                'ethical restrictions',
                'legal restrictions',
                'not publicly available'],
 'supplementary_material': ['supplementary material',
                            'supplementary information',
                            'supplementary files'],
 'within_article': ['included in this article',
                    'contained within the article',
                    'within the manuscript']}

Known_Repositories = ['genbank',
 'ena',
 'ddbj',
 'gsa',
 'uniprot',
 'proteomexchange',
 'pride',
 'dbsnp',
 'dbvar',
 'eva',
 'clinvar',
 'wwpdb',
 'pdb',
 'bmrb',
 'emdb',
 'geo',
 'arrayexpress',
 'ccdc',
 'csd',
 'cod',
 'ega',
 'jga',
 'dbgap',
 'figshare',
 'zenodo',
 'dryad']

Identifier_Patterns = {'arrayexpress_accession': '\\bE-[A-Z]+-\\d+\\b',
 'doi': '\\b10\\.\\d{4,9}/[-._;()/:A-Z0-9]+\\b',
 'ega_accession': '\\bEGA[DS]\\d+\\b',
 'ena_accession': '\\b(?:ERP|ERR|ERX|ERS)\\d+\\b',
 'genbank_accession': '\\b[A-Z]{1,2}\\d{5,8}(?:\\.\\d+)?\\b',
 'geo_accession': '\\bGSE\\d+\\b',
 'sra_accession': '\\b(?:SRP|SRA|SRR|SRX|SRS)\\d+\\b'}

Center_Indicators = {'multi_center': [
                 'multicenter',
                 'multicentre',
                 'multi-center',
                 'multi-centre',
                 'multiple centers',
                 'multiple centres',
                 'multiple hospitals',
                 'multiple institutions',
                 'multiple sites',
                 'multiple study sites'],
 'single_center': ['single-center',
                   'single-centre',
                   'single center',
                   'single centre',
                   'single institution',
                   'single hospital',
                   'one hospital',
                   'one center',
                   'one centre']}

Cam_Indicators = {'acupuncture': ['acupuncture', 'electroacupuncture', 'electro-acupuncture'],
 'herbal_medicine': ['herbal medicine',
                     'herbal therapy',
                     'herbal treatment',
                     'herbal remedy',
                     'herbal remedies'],
 'homeopathy': ['homeopathy', 'homeopathic'],
 'manual_therapy': ['chiropractic', 'chiropractic therapy'],
 'mind_body': ['meditation', 'mindfulness', 'yoga', 'tai chi', 'qigong'],
 'traditional_medicine': ['traditional medicine',
                          'traditional chinese medicine',
                          'ayurveda',
                          'ayurvedic medicine',
                          'unani medicine']}

Durc_Indicators = {'biological_agent': ['pathogen',
                      'virus',
                      'bacterium',
                      'bacteria',
                      'toxin',
                      'infectious agent',
                      'microorganism'],
 'experimental_action': ['genetically modified',
                         'genetic modification',
                         'engineered strain',
                         'engineered virus',
                         'modified strain',
                         'serial passage',
                         'host range',
                         'immune evasion'],
 'risk_context': ['increased virulence',
                  'enhanced virulence',
                  'increased pathogenicity',
                  'enhanced pathogenicity',
                  'increased transmissibility',
                  'enhanced transmissibility',
                  'resistance to treatment',
                  'drug resistance',
                  'immune escape']}
p_value_pattern = r'\bp\s*[=<>≤≥]\s*0?\.\d+\b'
SIGNIFICANCE_THRESHOLD = 0.05

SAMPLE_NUMBER_PATTERN = r'(?:\d{1,3}(?:,\d{3})*|\d+)'

SAMPLE_SIZE_PATTERNS = [
    rf'\b[nN]\s*=\s*{SAMPLE_NUMBER_PATTERN}\b',

    rf'\b{SAMPLE_NUMBER_PATTERN}\s+patients?\b',
    rf'\b{SAMPLE_NUMBER_PATTERN}\s+participants?\b',
    rf'\b{SAMPLE_NUMBER_PATTERN}\s+subjects?\b',
    rf'\b{SAMPLE_NUMBER_PATTERN}\s+individuals?\b',
    rf'\b{SAMPLE_NUMBER_PATTERN}\s+volunteers?\b',

    # Pediatric / neonatal participant terms
    rf'\b{SAMPLE_NUMBER_PATTERN}\s+newborns?\b',
    rf'\b{SAMPLE_NUMBER_PATTERN}\s+babies\b',

    rf'\bsample\s+of\s+{SAMPLE_NUMBER_PATTERN}\b',

    rf'\btotal\s+of\s+{SAMPLE_NUMBER_PATTERN}\s+'
    rf'(?:patients?|participants?|subjects?|individuals?|'
    rf'newborns?|babies)\b'
]
Sample_size_roles = {'ANALYZED': ['analyzed', 'analysed', 'included in the analysis', 'included in the final analysis'],
 'COMPLETED': ['completed the study', 'completed follow-up', 'completed treatment'],
 'ENROLLED': ['enrolled', 'recruited', 'included in the study'],
 'EXCLUDED': ['excluded', 'removed', 'lost to follow-up', 'withdrew', 'withdrawn'],
 'RANDOMIZED': ['randomized', 'randomised', 'assigned']}

computational_reproducibility_indicators = {'code_availability': ['code availability', 'source code', 'github', 'gitlab', 'code repository'],
 'evaluation_metrics': ['evaluation metric',
                        'evaluation metrics',
                        'performance metric',
                        'performance metrics',
                        'benchmark metric',
                        'benchmark metrics',
                        'primary metric',
                        'accuracy',
                        'precision',
                        'recall',
                        'f1 score',
                        'auc'],
 'initial_conditions': ['initial conditions', 'initial condition'],
 'model_parameters': ['parameter values',
                      'parameters were set',
                      'parameter estimates',
                      'model parameters'],
 'numerical_solver': ['ode solver', 'numerical solver', 'integration method', 'integration scheme'],
 'optimizer': ['optimizer', 'optimiser', 'optimization method', 'optimisation method'],
 'parameter_bounds': ['parameter bounds', 'parameter range', 'parameter ranges'],
 'random_seed': ['random seed', 'random seeds', 'seed value'],
 'simulation_setup': ['simulation setup',
                      'simulation settings',
                      'synthetic data',
                      'synthetic dataset',
                      'synthetic datasets',
                      'synthetic outbreak',
                      'synthetic outbreaks'],
 'software_environment': ['python',
                          'r version',
                          'matlab',
                          'software version',
                          'package version',
                          'library version',
                          'software environment'],
 'tolerance_settings': ['tolerance settings',
                        'solver tolerance',
                        'solver tolerances',
                        'convergence tolerance',
                        'convergence criterion',
                        'convergence criteria']}

reproducibility_sections = ['methods', 'experiments']

missing_information_patterns = ['\\bnot reported\\b',
 '\\bnot provided\\b',
 '\\bnot specified\\b',
 '\\bnot described\\b',
 '\\bnot available\\b',
 '\\bunavailable\\b',
 '\\bdoes not preserve\\b',
 '\\bnot preserved\\b',
 '\\bwas not reported\\b',
 '\\bwere not reported\\b',
 '\\bwas not specified\\b',
 '\\bwere not specified\\b']

PLACEHOLDER_VALUE_PATTERNS = ['\\s—\\s',
 '\\s–\\s',
 '\\s-\\s',
 '\\bnot available\\b',
 '\\bunavailable\\b',
 '\\bnot reported\\b',
 '\\bnot specified\\b']



def detect_heading(line):

  cleaned = line.strip().lower()

  for section, patterns in SECTION_PATTERNS.items():

    for pattern in patterns:

      if re.match(pattern, cleaned, re.IGNORECASE):

        return section

  return None



def extract_sections(lines):

    sections = {}
 
    # Text before the first recognized manuscript
    # heading is preserved as front/title material.
    current_section = "title"
    current_text = []

    # Inline section headings that may contain text
    inline_heading_patterns = {
        "data_availability": [
            r"^\s*data availability\s*:\s*(.*)$",
            r"^\s*availability of data and materials\s*:\s*(.*)$"
        ],
        "competing_interests": [
            r"^\s*competing interests\s*:\s*(.*)$",
            r"^\s*conflict of interest\s*:\s*(.*)$",
            r"^\s*conflicts of interest\s*:\s*(.*)$"
        ]
    }

    for line in lines:

        # -----------------------------------------
        # 1. Check for inline heading + content
        # -----------------------------------------

        inline_match_found = False

        for section_name, patterns in inline_heading_patterns.items():

            for pattern in patterns:

                match = re.match(
                    pattern,
                    line,
                    flags=re.IGNORECASE
                )

                if match:

                    # Save previous section
                    if current_section is not None:
                        sections[current_section] = "\n".join(
                            current_text
                        ).strip()

                    # Start new section
                    current_section = section_name
                    current_text = []

                    # IMPORTANT:
                    # preserve text after the colon
                    remaining_text = match.group(1).strip()

                    if remaining_text:
                        current_text.append(remaining_text)

                    inline_match_found = True
                    break

            if inline_match_found:
                break

        if inline_match_found:
            continue

        # -----------------------------------------
        # 2. Normal standalone heading detection
        # -----------------------------------------

        detected_section = detect_heading(line)

        if detected_section:

            # Save previous section
            if current_section is not None:
                sections[current_section] = "\n".join(
                    current_text
                ).strip()

            # Start new section
            current_section = detected_section
            current_text = []

        else:

            # Add text to current section
            if current_section is not None:
                current_text.append(line)

    # Save final section
    if current_section is not None:
        sections[current_section] = "\n".join(
            current_text
        ).strip()

    return sections


def detect_study_characters(text):

    results = {}

    for study_type, keywords in STUDY_INDICATORS.items():

        matches = []

        for keyword in keywords:

            # Match complete words/phrases only
            pattern = r'\b' + re.escape(keyword) + r'\b'

            if re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            ):
                matches.append(keyword)

        # --------------------------------------------------
        # Animal-study logic
        # --------------------------------------------------

        if study_type == "animal_study":

            strong_indicators = {
                "animal model",
                "animal models",
                "animal study",
                "animal studies",
                "animal experiment",
                "animal experiments",
                "animal experimentation",
                "animal manipulation",
                "animal manipulations",
                "animal husbandry",
                "euthanasia",
                "euthanized",
                "euthanised",
                "sacrificed",
                "anaesthetized",
                "anaesthetised"
            }

            species_indicators = {
                "mouse",
                "mice",
                "rat",
                "rats",
                "rabbit",
                "rabbits",
                "hamster",
                "hamsters",
                "guinea pig",
                "guinea pigs",
                "zebrafish",
                "drosophila",
                "fruit fly",
                "fruit flies",
                "cricket",
                "crickets",
                "crustacean",
                "crustaceans"
            }

            strong_matches = [
                match for match in matches
                if match.lower() in strong_indicators
            ]

            species_matches = [
                match for match in matches
                if match.lower() in species_indicators
            ]

            # Animal study detected when:
            # 1. At least one strong experimental animal
            #    indicator is present, OR
            # 2. Multiple distinct species indicators occur.
            #
            # This avoids classifying a manuscript as an
            # animal study from one incidental species mention.
            detected = (
                len(strong_matches) >= 1
                or len(set(
                    match.lower()
                    for match in species_matches
                )) >= 2
            )

        # --------------------------------------------------
        # Computational-study logic
        # --------------------------------------------------

        elif study_type == "computational_study":

            strong_indicators = {
                "computational",
                "simulation",
                "benchmark"
            }

            weak_indicators = {
                "modeling",
                "modelling",
                "algorithm"
            }

            strong_matches = [
                match for match in matches
                if match.lower() in strong_indicators
            ]

            weak_matches = [
                match for match in matches
                if match.lower() in weak_indicators
            ]

            detected = (
                len(strong_matches) >= 1
                or len(set(weak_matches)) >= 2
            )

        # --------------------------------------------------
        # Systematic-review logic
        # --------------------------------------------------

        elif study_type == "systematic_review":

            strong_indicators = {
                "systematic review",
                "prisma"
            }

            weak_indicators = {
                "meta-analysis",
                "meta analysis"
            }

            strong_matches = [
                match for match in matches
                if match.lower() in strong_indicators
            ]

            weak_matches = [
                match for match in matches
                if match.lower() in weak_indicators
            ]

            detected = (
                len(strong_matches) >= 1
                or len(set(weak_matches)) >= 2
            )

        # --------------------------------------------------
        # All other study types
        # --------------------------------------------------

        else:

            detected = len(matches) > 0

        results[study_type] = {
            "detected": detected,
            "matches": matches
        }

    return results


def ethics_indicator_evidence(sections, indicators):

    results = {}

    for category, keywords in indicators.items():

        evidence = []

        for section_name, section_text in sections.items():

            # Skip references
            if section_name == "references":
                continue

            # Normalize PDF whitespace
            normalized_text = re.sub(
                r'\s+',
                ' ',
                section_text
            ).strip()

            sentences = sent_tokenize(
                normalized_text
            )

            for sentence in sentences:

                # Normalize sentence whitespace
                normalized_sentence = re.sub(
                    r'\s+',
                    ' ',
                    sentence
                ).strip()

                for keyword in keywords:

                    normalized_keyword = re.sub(
                        r'\s+',
                        ' ',
                        keyword
                    ).strip()

                    pattern = (
                        r'\b'
                        + re.escape(normalized_keyword)
                        + r'\b'
                    )

                    if re.search(
                        pattern,
                        normalized_sentence,
                        flags=re.IGNORECASE
                    ):

                        evidence.append({
                            "keyword": keyword,
                            "section": section_name,
                            "sentence": normalized_sentence
                        })

                        break

        results[category] = {
            "detected": len(evidence) > 0,
            "evidence": evidence
        }

    return results


def evaluate_ethics_screening(
    study_characteristics,
    ethics_results
):

    human = study_characteristics[
        "human_study"
    ]["detected"]

    animal = study_characteristics[
        "animal_study"
    ]["detected"]

    clinical = study_characteristics[
        "clinical_trial"
    ]["detected"]

    computational = study_characteristics[
        "computational_study"
    ]["detected"]

    systematic_review = study_characteristics[
        "systematic_review"
    ]["detected"]

    ethics_found = ethics_results[
        "ethics_approval"
    ]["detected"]

    consent_found = ethics_results[
        "informed_consent"
    ]["detected"]

    accordance_found = ethics_results.get(
        "accordance_statement",
        {"detected": False}
    )["detected"]

    waiver_found = ethics_results[
        "consent_waiver"
    ]["detected"]

    exemption_found = ethics_results[
        "ethics_exemption"
    ]["detected"]


    # --------------------------------------------------
    # SYSTEMATIC REVIEW / META-ANALYSIS
    # --------------------------------------------------
    # Secondary research does not directly recruit
    # participants or conduct new animal experiments.
    #
    # Mentions of patients, participants, ethics approval,
    # or consent may describe included primary studies.
    # --------------------------------------------------

    if systematic_review:

        ethics_status = "NOT_APPLICABLE"
        consent_status = "NOT_APPLICABLE"


    # --------------------------------------------------
    # HUMAN / CLINICAL STUDY
    # --------------------------------------------------

    elif human or clinical:

        if ethics_found:
            ethics_status = "PASS"

        elif exemption_found:
            ethics_status = "REVIEW_EXEMPTION"

        else:
            ethics_status = "REVIEW_MISSING"


        if consent_found:
            consent_status = "PASS"

        elif waiver_found:
            consent_status = "REVIEW_WAIVER"

        else:
            consent_status = "REVIEW_MISSING"


    # --------------------------------------------------
    # ANIMAL STUDY
    # --------------------------------------------------

    elif animal:

        ethics_status = "REVIEW_ANIMAL_ETHICS"
        consent_status = "NOT_APPLICABLE"


    # --------------------------------------------------
    # COMPUTATIONAL / SYNTHETIC STUDY
    # --------------------------------------------------

    elif computational or synthetic:

        ethics_status = "NOT_TRIGGERED"
        consent_status = "NOT_TRIGGERED"


    # --------------------------------------------------
    # UNKNOWN STUDY TYPE
    # --------------------------------------------------

    else:

        ethics_status = "UNDETERMINED"
        consent_status = "UNDETERMINED"


    return {
        "ethics_status": ethics_status,
        "consent_status": consent_status,
        "ethics_statement_detected": ethics_found,
        "consent_statement_detected": consent_found,
        "consent_waiver_detected": waiver_found,
        "ethics_exemption_detected": exemption_found,
        "accordance_statement_detected": accordance_found
    }

def detect_mandated_data(sections):

    findings = []

    for section_name, section_text in sections.items():

        if section_name == "references":
            continue

        sentences = sent_tokenize(section_text)

        for sentence in sentences:

            for data_type, rule in Mandated_Data_Rules.items():

                matched_keywords = []

                for keyword in rule["keywords"]:

                    pattern = (
                        r'\b'
                        + re.escape(keyword)
                        + r'\b'
                    )

                    if re.search(
                        pattern,
                        sentence,
                        flags=re.IGNORECASE
                    ):
                        matched_keywords.append(keyword)

                if matched_keywords:

                    findings.append({
                        "data_type": data_type,
                        "section": section_name,
                        "keywords": matched_keywords,
                        "evidence": sentence.strip()
                    })

    return findings



def detect_data_availability_statement(sections):
 

    evidence = []

    # rest of your existing function continues...

 

   

    # -----------------------------------------
    # 1. Strongest evidence:
    #    dedicated Data Availability section
    # -----------------------------------------

    if "data_availability" in sections:

        section_text = sections["data_availability"].strip()

        if section_text:

            evidence.append({
                "section": "data_availability",
                "keyword": "dedicated_section",
                "sentence": section_text
            })

    # -----------------------------------------
    # 2. Explicit availability statements
    # -----------------------------------------

    strong_patterns = [

        r"\bdata (?:are|is) available\b",

        r"\bdatasets? (?:are|is) available\b",

        # Handles:
        # "datasets generated during ... are available"
        r"\bdatasets?\b.{0,200}?\b(?:are|is) available\b",

        r"\bdata (?:can|may) be accessed\b",

        r"\bdata (?:can|may) be obtained\b",

        r"\bdata (?:are|is) deposited\b",

        r"\bdata underlying (?:this|the) (?:study|article)\b",

        r"\bdata generated (?:during|in) this study\b",

        r"\bdata supporting (?:the|this) (?:findings|study)\b",

        # Common available-on-request wording
        r"\bavailable from the corresponding author\b",

        r"\bavailable (?:from|upon) reasonable request\b",

        r"\bavailable (?:on|upon) request\b"
    ]

    for section_name, section_text in sections.items():

        if section_name == "references":
            continue

        # Normalize PDF whitespace
        normalized_text = re.sub(
            r"\s+",
            " ",
            section_text
        ).strip()

        sentences = sent_tokenize(normalized_text)

        for sentence in sentences:

            for pattern in strong_patterns:

                if re.search(
                    pattern,
                    sentence,
                    flags=re.IGNORECASE
                ):

                    evidence.append({
                        "section": section_name,
                        "keyword": pattern,
                        "sentence": sentence.strip()
                    })

                    break

    return {
        "detected": len(evidence) > 0,
        "evidence": evidence
    }



def build_das_text(das_result):

    evidence_sentences = []

    for item in das_result["evidence"]:
        evidence_sentences.append(
            item["sentence"]
        )

    das_text = " ".join(evidence_sentences)

    # ---------------------------------------------
    # Stop DAS text when the next manuscript
    # declaration/section begins
    # ---------------------------------------------

    stop_headings = [
        "authors contributions",
        "author contributions",
        "authors' contributions",
        "author's contributions",
        "acknowledgements",
        "acknowledgments",
        "competing interests",
        "conflict of interest",
        "conflicts of interest",
        "funding",
        "references"
    ]

    # Find the earliest following section heading
    stop_positions = []

    for heading in stop_headings:

        match = re.search(
            r'\b' + re.escape(heading) + r'\b',
            das_text,
            flags=re.IGNORECASE
        )

        if match:
            stop_positions.append(
                match.start()
            )

    if stop_positions:

        das_text = das_text[
            :min(stop_positions)
        ]

    # Normalize whitespace
    das_text = re.sub(
        r'\s+',
        ' ',
        das_text
    ).strip()

    return das_text



def detect_persistent_identifiers(text):

    identifiers = {}

    for identifier_type, pattern in Identifier_Patterns.items():

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if matches:
            identifiers[identifier_type] = list(
                dict.fromkeys(matches)
            )

    return identifiers



def determine_data_access_type(das_result, repositories_found=None):

    if not das_result["detected"]:
        return ["NOT_ASSESSABLE"]

    das_text = " ".join(
        item["sentence"]
        for item in das_result["evidence"]
    )

    text_lower = das_text.lower()

    # ----------------------------------
    # 1. NO NEW DATA / NOT APPLICABLE
    # ----------------------------------
    # Common in systematic reviews,
    # reviews, commentaries, and other
    # secondary-research manuscripts.
    # ----------------------------------

    no_new_data_patterns = [
        r"\bno datasets? (?:were|was) generated\b",
        r"\bno datasets? (?:were|was) generated or analysed\b",
        r"\bno datasets? (?:were|was) generated or analyzed\b",
        r"\bno new data (?:were|was) generated\b",
        r"\bno new datasets? (?:were|was) generated\b",
        r"\bdata sharing is not applicable\b",
        r"\bdata availability is not applicable\b",
        r"\bnot applicable to this article as no datasets?\b"
    ]

    for pattern in no_new_data_patterns:

        if re.search(pattern, text_lower):
            return ["not_applicable"]

    # ----------------------------------
    # 2. RESTRICTED ACCESS
    # ----------------------------------

    restricted_patterns = [
        r"\bnot publicly available\b",
        r"\brestricted access\b",
        r"\bcontrolled access\b",
        r"\bprivacy restrictions?\b",
        r"\bethical restrictions?\b",
        r"\blegal restrictions?\b"
    ]

    for pattern in restricted_patterns:

        if re.search(pattern, text_lower):
            return ["restricted"]

    # ----------------------------------
    # 3. AVAILABLE ON REQUEST
    # ----------------------------------

    request_patterns = [
        r"\bavailable on request\b",
        r"\bupon reasonable request\b",
        r"\bupon request\b",
        r"\bavailable from the corresponding author\b"
    ]

    for pattern in request_patterns:

        if re.search(pattern, text_lower):
            return ["available_on_request"]

    # ----------------------------------
    # 4. PUBLIC REPOSITORY
    # ----------------------------------

    public_patterns = [
        r"\bpublicly available\b",
        r"\bpublic repository\b",
        r"\bdeposited in\b",
        r"\bdeposited at\b",
        r"\bavailable in zenodo\b",
        r"\bavailable in figshare\b",
        r"\bavailable in dryad\b"
    ]

    for pattern in public_patterns:

        if re.search(pattern, text_lower):
            return ["public_repository"]

    # ----------------------------------
    # 5. SUPPLEMENTARY MATERIAL
    # ----------------------------------

    supplementary_patterns = [
        r"\bsupplementary material\b",
        r"\bsupplementary information\b",
        r"\bsupplementary files\b"
    ]

    for pattern in supplementary_patterns:

        if re.search(pattern, text_lower):
            return ["supplementary_material"]

    # ----------------------------------
    # 6. WITHIN ARTICLE
    # ----------------------------------

    article_patterns = [
        r"\bincluded in this article\b",
        r"\bcontained within the article\b",
        r"\bwithin the manuscript\b"
    ]

    for pattern in article_patterns:

        if re.search(pattern, text_lower):
            return ["within_article"]

    # ----------------------------------
    # 7. Repository already detected
    # ----------------------------------

    if repositories_found:
        return ["repository_deposition"]

    return ["UNCLEAR"]


def evaluate_data_availability(
    mandated_findings,
    das_result,
    data_access_types,
    repositories_found,
    identifiers_found
):

    mandated = len(mandated_findings) > 0
    statement_found = das_result["detected"]

    repository_found = len(repositories_found) > 0
    identifier_found = len(identifiers_found) > 0


    # ==========================================
    # MANDATED DATA
    # ==========================================

    if mandated:

        applicability = "MANDATED"

        if not statement_found:

            status = "REVIEW"

            reason = (
                "Potential mandated data were detected, "
                "but no clear Data Availability Statement "
                "was identified."
            )

        elif not repository_found:

            status = "REVIEW"

            reason = (
                "Potential mandated data and a Data "
                "Availability Statement were detected, "
                "but no recognised repository was identified."
            )

        elif not identifier_found:

            status = "REVIEW"

            reason = (
                "A repository was detected for potential "
                "mandated data, but no persistent identifier "
                "or accession number was identified."
            )

        else:

            status = "PASS_CANDIDATE"

            reason = (
                "Potential mandated data, a Data Availability "
                "Statement, repository information, and a "
                "persistent identifier were detected. "
                "Editorial verification is still recommended."
            )


    # ==========================================
    # NON-MANDATED DATA
    # ==========================================

    else:

        applicability = "NON_MANDATED"

        if not statement_found:

            status = "REVIEW"

            reason = (
                "No mandated-data indicators were detected, "
                "but no clear Data Availability Statement "
                "was identified."
            )

        else:

            if "UNCLEAR" in data_access_types:

                status = "REVIEW"

                reason = (
                    "A Data Availability Statement was detected, "
                    "but the data access conditions could not be "
                    "clearly determined."
                )

            else:

                status = "PASS_CANDIDATE"

                reason = (
                    "A Data Availability Statement with identifiable "
                    "data access information was detected. "
                    "Editorial verification is recommended."
                )



    return {

        "applicability": applicability,

        "statement_detected":
            statement_found,

        "access_type":
            data_access_types,

        "repositories":
            repositories_found,

        "persistent_identifiers":
            identifiers_found,

        "status":
            status,

        "reason":
            reason
    }



def detect_repositories(text):

    repositories = []

    for repository in Known_Repositories:

        pattern = (
            r'\b'
            + re.escape(repository)
            + r'\b'
        )

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):
            repositories.append(repository)

    return repositories



def determine_center_applicability(study_characteristics):

    human = study_characteristics["human_study"]["detected"]

    clinical = study_characteristics["clinical_trial"]["detected"]

    if human or clinical:
        return "APPLICABLE"

    return "NOT_APPLICABLE"



def detect_center_evidence(sections):

  findings= {
      "single_center":[],
      "multi_center":[]
  }

  # Prioritize sections describing study design
  preferred_section = ["methods","experiments","abstract"]

  for section_name in preferred_section:

    if section_name not in sections:
      continue

    section_text = sections[section_name]

    for sentence in sent_tokenize(section_text):
      for center_type, keywords in Center_Indicators.items():
         for keyword in keywords:
          pattern = (r'\b' + re.escape(keyword) + r'\b')

          if re.search(pattern, sentence, flags=re.IGNORECASE):

            findings[center_type].append({
                "sention": section_name,
                "keywors": keyword,
                "evidence" : sentence.strip()
            })

            break

  return findings



def evaluate_center_screening(
    study_characters,
    center_findings
):

    # --------------------------------------------------
    # SYSTEMATIC REVIEW / META-ANALYSIS
    # --------------------------------------------------
    # Center/site classification describes the design
    # of a primary study.
    #
    # A systematic review may discuss single-center or
    # multicenter studies without itself being either.
    # --------------------------------------------------

    systematic_review = study_characters.get(
        "systematic_review",
        {"detected": False}
    )["detected"]

    if systematic_review:

        return {
            "applicability": "NOT_APPLICABLE",
            "classification": "NOT_ASSESSABLE",
            "status": "NOT_TRIGGERED",
            "reason": (
                "Center/site classification is not "
                "applicable to a systematic review "
                "or meta-analysis."
            )
        }


    # --------------------------------------------------
    # NORMAL APPLICABILITY CHECK
    # --------------------------------------------------

    applicability = determine_center_applicability(
        study_characters
    )

    # Not a human/clinical study
    if applicability == "NOT_APPLICABLE":

        return {
            "applicability": "NOT_APPLICABLE",
            "classification": "NOT_ASSESSABLE",
            "status": "NOT_TRIGGERED",
            "reason": (
                "No human or clinical study indicators "
                "were detected."
            )
        }


    single_found = (
        len(center_findings["single_center"]) > 0
    )

    multi_found = (
        len(center_findings["multi_center"]) > 0
    )


    # --------------------------------------------------
    # Explicit single-center evidence
    # --------------------------------------------------

    if single_found and not multi_found:

        return {
            "applicability": "APPLICABLE",
            "classification": "SINGLE_CENTER",
            "status": "DETECTED",
            "reason": (
                "Explicit single-center study "
                "language was detected."
            )
        }


    # --------------------------------------------------
    # Explicit multi-center evidence
    # --------------------------------------------------

    elif multi_found and not single_found:

        return {
            "applicability": "APPLICABLE",
            "classification": "MULTI_CENTER",
            "status": "DETECTED",
            "reason": (
                "Explicit multi-center study "
                "language was detected."
            )
        }


    # --------------------------------------------------
    # Conflicting evidence
    # --------------------------------------------------

    elif single_found and multi_found:

        return {
            "applicability": "APPLICABLE",
            "classification": "CONFLICTING",
            "status": "REVIEW",
            "reason": (
                "Both single-center and multi-center "
                "language were detected."
            )
        }


    # --------------------------------------------------
    # Human study, but center type unclear
    # --------------------------------------------------

    else:

        return {
            "applicability": "APPLICABLE",
            "classification": "UNDETERMINED",
            "status": "REVIEW",
            "reason": (
                "The center/site configuration could "
                "not be determined from explicit study "
                "design language."
            )
        }


def detect_center_evidence(sections):

    findings = {
        "single_center": [],
        "multi_center": []
    }

    # Sections most likely to contain study-design information
    preferred_sections = [
        "title",
        "abstract",
        "methods",
        "experiments"
    ]

    for section_name in preferred_sections:

        if section_name not in sections:
            continue

        section_text = sections[section_name]

        # Normalize PDF whitespace
        normalized_text = re.sub(
            r'\s+',
            ' ',
            section_text
        ).strip()

        for sentence in sent_tokenize(normalized_text):

            # ----------------------------------------------
            # 1. Explicit center terminology
            # ----------------------------------------------
            for center_type, keywords in Center_Indicators.items():

                for keyword in keywords:

                    normalized_keyword = re.sub(
                        r'\s+',
                        ' ',
                        keyword
                    ).strip()

                    pattern = (
                        r'\b'
                        + re.escape(normalized_keyword)
                        + r'\b'
                    )

                    if re.search(
                        pattern,
                        sentence,
                        flags=re.IGNORECASE
                    ):

                        findings[center_type].append({
                            "section": section_name,
                            "keyword": keyword,
                            "evidence": sentence.strip()
                        })

                        break

            # ----------------------------------------------
            # 2. Contextual multi-center terminology
            # Examples:
            # "six clinics"
            # "3 hospitals"
            # "four centres"
            # "12 study sites"
            # ----------------------------------------------

            number_words = (
                r'two|three|four|five|six|seven|eight|nine|ten'
            )

            multi_site_pattern = (
                r'\b(?:'
                + number_words
                + r'|\d+)'
                + r'\s+'
                + r'(?:centers|centres|sites|clinics|'
                  r'hospitals|institutions)\b'
            )

            if re.search(
                multi_site_pattern,
                sentence,
                flags=re.IGNORECASE
            ):

                findings["multi_center"].append({
                    "section": section_name,
                    "keyword": "multiple-site expression",
                    "evidence": sentence.strip()
                })

    return findings

def detect_cam_evidence(sections):

    findings = []

    # Sections most relevant for intervention / treatment detection
    preferred_sections = [
        "abstract",
        "methods",
        "experiments",
        "results"
    ]

    for section_name in preferred_sections:

        if section_name not in sections:
            continue

        section_text = sections[section_name]

        # Normalize whitespace from PDF extraction
        normalized_text = re.sub(
            r'\s+',
            ' ',
            section_text
        ).strip()

        for sentence in sent_tokenize(normalized_text):

            for category, keywords in Cam_Indicators.items():

                for keyword in keywords:

                    normalized_keyword = re.sub(
                        r'\s+',
                        ' ',
                        keyword
                    ).strip()

                    pattern = (
                        r'\b'
                        + re.escape(normalized_keyword)
                        + r'\b'
                    )

                    if re.search(
                        pattern,
                        sentence,
                        flags=re.IGNORECASE
                    ):

                        findings.append({
                            "category": category,
                            "keyword": keyword,
                            "section": section_name,
                            "evidence": sentence.strip()
                        })

                        # One finding per CAM category per sentence
                        break

    return findings


def evaluate_cam_screening(cam_findings):

    if len(cam_findings) == 0:

        return {
            "cam_detected": False,
            "categories": [],
            "status": "NOT_DETECTED",
            "reason": (
                "No predefined complementary or alternative "
                "medicine indicators were detected."
            )
        }

    categories = sorted(
        set(
            finding["category"]
            for finding in cam_findings
        )
    )

    return {
        "cam_detected": True,
        "categories": categories,
        "status": "REVIEW",
        "reason": (
            "Potential complementary or alternative medicine "
            "content was detected. Editorial verification "
            "is recommended."
        )
    }



def detect_durc_evidence(sections):

    findings = {
        "biological_agent": [],
        "experimental_action": [],
        "risk_context": []
    }

    for section_name, section_text in sections.items():

        if section_name == "references":
            continue

        sentences = sent_tokenize(section_text)

        for sentence in sentences:

            for signal_type, keywords in Durc_Indicators.items():

                for keyword in keywords:

                    pattern = (
                        r'\b'
                        + re.escape(keyword)
                        + r'\b'
                    )

                    if re.search(
                        pattern,
                        sentence,
                        flags=re.IGNORECASE
                    ):

                        findings[signal_type].append({
                            "keyword": keyword,
                            "section": section_name,
                            "evidence": sentence.strip()
                        })

                        # One keyword per signal type
                        # per sentence is enough
                        break

    return findings



def evaluate_durc_screening(durc_findings):

    agent_found = (len(durc_findings["biological_agent"]) > 0)

    action_found = (len(durc_findings["experimental_action"]) > 0)

    risk_found = (len(durc_findings["risk_context"]) > 0)

    # Strongest combination
    if (
        agent_found
        and action_found
        and risk_found
    ):

        return {
            "biological_agent_detected": True,
            "experimental_action_detected": True,
            "risk_context_detected": True,
            "classification": "POTENTIAL_DURC",
            "status": "REVIEW",
            "reason": (
                "Biological-agent, experimental-action, "
                "and risk-related indicators were detected. "
                "Specialist editorial review is recommended."
            )
        }

    # Some relevant signals, but insufficient
    elif agent_found and action_found:

        return {
            "biological_agent_detected": True,
            "experimental_action_detected": True,
            "risk_context_detected": risk_found,
            "classification": "POSSIBLE_RELEVANCE",
            "status": "REVIEW",
            "reason": (
                "Biological-agent and experimental-action "
                "indicators were detected, but the available "
                "signals are insufficient for stronger "
                "classification."
            )
        }

    # Agent alone should NOT trigger DURC
    else:

        return {
            "biological_agent_detected": agent_found,
            "experimental_action_detected": action_found,
            "risk_context_detected": risk_found,
            "classification": "NOT_TRIGGERED",
            "status": "NOT_DETECTED",
            "reason": (
                "The combination of indicators required "
                "for DURC screening was not detected."
            )
        }



def extract_pvalues_by_section(sections):

  findings = []

  for section_name, section_text in sections.items():
    if section_name == "references":
      continue
    sentences = sent_tokenize(section_text)
    for sentence in sentences:
      matches = re.findall(p_value_pattern, sentence, flags=re.IGNORECASE)

      for match in matches:
        findings.append({
            "section": section_name,
            "value": match,
            "context":sentence.strip()
        })
  return findings



def  parse_pvalue(p_text):
  operator_match = re.search(r'[=<>≤≥]',p_text)
  value_match = re.search(r'0?\.\d+',p_text)
  operator = (operator_match.group() if operator_match else None)
  value = (float(value_match.group()) if value_match else None)
  return {
      "operator": operator,
      "numeric_value": value
  }



def compare_abstract_results_pvalues(
    pvalue_findings
):

    abstract_values = [
        finding
        for finding in pvalue_findings
        if finding["section"] == "abstract"
    ]

    results_values = [
        finding
        for finding in pvalue_findings
        if finding["section"] == "results"
    ]

    # No p-value in abstract
    if not abstract_values:

        return {
            "status": "NOT_APPLICABLE",
            "reason": (
                "No p-value was detected in the abstract."
            ),
            "abstract_pvalues": [],
            "results_pvalues": []
        }

    # Abstract reports p-value but Results does not
    if not results_values:

        return {
            "status": "REVIEW",
            "reason": (
                "A p-value was reported in the abstract, "
                "but no p-value was detected in the Results section."
            ),
            "abstract_pvalues": [
                x["numeric_value"]
                for x in abstract_values
            ],
            "results_pvalues": []
        }

    abstract_numbers = {
        x["numeric_value"]
        for x in abstract_values
    }

    results_numbers = {
        x["numeric_value"]
        for x in results_values
    }

    common_values = (
        abstract_numbers
        & results_numbers
    )

    if common_values:

        return {
            "status": "PASS_CANDIDATE",
            "reason": (
                "At least one p-value reported in the abstract "
                "was also detected in the Results section."
            ),
            "abstract_pvalues": sorted(
                abstract_numbers
            ),
            "results_pvalues": sorted(
                results_numbers
            ),
            "matched_pvalues": sorted(
                common_values
            )
        }

    return {
        "status": "DISCREPANCY",
        "reason": (
            "P-values were detected in both the abstract "
            "and Results section, but no matching numerical "
            "values were identified."
        ),
        "abstract_pvalues": sorted(
            abstract_numbers
        ),
        "results_pvalues": sorted(
            results_numbers
        ),
        "matched_pvalues": []
    }



def detect_significance_claims(text):

    claims = []

    sentences = sent_tokenize(text)

    for sentence in sentences:

        # Normalize whitespace caused by PDF extraction
        normalized = re.sub(
            r'\s+',
            ' ',
            sentence
        ).strip().lower()

        # ---------------------------------
        # NOT SIGNIFICANT
        # Check negative forms FIRST
        # ---------------------------------

        negative_patterns = [

            r'\bnot\s+statistically\s+significant\b',

            r'\bnot\s+significant\b',

            r'\bnon[\s-]?significant\b',

            r'\bnonsignificant\b',

            r'\bno\s+statistically\s+significant\b',

            r'\bno\s+significant\s+difference\b'
        ]

        negative_found = any(
            re.search(pattern, normalized)
            for pattern in negative_patterns
        )

        if negative_found:

            claims.append({
                "claim": "NOT_SIGNIFICANT",
                "context": sentence.strip()
            })

            # Very important:
            # don't test this same sentence as SIGNIFICANT
            continue

        # ---------------------------------
        # SIGNIFICANT
        # ---------------------------------

        positive_patterns = [

            r'\bstatistically\s+significant\b',

            r'\bsignificant\s+difference\b',

            r'\bsignificantly\s+(?:higher|lower|greater|different)\b'
        ]

        positive_found = any(
            re.search(pattern, normalized)
            for pattern in positive_patterns
        )

        if positive_found:

            claims.append({
                "claim": "SIGNIFICANT",
                "context": sentence.strip()
            })

    return claims



def evaluate_claim_against_pvalue(
    claim,
    pvalue,
    threshold=SIGNIFICANCE_THRESHOLD
):

    if pvalue is None:
        return "NOT_ASSESSABLE"

    if claim == "SIGNIFICANT":

        if pvalue < threshold:
            return "CONSISTENT"
        else:
            return "DISCREPANCY"

    if claim == "NOT_SIGNIFICANT":

        if pvalue >= threshold:
            return "CONSISTENT"
        else:
            return "DISCREPANCY"

    return "NOT_ASSESSABLE"



def build_statistical_consistency_report(
    sections,
    pvalue_findings,
    threshold=0.05
):

    abstract_claims = detect_significance_claims(
        sections.get("abstract", "")
    )

    results_claims = detect_significance_claims(
        sections.get("results", "")
    )

    abstract_pvalues = [
        x for x in pvalue_findings
        if x["section"] == "abstract"
    ]

    results_pvalues = [
        x for x in pvalue_findings
        if x["section"] == "results"
    ]

    # ---------------------------------
    # 1. Claim consistency
    # ---------------------------------

    abstract_claim_types = {
        x["claim"] for x in abstract_claims
    }

    results_claim_types = {
        x["claim"] for x in results_claims
    }

    if (
        abstract_claim_types
        and results_claim_types
        and abstract_claim_types
        == results_claim_types
    ):
        claim_consistency = "CONSISTENT"

    elif (
        abstract_claim_types
        and results_claim_types
    ):
        claim_consistency = "POTENTIAL_DISCREPANCY"

    else:
        claim_consistency = "NOT_ASSESSABLE"

    # ---------------------------------
    # 2. Claim vs p-value
    # ---------------------------------

    claim_pvalue_checks = []

    for pvalue in abstract_pvalues:

        for claim in abstract_claims:

            check = evaluate_claim_against_pvalue(
                claim["claim"],
                pvalue["numeric_value"],
                threshold
            )

            claim_pvalue_checks.append({
                "claim": claim["claim"],
                "pvalue": pvalue["numeric_value"],
                "result": check
            })

    # ---------------------------------
    # 3. Numeric traceability
    # ---------------------------------

    abstract_numbers = {
        x["numeric_value"]
        for x in abstract_pvalues
    }

    results_numbers = {
        x["numeric_value"]
        for x in results_pvalues
    }

    matched_values = (
        abstract_numbers
        & results_numbers
    )

    if not abstract_numbers:

        numeric_traceability = (
            "NOT_APPLICABLE"
        )

    elif matched_values:

        numeric_traceability = (
            "TRACEABLE"
        )

    else:

        numeric_traceability = (
            "NOT_TRACEABLE"
        )

    # ---------------------------------
    # 4. Final status
    # ---------------------------------

    discrepancy_found = any(
        item["result"] == "DISCREPANCY"
        for item in claim_pvalue_checks
    )

    if (
        claim_consistency
        == "POTENTIAL_DISCREPANCY"
        or discrepancy_found
    ):

        status = "DISCREPANCY"

        reason = (
            "Potential inconsistency was detected "
            "between statistical claims or reported "
            "p-values."
        )

    elif (
        numeric_traceability
        == "NOT_TRACEABLE"
    ):

        status = "REVIEW"

        reason = (
            "The statistical interpretation appears "
            "internally consistent, but an abstract "
            "p-value could not be numerically traced "
            "to the Results section."
        )

    else:

        status = "PASS_CANDIDATE"

        reason = (
            "The detected statistical claims and "
            "p-values appear internally consistent."
        )

    return {
        "abstract_pvalues": sorted(
            abstract_numbers
        ),
        "results_pvalues": sorted(
            results_numbers
        ),
        "abstract_claims": sorted(
            abstract_claim_types
        ),
        "results_claims": sorted(
            results_claim_types
        ),
        "claim_consistency": claim_consistency,
        "claim_pvalue_checks": claim_pvalue_checks,
        "numeric_traceability": numeric_traceability,
        "matched_pvalues": sorted(
            matched_values
        ),
        "status": status,
        "reason": reason
    }



def extract_sample_sizes(sections):

    findings = []

    for section_name, section_text in sections.items():

        if section_name == "references":
            continue

        sentences = sent_tokenize(section_text)

        for sentence in sentences:

            # Normalize PDF whitespace
            normalized = re.sub(
                r'\s+',
                ' ',
                sentence
            ).strip()

            for pattern in SAMPLE_SIZE_PATTERNS:

                # Use finditer instead of findall so that we know
                # the exact position of every sample-size match.
                matches = re.finditer(
                    pattern,
                    normalized,
                    flags=re.IGNORECASE
                )

                for match_obj in matches:

                    match = match_obj.group()

                    # ---------------------------------
                    # Ignore section-number artifacts
                    #
                    # Examples:
                    # 2.2 Patient Inclusion...
                    #     ^ "2 Patient"
                    #
                    # 3.1 Patient Baseline...
                    #     ^ "1 Patient"
                    # ---------------------------------

                    match_start = match_obj.start()

                    prefix = normalized[
                        max(0, match_start - 10):
                        match_start
                    ]

                    # If the matched number is the decimal part
                    # of a section heading such as 2.2 or 3.1,
                    # ignore it.
                    if re.search(
                        r'\b\d+\.$',
                        prefix
                    ):
                        continue

                    # ---------------------------------
                    # Extract numeric value
                    # including comma-formatted numbers
                    # ---------------------------------

                    number_match = re.search(
                        r'\d{1,3}(?:,\d{3})*|\d+',
                        match
                    )

                    if not number_match:
                        continue

                    numeric_value = int(
                        number_match.group().replace(",", "")
                    )

                    # ---------------------------------
                    # Capture local context
                    # ---------------------------------

                    start = max(
                        0,
                        match_obj.start() - 80
                    )

                    end = min(
                        len(normalized),
                        match_obj.end() + 80
                    )

                    local_context = normalized[start:end]

                    findings.append({
                        "section": section_name,
                        "expression": match,
                        "numeric_value": numeric_value,
                        "context": normalized,
                        "local_context": local_context
                    })

    return findings
 

def determine_sample_size_applicability(study_characters):

    human = study_characters[
        "human_study"
    ]["detected"]

    clinical = study_characters[
        "clinical_trial"
    ]["detected"]

    if human or clinical:
        return "APPLICABLE"

    return "NOT_APPLICABLE"



def classify_sample_size_role(context, expression=None):

    context_lower = context.lower()

    # --------------------------------------------------
    # Locate the specific sample-size expression
    # --------------------------------------------------

    expression_start = None
    expression_end = None

    if expression:

        match = re.search(
            re.escape(expression.lower()),
            context_lower
        )

        if match:
            expression_start = match.start()
            expression_end = match.end()

    # --------------------------------------------------
    # Explicit participant-flow relationships
    # --------------------------------------------------

    if expression_end is not None:

        text_after_expression = context_lower[
            expression_end:
            expression_end + 150
        ]

        # ----------------------------------------------
        # EXCLUDED / LOST TO FOLLOW-UP
        #
        # The exclusion phrase must be reasonably close
        # to the specific population expression.
        #
        # Example:
        # "47 babies were lost to follow-up"
        # ----------------------------------------------

        excluded_patterns = [
            r'^\s*(?:were|was)?\s*excluded\b',
            r'^\s*(?:were|was)?\s*removed\b',
            r'^\s*(?:were|was)?\s*lost to follow-up\b',
            r'^\s*(?:were|was)?\s*withdrawn\b',
            r'^\s*withdrew\b'
        ]

        if any(
            re.search(pattern, text_after_expression)
            for pattern in excluded_patterns
        ):
            return "EXCLUDED"

        # ----------------------------------------------
        # COMPLETED / FOLLOWED COHORT
        #
        # This allows intervening study-process language
        # such as:
        #
        # "394 newborns ... were enrolled, screened ...
        # and successfully followed to 28 days."
        #
        # But do not classify a population as completed
        # if it is explicitly described as lost/excluded.
        # ----------------------------------------------

        completed_followup_patterns = [
            # Direct description of the detected population
            r'^.{0,80}\b(?:were|was)\b.{0,50}\bsuccessfully followed\b',
            r'^.{0,80}\b(?:were|was)\b.{0,50}\bcompleted follow-up\b',
            r'^.{0,80}\b(?:were|was)\b.{0,50}\bcompleted the study\b',
            r'^.{0,80}\b(?:were|was)\b.{0,50}\bcompleted treatment\b',
        ]

        exclusion_before_completion = re.search(
            r'\b(?:lost to follow-up|excluded|removed|withdrawn|withdrew)\b',
            text_after_expression
        )
        
        # Prevent completion language belonging to a comparison
        # population from being assigned to the detected count.
        #
        # Example:
        # "47 babies were less likely ... than those
        # successfully followed to 28 days"
        comparison_population = re.search(
            r'\b(?:than|compared (?:with|to))\s+those\b',
            text_after_expression
        )
        
        if (
            not exclusion_before_completion
            and not comparison_population
            and any(
                re.search(pattern, text_after_expression)
                for pattern in completed_followup_patterns
            )
        ):
            return "COMPLETED"

    # --------------------------------------------------
    # Role patterns
    # --------------------------------------------------

    role_patterns = {

        "PLANNED": [
            r'\bplanned sample size\b',
            r'\btarget sample size\b',
            r'\brequired sample size\b',
            r'\bcalculated sample size\b',
            r'\bestimated sample size\b',
            r'\bminimum sample size\b',
            r'\bminimal sample size\b',
            r'\bsample size would be\b',
            r'\bsample size was calculated\b',
            r'\bsample size was estimated\b',
            r'\bpatients? per arm\b',
            r'\bparticipants? per arm\b',
            r'\bsubjects? per arm\b'
        ],

        "SCREENED": [
            r'\bscreened\b',
            r'\bwere screened\b',
            r'\bwas screened\b'
        ],

        "ANALYZED": [
            r'\banaly[sz]ed\b',
            r'\bincluded in (?:the )?analysis\b',
            r'\bincluded in (?:the )?final analysis\b',
            r'\bfor (?:the )?final analysis\b',
            r'\bfor (?:the )?analysis\b',
            r'\bused in (?:the )?analysis\b',
            r'\bused for (?:the )?analysis\b'
        ],

        "RANDOMIZED": [
            r'\brandomi[sz]ed\b',
            r'\brandomly assigned\b',
            r'\brandomly allocated\b',
            r'\ballocated at random\b'
        ],

        "COMPLETED": [
            r'\bcompleted the study\b',
            r'\bcompleted follow-up\b',
            r'\bcompleted treatment\b',
            r'\bsuccessfully followed\b',
            r'\bsuccessfully followed (?:up )?to\b',
            r'\bfollowed (?:up )?to \d+\s*(?:days?|weeks?|months?|years?)\b',
            r'\bcompleted \d+\s*(?:days?|weeks?|months?|years?) of follow-up\b'
        ],

        "EXCLUDED": [
            r'\bexcluded\b',
            r'\bremoved\b',
            r'\blost to follow-up\b',
            r'\bwithdrew\b',
            r'\bwithdrawn\b'
        ],

        "ENROLLED": [
            r'\benrolled\b',
            r'\brecruited\b',
            r'\bincluded in (?:the )?study\b',
            r'\bstudy included\b',
            r'\bwere included\b',
            r'\bwas included\b'
        ]
    }

    # --------------------------------------------------
    # Choose the closest role evidence
    # --------------------------------------------------

    if expression_start is not None:

        candidates = []

        for role, patterns in role_patterns.items():

            for pattern in patterns:

                for role_match in re.finditer(
                    pattern,
                    context_lower
                ):

                    if role_match.end() <= expression_start:

                        distance = (
                            expression_start
                            - role_match.end()
                        )

                    elif role_match.start() >= expression_end:

                        distance = (
                            role_match.start()
                            - expression_end
                        )

                    else:
                        distance = 0

                    candidates.append({
                        "role": role,
                        "distance": distance
                    })

        nearby_candidates = [
            candidate
            for candidate in candidates
            if candidate["distance"] <= 40
        ]

        if nearby_candidates:

            closest = min(
                nearby_candidates,
                key=lambda x: x["distance"]
            )

            return closest["role"]

    # --------------------------------------------------
    # Fallback
    # --------------------------------------------------

    for role, patterns in role_patterns.items():

        for pattern in patterns:

            if re.search(
                pattern,
                context_lower
            ):
                return role

    return "UNSPECIFIED"


def add_sample_size_roles(findings):

    enriched = []

    for finding in findings:

        new_finding = finding.copy()

        new_finding["role"] = (
            classify_sample_size_role(
                finding["context"],
                finding.get("expression")
            )
        )
        enriched.append(new_finding)

    return enriched
 

def remove_duplicate_sample_sizes(findings):

    unique_findings = []
    seen = set()

    for finding in findings:

        key = (
            finding["section"],
            finding["numeric_value"],
            finding["context"]
        )

        if key not in seen:

            seen.add(key)
            unique_findings.append(
                finding
            )

    return unique_findings



def evaluate_sample_size_consistency(
    study_characteristics,
    findings
):

    # ---------------------------------
    # Systematic review / meta-analysis
    # ---------------------------------
    # Participant counts in systematic
    # reviews usually describe included
    # studies or pooled populations rather
    # than a newly recruited study cohort.
    # ---------------------------------

    systematic_review = study_characteristics.get(
        "systematic_review",
        {"detected": False}
    )["detected"]

    if systematic_review:

        return {
            "applicability": "NOT_APPLICABLE",
            "same_role_comparisons": [],
            "final_population_comparisons": [],
            "participant_flow": [],
            "raw_findings": findings,
            "status": "NOT_TRIGGERED",
            "reason": (
                "Sample-size consistency screening is not "
                "applicable to a systematic review or "
                "meta-analysis."
            )
        }

    # ---------------------------------
    # Normal applicability check
    # ---------------------------------

    applicability = determine_sample_size_applicability(
        study_characteristics
    )

    # ---------------------------------
    # Not applicable
    # ---------------------------------

    if applicability == "NOT_APPLICABLE":

        return {
            "applicability": "NOT_APPLICABLE",
            "same_role_comparisons": [],
            "final_population_comparisons": [],
            "participant_flow": [],
            "status": "NOT_TRIGGERED",
            "reason": (
                "Participant sample-size consistency "
                "screening was not applicable."
            )
        }

    # ---------------------------------
    # No sample sizes
    # ---------------------------------

    if not findings:

        return {
            "applicability": "APPLICABLE",
            "same_role_comparisons": [],
            "final_population_comparisons": [],
            "participant_flow": [],
            "status": "REVIEW",
            "reason": (
                "No participant sample-size information "
                "was detected."
            )
        }

    # ---------------------------------
    # Group values by role + section
    # ---------------------------------

    role_section_values = {}

    for finding in findings:

        role = finding["role"]
        section = finding["section"]
        value = finding["numeric_value"]
    
        if role == "UNSPECIFIED":
            continue
    
        # ---------------------------------------------
        # PLANNED sample sizes
        # ---------------------------------------------
        # Planned sample-size evidence should come from
        # study-design sections. Introduction/background
        # text may describe sample sizes from prior studies.
        #
        # Also, multiple PLANNED values within the same
        # section may legitimately represent:
        #   - total planned sample size
        #   - planned sample size per arm
        #
        # Therefore PLANNED values should not be treated
        # as ordinary same-role cross-section discrepancies.
        # ---------------------------------------------
    
        if role == "PLANNED":
            continue
    
        role_section_values.setdefault(role, {})
        role_section_values[role].setdefault(section, set())
        role_section_values[role][section].add(value)

        role_section_values[role].setdefault(
            section,
            set()
        )

        role_section_values[role][section].add(
            value
        )

    # ---------------------------------
    # Compare SAME roles across sections
    # ---------------------------------

    comparisons = []

    for role, section_values in role_section_values.items():

        sections_available = list(
            section_values.keys()
        )

        if len(sections_available) < 2:
            continue

        all_values = set()

        for values in section_values.values():
            all_values.update(values)

        if len(all_values) == 1:
            result = "CONSISTENT"
        else:
            result = "POTENTIAL_DISCREPANCY"

        comparisons.append({
            "role": role,
            "sections": {
                section: sorted(values)
                for section, values
                in section_values.items()
            },
            "result": result
        })

    # ---------------------------------
    # Compare FINAL STUDY POPULATION
    #
    # A final population may be described as:
    #
    # Methods:
    # "247 patients for final analysis"
    #       -> ANALYZED
    #
    # Results:
    # "247 patients were included"
    #       -> ENROLLED
    #
    # These different role labels may still describe
    # the same final study population.
    # ---------------------------------

    final_population_comparisons = []

    methods_final_values = set()
    results_final_values = set()

    for finding in findings:

        role = finding["role"]
        section = finding["section"]
        value = finding["numeric_value"]

        if (
            section in ["methods", "experiments"]
            and role == "ANALYZED"
        ):
            methods_final_values.add(value)

        if (
            section == "results"
            and role in ["ANALYZED", "ENROLLED"]
        ):
            results_final_values.add(value)

    matching_final_values = (
        methods_final_values
        & results_final_values
    )

    if matching_final_values:

        final_population_comparisons.append({
            "methods_values": sorted(
                methods_final_values
            ),
            "results_values": sorted(
                results_final_values
            ),
            "matching_values": sorted(
                matching_final_values
            ),
            "result": "CONSISTENT"
        })

    # ---------------------------------
    # Participant flow
    # ENROLLED -> ANALYZED
    #
    # Informational only.
    # Does NOT determine discrepancy status.
    # ---------------------------------

    participant_flow = []

    enrolled_values = []

    analyzed_values = []

    for finding in findings:

        if finding["role"] == "ENROLLED":
            enrolled_values.append(
                finding["numeric_value"]
            )

        elif finding["role"] == "ANALYZED":
            analyzed_values.append(
                finding["numeric_value"]
            )

    if enrolled_values and analyzed_values:

        participant_flow.append({
            "enrolled_values": sorted(
                set(enrolled_values)
            ),
            "analyzed_values": sorted(
                set(analyzed_values)
            ),
            "interpretation": (
                "INFORMATIONAL_ONLY"
            )
        })

    # ---------------------------------
    # Final decision
    # ---------------------------------

    discrepancy_found = any(
        comparison["result"]
        == "POTENTIAL_DISCREPANCY"

        for comparison in comparisons
    )

    final_population_consistent = any(
        comparison["result"] == "CONSISTENT"
        for comparison
        in final_population_comparisons
    )

    if discrepancy_found:

        status = "REVIEW"

        reason = (
            "Different participant counts were detected "
            "for the same sample-size role across manuscript "
            "sections."
        )

    elif comparisons:

        status = "PASS_CANDIDATE"

        reason = (
            "Sample sizes representing the same participant "
            "role were consistent across the assessed sections."
        )

    elif final_population_consistent:

        status = "PASS_CANDIDATE"

        reason = (
            "The final participant population was consistent "
            "between the Methods and Results sections."
        )

    else:

        status = "REVIEW"

        reason = (
            "Participant counts were detected, but there "
            "was insufficient comparable cross-section "
            "information for a direct consistency comparison."
        )

    return {
        "applicability": "APPLICABLE",
        "same_role_comparisons": comparisons,
        "final_population_comparisons":
            final_population_comparisons,
        "participant_flow": participant_flow,
        "raw_findings": findings,
        "status": status,
        "reason": reason
    }

def detect_reproducibility_indicators(
    sections,
    indicators
):

    results = {}

    for category, keywords in indicators.items():

        reported_evidence = []
        unavailable_evidence = []

        for section_name in reproducibility_sections:

            section_text = sections.get(
                section_name,
                ""
            )

            if not section_text:
                continue

            sentences = sent_tokenize(
                section_text
            )

            for sentence in sentences:

                normalized = re.sub(
                    r'\s+',
                    ' ',
                    sentence
                ).strip()

                matched_keyword = None

                for keyword in keywords:

                    pattern = (
                        r'\b'
                        + re.escape(keyword)
                        + r'\b'
                    )

                    if re.search(
                        pattern,
                        normalized,
                        flags=re.IGNORECASE
                    ):
                        matched_keyword = keyword
                        break

                if matched_keyword is None:
                    continue

                evidence = {
                    "section": section_name,
                    "keyword": matched_keyword,
                    "context": normalized
                }

                if (contains_missing_information_language(
                    normalized)
                    or
                    contains_placeholder_value(
                        normalized, matched_keyword
                    )
                    
                ):

                    unavailable_evidence.append(
                        evidence
                    )

                else:

                    reported_evidence.append(
                        evidence
                    )

        # ---------------------------------
        # Determine state
        # ---------------------------------

        if reported_evidence and unavailable_evidence:

            state = "MIXED_EVIDENCE"

        elif reported_evidence:

            state = "REPORTED"

        elif unavailable_evidence:

            state = "EXPLICITLY_UNAVAILABLE"

        else:

            state = "NOT_DETECTED"

        results[category] = {
            "state": state,
            "reported_evidence": reported_evidence,
            "unavailable_evidence": unavailable_evidence
        }

    return results



def build_reproducibility_report(
    study_characteristics,
    reproducibility_results
):

    computational = study_characteristics[
        "computational_study"
    ]["detected"]

    # ---------------------------------
    # Applicability
    # ---------------------------------

    if not computational:

        return {
            "applicability": "NOT_APPLICABLE",
            "reported": [],
            "explicitly_unavailable": [],
            "not_detected": [],
            "mixed_evidence": [],
            "status": "NOT_TRIGGERED",
            "reason": (
                "Computational reproducibility screening "
                "was not triggered because no computational "
                "study indicators were detected."
            )
        }

    # ---------------------------------
    # Group findings by state
    # ---------------------------------

    reported = []
    explicitly_unavailable = []
    not_detected = []
    mixed_evidence = []

    for category, result in (
        reproducibility_results.items()
    ):

        state = result["state"]

        if state == "REPORTED":
            reported.append(category)

        elif state == "EXPLICITLY_UNAVAILABLE":
            explicitly_unavailable.append(
                category
            )

        elif state == "NOT_DETECTED":
            not_detected.append(category)

        elif state == "MIXED_EVIDENCE":
            mixed_evidence.append(category)

    # ---------------------------------
    # Editorial decision
    # ---------------------------------

    if explicitly_unavailable:

        status = "REVIEW"

        reason = (
            "One or more reproducibility-relevant "
            "methodological details were explicitly "
            "reported as unavailable. Editorial "
            "verification is recommended."
        )

    elif mixed_evidence:

        status = "REVIEW"

        reason = (
            "Mixed evidence was detected for one or more "
            "reproducibility-relevant methodological "
            "details. Editorial verification is recommended."
        )

    elif not_detected:

        status = "REVIEW"

        reason = (
            "Some reproducibility-relevant details could "
            "not be identified automatically. Manual "
            "verification may be appropriate."
        )

    else:

        status = "PASS_CANDIDATE"

        reason = (
            "The assessed computational reproducibility "
            "indicators were identified in the manuscript."
        )

    return {
        "applicability": "APPLICABLE",
        "reported": reported,
        "explicitly_unavailable": explicitly_unavailable,
        "not_detected": not_detected,
        "mixed_evidence": mixed_evidence,
        "status": status,
        "reason": reason
    }



def contains_missing_information_language(sentence):
  normalized = re.sub(
      r'\s+',
      ' ',
      sentence
  ).strip().lower()

  return any(
      re.search(pattern, normalized)
      for pattern in missing_information_patterns
  )



def contains_placeholder_value(
    sentence,
    keyword
):

    normalized = re.sub(
        r'\s+',
        ' ',
        sentence
    ).strip()

    keyword_pattern = re.escape(
        keyword
    )

    # Examples:
    # ODE solver —
    # Optimizer —
    # Parameter bounds —
    
    pattern = (
        keyword_pattern
        + r'\s*[:=]?\s*[—–-]'
    )

    return bool(
        re.search(
            pattern,
            normalized,
            flags=re.IGNORECASE
        )
    )



def generate_manuscript_report(
    study_characters,
    ethics_screening,
    data_screening,
    center_screening,
    cam_screening,
    durc_screening,
    statistical_report,
    sample_size_screening,
    reproducibility_report
):

    report = {

        "study_characteristics": study_characters,

        "editorial_screening": {
            "ethics_consent": ethics_screening,
            "data_availability": data_screening,
            "center_screening": center_screening,
            "cam": cam_screening,
            "durc": durc_screening
        },

        "discrepancy_checks": {
            "statistical_consistency": statistical_report,
            "sample_size_consistency": sample_size_screening
        },

        "reproducibility": reproducibility_report
    }

    return report



def build_overall_editorial_decision(
    manuscript_report
):

    review_items = []
    pass_items = []
    neutral_items = []

    # ---------------------------------
    # Helper
    # ---------------------------------

    def classify_module(
        module_name,
        module_result
    ):

        if not isinstance(module_result, dict):
            return

        status = module_result.get(
            "status"
        )

        reason = module_result.get(
            "reason",
            ""
        )

        if status in [
            "REVIEW",
            "DISCREPANCY"
        ]:

            review_items.append({
                "module": module_name,
                "status": status,
                "reason": reason
            })

        elif status in [
            "PASS",
            "PASS_CANDIDATE",
            "CONSISTENT",
            "NOT_DETECTED"
        ]:

            pass_items.append({
                "module": module_name,
                "status": status
            })

        elif status in [
            "NOT_TRIGGERED",
            "NOT_APPLICABLE",
            "UNDETERMINED"
        ]:

            neutral_items.append({
                "module": module_name,
                "status": status
            })

    # ---------------------------------
    # Editorial screening
    # ---------------------------------

    editorial = manuscript_report[
        "editorial_screening"
    ]

    classify_module(
        "Data Availability",
        editorial["data_availability"]
    )

    classify_module(
        "Single/Multi-Center",
        editorial["center_screening"]
    )

    classify_module(
        "CAM",
        editorial["cam"]
    )

    classify_module(
        "DURC",
        editorial["durc"]
    )

    # Ethics has two separate statuses,
    # so handle it separately.

    ethics = editorial[
        "ethics_consent"
    ]

    ethics_status = ethics.get(
        "ethics_status"
    )

    consent_status = ethics.get(
        "consent_status"
    )

    if (
        ethics_status in [
            "REVIEW_MISSING",
            "REVIEW_EXEMPTION",
            "REVIEW_ANIMAL_ETHICS"
        ]
        or
        consent_status in [
            "REVIEW_MISSING",
            "REVIEW_WAIVER"
        ]
    ):

        review_items.append({
            "module": "Ethics & Consent",
            "status": "REVIEW",
            "reason": (
                "Ethics or consent information "
                "requires editorial verification."
            )
        })

    else:

        neutral_items.append({
            "module": "Ethics & Consent",
            "status": (
                "NOT_TRIGGERED"
                if ethics_status == "NOT_TRIGGERED"
                else ethics_status
            )
        })

    # ---------------------------------
    # Discrepancy checks
    # ---------------------------------

    discrepancy = manuscript_report[
        "discrepancy_checks"
    ]

    classify_module(
        "Statistical Consistency",
        discrepancy[
            "statistical_consistency"
        ]
    )

    classify_module(
        "Sample Size Consistency",
        discrepancy[
            "sample_size_consistency"
        ]
    )

    # ---------------------------------
    # Reproducibility
    # ---------------------------------

    classify_module(
        "Reproducibility",
        manuscript_report[
            "reproducibility"
        ]
    )

    # ---------------------------------
    # Overall status
    # ---------------------------------

    if review_items:

        overall_status = "REVIEW"

    else:

        overall_status = "PASS_CANDIDATE"

    return {
        "overall_status": overall_status,
        "review_count": len(review_items),
        "review_items": review_items,
        "pass_items": pass_items,
        "neutral_items": neutral_items
    }



def analyze_manuscript_text(full_text):
    print("=" * 70)
    print("AI SCIENTIFIC MANUSCRIPT ANALYSIS (COMPLETE - 10 STAGES)")
    print("=" * 70)

    # 1. Section Detection
    lines = full_text.split("\n")
    sections = extract_sections(lines)
    print(f"✓ Sections Detected: {len(sections)}")

    # 2. Study Characteristics
    analysis_sections = {
        name: text
        for name, text in sections.items()
        if name != "references"
    }
    analysis_text = "\n".join(analysis_sections.values())
    study_characters = detect_study_characters(analysis_text)
    print("✓ Study Characteristics Analysed")

    # 3. Ethics & Consent
    ethics_results = ethics_indicator_evidence(sections, ETHICS_INDICATORS)
    ethics_screening = evaluate_ethics_screening(study_characters, ethics_results)
    print("✓ Ethics & Consent Screening Completed")

    # 4. Data Availability
    mandated_findings = detect_mandated_data(sections)
    das_result = detect_data_availability_statement(sections)
    das_text = build_das_text(das_result)
    identifiers_found = detect_persistent_identifiers(das_text)
    data_access_types = determine_data_access_type(das_result, repositories_found=None)
    data_screening = evaluate_data_availability(
        mandated_findings, das_result, data_access_types, [], identifiers_found
    )
    print("✓ Data Availability Screening Completed")

    # 5. Single / Multi-Center Screening
    center_findings = detect_center_evidence(sections)
    center_screening = evaluate_center_screening(study_characters, center_findings)
    print("✓ Single/Multi-Center Screening Completed")

    # 6. CAM Screening
    cam_findings = detect_cam_evidence(sections)
    cam_screening = evaluate_cam_screening(cam_findings)
    print("✓ CAM Screening Completed")

    # 7. DURC Screening
    durc_findings = detect_durc_evidence(sections)
    durc_screening = evaluate_durc_screening(durc_findings)
    print("✓ DURC Screening Completed")

    # 8. Statistical Consistency
    pvalue_findings = extract_pvalues_by_section(sections)
    for finding in pvalue_findings:
        parsed = parse_pvalue(finding["value"])
        finding.update(parsed)
    statistical_report = build_statistical_consistency_report(sections, pvalue_findings)
    print("✓ Statistical Consistency Screening Completed")

    # 9. Sample Size Consistency
    print("\n===== RESULTS SECTION DEBUG =====")

    results_text = sections.get("results", "")
    
    print(results_text)
    
    print("\n===== TARGET CHECK =====")
    print("441 present:", "441" in results_text)
    print("394 present:", "394" in results_text)
    print("47 present:", "47" in results_text)
    
    print("newborn present:", "newborn" in results_text.lower())
    print("babies present:", "babies" in results_text.lower())
    
    print("===== END RESULTS SECTION DEBUG =====\n")
 
    sample_size_findings = extract_sample_sizes(sections)
    sample_size_findings = add_sample_size_roles(sample_size_findings)
    sample_size_findings = remove_duplicate_sample_sizes(sample_size_findings)
    print("\n===== SAMPLE SIZE DEBUG =====")

    for finding in sample_size_findings:
        print(
            "VALUE:", finding.get("numeric_value"),
            "| ROLE:", finding.get("role"),
            "| SECTION:", finding.get("section")
            
        )
        print(
            "CONTEXT:",
            finding.get("context")
        )
        print("-" * 70)
    
    print("===== END SAMPLE SIZE DEBUG =====\n")
    sample_size_screening = evaluate_sample_size_consistency(study_characters, sample_size_findings)
    print("✓ Sample Size Consistency Screening Completed")

    # 10. Reproducibility Screening
    reproducibility_results = detect_reproducibility_indicators(sections, computational_reproducibility_indicators)
    reproducibility_report = build_reproducibility_report(study_characters, reproducibility_results)
    print("✓ Reproducibility Screening Completed")

    # 11. Master Manuscript Report
    manuscript_report = generate_manuscript_report(
        study_characters,
        ethics_screening,
        data_screening,
        center_screening,
        cam_screening,
        durc_screening,
        statistical_report,
        sample_size_screening,
        reproducibility_report
    )
    print("✓ Master Manuscript Report Generated !!!")

    # 12. Overall Editorial Decision
    
    overall_decision = build_overall_editorial_decision(manuscript_report)

    print("✓ Overall Editorial Decision Generated !!!")


    return {
        "sections": sections,
        "analysis_text": analysis_text,
        "study_characters": study_characters,
        "ethics_screening": ethics_screening,
        "data_screening": data_screening,
        "das_text": das_text,
        "center_findings": center_findings,
        "center_screening": center_screening,
        "cam_screening": cam_screening,
        "durc_screening": durc_screening,
        "statistical_report": statistical_report,
        "sample_size_screening": sample_size_screening,
        "sample_size_findings": sample_size_findings,
        "reproducibility_report": reproducibility_report,
        "manuscript_report": manuscript_report,
        "overall_decision": overall_decision
    }



def analyze_manuscript(pdf_path):
    """
    Complete manuscript analysis pipeline.

    Input:
        pdf_path : Path to a scientific manuscript PDF

    Output:
        Complete manuscript analysis containing:
        - Master manuscript report
        - Overall editorial decision
    """

    print("=" * 70)
    print("LOADING MANUSCRIPT")
    print("=" * 70)

    # ------------------------------------------------------
    # 1. OPEN PDF
    # ------------------------------------------------------

    document = fitz.open(pdf_path)

    print(f"✓ PDF Loaded: {len(document)} pages")


    # ------------------------------------------------------
    # 2. EXTRACT TEXT
    # ------------------------------------------------------

    page_text = []

    for page in document:
        text = page.get_text("text")
        page_text.append(text)

    document.close()

    full_text = "\n".join(page_text)

    print(f"✓ Text Extracted: {len(full_text):,} characters")


    # Basic extraction safety check
    if not full_text.strip():
        raise ValueError(
            "No readable text could be extracted from the PDF."
        )


    # ------------------------------------------------------
    # 3. RUN COMPLETE ANALYSIS ENGINE
    # ------------------------------------------------------

    final_analysis = analyze_manuscript_text(
        full_text
    )
    

    return final_analysis
 

