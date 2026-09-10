"""
languages.py  (Phase 7 - Hindi / English support)
-------------------------------------------------
Every fixed piece of text the app shows or says lives here, in BOTH
languages. The rest of the app asks for text with t(key, language).

    t("opt_search", "hi")  ->  "दवा खोजें"

Rules:
  * English ("en") is always the reference language.
  * If a key is missing in Hindi, we fall back to English
    (a wrong translation is worse than an honest English fallback).
  * Unknown keys raise KeyError loudly - so a typo is caught in tests,
    never silent garbage on a medical screen.
"""

SUPPORTED_LANGUAGES = {"en": "English", "hi": "हिन्दी (Hindi)"}
EN = "en"
HI = "hi"

STRINGS = {
    # ---------------- main app / menus ----------------
    "app_title":        {"en": "MEDICINE ASSISTANT", "hi": "मेडिसिन असिस्टेंट"},
    "menu_prompt":      {"en": "What would you like to do?", "hi": "आप क्या करना चाहेंगे?"},
    "opt_search":       {"en": "Search medicine", "hi": "दवा खोजें"},
    "opt_scan":         {"en": "Scan medicine (photo)", "hi": "दवा स्कैन करें (फोटो)"},
    "opt_list":         {"en": "List all medicines in the database", "hi": "डेटाबेस की सभी दवाएँ देखें"},
    "opt_language":     {"en": "Change language", "hi": "भाषा बदलें"},
    "opt_quit":         {"en": "Quit", "hi": "बाहर निकलें"},
    "choose":           {"en": "Choose 1-{max}:", "hi": "1-{max} चुनें:"},
    "invalid_menu":     {"en": "Please choose a number from the menu.", "hi": "कृपया मेनू से कोई नंबर चुनें।"},
    "goodbye":          {"en": "Goodbye. Stay safe!", "hi": "अलविदा! स्वस्थ रहें, सुरक्षित रहें!"},
    "demo_loaded":      {"en": "(Loaded {n} DEMO medicines for development.)", "hi": "(विकास हेतु {n} DEMO दवाएँ लोड की गईं।)"},

    # ---------------- search flow ----------------
    "enter_name":       {"en": "Enter medicine name (or brand/generic): ", "hi": "दवा का नाम लिखें (या ब्रांड/जेनेरिक): "},
    "type_name":        {"en": "Please type a medicine name to search.", "hi": "कृपया खोजने के लिए दवा का नाम लिखें।"},
    "not_found":        {"en": "No medicine matching '{q}' was found in the database.\nPlease check the spelling, or ask a pharmacist for help.",
                         "hi": "'{q}' नाम की कोई दवा डेटाबेस में नहीं मिली।\nकृपया spelling जाँचें, या फार्मासिस्ट से पूछें।"},
    "found_results":    {"en": "Found {n} result(s):", "hi": "{n} नतीजे मिले:"},
    "number_prompt":    {"en": "Enter the number of a medicine to see its full details (or press Enter to go back): ",
                         "hi": "पूरी जानकारी देखने के लिए दवा का नंबर दबाएँ (वापस जाने के लिए Enter दबाएँ): "},
    "invalid_number":   {"en": "That number is not on the list - going back to the menu.",
                         "hi": "वह नंबर सूची में नहीं है - मुख्य मेनू पर वापस।"},
    "exact_tag":        {"en": "EXACT MATCH", "hi": "पूर्ण मिलान (EXACT)"},
    "possible_tag":     {"en": "POSSIBLE", "hi": "संभावित"},
    "possible_note":    {"en": "Possible match - please confirm the printed name on the pack.",
                         "hi": "संभावित मिलान - कृपया packet पर छपा नाम ज़रूर जाँचें।"},
    "very_close":       {"en": "very close spelling", "hi": "लगभग वही spelling"},
    "pct_similar":      {"en": "{n}% similar", "hi": "{n}% मिलता-जुलता"},
    "list_header":      {"en": "{n} medicine(s) in the local database:", "hi": "स्थानीय डेटाबेस में {n} दवाएँ:"},
    "generic_unknown":  {"en": "generic unknown", "hi": "जेनेरिक अज्ञात"},

    # ---------------- scan flow ----------------
    "enter_photo":      {"en": "Enter the full path of the medicine photo (tip: drag the photo into this window): ",
                         "hi": "दवा की फोटो का पूरा path लिखें (tip: फोटो को इस window में drag करें): "},
    "no_image":         {"en": "No image path given - back to the menu.", "hi": "फोटो का path नहीं दिया - मेनू पर वापस।"},
    "image_not_found":  {"en": "Image file not found: {p}", "hi": "फोटो file नहीं मिली: {p}"},
    "processing":       {"en": "Processing the photo, please wait...", "hi": "फोटो पढ़ी जा रही है, कृपया प्रतीक्षा करें..."},
    "not_identified":   {"en": "Medicine could not be identified with sufficient confidence.\nPlease enter the medicine name manually, or upload a clearer image.",
                         "hi": "दवा को पर्याप्त विश्वास के साथ पहचाना नहीं जा सका।\nकृपया दवा का नाम खुद लिखें, या साफ़ फोटो के साथ फिर कोशिश करें।"},
    "ocr_text_label":   {"en": "(Text read from the photo, for your reference:)",
                         "hi": "(फोटो से पढ़ा गया text, आपकी जाँच हेतु:)"},

    # ---------------- listen / voice ----------------
    "listen_prompt":    {"en": "Press L + Enter to LISTEN to a spoken summary (or just Enter to go back): ",
                         "hi": "सुनने के लिए L + Enter दबाएँ (वापस जाने के लिए Enter दबाएँ): "},
    "speaking":         {"en": "Speaking...", "hi": "बोला जा रहा है..."},
    "tts_tip":          {"en": "(Tip: 'pip install pyttsx3' enables the LISTEN feature -\n the app will then read medicine summaries aloud, offline.)",
                         "hi": "(सुझाव: 'pip install pyttsx3' करने से सुनने की सुविधा चालू हो जाएगी -\n ऐप दवा की जानकारी बोलकर सुनाएगा, बिना internet के.)"},
    "no_hindi_voice":   {"en": "(Hindi voice not found on this computer - speaking with the default voice instead.)",
                         "hi": "(इस computer पर Hindi voice नहीं मिली - default voice में बोला जा रहा है.)"},

    # ---------------- details page ----------------
    "conf_exact":       {"en": "Confidence: EXACT MATCH", "hi": "विश्वास: पूर्ण मिलान (EXACT)"},
    "conf_possible":    {"en": "Confidence: POSSIBLE MATCH - please verify the name on the packaging",
                         "hi": "विश्वास: संभावित मिलान - कृपया packet पर छपा नाम ज़रूर जाँचें"},
    "conf_manual":      {"en": "Confidence: opened from history/manual selection",
                         "hi": "विश्वास: history/मैन्युअल चयन से खोला गया"},
    "generic_lbl":      {"en": "Generic / active ingredient", "hi": "जेनेरिक / सक्रिय घटक"},
    "strength_lbl":     {"en": "Strength", "hi": "मात्रा (Strength)"},
    "form_lbl":         {"en": "Dosage form", "hi": "दवा का रूप"},
    "manufacturer_lbl": {"en": "Manufacturer", "hi": "निर्माता (Manufacturer)"},
    "demo_source":      {"en": "[Source: DEMO data - unverified sample, development use only]",
                         "hi": "[स्रोत: DEMO डेटा - असत्यापित नमूना, केवल विकास हेतु]"},
    "what_is":          {"en": "WHAT IS THIS MEDICINE?", "hi": "यह दवा क्या है?"},
    "official_category":{"en": "Official category", "hi": "आधिकारिक श्रेणी"},
    "simple_words":     {"en": "In simple words:", "hi": "सरल शब्दों में:"},
    "uses_hdr":         {"en": "WHAT IS IT USED FOR?", "hi": "यह किस काम आती है?"},
    "how_taken":        {"en": "HOW IS IT GENERALLY TAKEN?", "hi": "इसे सामान्यतः कैसे लिया जाता है?"},
    "general_note":     {"en": "NOTE: The above is GENERAL information only. Your doctor or\n  pharmacist's instructions for YOU may be different - always\n  follow their advice and the package label.",
                         "hi": "ध्यान दें: ऊपर की जानकारी केवल सामान्य जानकारी है। आपके लिए डॉक्टर या\n  फार्मासिस्ट के निर्देश अलग हो सकते हैं - हमेशा उनकी सलाह\n  और packet के label का पालन करें।"},
    "storage_lbl":      {"en": "Storage", "hi": "स्टोरेज (कहाँ रखें)"},
    "safety_hdr":       {"en": "SAFETY & WARNINGS  (!! read before use)", "hi": "सुरक्षा और चेतावनियाँ  (!! उपयोग से पहले ज़रूर पढ़ें)"},
    "side_fx_hdr":      {"en": "SIDE EFFECTS", "hi": "दुष्प्रभाव (SIDE EFFECTS)"},
    "common_fx":        {"en": "Common (usually mild):", "hi": "सामान्य (आमतौर पर हल्के):"},
    "serious_signs":    {"en": "!! SERIOUS WARNING SIGNS - stop and get medical help:",
                         "hi": "!! गंभीर चेतावनी के संकेत - रोकें और तुरंत चिकित्सा सहायता लें:"},
    "not_available":    {"en": "Not available in the database.", "hi": "जानकारी डेटाबेस में उपलब्ध नहीं है।"},
    "disclaimer_lbl":   {"en": "DISCLAIMER", "hi": "अस्वीकरण (DISCLAIMER)"},

    # warning field labels
    "warn_pregnancy":     {"en": "Pregnancy", "hi": "गर्भावस्था (Pregnancy)"},
    "warn_breastfeeding": {"en": "Breastfeeding", "hi": "स्तनपान (Breastfeeding)"},
    "warn_children":      {"en": "Children", "hi": "बच्चे"},
    "warn_elderly":       {"en": "Elderly people", "hi": "बुजुर्ग लोग"},
    "warn_kidney":        {"en": "Kidney problems", "hi": "किडनी संबंधी समस्या"},
    "warn_liver":         {"en": "Liver problems", "hi": "लिवर (जिगर) संबंधी समस्या"},
    "warn_drugs":         {"en": "Interactions with other medicines", "hi": "दूसरी दवाओं के साथ परस्पर प्रभाव"},
    "warn_food":          {"en": "Food / alcohol", "hi": "भोजन / शराब"},

    # ---------------- packaging / expiry ----------------
    "pkg_hdr":          {"en": "PACKAGING INFORMATION (read from the photo)", "hi": "पैकेट की जानकारी (फोटो से पढ़ी गई)"},
    "batch_lbl":        {"en": "Batch number", "hi": "बैच नंबर"},
    "mfg_lbl":          {"en": "Manufacturing date", "hi": "निर्माण तिथि (MFG)"},
    "exp_lbl":          {"en": "Expiry date", "hi": "समाप्ति तिथि (EXP)"},
    "month_printed":    {"en": "(month printed on the pack)", "hi": "(packet पर छपा महीना)"},
    "status_lbl":       {"en": "EXPIRY STATUS", "hi": "समाप्ति स्थिति"},
    "status_expired":   {"en": "!! EXPIRED (as per the printed date)",
                         "hi": "!! समाप्त हो चुकी है (छपी तारीख के अनुसार)"},
    "expired_advice":   {"en": "Do NOT use this medicine. Ask a\n                           pharmacist about safe disposal.",
                         "hi": "इस दवा का उपयोग न करें। सुरक्षित निस्तारण हेतु\n                           फार्मासिस्ट से पूछें।"},
    "status_soon":      {"en": "!! EXPIRING SOON - within about\n                           {n} days (as per the printed date).",
                         "hi": "!! जल्द समाप्त होने वाली - लगभग {n} दिनों के\n                           भीतर (छपी तारीख के अनुसार)।"},
    "soon_advice":      {"en": "Ask a pharmacist before use.",
                         "hi": "उपयोग से पहले फार्मासिस्ट से पूछें।"},
    "status_valid":     {"en": "NOT EXPIRED (as per the printed date)",
                         "hi": "समाप्त नहीं हुई (छपी तारीख के अनुसार)"},
    "month_convention": {"en": "Note: packs showing only a month are generally valid\n        until the END of that month - follow the label.",
                         "hi": "ध्यान दें: केवल महीना छपी packs आमतौर पर उस महीने के\n        अंत तक मान्य होती हैं - label का पालन करें।"},
    "no_expiry":        {"en": "Expiry date could not be detected. Please check the medicine packaging manually.",
                         "hi": "समाप्ति तिथि नहीं पढ़ी जा सकी। कृपया दवा का packet स्वयं जाँचें।"},
    "no_pkg_details":   {"en": "No manufacturing / expiry / batch details could be read\n  from this photo.",
                         "hi": "इस फोटो से निर्माण / समाप्ति / बैच की जानकारी\n  नहीं पढ़ी जा सकी।"},
    "ocr_verify":       {"en": "IMPORTANT: OCR can misread dates - always confirm on the\n  physical packaging. Even an unexpired medicine can be unfit\n  if stored badly; when in doubt, ask a pharmacist.",
                         "hi": "महत्वपूर्ण: OCR तारीख गलत पढ़ सकता है - हमेशा असली packet\n  से जाँच करें। समाप्ति से पहले की दवा भी खराब storage से\n  बेकार हो सकती है; संदेह हो तो फार्मासिस्ट से पूछें।"},

    # ---------------- history (Phase 8) ----------------
    "opt_history":        {"en": "Medicine history", "hi": "दवा history (पिछली खोजें)"},
    "history_hdr":        {"en": "Your medicine history (newest first):", "hi": "आपकी दवा history (सबसे नई पहले):"},
    "history_empty":      {"en": "No history yet. Medicines you open will appear here.",
                           "hi": "अभी कोई history नहीं है। आप जो दवाएँ खोलेंगे वे यहाँ दिखेंगी।"},
    "history_prompt":     {"en": "Enter a number to open it, D+number to delete (e.g. D3), C to clear all, or Enter to go back: ",
                           "hi": "खोलने के लिए नंबर दबाएँ, मिटाने के लिए D+नंबर (जैसे D3), सब मिटाने के लिए C, वापस जाने के लिए Enter: "},
    "history_confirm":    {"en": "Really clear ALL history? Type Y to confirm: ",
                           "hi": "क्या पूरी history सच में मिटा दें? पक्का करने के लिए Y दबाएँ: "},
    "history_cancelled":  {"en": "Cancelled - nothing was deleted.", "hi": "रद्द किया गया - कुछ भी नहीं मिटा।"},
    "history_cleared":    {"en": "Cleared {n} history entries.", "hi": "{n} history entries मिटा दी गईं।"},
    "history_deleted":    {"en": "Deleted that history entry.", "hi": "वह history entry मिटा दी गई।"},
    "history_invalid":    {"en": "That is not a valid history number.", "hi": "यह सही history नंबर नहीं है।"},
    "history_med_gone":   {"en": "That medicine is no longer in the database.",
                           "hi": "वह दवा अब डेटाबेस में नहीं है।"},
    "via_search":         {"en": "search", "hi": "खोज"},
    "via_scan":           {"en": "scan", "hi": "स्कैन"},
    "st_valid":           {"en": "Not expired", "hi": "समाप्त नहीं हुई"},
    "st_expired":         {"en": "EXPIRED !!", "hi": "समाप्त !!"},
    "st_soon":            {"en": "Expiring soon", "hi": "जल्द समाप्त"},
    "st_none":            {"en": "-", "hi": "-"},

    # ================= Phase 9 (v0.5): new home + settings ================
    "greet_morning":    {"en": "Good morning", "hi": "सुप्रभात"},
    "greet_afternoon":  {"en": "Good afternoon", "hi": "नमस्कार"},
    "greet_evening":    {"en": "Good evening", "hi": "शुभ संध्या"},
    "status_none":      {"en": "No doses scheduled today", "hi": "आज कोई dose निर्धारित नहीं"},
    "status_progress":  {"en": "{taken} of {total} doses taken today", "hi": "आज {total} में से {taken} doses ली गईं"},
    "status_all_done":  {"en": "All doses taken today - great!", "hi": "आज की सभी doses ली गईं - बहुत बढ़िया!"},
    "search_hint":      {"en": "Search pills, symptoms, or brand", "hi": "गोली, लक्षण या brand खोजें"},
    "upcoming_dose":    {"en": "UPCOMING DOSE", "hi": "आगामी DOSE"},
    "due_now":          {"en": "DUE NOW", "hi": "अभी लेनी है"},
    "alert_note":       {"en": "We will alert you at the scheduled time", "hi": "तय समय पर हम आपको सुनाएंगे"},
    "take_now":         {"en": "Take Now", "hi": "अभी लें"},
    "snooze_15":        {"en": "Snooze 15m", "hi": "15 मिनट बाद"},
    "snoozed_msg":      {"en": "Snoozed for 15 minutes.", "hi": "15 मिनट के लिए टाला गया."},
    "dose_recorded":    {"en": "Dose recorded - well done!", "hi": "Dose दर्ज हो गई - बहुत बढ़िया!"},
    "no_doses_today":   {"en": "No doses scheduled for today. Tap + to add a reminder.",
                         "hi": "आज कोई dose निर्धारित नहीं। Reminder जोड़ने के लिए + दबाएँ।"},
    "quick_actions":    {"en": "Quick Actions", "hi": "त्वरित कार्य (Quick Actions)"},
    "on_device_ai":     {"en": "On-device AI", "hi": "On-device AI"},
    "add_scan":         {"en": "Add / Scan", "hi": "जोड़ें / स्कैन करें"},
    "qa_scan":          {"en": "Scan Medicine", "hi": "दवा स्कैन करें"},
    "qa_scan_sub":      {"en": "Scan bottles, strips and labels", "hi": "बोतल, strip और label स्कैन करें"},
    "qa_reminders":     {"en": "Reminders", "hi": "रिमाइंडर"},
    "qa_rem_sub":       {"en": "{n} active", "hi": "{n} चालू"},
    "qa_cabinet":       {"en": "My Cabinet", "hi": "मेरी Cabinet"},
    "qa_cab_sub":       {"en": "{n} items", "hi": "{n} दवाएँ"},
    "qa_family":        {"en": "Family Care", "hi": "परिवार की देखभाल"},
    "qa_fam_sub":       {"en": "{n} members", "hi": "{n} सदस्य"},
    "qa_auth":          {"en": "Authenticity", "hi": "असली या नकली?"},
    "qa_auth_sub":      {"en": "Genuine-pack checklist", "hi": "असली packet की checklist"},
    "qa_storage":       {"en": "Storage Guide", "hi": "स्टोरेज गाइड"},
    "qa_storage_sub":   {"en": "Where to keep medicines", "hi": "दवाएं कहाँ रखें"},
    "nav_home":         {"en": "Home", "hi": "होम"},
    "nav_history":      {"en": "History", "hi": "History"},
    "nav_reminders":    {"en": "Reminders", "hi": "रिमाइंडर"},
    "nav_profile":      {"en": "Profile", "hi": "प्रोफ़ाइल"},

    # ---------------- add / scan sheet ----------------
    "sheet_scan":       {"en": "Scan a pack photo", "hi": "Packet की फोटो स्कैन करें"},
    "sheet_reminder":   {"en": "Add a reminder", "hi": "Reminder जोड़ें"},
    "sheet_cabinet":    {"en": "Add to medicine cabinet", "hi": "Cabinet में दवा जोड़ें"},
    "sheet_member":     {"en": "Add a family member", "hi": "परिवार के सदस्य को जोड़ें"},
    "sheet_search":     {"en": "Search a medicine", "hi": "दवा खोजें"},

    # ---------------- voice search ----------------
    "voice_listening":  {"en": "Listening - please speak the medicine name...",
                         "hi": "सुन रहे हैं - कृपया दवा का नाम बोलें..."},
    "voice_fail":       {"en": "Sorry, I could not hear that. Please type the name instead.",
                         "hi": "माफ़ कीजिए, ठीक से सुनाई नहीं दिया। कृपया नाम लिखें।"},
    "voice_perm":       {"en": "Microphone permission is needed for voice search.",
                         "hi": "Voice search के लिए microphone की अनुमति चाहिए।"},
    "voice_none":       {"en": "No speech recognised - please type instead.",
                         "hi": "कुछ भी सुनाई नहीं दिया - कृपया लिखकर खोजें।"},
    "voice_desktop":    {"en": "(Voice search works in the Android app; here please type.)",
                         "hi": "(Voice search Android ऐप में चलता है; यहाँ कृपया लिखें.)"},

    # ---------------- profile & settings ----------------
    "prof_title":       {"en": "Profile & Settings", "hi": "प्रोफ़ाइल और Settings"},
    "your_name":        {"en": "YOUR NAME", "hi": "आपका नाम"},
    "save":             {"en": "Save", "hi": "सेव करें"},
    "language":         {"en": "Language", "hi": "भाषा"},
    "dark_mode":        {"en": "Dark mode", "hi": "डार्क मोड"},
    "light_app":        {"en": "Light appearance", "hi": "हल्का रूप"},
    "dark_app":         {"en": "Dark appearance", "hi": "गहरा रूप"},
    "light_short":      {"en": "Light", "hi": "लाइट"},
    "dark_short":       {"en": "Dark", "hi": "डार्क"},
    "explain_lbl":      {"en": "Explanation level", "hi": "जानकारी का स्तर"},
    "lv_simple":        {"en": "Simple", "hi": "सरल"},
    "lv_normal":        {"en": "Normal", "hi": "सामान्य"},
    "lv_detailed":      {"en": "Detailed", "hi": "विस्तृत"},
    "notif_row":        {"en": "Notifications & reminders", "hi": "सूचनाएं और reminders"},
    "notif_sub":        {"en": "Voice reminders speak inside the app while it is open",
                         "hi": "ऐप खुली होने पर voice reminders बोलकर सुनाते हैं"},
    "clear_hist":       {"en": "Clear history & logs", "hi": "History और records मिटाएँ"},
    "clear_hist_sub":   {"en": "Remove locally saved records", "hi": "फ़ोन में सहेजे records हटाएँ"},
    "clear_done":       {"en": "Done - local records cleared.", "hi": "हो गया - records मिटा दिए गए।"},
    "privacy_footer":   {"en": "Medicine Assistant - everything runs on this device.\nReminders, scan, search and history never leave your phone.\nBundled medicine records are DEMO data (unverified sample).",
                         "hi": "Medicine Assistant - सब कुछ इसी फ़ोन पर चलता है।\nReminders, scan, search और history कभी फ़ोन से बाहर नहीं जाती।\nसाथ में दिए medicine records DEMO data हैं (असत्यापित नमूना)।"},

    # ---------------- medicine cabinet ----------------
    "cabinet_title":    {"en": "Medicine Cabinet", "hi": "मेडिसिन Cabinet"},
    "cab_empty":        {"en": "Your cabinet is empty. Add the medicines you keep at home - quantity, dosage and expiry - and the app will watch them for you.",
                         "hi": "आपकी cabinet खाली है। घर पर रखी दवाएँ जोड़ें - मात्रा, dose और expiry - ऐप उन पर नज़र रखेगा।"},
    "cab_add":          {"en": "Add medicine to cabinet", "hi": "Cabinet में दवा जोड़ें"},
    "cab_name":         {"en": "Medicine name", "hi": "दवा का नाम"},
    "cab_strength2":    {"en": "Strength (e.g. 500 mg)", "hi": "मात्रा (जैसे 500 mg)"},
    "cab_qty":          {"en": "Quantity left", "hi": "बची मात्रा"},
    "cab_unit":         {"en": "Unit (tablets/ml)", "hi": "इकाई (गोलियाँ/ml)"},
    "cab_dosage":       {"en": "Dosage (e.g. 1 tablet twice a day)", "hi": "Dose (जैसे दिन में दो बार 1 गोली)"},
    "cab_exp":          {"en": "Expiry (e.g. 2027-03)", "hi": "Expiry (जैसे 2027-03)"},
    "cab_place":        {"en": "Where do you keep it?", "hi": "इसे कहाँ रखते हैं?"},
    "cab_save":         {"en": "Save to cabinet", "hi": "Cabinet में सहेजें"},
    "cab_need_name":    {"en": "Please type the medicine name.", "hi": "कृपया दवा का नाम लिखें।"},
    "cab_took1":        {"en": "Took 1 dose", "hi": "1 dose ली"},
    "cab_left":         {"en": "{qty} {unit} left", "hi": "{qty} {unit} बची हैं"},
    "cab_delete2":      {"en": "Delete", "hi": "हटाएँ"},
    "who_card":         {"en": "Who can take it?", "hi": "इसे कौन ले सकता है?"},
    "storage_card":     {"en": "Storage", "hi": "स्टोरेज (कहाँ रखें)"},

    # ---------------- expiry dashboard ----------------
    "exp_dash":         {"en": "Expiry Status", "hi": "Expiry की स्थिति"},
    "exp_active":       {"en": "Active (not expired)", "hi": "सही (समाप्त नहीं)"},
    "exp_soon2":        {"en": "Expiring soon", "hi": "जल्द समाप्त"},
    "exp_expired2":     {"en": "Expired - do NOT use", "hi": "समाप्त - उपयोग न करें"},
    "exp_nodate":       {"en": "No date recorded", "hi": "कोई तारीख नहीं"},
    "speak_summary":    {"en": "Speak expiry summary", "hi": "Expiry सारांश सुनें"},
    "exp_dispose_note": {"en": "Do NOT use expired medicines. Ask a pharmacist about safe disposal.",
                         "hi": "समाप्त दवाओं का उपयोग न करें। सुरक्षित निस्तारण हेतु फार्मासिस्ट से पूछें।"},

    # ---------------- reminders ----------------
    "rem_title":        {"en": "Reminders", "hi": "रिमाइंडर"},
    "rem_empty":        {"en": "No reminders yet. Add one and the app will SPEAK the dose at the right time while it is open.",
                         "hi": "अभी कोई reminder नहीं। एक जोड़ें - ऐप खुली होने पर सही समय पर dose बोलकर बताएगा।"},
    "rem_add":          {"en": "Add reminder", "hi": "Reminder जोड़ें"},
    "rem_member":       {"en": "Who takes this medicine?", "hi": "यह दवा कौन लेता है?"},
    "self_member":      {"en": "You (Self)", "hi": "आप (खुद)"},
    "rem_med":          {"en": "Medicine name", "hi": "दवा का नाम"},
    "rem_str":          {"en": "Strength", "hi": "मात्रा"},
    "rem_times":        {"en": "Dose times, 24h (e.g. 08:00, 20:30)", "hi": "Dose का समय, 24h (जैसे 08:00, 20:30)"},
    "rem_save":         {"en": "Save reminder", "hi": "Reminder सहेजें"},
    "rem_need_med":     {"en": "Please type the medicine name.", "hi": "कृपया दवा का नाम लिखें।"},
    "rem_on":           {"en": "on", "hi": "चालू"},
    "rem_off":          {"en": "off", "hi": "बंद"},
    "daily":            {"en": "Daily", "hi": "रोज़"},
    "rem_at":           {"en": "at", "hi": "बजे"},

    # ---------------- family care ----------------
    "fam_title":        {"en": "Family Care", "hi": "परिवार की देखभाल"},
    "fam_empty":        {"en": "Add family members to manage their medicines and reminders in one place.",
                         "hi": "परिवार के सदस्यों को जोड़ें और उनकी दवाएँ व reminders एक जगह संभालें।"},
    "fam_add":          {"en": "Add member", "hi": "सदस्य जोड़ें"},
    "fam_name":         {"en": "Name (e.g. Dadi)", "hi": "नाम (जैसे दादी)"},
    "fam_relation":     {"en": "Relation (e.g. Grandmother)", "hi": "रिश्ता (जैसे दादी)"},
    "fam_need_name":    {"en": "Please type the member's name.", "hi": "कृपया सदस्य का नाम लिखें।"},
    "fam_rem_count":    {"en": "{n} reminders", "hi": "{n} reminders"},

    # ---------------- authenticity + storage screens ----------------
    "auth_title":       {"en": "Authenticity Checklist", "hi": "असली दवा की Checklist"},
    "auth_link":        {"en": "How to spot a genuine or fake medicine >", "hi": "असली या नकली दवा कैसे पहचानें >"},
    "stor_title":       {"en": "Storage Guide", "hi": "स्टोरेज गाइड"},
    "stor_from_cabinet": {"en": "Your recorded storage places", "hi": "आपके दर्ज किए storage स्थान"},
    "stor_tips":        {"en": "1. Keep medicines in a cool, dry place - away from sunlight and the bathroom's dampness.\n\n2. Only syrups/drops that say so on the label go in the fridge - not every medicine.\n\n3. Keep everything out of children's reach, in a locked or high cabinet.\n\n4. Never store medicines near the kitchen stove or a window - heat damages them.\n\n5. Keep tablets in their original strip/bottle with the name and expiry visible.",
                         "hi": "1. दवाएं ठंडी, सूखी जगह रखें - धूप और बाथरूम की नमी से दूर।\n\n2. केवल वही syrup/drops fridge में रखें जिनके label पर लिखा हो - हर दवा नहीं।\n\n3. सभी दवाएं बच्चों की पहुँच से दूर, ऊँची या बंद अलमारी में रखें।\n\n4. चूल्हे या खिड़की के पास दवाएं न रखें - गर्मी से खराब होती हैं।\n\n5. गोलियाँ उनकी असली strip/बोतल में रखें जिस पर नाम और expiry दिखे।"},
}


# =====================================================================
# v0.6 - professional-pass keys (toasts, scan screen, details actions,
# short expiry chips, back button, topbar tagline)
# =====================================================================
STRINGS.update({
    # ---- generic action feedback (toasts) ----
    "saved_done":        {"en": "Saved", "hi": "सेव हो गया"},
    "deleted_done":      {"en": "Deleted", "hi": "हटा दिया गया"},
    "rem_saved":         {"en": "Reminder saved", "hi": "Reminder सेव हो गया"},
    "rem_on_msg":        {"en": "Reminder is ON", "hi": "Reminder चालू है"},
    "rem_off_msg":       {"en": "Reminder is OFF", "hi": "Reminder बंद है"},
    "cab_added":         {"en": "Added to your cabinet", "hi": "Cabinet में जोड़ दी गई"},
    "qty_updated":       {"en": "Quantity updated", "hi": "मात्रा अपडेट हो गई"},
    "member_added":      {"en": "Member added", "hi": "सदस्य जोड़ दिया गया"},
    "lang_changed":      {"en": "Language updated", "hi": "भाषा बदल गई"},
    "cancelled":         {"en": "Cancelled.", "hi": "रद्द किया।"},

    # ---- topbar / back ----
    "topbar_sub":        {"en": "OFFLINE  •  PRIVATE  •  FREE",
                          "hi": "ऑफ़लाइन  •  निजी  •  मुफ़्त"},
    "back_btn":          {"en": "Back", "hi": "वापस"},

    # ---- details action row + share ----
    "btn_listen":        {"en": "LISTEN", "hi": "सुनें"},
    "btn_stop":          {"en": "STOP", "hi": "रोकें"},
    "btn_share":         {"en": "SHARE", "hi": "शेयर"},
    "add_to_cab":        {"en": "+ Cabinet", "hi": "+ Cabinet"},
    "share_note":        {"en": "Shared from Medicine Assistant (offline app)\nNOTE: General info only - not medical advice.\n\n",
                          "hi": "Medicine Assistant (offline ऐप) से share किया\nध्यान दें: केवल सामान्य जानकारी - medical सलाह नहीं।\n\n"},
    "share_app_only":    {"en": "(Share works inside the Android app.)",
                          "hi": "(Share Android ऐप में चलता है।)"},

    # ---- expired banner on details ----
    "expired_go":        {"en": "EXPIRED - DO NOT USE THIS MEDICINE",
                          "hi": "समाप्त - इस दवा का उपयोग न करें"},
    "expired_get_fresh": {"en": "Please get a fresh supply - ask a pharmacist/doctor.",
                          "hi": "कृपया नई दवा लें - फार्मासिस्ट/डॉक्टर से पूछें।"},

    # ---- scan screen ----
    "or_type_pack":      {"en": "OR TYPE THE PACK TEXT",
                          "hi": "या packet का text लिखें"},
    "check_expiry_btn":  {"en": "Check expiry", "hi": "Expiry जाँचें"},
    "scan_no_known":     {"en": "NO KNOWN MEDICINE FOUND",
                          "hi": "कोई जानी दवा नहीं मिली"},
    "scan_text_read":    {"en": "TEXT THAT WAS READ", "hi": "जो text पढ़ा गया"},
    "scan_gallery_sub":  {"en": "From gallery - the photo is never saved,\nit is scanned fully on this device",
                          "hi": "Gallery से - फोटो कभी save नहीं होती,\nइसी फ़ोन पर स्कैन होती है"},
    "scan_app_only":     {"en": "Photo scan works inside the Android app.",
                          "hi": "फोटो स्कैन Android ऐप में चलता है।"},
    "scan_text_ok":      {"en": "OK - text received - results below.",
                          "hi": "OK - text मिल गया - results नीचे।"},
    "scan_text_empty":   {"en": "Text is empty.", "hi": "Text खाली है।"},

    # ---- history ----
    "hist_note":         {"en": "Text only - photos are never stored.",
                          "hi": "Sirf text - फोटो कभी save नहीं होती।"},
    "go_short":          {"en": "Search", "hi": "खोजें"},

    # ---- short expiry chips (tight rows) ----
    "exp_active_short":  {"en": "Active", "hi": "सही"},
    "exp_soon_short":    {"en": "Soon", "hi": "जल्द"},
    "exp_expired_short": {"en": "Expired", "hi": "समाप्त"},
})


def t(key: str, language: str = EN, **format_values) -> str:
    """
    Get the text for `key` in `language` (falls back to English).
    Use {placeholders} via format_values, e.g. t("found_results", "hi", n=3).
    """
    if key not in STRINGS:
        raise KeyError(f"Unknown language key: {key!r}")
    entry = STRINGS[key]
    text = entry.get(language) or entry[EN]
    if format_values:
        text = text.format(**format_values)
    return text
