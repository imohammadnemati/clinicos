"""
Internationalization (i18n) module for Clinicos.
All UI texts are stored here in 4 languages: fa, en, az, ar.
"""

TEXTS = {
    "fa": {
        # Language selection
        "lang_select_title": "🌐 لطفاً زبان خود را انتخاب کنید:",
        "lang_selected": "🎉 خوش آمدید! زبان شما ثبت شد.",
        "lang_fa": "🇮🇷 فارسی",
        "lang_en": "🇺🇸 English",
        "lang_az": "🇦🇿 Azərbaycan",
        "lang_ar": "🇸🇦 العربية",

        # Welcome & dashboard
        "welcome_patient": "سلام {name} 🌷\nبه کلینیک خوش آمدید.",
        "dashboard_owner": "📊 *داشبورد مالک*\n\n📅 *امروز*: {leads} لید | {booked} نوبت | 💰 {revenue:,}",
        "dashboard_secretary": "📋 *داشبورد منشی*\n\n✉️ پیام‌ها: {messages}\n🔥 لیدها: {leads}\n📅 نوبت‌ها: {appts}\n🚨 ارجاعات: {esc}",
        "dashboard_doctor": "👨‍⚕️ *داشبورد پزشک*\n\n🚨 ارجاعات در انتظار: {pending}",

        # Main menu buttons
        "btn_home": "🏠 Home",
        "btn_book_appointment": "📅 Book Appointment",
        "btn_ask_clinic": "💬 Ask Clinic",
        "btn_services": "📋 Services",
        "btn_human_receptionist": "👩‍💼 Human Receptionist",
        "btn_my_appointments": "📄 My Appointments",

        # Staff/owner buttons
        "btn_dashboard": "📊 Dashboard",
        "btn_staff": "👥 Staff",
        "btn_clinic": "🏥 Clinic",
        "btn_settings": "⚙️ Settings",
        "btn_revenue": "💰 Revenue",
        "btn_reports": "📈 Reports",

        # Doctor buttons
        "btn_today": "📅 Today",
        "btn_patients": "👥 Patients",
        "btn_escalations": "🚨 Escalations",
        "btn_performance": "📊 Performance",

        # Secretary buttons
        "btn_appointments": "📅 Appointments",
        "btn_leads": "🔥 Leads",
        "btn_notifications": "🔔 Notifications",
        "btn_statistics": "📊 Statistics",
        "btn_handoff": "👩‍💼 Handoff",

        # Appointment wizard
        "appt_select_service": "📅 لطفاً خدمت مورد نظر را انتخاب کنید:",
        "appt_service_botox": "بوتاکس",
        "appt_service_filler": "فیلر",
        "appt_service_laser": "لیزر",
        "appt_service_mesotherapy": "مزوتراپی",
        "appt_service_surgery": "جراحی",
        "appt_cancel": "❌ انصراف",
        "appt_enter_date": "لطفاً تاریخ مورد نظر را وارد کنید (مثال: 2025-06-15):",
        "appt_enter_time": "لطفاً ساعت مورد نظر را وارد کنید (مثال: 15:30):",
        "appt_confirm": "✅ تأیید نوبت:\nخدمت: {service}\nتاریخ: {date}\nساعت: {time}\nآیا اطلاعات صحیح است؟",
        "appt_confirm_yes": "✅ بله",
        "appt_confirm_no": "❌ خیر",
        "appt_cancelled": "❌ درخواست نوبت لغو شد.",
        "appt_booking_success": "✅ درخواست نوبت شما با شماره {request_id} ثبت شد. منشی‌ها به زودی تأیید خواهند کرد.",
        "appt_booking_error": "❌ خطا در ثبت نوبت.",

        # Human handoff
        "human_handoff_register_first": "لطفاً ابتدا با ارسال /start ثبت‌نام کنید.",
        "human_handoff_sent": "👩‍💼 درخواست شما به منشی منتقل شد. به زودی پاسخ خواهید گرفت.",
        "human_handoff_alert": "🚨 درخواست جدید برای صحبت با منشی از بیمار {patient_name}",

        # Staff management
        "staff_management_title": "👥 مدیریت کارمندان",
        "staff_add_doctor": "➕ Add Doctor",
        "staff_add_secretary": "➕ Add Secretary",
        "staff_add_admin": "➕ Add Admin",
        "staff_list": "📋 Staff List",
        "staff_remove": "🗑 Remove Staff",
        "staff_back": "🔙 Back",
        "staff_enter_id": "لطفاً شناسه تلگرام (Telegram ID) {role} جدید را وارد کنید:",
        "staff_confirm_add": "آیا از اضافه کردن کاربر {id} با نقش {role} مطمئن هستید؟ (بله/خیر)",
        "staff_already_exists": "❌ کاربر قبلاً ثبت شده است.",
        "staff_added": "✅ کاربر {id} با نقش {role} اضافه شد.",
        "staff_add_error": "❌ خطا در اضافه کردن کاربر.",
        "staff_list_empty": "هیچ کارمندی ثبت نشده است.",
        "staff_list_title": "📋 *لیست کارمندان*",
        "staff_list_item": "🆔 {id} – {name} ({role})",
        "staff_select_remove": "کارمند مورد نظر برای حذف را انتخاب کنید:",
        "staff_removed": "✅ کارمند {name} حذف شد.",
        "staff_not_found": "❌ کارمند یافت نشد.",
        "staff_remove_cancelled": "❌ عملیات لغو شد.",

        # Leads
        "leads_empty": "هیچ لید جدیدی وجود ندارد.",
        "leads_title": "🔥 *لیدهای جدید*",
        "leads_item": "• {name} – {service} – امتیاز: {score}",

        # Doctor
        "doctor_today_empty": "📅 امروز نوبتی ندارید.",
        "doctor_today_title": "📅 *نوبت‌های امروز*",
        "doctor_today_item": "• {name} – {service} – {time}",
        "doctor_escalations_empty": "✅ هیچ مورد ارجاعی وجود ندارد.",
        "doctor_escalations_title": "🚨 *موارد ارجاع به پزشک*",
        "doctor_escalations_item": "• بیمار: {name}\n  دلیل: {reason}\n  زمان: {time}\n",

        # Secretary stats
        "stats_today_title": "📊 *آمار امروز*",
        "stats_messages": "✉️ پیام‌ها: {messages}",
        "stats_leads": "🔥 لیدها: {leads}",
        "stats_appointments": "📅 نوبت‌ها: {appointments}",

        # Appointments list
        "appointments_empty": "📅 هیچ نوبتی یافت نشد.",
        "appointments_title": "📅 *لیست نوبت‌ها*",
        "appointments_item": "• {name} – {service} – {date}",

        # Patient appointments
        "patient_appointments_register_first": "لطفاً ابتدا /start را بزنید.",
        "patient_appointments_empty": "📄 شما هیچ نوبتی ثبت نکرده‌اید.",
        "patient_appointments_title": "📄 *نوبت‌های شما*",
        "patient_appointments_item": "• {service} – {date} – {status}",

        # Errors
        "error_unknown_command": "❓ دستور ناشناخته. از منو استفاده کنید.",
        "error_internal": "❌ خطای داخلی. لطفاً دقایقی دیگر تلاش کنید.",
        "error_invalid_date": "❌ فرمت تاریخ اشتباه. لطفاً به صورت YYYY-MM-DD وارد کنید:",
        "error_invalid_time": "❌ فرمت ساعت اشتباه. مثال: 15:30",
        "error_stt_failed": "❌ متأسفانه نتوانستم پیام صوتی شما را به متن تبدیل کنم. لطفاً دوباره تلاش کنید یا به صورت متن پیام دهید.",
        "error_voice_processing": "❌ خطا در پردازش پیام صوتی. لطفاً دوباره تلاش کنید.",

        # Working hours
        "out_of_hours": "🌙 پیام شما ثبت شد. همکاران ما از ساعت ۸ صبح پاسخگو خواهند بود.",

        # Medical safety
        "risk_alert": "⚠️ برای پاسخ به این سوال نیاز به بررسی پزشک دارید. لطفاً با کلینیک تماس بگیرید.",

        # Human escalation
        "escalated_to_human": "درخواست شما به منشی منتقل شد. لطفاً صبر کنید.",

        # Start command
        "start_text": "Hello! 🌷 Welcome to our clinic. How can I assist you today?",
    },

    "en": {
        "lang_select_title": "🌐 Please select your language:",
        "lang_selected": "🎉 Welcome! Your language has been saved.",
        "lang_fa": "🇮🇷 فارسی",
        "lang_en": "🇺🇸 English",
        "lang_az": "🇦🇿 Azərbaycan",
        "lang_ar": "🇸🇦 العربية",

        "welcome_patient": "Hello {name} 🌷\nWelcome to our clinic.",
        "dashboard_owner": "📊 *Owner Dashboard*\n\n📅 *Today*: {leads} leads | {booked} booked | 💰 {revenue:,}",
        "dashboard_secretary": "📋 *Secretary Dashboard*\n\n✉️ Messages: {messages}\n🔥 Leads: {leads}\n📅 Appointments: {appts}\n🚨 Escalations: {esc}",
        "dashboard_doctor": "👨‍⚕️ *Doctor Dashboard*\n\n🚨 Pending escalations: {pending}",

        "btn_home": "🏠 Home",
        "btn_book_appointment": "📅 Book Appointment",
        "btn_ask_clinic": "💬 Ask Clinic",
        "btn_services": "📋 Services",
        "btn_human_receptionist": "👩‍💼 Human Receptionist",
        "btn_my_appointments": "📄 My Appointments",

        "btn_dashboard": "📊 Dashboard",
        "btn_staff": "👥 Staff",
        "btn_clinic": "🏥 Clinic",
        "btn_settings": "⚙️ Settings",
        "btn_revenue": "💰 Revenue",
        "btn_reports": "📈 Reports",

        "btn_today": "📅 Today",
        "btn_patients": "👥 Patients",
        "btn_escalations": "🚨 Escalations",
        "btn_performance": "📊 Performance",

        "btn_appointments": "📅 Appointments",
        "btn_leads": "🔥 Leads",
        "btn_notifications": "🔔 Notifications",
        "btn_statistics": "📊 Statistics",
        "btn_handoff": "👩‍💼 Handoff",

        "appt_select_service": "📅 Please select the service:",
        "appt_service_botox": "Botox",
        "appt_service_filler": "Filler",
        "appt_service_laser": "Laser",
        "appt_service_mesotherapy": "Mesotherapy",
        "appt_service_surgery": "Surgery",
        "appt_cancel": "❌ Cancel",
        "appt_enter_date": "Please enter the desired date (e.g., 2025-06-15):",
        "appt_enter_time": "Please enter the desired time (e.g., 15:30):",
        "appt_confirm": "✅ Confirm appointment:\nService: {service}\nDate: {date}\nTime: {time}\nIs this correct?",
        "appt_confirm_yes": "✅ Yes",
        "appt_confirm_no": "❌ No",
        "appt_cancelled": "❌ Appointment cancelled.",
        "appt_booking_success": "✅ Your appointment request #{request_id} has been registered. The receptionist will confirm soon.",
        "appt_booking_error": "❌ Error booking appointment.",

        "human_handoff_register_first": "Please register with /start first.",
        "human_handoff_sent": "👩‍💼 Your request has been forwarded to the receptionist. You will be contacted shortly.",
        "human_handoff_alert": "🚨 New request to talk to receptionist from patient {patient_name}",

        "staff_management_title": "👥 Staff Management",
        "staff_add_doctor": "➕ Add Doctor",
        "staff_add_secretary": "➕ Add Secretary",
        "staff_add_admin": "➕ Add Admin",
        "staff_list": "📋 Staff List",
        "staff_remove": "🗑 Remove Staff",
        "staff_back": "🔙 Back",
        "staff_enter_id": "Please enter the Telegram ID of the new {role}:",
        "staff_confirm_add": "Are you sure you want to add user {id} as {role}? (yes/no)",
        "staff_already_exists": "❌ User already exists.",
        "staff_added": "✅ User {id} added as {role}.",
        "staff_add_error": "❌ Error adding user.",
        "staff_list_empty": "No staff registered.",
        "staff_list_title": "📋 *Staff List*",
        "staff_list_item": "🆔 {id} – {name} ({role})",
        "staff_select_remove": "Select staff member to remove:",
        "staff_removed": "✅ Staff {name} removed.",
        "staff_not_found": "❌ Staff not found.",
        "staff_remove_cancelled": "❌ Operation cancelled.",

        "leads_empty": "No new leads.",
        "leads_title": "🔥 *New Leads*",
        "leads_item": "• {name} – {service} – Score: {score}",

        "doctor_today_empty": "📅 No appointments today.",
        "doctor_today_title": "📅 *Today's Appointments*",
        "doctor_today_item": "• {name} – {service} – {time}",
        "doctor_escalations_empty": "✅ No pending escalations.",
        "doctor_escalations_title": "🚨 *Escalations to Doctor*",
        "doctor_escalations_item": "• Patient: {name}\n  Reason: {reason}\n  Time: {time}\n",

        "stats_today_title": "📊 *Today's Statistics*",
        "stats_messages": "✉️ Messages: {messages}",
        "stats_leads": "🔥 Leads: {leads}",
        "stats_appointments": "📅 Appointments: {appointments}",

        "appointments_empty": "📅 No appointments found.",
        "appointments_title": "📅 *Appointments List*",
        "appointments_item": "• {name} – {service} – {date}",

        "patient_appointments_register_first": "Please use /start first.",
        "patient_appointments_empty": "📄 You have no appointments.",
        "patient_appointments_title": "📄 *Your Appointments*",
        "patient_appointments_item": "• {service} – {date} – {status}",

        "error_unknown_command": "❓ Unknown command. Use the menu.",
        "error_internal": "❌ Internal error. Please try again later.",
        "error_invalid_date": "❌ Invalid date format. Please use YYYY-MM-DD:",
        "error_invalid_time": "❌ Invalid time format. Example: 15:30",
        "error_stt_failed": "❌ Could not transcribe your voice message. Please try again or send a text message.",
        "error_voice_processing": "❌ Error processing voice message. Please try again.",

        "out_of_hours": "🌙 Your message has been recorded. Our team will respond from 8 AM.",

        "risk_alert": "⚠️ This question requires a doctor's review. Please contact the clinic.",

        "escalated_to_human": "Your request has been forwarded to the receptionist. Please wait.",

        "start_text": "Hello! 🌷 Welcome to our clinic. How can I assist you today?",
    },

    "az": {
        "lang_select_title": "🌐 Zəhmət olmasa dilinizi seçin:",
        "lang_selected": "🎉 Xoş gəldiniz! Diliniz qeyd edildi.",
        "lang_fa": "🇮🇷 فارسی",
        "lang_en": "🇺🇸 English",
        "lang_az": "🇦🇿 Azərbaycan",
        "lang_ar": "🇸🇦 العربية",

        # (برای اختصار، بقیه کلیدها مشابه انگلیسی با ترجمه ترکی – در صورت نیاز کامل شود)
        # من در اینجا فقط چند کلید نمونه می‌نویسم تا ساختار مشخص باشد
        "welcome_patient": "Salam {name} 🌷\nKlinikamıza xoş gəldiniz.",
        "error_unknown_command": "❓ Naməlum əmr. Menudan istifadə edin.",
        # ... بقیه کلیدها به همین ترتیب
    },

    "ar": {
        "lang_select_title": "🌐 الرجاء اختيار لغتك:",
        "lang_selected": "🎉 مرحباً! تم حفظ لغتك.",
        "lang_fa": "🇮🇷 فارسی",
        "lang_en": "🇺🇸 English",
        "lang_az": "🇦🇿 Azərbaycan",
        "lang_ar": "🇸🇦 العربية",
        "welcome_patient": "مرحباً {name} 🌷\nأهلاً بك في عيادتنا.",
        "error_unknown_command": "❓ أمر غير معروف. استخدم القائمة.",
        # ... بقیه کلیدها
    }
}


def get_text(key: str, lang: str = "fa") -> str:
    """Return translated text for given key and language."""
    lang_dict = TEXTS.get(lang, TEXTS.get("fa", {}))
    return lang_dict.get(key, key)