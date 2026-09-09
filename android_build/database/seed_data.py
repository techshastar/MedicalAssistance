"""
seed_data.py
------------
A small SAMPLE dataset used ONLY for software development and testing.

⚠️  IMPORTANT — READ BEFORE REAL USE ⚠️
Every record below is *demo data*. It is written in deliberately cautious,
general language (mirroring typical package-leaflet wording), but it has
NOT been medically verified for this application. Before anyone relies on
this app, this table must be replaced with data imported from reliable,
official medicine references. The `source` column makes the demo status
explicit, and the tests verify that demo rows are always labelled.
"""

import sqlite3

from .database import insert_medicine, count_medicines

DEMO_SOURCE = (
    "DEMO DATA (unverified, for software development only - "
    "replace with verified medical sources before real use)"
)
DEMO_DATE = "2026-08-24"

SAMPLE_MEDICINES = [
    {
        "medicine_name": "Paracetamol 500",
        "brand_name": "Crocin 500 (demo example)",
        "generic_name": "Paracetamol",
        "active_ingredient": "Paracetamol",
        "strength": "500 mg",
        "category": "Analgesic and antipyretic (simple words: pain-relieving and fever-reducing medicine)",
        "common_uses": "Fever; Headache; Mild to moderate body pain",
        "general_usage": "General information only - commonly used to lower fever and relieve mild pain.",
        "administration": "Taken by mouth with water. Can usually be taken with or without food. Always follow the package label or your doctor/pharmacist's instructions.",
        "common_side_effects": "Nausea; Stomach discomfort; Skin rash (uncommon)",
        "serious_warnings": "Taking more than the maximum dose stated on the package can seriously damage the liver. In case of overdose, seek medical help immediately.",
        "pregnancy_warning": "Ask a doctor before use during pregnancy. Never assume a medicine is safe in pregnancy.",
        "breastfeeding_warning": "Ask a doctor or pharmacist before use while breastfeeding.",
        "children_warning": "Doses for children are different and depend on age and weight. Ask a doctor or pharmacist.",
        "elderly_warning": "Older adults should confirm the correct dose with a doctor or pharmacist.",
        "kidney_warning": "People with kidney problems may need special precautions. Consult a doctor before use.",
        "liver_warning": "People with liver disease may need special precautions. Consult a doctor before use.",
        "drug_interactions": "May interact with other medicines that also contain paracetamol (overdose risk) and with certain other medicines. Check with a pharmacist.",
        "food_interactions": "No major food interactions in typical use. Follow the package directions.",
        "storage_information": "Store in a cool, dry place away from direct sunlight. Keep out of reach of children.",
        "manufacturer": "Demo Pharma Ltd. (fictional, development only)",
        "dosage_form": "Tablet",
        "source": DEMO_SOURCE,
        "last_updated": DEMO_DATE,
    },
    {
        "medicine_name": "Dolo 650",
        "brand_name": "Dolo 650",
        "generic_name": "Paracetamol",
        "active_ingredient": "Paracetamol",
        "strength": "650 mg",
        "category": "Analgesic and antipyretic (simple words: pain-relieving and fever-reducing medicine)",
        "common_uses": "Fever; Mild to moderate pain",
        "general_usage": "General information only - a paracetamol brand commonly used for fever and pain.",
        "administration": "Taken by mouth with water, usually after food. Follow the package label or your doctor/pharmacist's instructions.",
        "common_side_effects": "Nausea; Stomach discomfort",
        "serious_warnings": "Contains paracetamol - do not combine with other paracetamol medicines. Overdose can seriously damage the liver.",
        "pregnancy_warning": "Ask a doctor before use during pregnancy.",
        "breastfeeding_warning": "Ask a doctor or pharmacist before use while breastfeeding.",
        "children_warning": "This strength may not suit children. Ask a doctor or pharmacist.",
        "elderly_warning": "Older adults should confirm the correct dose with a doctor or pharmacist.",
        "kidney_warning": "People with kidney problems may need special precautions. Consult a doctor before use.",
        "liver_warning": "People with liver disease may need special precautions. Consult a doctor before use.",
        "drug_interactions": "May interact with other paracetamol-containing medicines. Check with a pharmacist.",
        "food_interactions": "No major food interactions in typical use.",
        "storage_information": "Store in a cool, dry place. Keep out of reach of children.",
        "manufacturer": "Demo Pharma Ltd. (fictional, development only)",
        "dosage_form": "Tablet",
        "source": DEMO_SOURCE,
        "last_updated": DEMO_DATE,
    },
    {
        "medicine_name": "Ibuprofen 400",
        "brand_name": "Brufen 400 (demo example)",
        "generic_name": "Ibuprofen",
        "active_ingredient": "Ibuprofen",
        "strength": "400 mg",
        "category": "NSAID - non-steroidal anti-inflammatory drug (simple words: pain, swelling and fever relieving medicine)",
        "common_uses": "Pain; Inflammation/swelling; Fever; Menstrual cramps",
        "general_usage": "General information only - commonly used for pain with swelling/inflammation.",
        "administration": "Taken by mouth, usually with or after food to protect the stomach. Follow the package label or your doctor/pharmacist's instructions.",
        "common_side_effects": "Stomach upset; Heartburn; Dizziness",
        "serious_warnings": "Can cause stomach irritation or bleeding, especially with long use or in higher doses. Stop and seek medical advice if you notice black stools or severe stomach pain.",
        "pregnancy_warning": "May not be suitable in pregnancy, especially later stages. Consult a doctor first.",
        "breastfeeding_warning": "Ask a doctor or pharmacist before use while breastfeeding.",
        "children_warning": "Children need weight-based dosing. Ask a doctor or pharmacist.",
        "elderly_warning": "Elderly people have a higher risk of stomach and kidney side effects. Consult a doctor before use.",
        "kidney_warning": "People with kidney problems may need to avoid NSAIDs. Consult a doctor before use.",
        "liver_warning": "Consult a doctor if you have liver problems.",
        "drug_interactions": "May interact with blood thinners, blood-pressure medicines, and other NSAIDs (including aspirin). Check with a pharmacist.",
        "food_interactions": "Taking it with food reduces stomach upset. Avoid alcohol - it raises stomach-bleeding risk.",
        "storage_information": "Store in a cool, dry place. Keep out of reach of children.",
        "manufacturer": "Demo Pharma Ltd. (fictional, development only)",
        "dosage_form": "Tablet",
        "source": DEMO_SOURCE,
        "last_updated": DEMO_DATE,
    },
    {
        "medicine_name": "Cetirizine 10",
        "brand_name": "Cetzine 10 (demo example)",
        "generic_name": "Cetirizine",
        "active_ingredient": "Cetirizine hydrochloride",
        "strength": "10 mg",
        "category": "Antihistamine (simple words: anti-allergy medicine)",
        "common_uses": "Sneezing and runny nose from allergy; Itchy/watery eyes; Skin itching and hives",
        "general_usage": "General information only - commonly used to relieve allergy symptoms.",
        "administration": "Taken by mouth with water, with or without food, often once daily as per the label or your doctor's advice.",
        "common_side_effects": "Drowsiness; Dry mouth; Tiredness",
        "serious_warnings": "May cause drowsiness - be careful with driving or operating machines until you know how it affects you.",
        "pregnancy_warning": "Ask a doctor before use during pregnancy.",
        "breastfeeding_warning": "Ask a doctor or pharmacist before use while breastfeeding.",
        "children_warning": "Children's doses differ by age. Ask a doctor or pharmacist.",
        "elderly_warning": "Older adults may be more sensitive to drowsiness. Consult a doctor or pharmacist.",
        "kidney_warning": "People with kidney problems may need a lower dose. Consult a doctor before use.",
        "liver_warning": "Consult a doctor if you have liver problems.",
        "drug_interactions": "Other sedating medicines can increase drowsiness. Check with a pharmacist.",
        "food_interactions": "Avoid alcohol - it increases drowsiness.",
        "storage_information": "Store in a cool, dry place. Keep out of reach of children.",
        "manufacturer": "Demo Pharma Ltd. (fictional, development only)",
        "dosage_form": "Tablet",
        "source": DEMO_SOURCE,
        "last_updated": DEMO_DATE,
    },
    {
        "medicine_name": "Amoxicillin 500",
        "brand_name": "Novamox 500 (demo example)",
        "generic_name": "Amoxicillin",
        "active_ingredient": "Amoxicillin trihydrate",
        "strength": "500 mg",
        "category": "Antibiotic - penicillin group (simple words: medicine that fights bacterial infections)",
        "common_uses": "Bacterial infections as diagnosed by a doctor (it does NOT work on viruses like the common cold or flu)",
        "general_usage": "General information only - an antibiotic that must be used only when prescribed.",
        "administration": "Taken by mouth exactly as prescribed. Complete the full prescribed course even if you feel better. Never self-start or share antibiotics.",
        "common_side_effects": "Nausea; Diarrhoea; Mild skin rash",
        "serious_warnings": "People allergic to penicillin can have severe allergic reactions. Stop immediately and seek urgent medical help for rash with swelling, breathing difficulty, or face/throat swelling.",
        "pregnancy_warning": "Use only if prescribed by a doctor during pregnancy.",
        "breastfeeding_warning": "Ask a doctor before use while breastfeeding.",
        "children_warning": "Children's doses are weight-based and must come from a doctor.",
        "elderly_warning": "Dose may need adjustment with age-related kidney changes. Consult a doctor.",
        "kidney_warning": "People with kidney problems may need a different dose schedule. Consult a doctor before use.",
        "liver_warning": "Inform your doctor about any liver problems.",
        "drug_interactions": "May interact with certain other medicines (e.g. some gout medicines, blood thinners). Tell your doctor/pharmacist everything you take.",
        "food_interactions": "Can usually be taken with or without food.",
        "storage_information": "Store as directed on the package. Keep out of reach of children.",
        "manufacturer": "Demo Pharma Ltd. (fictional, development only)",
        "dosage_form": "Capsule",
        "source": DEMO_SOURCE,
        "last_updated": DEMO_DATE,
    },
    {
        "medicine_name": "ORS Powder",
        "brand_name": "Electral (demo example)",
        "generic_name": "Oral Rehydration Salts",
        "active_ingredient": "Glucose and electrolyte salts (WHO-type formula)",
        "strength": "As printed on the sachet",
        "category": "Oral rehydration salts (simple words: replaces water and salts lost in diarrhoea/vomiting)",
        "common_uses": "Dehydration due to diarrhoea; Dehydration due to vomiting",
        "general_usage": "General information only - helps replace fluids and salts lost from the body.",
        "administration": "Dissolve the ENTIRE sachet in exactly the amount of clean drinking water stated on the packet. Sip small amounts frequently. Discard leftover solution after the time stated on the packet.",
        "common_side_effects": "Mild nausea if drunk too fast",
        "serious_warnings": "Severe dehydration (very little urine, extreme weakness, confusion, sunken eyes) needs urgent medical care - do not rely on ORS alone.",
        "pregnancy_warning": "Generally considered low risk, but ask a doctor for personal advice.",
        "breastfeeding_warning": "Generally considered low risk; ask a doctor or pharmacist if unsure.",
        "children_warning": "Widely used in children for dehydration, but see a doctor for infants or if symptoms persist.",
        "elderly_warning": "Elderly people dehydrate faster - monitor closely and seek care if symptoms persist.",
        "kidney_warning": "People with kidney disease should consult a doctor before using electrolyte solutions.",
        "liver_warning": "No specific warning in typical use. Consult a doctor if unsure.",
        "drug_interactions": "No major interactions in typical use.",
        "food_interactions": "Do not mix with soft drinks or juice - use only the stated amount of clean water.",
        "storage_information": "Keep sachets dry. Use the prepared solution within the time stated on the packet.",
        "manufacturer": "Demo Pharma Ltd. (fictional, development only)",
        "dosage_form": "Powder (sachet)",
        "source": DEMO_SOURCE,
        "last_updated": DEMO_DATE,
    },
]


def seed_demo_data(connection: sqlite3.Connection, force: bool = False) -> int:
    """
    Insert the demo medicines if the table is empty (or if force=True).

    Returns the number of rows inserted. Seeding only-when-empty means the
    app can be started any number of times without duplicating data.
    """
    if not force and count_medicines(connection) > 0:
        return 0
    inserted = 0
    for record in SAMPLE_MEDICINES:
        insert_medicine(connection, record)
        inserted += 1
    return inserted
