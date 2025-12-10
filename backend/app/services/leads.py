"""Lead management service."""
from typing import Optional, List
from uuid import UUID
import csv
import io
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.lead import Lead
from ..schemas.lead import LeadCreate, LeadUpdate, LeadListResponse


class LeadService:
    """Service class for lead management operations."""
    
    def __init__(self, db: Session):
        """
        Initialize LeadService.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_leads(self, page: int = 1, page_size: int = 50) -> LeadListResponse:
        """
        Get paginated list of leads.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of leads per page
            
        Returns:
            LeadListResponse: Paginated lead data
        """
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total count
        total = self.db.query(func.count(Lead.id)).scalar()
        
        # Get paginated leads
        leads = self.db.query(Lead)\
            .order_by(Lead.created_at.desc())\
            .offset(offset)\
            .limit(page_size)\
            .all()
        
        return LeadListResponse(
            total=total,
            page=page,
            page_size=page_size,
            leads=leads
        )
    
    def get_lead(self, lead_id: UUID) -> Optional[Lead]:
        """
        Get a single lead by ID.
        
        Args:
            lead_id: Lead UUID
            
        Returns:
            Optional[Lead]: Lead object or None
        """
        return self.db.query(Lead).filter(Lead.id == lead_id).first()
    
    def create_lead(self, lead_data: LeadCreate) -> Lead:
        """
        Create a new lead.
        
        Args:
            lead_data: Lead creation data
            
        Returns:
            Lead: Created lead object
        """
        # Generate full name
        full_name = f"{lead_data.first_name} {lead_data.last_name}"
        
        lead = Lead(
            first_name=lead_data.first_name,
            last_name=lead_data.last_name,
            full_name=full_name,
            email=lead_data.email,
            company=lead_data.company,
            title=getattr(lead_data, 'title', None),
            industry=getattr(lead_data, 'industry', None),
            phone=getattr(lead_data, 'phone', None),
            source=lead_data.source
        )
        
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead
    
    def update_lead(self, lead_id: UUID, lead_data: LeadUpdate) -> Optional[Lead]:
        """
        Update a lead.
        
        Args:
            lead_id: Lead UUID
            lead_data: Lead update data
            
        Returns:
            Optional[Lead]: Updated lead or None if not found
        """
        lead = self.get_lead(lead_id)
        if not lead:
            return None
        
        # Update fields if provided
        update_data = lead_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(lead, field, value)
        
        # Update full_name if first_name or last_name changed
        if 'first_name' in update_data or 'last_name' in update_data:
            lead.full_name = f"{lead.first_name} {lead.last_name}"
        
        self.db.commit()
        self.db.refresh(lead)
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
    
    def create_leads_from_csv(self, csv_content: bytes) -> int:
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
        
        for row in reader:
            try:
                # Create lead from CSV row
                full_name = f"{row['first_name']} {row['last_name']}"
                
                lead = Lead(
                    first_name=row['first_name'].strip(),
                    last_name=row['last_name'].strip(),
                    full_name=full_name,
                    email=row['email'].strip(),
                    company=row.get('company', '').strip() or None,
                    source='csv_upload'
                )
                
                self.db.add(lead)
                created_count += 1
            except Exception as e:
                # Skip invalid rows
                print(f"Skipping row due to error: {e}")
                continue
        
        self.db.commit()
        return created_count
