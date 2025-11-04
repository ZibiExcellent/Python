
import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Table )
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


# Usuwanie starej bazy danych
DB_FILE = "lab.db"
# if os.path.exists(DB_FILE):
#     os.remove(DB_FILE)

# Połączenie z bazą SQLite
engine = create_engine(f"sqlite:///{DB_FILE}", echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# Relacja wiele-do-wielu: Subject <-> Experiment
subject_experiment = Table(
    "subject_experiment", Base.metadata,
    Column("subject_id", Integer, ForeignKey("subjects.id")),
    Column("experiment_id", Integer, ForeignKey("experiments.id"))
    )

# MODELE

class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    type = Column(Integer)
    finished = Column(Boolean, default=False)

    # relacja 1:N z DataPoint
    data_points = relationship("DataPoint", back_populates="experiment")

    # relacja N:M z Subject
    subjects = relationship("Subject", secondary=subject_experiment, back_populates="experiments")


class DataPoint(Base):
    __tablename__ = "data_points"
    id = Column(Integer, primary_key=True)
    real_value = Column(Float)
    target_value = Column(Float)

    experiment_id = Column(Integer, ForeignKey("experiments.id"))
    experiment = relationship("Experiment", back_populates="data_points")


class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True)
    gdpr_accepted = Column(Boolean, default=False)

    experiments = relationship("Experiment", secondary=subject_experiment, back_populates="subjects")

# Tworzenie tabel
# Base.metadata.create_all(engine)

# Dodanie danych

# 2 eksperymenty
exp1 = Experiment(title="Test A", type=1)
exp2 = Experiment(title="Test B", type=2)
session.add_all([exp1, exp2])
session.commit()

# 10 punktów danych
points = [ DataPoint(real_value=i * 1.1, target_value=i * 1.5, experiment=exp1 if i < 5 else exp2)
           for i in range(10)  ]

session.add_all(points)
session.commit()

# Wyświetlenie danych
print("\nEksperymenty:")
for exp in session.query(Experiment).all():
    print(f"{exp.id}: {exp.title}, finished={exp.finished}")

print("\nPunkty danych:")
for dp in session.query(DataPoint).all():
    print(f"{dp.id}: {dp.real_value} -> {dp.target_value}, experiment_id={dp.experiment_id}")

# Aktualizacja eksperymentów
for exp in session.query(Experiment).all():
    exp.finished = True
session.commit()

# Usunięcie danych
session.query(DataPoint).delete()
session.query(Experiment).delete()
session.commit()

# Utwórz nowe eksperymenty
exp1 = Experiment(title="Nowy A", type=1)
exp2 = Experiment(title="Nowy B", type=2)
session.add_all([exp1, exp2])
session.commit()

# Dodaj Subjecty i relacje
sub1 = Subject(gdpr_accepted=True)
sub2 = Subject(gdpr_accepted=False)
exp1.subjects.append(sub1)
exp2.subjects.extend([sub1, sub2])
session.add_all([sub1, sub2])
session.commit()

print("\nSubiekty i ich eksperymenty:")
for sub in session.query(Subject).all():
    print(f"Subject {sub.id}, GDPR: {sub.gdpr_accepted}, Experiments: {[e.title for e in sub.experiments]}")
