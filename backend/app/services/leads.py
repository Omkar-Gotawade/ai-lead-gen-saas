"""Lead management service."""
from typing import Optional, List
from uuid import UUID
import csv
import io
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.lead import Lead
from ..schemas.lead import LeadCreate, LeadUpdate, LeadListResponse
from .audit_logger import AuditLogger
from ..config import settings
from .validation import normalize_email, sanitize_text


class LeadService:
    """Service class for lead management operations."""
    
    def __init__(self, db: Session):
        """
        Initialize LeadService.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_leads(self, page: int = 1, page_size: int = 50, org_id: Optional[UUID] = None) -> LeadListResponse:
        """
        Get paginated list of leads for an organization.

        Args:
            page: Page number (1-indexed)
            page_size: Number of leads per page
            org_id: Organization/User ID to filter leads

        Returns:
            LeadListResponse: Paginated lead data
        """
        # Calculate offset
        offset = (page - 1) * page_size

        # Build query with org_id filter
        query = self.db.query(Lead)
        if org_id:
            query = query.filter(Lead.org_id == org_id)

        # Get total count
        total = query.count()

        # Get paginated leads
        leads = query.order_by(Lead.created_at.desc())\
            .offset(offset)\
            .limit(page_size)\
            .all()

        return LeadListResponse(
            total=total,
            page=page,
            page_size=page_size,
            leads=leads
        )
    
    def get_lead(self, lead_id: UUID, org_id: Optional[UUID] = None) -> Optional[Lead]:
        """
        Get a single lead by ID, optionally filtered by organization.

        Args:
            lead_id: Lead UUID
            org_id: Organization/User ID to restrict access

        Returns:
            Optional[Lead]: Lead object or None
        """
        query = self.db.query(Lead).filter(Lead.id == lead_id)
        if org_id:
            query = query.filter(Lead.org_id == org_id)
        return query.first()
    
    def create_lead(self, lead_data: LeadCreate, org_id: Optional[UUID] = None) -> Lead:
        """
        Create a new lead.
        
        Args:
            lead_data: Lead creation data
            
        Returns:
            Lead: Created lead object
        """
        email = normalize_email(str(lead_data.email))
        first_name = sanitize_text(lead_data.first_name, max_len=100)
        last_name = sanitize_text(lead_data.last_name, max_len=100)
        company = sanitize_text(lead_data.company, max_len=255)

        if not first_name or not last_name or not email:
            raise ValueError("first_name, last_name, and email are required")

        # Duplicate protection per org/user
        existing = self.db.query(Lead).filter(
            Lead.org_id == org_id,
            func.lower(Lead.email) == email
        ).first()

        if existing:
            if settings.LEAD_DUPLICATE_STRATEGY == "update":
                existing.first_name = first_name
                existing.last_name = last_name
                existing.full_name = f"{first_name} {last_name}"
                existing.company = company
                self.db.commit()
                self.db.refresh(existing)
                return existing
            raise ValueError("Duplicate lead for this user/org")

        # Generate full name
        full_name = f"{first_name} {last_name}"
        
        lead = Lead(
            org_id=org_id,
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            email=email,
            company=company,
            title=getattr(lead_data, 'title', None),
            industry=getattr(lead_data, 'industry', None),
            phone=getattr(lead_data, 'phone', None),
            source=lead_data.source,
            linkedin_url=getattr(lead_data, 'linkedin_url', None),
            job_title=getattr(lead_data, 'job_title', None),
            seniority=getattr(lead_data, 'seniority', None),
            company_size=getattr(lead_data, 'company_size', None),
            location=getattr(lead_data, 'location', None),
            research_notes=getattr(lead_data, 'research_notes', None),
        )
        
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead
    
    def update_lead(self, lead_id: UUID, lead_data: LeadUpdate, user_id: Optional[UUID] = None) -> Optional[Lead]:
        """
        Update a lead.

        Args:
            lead_id: Lead UUID
            lead_data: Lead update data
            user_id: User ID for audit logging

        Returns:
            Optional[Lead]: Updated lead or None if not found
        """
        lead = self.get_lead(lead_id)
        if not lead:
            return None

        # Track DNC changes for audit logging
        dnc_changed = False
        old_dnc_value = lead.do_not_contact

        # Update fields if provided
        update_data = lead_data.model_dump(exclude_unset=True)

        if 'email' in update_data and update_data['email']:
            update_data['email'] = normalize_email(str(update_data['email']))

        for field in ['first_name', 'last_name', 'company', 'title', 'industry', 'location', 'research_notes', 'source', 'linkedin_url', 'job_title', 'seniority', 'company_size', 'dnc_reason']:
            if field in update_data:
                max_len = 5000 if field == 'research_notes' else 255
                update_data[field] = sanitize_text(update_data[field], max_len=max_len)

        # Check if DNC status is being changed
        if 'do_not_contact' in update_data:
            new_dnc_value = update_data['do_not_contact']
            if old_dnc_value != new_dnc_value:
                dnc_changed = True

        for field, value in update_data.items():
            setattr(lead, field, value)

        # Update full_name if first_name or last_name changed
        if 'first_name' in update_data or 'last_name' in update_data:
            lead.full_name = f"{lead.first_name} {lead.last_name}"

        self.db.commit()
        self.db.refresh(lead)

        # Audit log DNC changes
        if dnc_changed:
            AuditLogger.log_dnc_change(
                db=self.db,
                lead_id=lead_id,
                user_id=user_id,
                old_value=old_dnc_value,
                new_value=lead.do_not_contact,
                reason="Manual update via API"
            )

        return lead
    
    def delete_lead(self, lead_id: UUID) -> bool:
        """
        Delete a lead.
        
        Args:
            lead_id: Lead UUID
            
        Returns:
            bool: True if deleted, False if not found
        """
        lead = self.get_lead(lead_id)
        if not lead:
            return False
        
        self.db.delete(lead)
        self.db.commit()
        return True
    
    def create_leads_from_csv(self, csv_content: bytes, org_id: Optional[UUID] = None) -> dict:
        """
        Create multiple leads from CSV file.
        
        Expected CSV columns: first_name, last_name, email, company (optional)
        
        Args:
            csv_content: CSV file content as bytes
            
        Returns:
            int: Number of leads created
            
        Raises:
            ValueError: If CSV format is invalid
        """
        # Decode bytes to string
        csv_string = csv_content.decode('utf-8')
        csv_file = io.StringIO(csv_string)
        
        # Read CSV
        reader = csv.DictReader(csv_file)
        
        # Validate required columns
        required_columns = {'first_name', 'last_name', 'email'}
        if not required_columns.issubset(set(reader.fieldnames or [])):
            raise ValueError(f"CSV must contain columns: {', '.join(required_columns)}")
        
        created_count = 0
        skipped_count = 0
        duplicate_count = 0
        
        for row in reader:
            try:
                first_name = sanitize_text(row['first_name'], max_len=100)
                last_name = sanitize_text(row['last_name'], max_len=100)
                email = normalize_email(row['email'])
                company = sanitize_text(row.get('company', ''), max_len=255)

                if not first_name or not last_name or not email:
                    skipped_count += 1
                    continue

                existing = None
                if org_id:
                    existing = self.db.query(Lead).filter(
                        Lead.org_id == org_id,
                        func.lower(Lead.email) == email
                    ).first()

                if existing:
                    duplicate_count += 1
                    if settings.LEAD_DUPLICATE_STRATEGY == 'update':
                        existing.first_name = first_name
                        existing.last_name = last_name
                        existing.full_name = f"{first_name} {last_name}"
                        existing.company = company
                        created_count += 1
                    continue

                # Create lead from CSV row
                full_name = f"{first_name} {last_name}"
                
                lead = Lead(
                    first_name=first_name,
                    last_name=last_name,
                    full_name=full_name,
                    email=email,
                    company=company or None,
                    org_id=org_id,
                    source='csv_upload'
                )
                
                self.db.add(lead)
                created_count += 1
            except Exception as e:
                # Skip invalid rows
                print(f"Skipping row due to error: {e}")
                skipped_count += 1
                continue
        
        self.db.commit()
        return {
            "added": created_count,
            "skipped": skipped_count,
            "duplicates": duplicate_count,
        }
