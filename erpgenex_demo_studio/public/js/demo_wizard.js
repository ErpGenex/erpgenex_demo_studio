// i18n:managed-catalog — bilingual/regional catalog; UI via ar.csv
// Demo Wizard — guided steps + express registration
let wizard,
	templates,
	selectedTemplate,
	currentIndustry,
	pollTimer,
	currentWizardStep = 1,
	companyNameManual = false;

const STEP_KEYS = ["template", "details", "review"];

function getCookie(name) {
	const value = `; ${document.cookie}`;
	const parts = value.split(`; ${name}=`);
	if (parts.length === 2) return parts.pop().split(";").shift();
	return "";
}

async function apiCall(method, args = {}) {
	const response = await fetch(`/api/method/${method}`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			Accept: "application/json",
			"X-Frappe-CSRF-Token": (window.frappe && frappe.csrf_token) || getCookie("csrf_token") || "",
		},
		credentials: "same-origin",
		body: JSON.stringify(args),
	});

	const raw = await response.text();
	let payload = {};
	try {
		payload = raw ? JSON.parse(raw) : {};
	} catch (e) {
		payload = { message: raw };
	}

	if (!response.ok) {
		throw new Error(extractError(payload) || "تعذر الاتصال بالخادم");
	}

	return payload.message;
}

function extractError(payload) {
	if (!payload) return "";
	if (payload._server_messages) {
		try {
			const messages = JSON.parse(payload._server_messages);
			const first = messages
				.map((item) => {
					try {
						return JSON.parse(item).message || item;
					} catch (e) {
						return item;
					}
				})
				.filter(Boolean)[0];
			if (first) return first;
		} catch (e) {
			return payload._server_messages;
		}
	}
	return payload.message || payload.exception || payload.exc || "";
}

function formatLanguage(value) {
	return value === "ar" ? "العربية" : "English";
}

function resolveCustomerLabel(template, lang = "ar") {
	if (!template) return lang === "ar" ? "عملاء" : "Customers";
	if (template.party_context === "healthcare") return lang === "ar" ? "مرضى" : "Patients";
	if (template.party_context === "education") return lang === "ar" ? "طلاب" : "Students";
	if (template.party_context === "legal") return lang === "ar" ? "عملاء قانونيون" : "Legal Clients";
	return lang === "ar" ? "عملاء" : "Customers";
}

function refreshCustomerLabels(lang) {
	const language = lang || (document.getElementById("language") && document.getElementById("language").value) || "ar";
	document.querySelectorAll(".customer-party-label[data-template-name]").forEach((el) => {
		const template = templates.find((t) => t.name === el.dataset.templateName);
		el.textContent = resolveCustomerLabel(template, language);
	});
}

function getSelectedTemplate() {
	return templates.find((t) => t.name === selectedTemplate?.name) || selectedTemplate;
}

function setStatus(message, kind = "info") {
	const el = document.getElementById("statusAlert");
	if (el) {
		el.className = `alert ${kind}`;
		el.textContent = message;
	}
}

function showRegisterLink(demoName) {
	const wrap = document.getElementById("registerLinkWrap");
	if (!wrap || !demoName) return;
	wrap.style.display = "block";
	wrap.innerHTML = `تم التسجيل: <a href="/app/demo-environment/${encodeURIComponent(
		demoName
	)}" target="_blank">فتح Demo Environment</a> · <a href="/app/query-report/Demo Environment Register" target="_blank">سجل البيئات</a>`;
}

function renderSummary() {
	const template = getSelectedTemplate();
	const demoNameEl = document.getElementById("demoName");
	const companyNameEl = document.getElementById("companyName");
	if (!template) {
		["summaryTemplate", "summaryIndustry", "summaryScale", "summaryRecords", "summaryCompany", "summaryLanguage"].forEach(
			(id) => {
				const node = document.getElementById(id);
				if (node) node.textContent = "-";
			}
		);
		return;
	}

	if (document.getElementById("summaryTemplate")) document.getElementById("summaryTemplate").textContent = template.template_name;
	if (document.getElementById("summaryIndustry")) document.getElementById("summaryIndustry").textContent = template.industry || "-";
	if (document.getElementById("summaryScale")) document.getElementById("summaryScale").textContent = template.scale || "-";
	if (document.getElementById("summaryRecords")) {
		document.getElementById("summaryRecords").textContent = `${template.total_estimated_records || 0} سجل تقريبًا`;
	}
	if (document.getElementById("summaryCompany")) {
		const demo = demoNameEl ? (demoNameEl.value || "").trim() : "";
		const company = companyNameEl ? (companyNameEl.value || "").trim() : "";
		document.getElementById("summaryCompany").textContent = `${demo || "-"} / ${company || "-"}`;
	}
	if (document.getElementById("summaryLanguage")) {
		document.getElementById("summaryLanguage").textContent = formatLanguage(
			document.getElementById("language")?.value
		);
	}
}

function refreshTemplateSelection() {
	document.querySelectorAll("[data-template-card]").forEach((card) => {
		card.classList.toggle("is-selected", card.dataset.templateCard === (selectedTemplate && selectedTemplate.name));
	});
	renderSummary();
}

function suggestDemoName(template) {
	if (!template) return "Live Demo";
	const stamp = new Date().toISOString().slice(0, 16).replace("T", " ");
	return `${template.template_name} — ${stamp}`;
}

function suggestCompanyName(template) {
	if (!template) return "Live Demo Company";
	const stamp = new Date().toISOString().slice(0, 10);
	return `${template.template_name} Company — ${stamp}`;
}

function syncCompanyFromDemoName() {
	if (companyNameManual) return;
	const demoNameEl = document.getElementById("demoName");
	const companyNameEl = document.getElementById("companyName");
	if (!demoNameEl || !companyNameEl) return;
	const demo = (demoNameEl.value || "").trim();
	if (!demo) return;
	if (!demo.includes("Company")) {
		companyNameEl.value = `${demo} — Company`;
	} else {
		companyNameEl.value = demo;
	}
	renderSummary();
}

function applyTemplate(templateName) {
	selectedTemplate = templates.find((t) => t.name === templateName) || null;
	refreshTemplateSelection();

	if (selectedTemplate) {
		const demoNameEl = document.getElementById("demoName");
		const companyNameEl = document.getElementById("companyName");
		if (demoNameEl && companyNameEl) {
			const currentDemoName = demoNameEl.value.trim();
			const currentCompanyName = companyNameEl.value.trim();
			if (!currentDemoName || currentDemoName === (wizard.defaults && wizard.defaults.demo_name)) {
				demoNameEl.value = suggestDemoName(selectedTemplate);
			}
			if (!companyNameManual && (!currentCompanyName || currentCompanyName === (wizard.defaults && wizard.defaults.company_name))) {
				companyNameEl.value = suggestCompanyName(selectedTemplate);
			}
		}
		setStatus(`تم اختيار قالب "${selectedTemplate.template_name}" — اضغط «التالي» أو «ديمو سريع».`, "success");
	}
}

function filterTemplates() {
	const searchEl = document.getElementById("templateSearch");
	const search = searchEl ? (searchEl.value || "").trim().toLowerCase() : "";
	document.querySelectorAll("[data-template-card]").forEach((card) => {
		const matchesIndustry = currentIndustry === "all" || card.dataset.industry === currentIndustry;
		const matchesSearch = !search || (card.dataset.search || "").includes(search);
		card.style.display = matchesIndustry && matchesSearch ? "block" : "none";
	});
}

function updateStepIndicator(currentKey) {
	document.querySelectorAll("[data-step-chip]").forEach((chip) => {
		chip.classList.toggle("is-active", chip.dataset.stepChip === currentKey);
	});
}

function goToStep(step) {
	currentWizardStep = Math.max(1, Math.min(3, step));
	document.querySelectorAll("[data-wizard-step]").forEach((panel) => {
		panel.classList.toggle("is-active", Number(panel.dataset.wizardStep) === currentWizardStep);
	});
	const prevBtn = document.getElementById("prevStepBtn");
	const nextBtn = document.getElementById("nextStepBtn");
	if (prevBtn) prevBtn.disabled = currentWizardStep <= 1;
	if (nextBtn) {
		nextBtn.textContent = currentWizardStep >= 3 ? "—" : "التالي";
		nextBtn.style.visibility = currentWizardStep >= 3 ? "hidden" : "visible";
	}
	updateStepIndicator(STEP_KEYS[currentWizardStep - 1] || "template");
	if (currentWizardStep === 3) renderSummary();
}

function applySiteIndustryFilter() {
	const hint = wizard?.site_context?.suggested_industry;
	if (!hint) return;
	currentIndustry = hint;
	document.querySelectorAll(".filter-chip").forEach((chip) => {
		chip.classList.toggle("is-active", chip.dataset.industry === hint);
	});
	filterTemplates();
}

function buildProgressList(events) {
	if (!events || !events.length) {
		return [
			["التمهيد", "قيد الانتظار"],
			["تسجيل Demo Environment", "قيد الانتظار"],
			["إنشاء الشركة", "قيد الانتظار"],
			["توليد البيانات", "قيد الانتظار"],
		];
	}
	return events.map((item) => [item.step || item.stage || "خطوة", item.status || ""]);
}

function renderProgress(state) {
	const panel = document.getElementById("progressPanel");
	if (!panel) return;

	const progress = Math.max(0, Math.min(100, Number(state?.progress || 0)));
	const status = state?.status || "Generating";
	const message = state?.message || "جاري التنفيذ";
	const events = buildProgressList(state?.recent_events || []);
	panel.classList.add("is-visible");

	const progressFill = document.getElementById("progressFill");
	const progressPercent = document.getElementById("progressPercent");
	const progressTitle = document.getElementById("progressTitle");
	const progressSubtitle = document.getElementById("progressSubtitle");
	const progressList = document.getElementById("progressList");

	if (progressFill) progressFill.style.width = `${progress}%`;
	if (progressPercent) progressPercent.textContent = `${progress}%`;
	if (progressTitle) progressTitle.textContent = message;
	if (progressSubtitle) {
		progressSubtitle.textContent = state?.job?.name
			? `Job: ${state.job.name}`
			: state?.demo_name
				? `Demo Environment: ${state.demo_name}`
				: "نتابع التسجيل والنشر خطوة بخطوة.";
	}
	if (progressList) {
		progressList.innerHTML = events.map((item) => `<li><strong>${item[0]}</strong><span>${item[1]}</span></li>`).join("");
	}

	if (status === "Generating") {
		goToStep(3);
		updateStepIndicator("review");
	}
}

async function pollProgress(demoName) {
	if (pollTimer) clearInterval(pollTimer);
	pollTimer = setInterval(async () => {
		try {
			const state = await apiCall("erpgenex_demo_studio.demo_studio.page.demo_wizard.demo_wizard.get_demo_progress", {
				demo_name: demoName,
			});
			renderProgress(state);
			if (state?.status === "Ready") {
				clearInterval(pollTimer);
				setStatus("تم تسجيل الديمو وإنشاء البيانات بنجاح.", "success");
				showRegisterLink(state.demo_name || demoName);
				const launchBtn = document.getElementById("launchBtn");
				if (launchBtn) {
					launchBtn.disabled = false;
					launchBtn.textContent = "تسجيل ونشر الديمو";
				}
				if (state.redirect_url) {
					window.location.href = state.redirect_url;
				}
			} else if (state?.status === "Error") {
				clearInterval(pollTimer);
				setStatus(state.message || "حدث خطأ أثناء النشر", "error");
				const launchBtn = document.getElementById("launchBtn");
				if (launchBtn) {
					launchBtn.disabled = false;
					launchBtn.textContent = "تسجيل ونشر الديمو";
				}
			}
		} catch (error) {
			setStatus(error.message || "تعذر تحديث التقدم", "error");
		}
	}, 2000);
}

async function launchDemo(options = {}) {
	const template = options.template ? templates.find((t) => t.name === options.template) : getSelectedTemplate();
	if (!template) {
		setStatus("اختر قالبًا أولًا (الخطوة 1) أو استخدم «ديمو سريع».", "error");
		goToStep(1);
		return;
	}
	selectedTemplate = template;

	const demoNameEl = document.getElementById("demoName");
	const companyNameEl = document.getElementById("companyName");
	const languageEl = document.getElementById("language");
	const launchModeEl = document.getElementById("launchMode");

	const demoName = options.demo_name || (demoNameEl ? (demoNameEl.value || "").trim() : "");
	const companyName = options.company_name || (companyNameEl ? (companyNameEl.value || "").trim() : "");
	const language = options.language || (languageEl ? languageEl.value : "ar");
	const launchMode = launchModeEl ? launchModeEl.value : "guided";

	const payload = {
		template: template.name,
		demo_name: demoName || suggestDemoName(template),
		company_name: companyName || suggestCompanyName(template),
		language,
		launch_mode: launchMode,
	};

	const launchBtn = document.getElementById("launchBtn");
	const expressBtn = document.getElementById("expressBtn");
	[launchBtn, expressBtn].forEach((btn) => {
		if (btn) {
			btn.disabled = true;
		}
	});
	if (launchBtn) launchBtn.textContent = "جاري التسجيل...";
	if (expressBtn) expressBtn.textContent = "جاري التسجيل...";
	setStatus("تم إرسال طلب التسجيل — إنشاء Demo Environment والبيانات.", "info");
	goToStep(3);

	try {
		const result = await apiCall("erpgenex_demo_studio.demo_studio.page.demo_wizard.demo_wizard.start_demo_generation", {
			demo_data: JSON.stringify(payload),
		});
		if (!result || !result.success) {
			throw new Error(result?.error || "تعذر تسجيل الديمو");
		}
		showRegisterLink(result.demo_name);
		if (result.status === "Ready") {
			const state = await apiCall("erpgenex_demo_studio.demo_studio.page.demo_wizard.demo_wizard.get_demo_progress", {
				demo_name: result.demo_name,
			});
			renderProgress(state);
			setStatus(result.message || "تم تسجيل الديمو بنجاح.", "success");
			if (launchBtn) {
				launchBtn.disabled = false;
				launchBtn.textContent = "تسجيل ونشر الديمو";
			}
			if (expressBtn) {
				expressBtn.disabled = false;
				expressBtn.textContent = "ديمو سريع — تسجيل الآن";
			}
			if (state?.redirect_url) {
				window.location.href = state.redirect_url;
			}
			return;
		}
		renderProgress({
			progress: 5,
			status: "Generating",
			message: "تم تسجيل Demo Environment — جارٍ توليد البيانات...",
			demo_name: result.demo_name,
			recent_events: [],
		});
		await pollProgress(result.demo_name);
	} catch (error) {
		setStatus(error.message || "تعذر التسجيل", "error");
	} finally {
		if (launchBtn) {
			launchBtn.disabled = false;
			launchBtn.textContent = "تسجيل ونشر الديمو";
		}
		if (expressBtn) {
			expressBtn.disabled = false;
			expressBtn.textContent = "ديمو سريع — تسجيل الآن";
		}
	}
}

async function expressQuickDemo() {
	const recommended = wizard?.recommended_template || templates[0];
	if (recommended) {
		applyTemplate(recommended.name);
	}
	const languageEl = document.getElementById("language");
	const language = languageEl ? languageEl.value : "ar";
	setStatus("جاري تسجيل ديمو سريع بالقالب المقترح...", "info");
	try {
		const result = await apiCall("erpgenex_demo_studio.demo_studio.page.demo_wizard.demo_wizard.quick_register_demo", {
			template: recommended?.name || "",
			language,
		});
		if (!result?.success) {
			throw new Error(result?.error || "تعذر التسجيل السريع");
		}
		if (recommended) {
			const demoNameEl = document.getElementById("demoName");
			if (demoNameEl && result.demo_name) demoNameEl.value = result.demo_name;
		}
		showRegisterLink(result.demo_name);
		if (result.status === "Ready") {
			setStatus(result.message || "تم التسجيل السريع.", "success");
			if (result.redirect_url) window.location.href = result.redirect_url;
			return;
		}
		renderProgress({
			progress: 5,
			status: "Generating",
			message: "تم التسجيل — جارٍ توليد البيانات...",
			demo_name: result.demo_name,
		});
		goToStep(3);
		await pollProgress(result.demo_name);
	} catch (error) {
		// Fallback: same flow via wizard fields
		await launchDemo({ template: recommended?.name, language });
	}
}

function resetWizard() {
	const templateSearchEl = document.getElementById("templateSearch");
	const demoNameEl = document.getElementById("demoName");
	const companyNameEl = document.getElementById("companyName");
	const languageEl = document.getElementById("language");
	const launchModeEl = document.getElementById("launchMode");
	const registerWrap = document.getElementById("registerLinkWrap");

	companyNameManual = false;
	if (templateSearchEl) templateSearchEl.value = "";
	currentIndustry = wizard?.site_context?.suggested_industry || "all";
	document.querySelectorAll(".filter-chip").forEach((chip) => {
		chip.classList.toggle("is-active", chip.dataset.industry === currentIndustry);
	});
	document.querySelectorAll("[data-template-card]").forEach((card) => {
		card.style.display = "block";
	});
	selectedTemplate = wizard.recommended_template || templates[0] || null;
	if (demoNameEl) demoNameEl.value = (wizard.defaults && wizard.defaults.demo_name) || "Live Demo";
	if (companyNameEl) companyNameEl.value = (wizard.defaults && wizard.defaults.company_name) || "Live Demo Company";
	if (languageEl) languageEl.value = (wizard.defaults && wizard.defaults.language) || "ar";
	if (launchModeEl) launchModeEl.value = "guided";
	if (registerWrap) registerWrap.style.display = "none";
	filterTemplates();
	refreshTemplateSelection();
	goToStep(1);
	setStatus("تمت إعادة الضبط. اختر قالبًا أو «ديمو سريع».", "info");
}

function onNextStep() {
	if (currentWizardStep === 1 && !getSelectedTemplate()) {
		setStatus("اختر قالبًا من القائمة أولًا.", "error");
		return;
	}
	if (currentWizardStep === 2) {
		syncCompanyFromDemoName();
		renderSummary();
	}
	if (currentWizardStep < 3) {
		goToStep(currentWizardStep + 1);
	}
}

function onPrevStep() {
	if (currentWizardStep > 1) goToStep(currentWizardStep - 1);
}

function bindWizardUi() {
	const templateSearchEl = document.getElementById("templateSearch");
	const demoNameEl = document.getElementById("demoName");
	const companyNameEl = document.getElementById("companyName");
	const languageEl = document.getElementById("language");
	const launchBtn = document.getElementById("launchBtn");
	const resetBtn = document.getElementById("resetBtn");
	const expressBtn = document.getElementById("expressBtn");
	const nextBtn = document.getElementById("nextStepBtn");
	const prevBtn = document.getElementById("prevStepBtn");
	const advancedToggle = document.getElementById("advancedToggle");
	const advancedPanel = document.getElementById("advancedPanel");

	if (templateSearchEl) templateSearchEl.addEventListener("input", filterTemplates);
	if (demoNameEl) {
		demoNameEl.addEventListener("input", () => {
			syncCompanyFromDemoName();
			renderSummary();
		});
	}
	if (companyNameEl) {
		companyNameEl.addEventListener("input", () => {
			companyNameManual = true;
			renderSummary();
		});
	}
	if (languageEl) {
		languageEl.addEventListener("change", () => {
			refreshCustomerLabels(languageEl.value);
			renderSummary();
		});
	}

	if (launchBtn) launchBtn.addEventListener("click", () => launchDemo());
	if (resetBtn) resetBtn.addEventListener("click", resetWizard);
	if (expressBtn) expressBtn.addEventListener("click", expressQuickDemo);
	if (nextBtn) nextBtn.addEventListener("click", onNextStep);
	if (prevBtn) prevBtn.addEventListener("click", onPrevStep);

	if (advancedToggle && advancedPanel) {
		advancedToggle.addEventListener("click", () => {
			const open = advancedPanel.classList.toggle("is-open");
			advancedToggle.setAttribute("aria-expanded", open ? "true" : "false");
		});
	}

	document.querySelectorAll(".filter-chip").forEach((chip) => {
		chip.addEventListener("click", () => {
			currentIndustry = chip.dataset.industry || "all";
			document.querySelectorAll(".filter-chip").forEach((btn) => btn.classList.toggle("is-active", btn === chip));
			filterTemplates();
		});
	});

	document.querySelectorAll("[data-template-card]").forEach((card) => {
		card.addEventListener("click", () => applyTemplate(card.dataset.templateCard));
	});
}

function initWizard() {
	const languageEl = document.getElementById("language");
	const initialLang = languageEl ? languageEl.value : "ar";

	apiCall("erpgenex_demo_studio.demo_studio.page.demo_wizard.demo_wizard.get_wizard_payload", { lang: initialLang })
		.then((payload) => {
			wizard = payload || {};
		})
		.catch((err) => {
			console.error("Failed to fetch wizard payload:", err);
			wizard = {};
		})
		.finally(() => {
			templates = wizard.templates || [];
			selectedTemplate = wizard.recommended_template || templates[0] || null;
			currentIndustry = "all";
			pollTimer = null;

			applySiteIndustryFilter();
			bindWizardUi();
			refreshTemplateSelection();
			refreshCustomerLabels(initialLang);

			if (selectedTemplate) {
				applyTemplate(selectedTemplate.name);
			}
			goToStep(1);
		});
}

if (document.readyState === "loading") {
	document.addEventListener("DOMContentLoaded", initWizard);
} else {
	initWizard();
}
