import frappe
from frappe.model.document import Document
from frappe import _
import uuid
import json
from datetime import datetime

class DemoGenerationJob(Document):
	def before_save(self):
		self.generate_job_id()
		self.set_metadata()
	
	def generate_job_id(self):
		"""Generate unique job ID"""
		if not self.job_id:
			self.job_id = f"JOB-{uuid.uuid4().hex[:8].upper()}"
	
	def set_metadata(self):
		"""Set metadata fields"""
		if not self.started_by:
			self.started_by = frappe.session.user
		if self.status == "Running" and not self.started_at:
			self.started_at = frappe.utils.now()
		if self.status == "Completed" and not self.completed_at:
			self.completed_at = frappe.utils.now()
			if self.started_at:
				start = datetime.strptime(self.started_at, "%Y-%m-%d %H:%M:%S.%f")
				end = datetime.strptime(self.completed_at, "%Y-%m-%d %H:%M:%S.%f")
				self.duration_seconds = int((end - start).total_seconds())
	
	def validate(self):
		"""Validate job"""
		self.validate_unique_job_name()
	
	def validate_unique_job_name(self):
		"""Ensure job name is unique"""
		if self.job_name:
			existing = frappe.db.exists("Demo Generation Job", {"job_name": self.job_name, "name": ["!=", self.name]})
			if existing:
				frappe.throw(_("Job name already exists"))
	
	def update_progress(self, current_step, total_steps, progress):
		"""Update job progress"""
		self.current_step = current_step
		self.total_steps = total_steps
		self.progress = progress
		self.save()
	
	def add_log_entry(self, log_data):
		"""Add log entry to job log"""
		current_log = []
		if self.job_log:
			try:
				current_log = json.loads(self.job_log)
			except json.JSONDecodeError:
				current_log = []
		
		log_data["timestamp"] = frappe.utils.now()
		current_log.append(log_data)
		self.job_log = json.dumps(current_log, indent=2)
		self.save()
	
	def mark_completed(self):
		"""Mark job as completed"""
		self.status = "Completed"
		self.progress = 100
		self.save()
	
	def mark_failed(self, error_message, error_traceback=None):
		"""Mark job as failed"""
		self.status = "Failed"
		self.error_message = error_message
		if error_traceback:
			self.error_traceback = error_traceback
		self.save()
	
	def mark_cancelled(self):
		"""Mark job as cancelled"""
		self.status = "Cancelled"
		self.save()

@frappe.whitelist()
def cancel_job(job_name):
	"""Cancel a running job"""
	job = frappe.get_doc("Demo Generation Job", job_name)
	if not job.is_cancellable:
		frappe.throw(_("This job cannot be cancelled"))
	if job.status not in ["Pending", "Running"]:
		frappe.throw(_("Can only cancel pending or running jobs"))
	
	job.cancel_requested = 1
	job.save()
	return True

@frappe.whitelist()
def get_job_status(job_name):
	"""Get current status of a job"""
	job = frappe.get_doc("Demo Generation Job", job_name)
	return {
		"status": job.status,
		"progress": job.progress,
		"current_step": job.current_step,
		"total_steps": job.total_steps,
		"records_created": job.records_created,
		"records_failed": job.records_failed,
		"error_message": job.error_message
	}
