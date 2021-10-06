from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import functions

Base = declarative_base()


def compile_query(query):
    from sqlalchemy.dialects import postgresql
    return str(query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


class Patient(Base):
    __tablename__ = "patient"

    id = Column(Integer, primary_key=True, index=True)
    demographics = Column(JSONB)
    creation_date = Column(DateTime, nullable=False, server_default=functions.now())

    diagnoses = relationship("Diagnosis", back_populates="patient")


class Diagnosis(Base):
    __tablename__ = "diagnosis"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient.id"))
    diagnosis_type_id = Column(Integer, ForeignKey("configuration.id"), nullable=False)
    details = Column(JSONB)
    creation_date = Column(DateTime, nullable=False, server_default=functions.now())
    previous_diagnosis = Column(Integer, nullable=True)

    patient = relationship("Patient", back_populates="diagnoses")


