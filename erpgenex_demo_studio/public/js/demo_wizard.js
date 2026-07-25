// Demo Wizard - Simple initialization script
let wizard, templates, selectedTemplate, currentIndustry, pollTimer;

	function getCookie(name) {
		const value = `; ${document.cookie}`;
		const parts = value.split(`; ${name}=`);
		if (parts.length === 2) return parts.pop().split(';').shift();
		return '';
	}

	async function apiCall(method, args = {}) {
		const response = await fetch(`/api/method/${method}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json',
				'X-Frappe-CSRF-Token': (window.frappe && frappe.csrf_token) || getCookie('csrf_token') || ''
			},
			credentials: 'same-origin',
			body: JSON.stringify(args)
		});

		const raw = await response.text();
		let payload = {};
		try {
			payload = raw ? JSON.parse(raw) : {};
		} catch (e) {
			payload = { message: raw };
		}

		if (!response.ok) {
			throw new Error(extractError(payload) || 'تعذر الاتصال بالخادم');
		}

		return payload.message;
	}

	function extractError(payload) {
		if (!payload) return '';
		if (payload._server_messages) {
			try {
				const messages = JSON.parse(payload._server_messages);
				const first = messages.map(item => {
					try { return JSON.parse(item).message || item; } catch (e) { return item; }
				}).filter(Boolean)[0];
				if (first) return first;
			} catch (e) {
				return payload._server_messages;
			}
		}
		return payload.message || payload.exception || payload.exc || '';
	}

	function formatLanguage(value) {
		return value === 'ar' ? 'العربية' : 'English';
	}

	function getSelectedTemplate() {
		return templates.find(t => t.name === selectedTemplate?.name) || selectedTemplate;
	}

	function setStatus(message, kind = 'info') {
		const el = document.getElementById('statusAlert');
		if (el) {
			el.className = `alert ${kind}`;
			el.textContent = message;
		}
	}

	function renderSummary() {
		const template = getSelectedTemplate();
		if (!template) {
			if (document.getElementById('summaryTemplate')) document.getElementById('summaryTemplate').textContent = '-';
			if (document.getElementById('summaryIndustry')) document.getElementById('summaryIndustry').textContent = '-';
			if (document.getElementById('summaryScale')) document.getElementById('summaryScale').textContent = '-';
			if (document.getElementById('summaryRecords')) document.getElementById('summaryRecords').textContent = '-';
			if (document.getElementById('summaryCompany')) document.getElementById('summaryCompany').textContent = '-';
			if (document.getElementById('summaryLanguage')) document.getElementById('summaryLanguage').textContent = '-';
			return;
		}

		if (document.getElementById('summaryTemplate')) document.getElementById('summaryTemplate').textContent = template.template_name;
		if (document.getElementById('summaryIndustry')) document.getElementById('summaryIndustry').textContent = template.industry || '-';
		if (document.getElementById('summaryScale')) document.getElementById('summaryScale').textContent = template.scale || '-';
		if (document.getElementById('summaryRecords')) document.getElementById('summaryRecords').textContent = `${template.total_estimated_records || 0} سجل تقريبًا`;
		if (document.getElementById('summaryCompany')) {
			document.getElementById('summaryCompany').textContent = document.getElementById('companyName').value || document.getElementById('demoName').value || '-';
		}
		if (document.getElementById('summaryLanguage')) {
			document.getElementById('summaryLanguage').textContent = formatLanguage(document.getElementById('language').value);
		}
	}

	function refreshTemplateSelection() {
		document.querySelectorAll('[data-template-card]').forEach(card => {
			card.classList.toggle('is-selected', card.dataset.templateCard === (selectedTemplate && selectedTemplate.name));
		});
		renderSummary();
	}

	function applyTemplate(templateName) {
		selectedTemplate = templates.find(t => t.name === templateName) || null;
		refreshTemplateSelection();

		if (selectedTemplate) {
			const demoNameEl = document.getElementById('demoName');
			const companyNameEl = document.getElementById('companyName');
			if (demoNameEl && companyNameEl) {
				const currentDemoName = demoNameEl.value.trim();
				const currentCompanyName = companyNameEl.value.trim();
				if (!currentDemoName || currentDemoName === (wizard.defaults && wizard.defaults.demo_name)) {
					demoNameEl.value = selectedTemplate.template_name;
				}
				if (!currentCompanyName || currentCompanyName === (wizard.defaults && wizard.defaults.company_name)) {
					companyNameEl.value = `${selectedTemplate.template_name} Company`;
				}
			}
			setStatus(`تم اختيار قالب "${selectedTemplate.template_name}"`, 'success');
		}
	}

	function filterTemplates() {
		const searchEl = document.getElementById('templateSearch');
		const search = searchEl ? (searchEl.value || '').trim().toLowerCase() : '';
		document.querySelectorAll('[data-template-card]').forEach(card => {
			const matchesIndustry = currentIndustry === 'all' || card.dataset.industry === currentIndustry;
			const matchesSearch = !search || (card.dataset.search || '').includes(search);
			card.style.display = matchesIndustry && matchesSearch ? 'block' : 'none';
		});
	}

	function updateStepIndicator(currentKey) {
		document.querySelectorAll('[data-step-chip]').forEach(chip => {
			chip.classList.toggle('is-active', chip.dataset.stepChip === currentKey);
		});
	}

	function buildProgressList(events) {
		if (!events || !events.length) {
			return [
				['التمهيد', 'قيد الانتظار'],
				['إنشاء الشركة', 'قيد الانتظار'],
				['توليد البيانات', 'قيد الانتظار'],
				['التحقق النهائي', 'قيد الانتظار']
			];
		}
		return events.map(item => [item.step || item.stage || 'خطوة', item.status || '']);
	}

	function renderProgress(state) {
		const panel = document.getElementById('progressPanel');
		if (!panel) return;
		
		const progress = Math.max(0, Math.min(100, Number(state?.progress || 0)));
		const status = state?.status || 'Generating';
		const message = state?.message || 'جاري التنفيذ';
		const events = buildProgressList(state?.recent_events || []);
		panel.classList.add('is-visible');
		
		const progressFill = document.getElementById('progressFill');
		const progressPercent = document.getElementById('progressPercent');
		const progressTitle = document.getElementById('progressTitle');
		const progressSubtitle = document.getElementById('progressSubtitle');
		const progressList = document.getElementById('progressList');
		
		if (progressFill) progressFill.style.width = `${progress}%`;
		if (progressPercent) progressPercent.textContent = `${progress}%`;
		if (progressTitle) progressTitle.textContent = message;
		if (progressSubtitle) progressSubtitle.textContent = state?.job?.name ? `Job: ${state.job.name}` : 'نتابع النشر خطوة بخطوة.';
		if (progressList) progressList.innerHTML = events.map(item => `<li><strong>${item[0]}</strong><span>${item[1]}</span></li>`).join('');

		if (status === 'Generating') {
			updateStepIndicator(progress < 35 ? 'template' : progress < 85 ? 'details' : 'review');
		}
	}

	async function pollProgress(demoName) {
		if (pollTimer) clearInterval(pollTimer);
		pollTimer = setInterval(async () => {
			try {
				const state = await apiCall('erpgenex_demo_studio.demo_studio.page.demo_wizard.demo_wizard.get_demo_progress', { demo_name: demoName });
				renderProgress(state);
				if (state?.status === 'Ready') {
					clearInterval(pollTimer);
					setStatus('تم إنشاء الديمو بنجاح ويمكنك فتحه الآن.', 'success');
					const launchBtn = document.getElementById('launchBtn');
					if (launchBtn) {
						launchBtn.disabled = false;
						launchBtn.textContent = 'بدء نشر الديمو';
					}
					if (state.redirect_url) {
						window.location.href = state.redirect_url;
					}
				} else if (state?.status === 'Error') {
					clearInterval(pollTimer);
					setStatus(state.message || 'حدث خطأ أثناء النشر', 'error');
					const launchBtn = document.getElementById('launchBtn');
					if (launchBtn) {
						launchBtn.disabled = false;
						launchBtn.textContent = 'بدء نشر الديمو';
					}
				}
			} catch (error) {
				setStatus(error.message || 'تعذر تحديث التقدم', 'error');
			}
		}, 2000);
	}

	async function launchDemo() {
		if (!selectedTemplate) {
			setStatus('اختر قالبًا أولًا قبل التشغيل.', 'error');
			return;
		}

		const demoNameEl = document.getElementById('demoName');
		const companyNameEl = document.getElementById('companyName');
		const languageEl = document.getElementById('language');
		const launchModeEl = document.getElementById('launchMode');
		
		const demoName = demoNameEl ? (demoNameEl.value || '').trim() : '';
		const companyName = companyNameEl ? (companyNameEl.value || '').trim() : '';
		const language = languageEl ? languageEl.value : 'ar';
		const launchMode = launchModeEl ? launchModeEl.value : 'guided';

		const payload = {
			template: selectedTemplate.name,
			demo_name: demoName || selectedTemplate.template_name,
			company_name: companyName || `${selectedTemplate.template_name} Company`,
			language,
			launch_mode: launchMode
		};

		const launchBtn = document.getElementById('launchBtn');
		if (launchBtn) {
			launchBtn.disabled = true;
			launchBtn.textContent = 'جاري تجهيز الديمو...';
		}
		setStatus('تم إرسال الطلب، جاري إنشاء البيئة الآن.', 'info');

		try {
			const result = await apiCall('erpgenex_demo_studio.demo_studio.page.demo_wizard.demo_wizard.start_demo_generation', {
				demo_data: JSON.stringify(payload)
			});
			if (!result || !result.success) {
				throw new Error(result?.error || 'تعذر بدء إنشاء الديمو');
			}
			renderProgress({ progress: 0, status: 'Generating', message: 'تم استلام الطلب، جارٍ بدء النشر...', recent_events: [] });
			updateStepIndicator('review');
			await pollProgress(result.demo_name);
		} catch (error) {
			setStatus(error.message || 'تعذر بدء النشر', 'error');
			if (launchBtn) {
				launchBtn.disabled = false;
				launchBtn.textContent = 'بدء نشر الديمو';
			}
		}
	}

	function resetWizard() {
		const templateSearchEl = document.getElementById('templateSearch');
		const demoNameEl = document.getElementById('demoName');
		const companyNameEl = document.getElementById('companyName');
		const languageEl = document.getElementById('language');
		const launchModeEl = document.getElementById('launchMode');
		
		if (templateSearchEl) templateSearchEl.value = '';
		currentIndustry = 'all';
		document.querySelectorAll('.filter-chip').forEach(chip => chip.classList.toggle('is-active', chip.dataset.industry === 'all'));
		document.querySelectorAll('[data-template-card]').forEach(card => card.style.display = 'block');
		selectedTemplate = wizard.recommended_template || templates[0] || null;
		if (demoNameEl) demoNameEl.value = (wizard.defaults && wizard.defaults.demo_name) || 'Live Demo';
		if (companyNameEl) companyNameEl.value = (wizard.defaults && wizard.defaults.company_name) || 'Live Demo Company';
		if (languageEl) languageEl.value = (wizard.defaults && wizard.defaults.language) || 'ar';
		if (launchModeEl) launchModeEl.value = 'guided';
		refreshTemplateSelection();
		updateStepIndicator('template');
		setStatus('تمت إعادة الضبط. اختر قالبًا ثم ابدأ من جديد.', 'info');
	}

	function initWizard() {
		// Fetch wizard payload via API
		apiCall('erpgenex_demo_studio.demo_studio.page.demo_wizard.demo_wizard.get_wizard_payload')
			.then(payload => {
				wizard = payload || {};
			})
			.catch(err => {
				console.error('Failed to fetch wizard payload:', err);
				wizard = {};
			})
			.finally(() => {
				templates = wizard.templates || [];
				selectedTemplate = wizard.recommended_template || templates[0] || null;
				currentIndustry = 'all';
				pollTimer = null;

				refreshTemplateSelection();
				renderSummary();

				const templateSearchEl = document.getElementById('templateSearch');
				const demoNameEl = document.getElementById('demoName');
				const companyNameEl = document.getElementById('companyName');
				const languageEl = document.getElementById('language');
				const launchBtn = document.getElementById('launchBtn');
				const resetBtn = document.getElementById('resetBtn');

				if (templateSearchEl) templateSearchEl.addEventListener('input', filterTemplates);
				if (demoNameEl) demoNameEl.addEventListener('input', renderSummary);
				if (companyNameEl) companyNameEl.addEventListener('input', renderSummary);
				if (languageEl) languageEl.addEventListener('change', renderSummary);

				if (launchBtn) launchBtn.addEventListener('click', launchDemo);
				if (resetBtn) resetBtn.addEventListener('click', resetWizard);

				document.querySelectorAll('.filter-chip').forEach(chip => {
					chip.addEventListener('click', () => {
						currentIndustry = chip.dataset.industry || 'all';
						document.querySelectorAll('.filter-chip').forEach(btn => btn.classList.toggle('is-active', btn === chip));
						filterTemplates();
					});
				});

				document.querySelectorAll('[data-template-card]').forEach(card => {
					card.addEventListener('click', () => applyTemplate(card.dataset.templateCard));
				});

				if (selectedTemplate) {
					applyTemplate(selectedTemplate.name);
				}
				updateStepIndicator('template');
			});
	}

	// Initialize when DOM is ready
	if (document.readyState === 'loading') {
		document.addEventListener('DOMContentLoaded', initWizard);
	} else {
		initWizard();
	}
