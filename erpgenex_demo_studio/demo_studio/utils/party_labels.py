from __future__ import annotations

HEALTHCARE_TOKENS = frozenset(
	{
		"healthcare",
		"health care",
		"medical",
		"hospital",
		"clinic",
		"صحي",
		"صحة",
		"طبي",
		"مستشف",
	}
)
EDUCATION_TOKENS = frozenset(
	{
		"education",
		"nursery",
		"school",
		"academy",
		"training",
		"تعليم",
		"تعليمي",
		"مدرس",
		"أكاديم",
	}
)


def _normalize(value) -> str:
	return (value or "").strip().lower()


def _activity_blob(*values) -> str:
	return " ".join(_normalize(value) for value in values if value)


def classify_party_context(
	business_activity: str = "",
	industry_sector: str = "",
	industry: str = "",
) -> str:
	"""Return healthcare, education, or general based on company activity."""
	blob = _activity_blob(business_activity, industry_sector, industry)
	if any(token in blob for token in HEALTHCARE_TOKENS):
		return "healthcare"
	if any(token in blob for token in EDUCATION_TOKENS):
		return "education"
	return "general"


def resolve_customer_party_label(
	business_activity: str = "",
	industry_sector: str = "",
	industry: str = "",
	lang: str = "en",
	plural: bool = True,
) -> str:
	"""Return the user-facing customer-party label for the given activity."""
	arabic = (lang or "en").lower().startswith("ar")
	context = classify_party_context(business_activity, industry_sector, industry)

	if context == "healthcare":
		if plural:
			return "مرضى" if arabic else "Patients"
		return "مريض" if arabic else "Patient"

	if context == "education":
		if plural:
			return "طلاب" if arabic else "Students"
		return "طالب" if arabic else "Student"

	if plural:
		return "عملاء" if arabic else "Customers"
	return "عميل" if arabic else "Customer"
