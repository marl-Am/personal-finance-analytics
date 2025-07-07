from datetime import datetime, timezone
from sqlalchemy import UUID, Boolean, DateTime, Integer
import uuid
from extensions import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(320), nullable=False, unique=True, index=True)

    username = db.Column(db.String(50), nullable=False, unique=True, index=True)

    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)

    password_hash = db.Column(db.String(255), nullable=False)
    salt = db.Column(db.String(32), nullable=False)

    # Timestamps with timezone awareness
    created_at = db.Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Soft delete
    deleted_at = db.Column(DateTime(timezone=True), nullable=True)

    # Account status flags
    is_active = db.Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Account active status, allows temporary account suspension",
    )

    is_verified = db.Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Email verification status, important for account security",
    )

    # Optimistic locking for concurrent updates
    version = db.Column(
        Integer,
        nullable=False,
        default=1,
        comment="Version number for optimistic locking, prevents race conditions",
    )


    def __repr__(self) -> str:
        """String representation of user."""
        return f"<User {self.username} ({self.email})>"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return self.display_name
