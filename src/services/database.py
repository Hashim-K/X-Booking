"""Database service for managing bookings, accounts, and slot availability."""

from datetime import datetime, date, time as time_type
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, DateTime, 
    Date, Time, Text, ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool
import json
import os

Base = declarative_base()


class Account(Base):
    """User account for making bookings."""
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    netid = Column(String(100), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)  # TODO: Consider encryption
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    bookings = relationship("Booking", back_populates="account", cascade="all, delete-orphan")
    booking_logs = relationship("BookingLog", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Account(id={self.id}, netid='{self.netid}', is_active={self.is_active})>"


class Booking(Base):
    """Individual booking record."""
    __tablename__ = 'bookings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)
    booking_date = Column(Date, nullable=False, index=True)
    time_slot = Column(Time, nullable=False, index=True)
    location = Column(String(50), nullable=False, index=True)  # 'Fitness', 'X1', 'X3'
    sub_location = Column(String(50), nullable=True)  # 'X1 A', 'X1 B', 'X3 A', 'X3 B'
    status = Column(String(20), nullable=False, default='pending', index=True)  # pending, confirmed, failed, cancelled
    booking_reference = Column(String(100), nullable=True)  # Reference from TU Delft system
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    account = relationship("Account", back_populates="bookings")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('account_id', 'booking_date', 'time_slot', name='uix_account_date_time'),
        CheckConstraint("status IN ('pending', 'confirmed', 'failed', 'cancelled')", name='check_status'),
        CheckConstraint("location IN ('Fitness', 'X1', 'X3')", name='check_location'),
    )
    
    def __repr__(self):
        return f"<Booking(id={self.id}, account_id={self.account_id}, date={self.booking_date}, time={self.time_slot}, location='{self.location}', status='{self.status}')>"


class SlotAvailability(Base):
    """Cached slot availability information."""
    __tablename__ = 'slot_availability'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    location = Column(String(50), nullable=False, index=True)
    sub_location = Column(String(50), nullable=True, index=True)
    booking_date = Column(Date, nullable=False, index=True)
    time_slot = Column(Time, nullable=False, index=True)
    is_available = Column(Boolean, nullable=False, default=True)
    total_capacity = Column(Integer, nullable=True)
    remaining_capacity = Column(Integer, nullable=True)
    last_checked = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('location', 'sub_location', 'booking_date', 'time_slot', name='uix_slot_unique'),
        CheckConstraint("location IN ('Fitness', 'X1', 'X3')", name='check_location_avail'),
    )
    
    def __repr__(self):
        return f"<SlotAvailability(location='{self.location}', date={self.booking_date}, time={self.time_slot}, available={self.is_available})>"


class SnipeJob(Base):
    """Scheduled booking attempt (snipe job)."""
    __tablename__ = 'snipe_jobs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    target_date = Column(Date, nullable=False, index=True)
    target_time = Column(Time, nullable=False, index=True)
    location = Column(String(50), nullable=False, index=True)
    sub_location = Column(String(50), nullable=True)
    priority = Column(Integer, nullable=False, default=1)  # Lower = higher priority
    scheduled_execution = Column(DateTime, nullable=False, index=True)  # When to execute (xx:00:01)
    status = Column(String(20), nullable=False, default='scheduled', index=True)  # scheduled, running, completed, failed
    assigned_accounts = Column(Text, nullable=False)  # JSON array of account IDs
    consecutive_hours = Column(Integer, default=1, nullable=False)
    time_window_start = Column(Time, nullable=True)
    time_window_end = Column(Time, nullable=True)
    result = Column(Text, nullable=True)  # JSON with results
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    executed_at = Column(DateTime, nullable=True)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('target_date', 'target_time', 'location', 'sub_location', name='uix_snipe_unique'),
        CheckConstraint("status IN ('scheduled', 'running', 'completed', 'failed', 'cancelled')", name='check_snipe_status'),
        CheckConstraint("location IN ('Fitness', 'X1', 'X3')", name='check_location_snipe'),
    )
    
    def __repr__(self):
        return f"<SnipeJob(id={self.id}, target={self.target_date} {self.target_time}, location='{self.location}', status='{self.status}')>"
    
    def get_assigned_accounts(self) -> List[int]:
        """Parse assigned_accounts JSON."""
        try:
            return json.loads(self.assigned_accounts) if self.assigned_accounts else []
        except json.JSONDecodeError:
            return []
    
    def set_assigned_accounts(self, account_ids: List[int]):
        """Set assigned_accounts as JSON."""
        self.assigned_accounts = json.dumps(account_ids)
    
    def get_result(self) -> Optional[Dict[str, Any]]:
        """Parse result JSON."""
        try:
            return json.loads(self.result) if self.result else None
        except json.JSONDecodeError:
            return None
    
    def set_result(self, result_data: Dict[str, Any]):
        """Set result as JSON."""
        self.result = json.dumps(result_data)


class BookingLog(Base):
    """Audit log for booking attempts."""
    __tablename__ = 'booking_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False, index=True)
    action = Column(String(20), nullable=False, index=True)  # attempt, success, failure, cancel
    booking_date = Column(Date, nullable=False, index=True)
    time_slot = Column(Time, nullable=False)
    location = Column(String(50), nullable=False)
    sub_location = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)  # How long the attempt took
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    account = relationship("Account", back_populates="booking_logs")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("action IN ('attempt', 'success', 'failure', 'cancel')", name='check_action'),
        CheckConstraint("location IN ('Fitness', 'X1', 'X3')", name='check_location_log'),
    )
    
    def __repr__(self):
        return f"<BookingLog(id={self.id}, account_id={self.account_id}, action='{self.action}', timestamp={self.timestamp})>"


class DatabaseService:
    """Service for managing database operations."""
    
    def __init__(self, db_path: str = "bookings.db"):
        """Initialize database service.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.engine = None
        self.SessionLocal = None
        
    def initialize_db(self):
        """Initialize database connection and create tables."""
        # Use absolute path
        if not os.path.isabs(self.db_path):
            self.db_path = os.path.abspath(self.db_path)
            
        # Create engine
        self.engine = create_engine(
            f'sqlite:///{self.db_path}',
            connect_args={'check_same_thread': False},
            poolclass=StaticPool
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create all tables
        Base.metadata.create_all(bind=self.engine)
        print(f"✓ Database initialized: {self.db_path}")
        
    def get_session(self) -> Session:
        """Get a new database session."""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize_db() first.")
        return self.SessionLocal()
    
    # Account Management
    def add_account(self, netid: str, password: str) -> Optional[Account]:
        """Add a new account."""
        session = self.get_session()
        try:
            account = Account(netid=netid, password=password)
            session.add(account)
            session.commit()
            session.refresh(account)
            return account
        except Exception as e:
            session.rollback()
            print(f"Error adding account: {e}")
            return None
        finally:
            session.close()
    
    def get_accounts(self, is_active: Optional[bool] = None) -> List[Account]:
        """Get all accounts, optionally filtered by active status."""
        session = self.get_session()
        try:
            query = session.query(Account)
            if is_active is not None:
                query = query.filter(Account.is_active == is_active)
            return query.all()
        finally:
            session.close()
    
    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        """Get account by ID."""
        session = self.get_session()
        try:
            return session.query(Account).filter(Account.id == account_id).first()
        finally:
            session.close()
    
    def get_account_by_netid(self, netid: str) -> Optional[Account]:
        """Get account by netid."""
        session = self.get_session()
        try:
            return session.query(Account).filter(Account.netid == netid).first()
        finally:
            session.close()
    
    def update_account(self, account_id: int, **kwargs) -> Optional[Account]:
        """Update account fields."""
        session = self.get_session()
        try:
            account = session.query(Account).filter(Account.id == account_id).first()
            if account:
                for key, value in kwargs.items():
                    if hasattr(account, key):
                        setattr(account, key, value)
                account.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(account)
            return account
        except Exception as e:
            session.rollback()
            print(f"Error updating account: {e}")
            return None
        finally:
            session.close()
    
    def delete_account(self, account_id: int) -> bool:
        """Delete an account."""
        session = self.get_session()
        try:
            account = session.query(Account).filter(Account.id == account_id).first()
            if account:
                session.delete(account)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting account: {e}")
            return False
        finally:
            session.close()
    
    # Booking Management
    def create_booking(self, account_id: int, booking_date: date, time_slot: time_type,
                      location: str, sub_location: Optional[str] = None,
                      status: str = 'pending') -> Optional[Booking]:
        """Create a new booking."""
        session = self.get_session()
        try:
            booking = Booking(
                account_id=account_id,
                booking_date=booking_date,
                time_slot=time_slot,
                location=location,
                sub_location=sub_location,
                status=status
            )
            session.add(booking)
            session.commit()
            session.refresh(booking)
            return booking
        except Exception as e:
            session.rollback()
            print(f"Error creating booking: {e}")
            return None
        finally:
            session.close()
    
    def get_bookings(self, account_id: Optional[int] = None, 
                    booking_date: Optional[date] = None,
                    status: Optional[str] = None) -> List[Booking]:
        """Get bookings with optional filters."""
        session = self.get_session()
        try:
            query = session.query(Booking)
            if account_id is not None:
                query = query.filter(Booking.account_id == account_id)
            if booking_date is not None:
                query = query.filter(Booking.booking_date == booking_date)
            if status is not None:
                query = query.filter(Booking.status == status)
            return query.order_by(Booking.booking_date, Booking.time_slot).all()
        finally:
            session.close()
    
    def get_booking_by_id(self, booking_id: int) -> Optional[Booking]:
        """Get booking by ID."""
        session = self.get_session()
        try:
            return session.query(Booking).filter(Booking.id == booking_id).first()
        finally:
            session.close()
    
    def update_booking_status(self, booking_id: int, status: str, 
                            booking_reference: Optional[str] = None,
                            error_message: Optional[str] = None) -> Optional[Booking]:
        """Update booking status."""
        session = self.get_session()
        try:
            booking = session.query(Booking).filter(Booking.id == booking_id).first()
            if booking:
                booking.status = status
                if booking_reference:
                    booking.booking_reference = booking_reference
                if error_message:
                    booking.error_message = error_message
                booking.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(booking)
            return booking
        except Exception as e:
            session.rollback()
            print(f"Error updating booking status: {e}")
            return None
        finally:
            session.close()
    
    def delete_booking(self, booking_id: int) -> bool:
        """Delete a booking."""
        session = self.get_session()
        try:
            booking = session.query(Booking).filter(Booking.id == booking_id).first()
            if booking:
                session.delete(booking)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting booking: {e}")
            return False
        finally:
            session.close()
    
    def can_account_book(self, account_id: int, booking_date: date, 
                        time_slot: time_type, location: str) -> bool:
        """Check if account can book this slot (no existing booking for same time)."""
        session = self.get_session()
        try:
            existing = session.query(Booking).filter(
                Booking.account_id == account_id,
                Booking.booking_date == booking_date,
                Booking.time_slot == time_slot,
                Booking.status.in_(['pending', 'confirmed'])
            ).first()
            return existing is None
        finally:
            session.close()
    
    # Slot Availability Management
    def update_slot_availability(self, location: str, booking_date: date, 
                                time_slot: time_type, is_available: bool,
                                sub_location: Optional[str] = None,
                                total_capacity: Optional[int] = None,
                                remaining_capacity: Optional[int] = None) -> SlotAvailability:
        """Update or create slot availability."""
        session = self.get_session()
        try:
            slot = session.query(SlotAvailability).filter(
                SlotAvailability.location == location,
                SlotAvailability.sub_location == sub_location,
                SlotAvailability.booking_date == booking_date,
                SlotAvailability.time_slot == time_slot
            ).first()
            
            if slot:
                slot.is_available = is_available
                slot.total_capacity = total_capacity
                slot.remaining_capacity = remaining_capacity
                slot.last_checked = datetime.utcnow()
            else:
                slot = SlotAvailability(
                    location=location,
                    sub_location=sub_location,
                    booking_date=booking_date,
                    time_slot=time_slot,
                    is_available=is_available,
                    total_capacity=total_capacity,
                    remaining_capacity=remaining_capacity
                )
                session.add(slot)
            
            session.commit()
            session.refresh(slot)
            return slot
        except Exception as e:
            session.rollback()
            print(f"Error updating slot availability: {e}")
            return None
        finally:
            session.close()
    
    def get_slot_availability(self, location: str, booking_date: date,
                            sub_location: Optional[str] = None) -> List[SlotAvailability]:
        """Get slot availability for a location and date."""
        session = self.get_session()
        try:
            query = session.query(SlotAvailability).filter(
                SlotAvailability.location == location,
                SlotAvailability.booking_date == booking_date
            )
            if sub_location:
                query = query.filter(SlotAvailability.sub_location == sub_location)
            return query.order_by(SlotAvailability.time_slot).all()
        finally:
            session.close()
    
    # Snipe Job Management
    def create_snipe_job(self, target_date: date, target_time: time_type,
                        location: str, priority: int, assigned_accounts: List[int],
                        scheduled_execution: datetime,
                        sub_location: Optional[str] = None,
                        consecutive_hours: int = 1,
                        time_window_start: Optional[time_type] = None,
                        time_window_end: Optional[time_type] = None) -> Optional[SnipeJob]:
        """Create a new snipe job."""
        session = self.get_session()
        try:
            job = SnipeJob(
                target_date=target_date,
                target_time=target_time,
                location=location,
                sub_location=sub_location,
                priority=priority,
                scheduled_execution=scheduled_execution,
                consecutive_hours=consecutive_hours,
                time_window_start=time_window_start,
                time_window_end=time_window_end
            )
            job.set_assigned_accounts(assigned_accounts)
            session.add(job)
            session.commit()
            session.refresh(job)
            return job
        except Exception as e:
            session.rollback()
            print(f"Error creating snipe job: {e}")
            return None
        finally:
            session.close()
    
    def get_snipe_jobs(self, status: Optional[str] = None) -> List[SnipeJob]:
        """Get snipe jobs, optionally filtered by status."""
        session = self.get_session()
        try:
            query = session.query(SnipeJob)
            if status:
                query = query.filter(SnipeJob.status == status)
            return query.order_by(SnipeJob.scheduled_execution).all()
        finally:
            session.close()
    
    def get_pending_snipe_jobs(self) -> List[SnipeJob]:
        """Get pending snipe jobs scheduled for execution."""
        return self.get_snipe_jobs(status='scheduled')
    
    def update_snipe_job_status(self, job_id: int, status: str,
                               result: Optional[Dict[str, Any]] = None) -> Optional[SnipeJob]:
        """Update snipe job status and result."""
        session = self.get_session()
        try:
            job = session.query(SnipeJob).filter(SnipeJob.id == job_id).first()
            if job:
                job.status = status
                if result:
                    job.set_result(result)
                if status in ['completed', 'failed']:
                    job.executed_at = datetime.utcnow()
                session.commit()
                session.refresh(job)
            return job
        except Exception as e:
            session.rollback()
            print(f"Error updating snipe job: {e}")
            return None
        finally:
            session.close()
    
    def delete_snipe_job(self, job_id: int) -> bool:
        """Delete a snipe job."""
        session = self.get_session()
        try:
            job = session.query(SnipeJob).filter(SnipeJob.id == job_id).first()
            if job:
                session.delete(job)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting snipe job: {e}")
            return False
        finally:
            session.close()
    
    # Booking Log Management
    def log_booking_attempt(self, account_id: int, action: str, booking_date: date,
                          time_slot: time_type, location: str,
                          sub_location: Optional[str] = None,
                          error_message: Optional[str] = None,
                          execution_time_ms: Optional[int] = None) -> Optional[BookingLog]:
        """Log a booking attempt."""
        session = self.get_session()
        try:
            log = BookingLog(
                account_id=account_id,
                action=action,
                booking_date=booking_date,
                time_slot=time_slot,
                location=location,
                sub_location=sub_location,
                error_message=error_message,
                execution_time_ms=execution_time_ms
            )
            session.add(log)
            session.commit()
            session.refresh(log)
            return log
        except Exception as e:
            session.rollback()
            print(f"Error logging booking attempt: {e}")
            return None
        finally:
            session.close()
    
    def get_booking_logs(self, account_id: Optional[int] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        action: Optional[str] = None) -> List[BookingLog]:
        """Get booking logs with optional filters."""
        session = self.get_session()
        try:
            query = session.query(BookingLog)
            if account_id is not None:
                query = query.filter(BookingLog.account_id == account_id)
            if start_date:
                query = query.filter(BookingLog.timestamp >= start_date)
            if end_date:
                query = query.filter(BookingLog.timestamp <= end_date)
            if action:
                query = query.filter(BookingLog.action == action)
            return query.order_by(BookingLog.timestamp.desc()).all()
        finally:
            session.close()
    
    def get_account_statistics(self, account_id: int) -> Dict[str, Any]:
        """Get statistics for an account."""
        session = self.get_session()
        try:
            total_bookings = session.query(Booking).filter(
                Booking.account_id == account_id
            ).count()
            
            confirmed_bookings = session.query(Booking).filter(
                Booking.account_id == account_id,
                Booking.status == 'confirmed'
            ).count()
            
            failed_bookings = session.query(Booking).filter(
                Booking.account_id == account_id,
                Booking.status == 'failed'
            ).count()
            
            total_attempts = session.query(BookingLog).filter(
                BookingLog.account_id == account_id
            ).count()
            
            success_rate = (confirmed_bookings / total_attempts * 100) if total_attempts > 0 else 0
            
            return {
                'total_bookings': total_bookings,
                'confirmed_bookings': confirmed_bookings,
                'failed_bookings': failed_bookings,
                'total_attempts': total_attempts,
                'success_rate': round(success_rate, 2)
            }
        finally:
            session.close()


# Global database instance
db_service = DatabaseService()


if __name__ == "__main__":
    # Test database initialization
    db_service.initialize_db()
    
    # Test adding accounts
    print("\nAdding test accounts...")
    acc1 = db_service.add_account("test1", "pass1")
    acc2 = db_service.add_account("test2", "pass2")
    print(f"Added: {acc1}, {acc2}")
    
    # Test creating booking
    print("\nCreating test booking...")
    from datetime import date, time
    booking = db_service.create_booking(
        account_id=acc1.id,
        booking_date=date(2025, 11, 17),
        time_slot=time(13, 0),
        location='X1',
        sub_location='X1 A',
        status='confirmed'
    )
    print(f"Created: {booking}")
    
    # Test logging
    print("\nLogging booking attempt...")
    log = db_service.log_booking_attempt(
        account_id=acc1.id,
        action='success',
        booking_date=date(2025, 11, 17),
        time_slot=time(13, 0),
        location='X1',
        sub_location='X1 A',
        execution_time_ms=1250
    )
    print(f"Logged: {log}")
    
    # Test statistics
    print("\nAccount statistics:")
    stats = db_service.get_account_statistics(acc1.id)
    print(stats)
    
    print("\n✓ All tests passed!")
